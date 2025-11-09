# SPDX-FileCopyrightText: 2025-present Anton Popov <a.popov.fizteh@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Optional, Union, cast

import numpy as np
import pandas as pd
import phik

from .helpers import dispmay_item
from .globals import translator

__all__ = ["show_df", "get_num_cols", "get_cat_cols", "print_unique_cat_vals", "highest_corrs"]


def show_df(df: pd.DataFrame, n: int = 5) -> None:
    """
    Выводит основную информацию о датафрейме.

    Параметры:
    ----------
    - df: DataFrame с данными.
    - n: Количество строк для отображения.
    """


    print(f"Первые {n} строк:")
    dispmay_item(df.head(n))
    try:
        temp = df.describe(include=[np.number])
        print("\nСтатистика по числовым столбцам:")
        dispmay_item(temp)
    except ValueError:
        print("\nНет числовых столбцов для отображения.")
    try:
        temp = df.describe(include=[object])
        print("\nСтатистика по категориальным столбцам:")
        dispmay_item(temp)
    except ValueError:
        print("\nНет категориальных столбцов для отображения.")
    print("\nИнформация о датафрейме:")
    df.info()


def get_num_cols(
    df: pd.DataFrame, exclude_cols: Optional[list[str]] = None
) -> list[str]:
    """
    Возвращает список числовых столбцов в датафрейме, исключая указанные колонки.

    Параметры
    ----------
    - df: Датафрейм с данными
    - exclude_cols: Список колонок, которые нужно исключить из результата
    """
    if exclude_cols is None:
        exclude_cols = []
    return list(df.drop(exclude_cols, axis=1).select_dtypes(np.number).columns)


def get_cat_cols(
    df: pd.DataFrame, exclude_cols: Optional[list[str]] = None
) -> list[str]:
    """
    Возвращает список категориальных столбцов в датафрейме, исключая указанные колонки.

    Параметры
    ----------
    - df: Датафрейм с данными
    - exclude_cols: Список колонок, которые нужно исключить из результата
    """
    if exclude_cols is None:
        exclude_cols = []
    return list(
        df.drop(exclude_cols, axis=1).select_dtypes([object, "category"]).columns
    )


def print_unique_cat_vals(
    dfs: Union[dict[str, pd.DataFrame], pd.DataFrame], exlculde: Optional[list[str]]
) -> None:
    """
    Выводит уникальные значения категориальных признаков.

    Может работать с отдельными датафреймами или с наборами (слоаврями) датафреймов.

    Параметры
    ---------
    - dfs: датафрейм или словарь датафреймов
    - exclude: список колонок, которые нужно исключить
    """

    def print_unique(df: pd.DataFrame) -> None:
        for j, col in enumerate(get_cat_cols(df, exclude_cols=exlculde), start=1):
            print(f'\t{j}. Признак "{col}". Уникальные значения:')
            print(f"\t {df[col].unique().tolist()}")

    print("Уникальные значения категориальных признаков:")
    if isinstance(dfs, pd.DataFrame):
        print_unique(dfs)
    else:
        for i, (df_name, df) in enumerate(dfs.items(), start=1):
            print(f"{i}. Датафрейм {df_name}:")
            print_unique(df)


def highest_corrs(
    df: pd.DataFrame,
    cols: Optional[list[str]] = None,
    interval_cols: Optional[list[str]] = None,
    num: int = 10,
) -> pd.DataFrame:
    """
    Функция для вычисления корреляций между парами числовых признаков

    Параметры:
    ----------
    - df: DataFrame с данными.
    - cols: Список числовых признаков для анализа.
    - interval_cols: Список численных признаков
    - num: Количество значений для вывода.
    """
    if cols is None:
        cols = list(df.columns)
    try:
        df = df.rename(translator, axis=1)
    except NameError:
        pass
    corr_matrix = cast(pd.DataFrame, df[cols].phik_matrix(interval_cols=interval_cols))  # type: ignore

    corrs = (
        corr_matrix.pipe(lambda x: x.where(np.triu(np.ones_like(x), k=1).astype(bool)))
        .stack()
        .dropna()
        .sort_values(key=abs, ascending=False)  # type: ignore
        .to_frame()
        .round(2)
        .head(num)
    )
    corrs = corrs.set_axis(["corrs"], axis=1)

    def signigicance(cor: float) -> str:
        cor = abs(cor)
        if cor < 0.25:
            return "отсутствует"
        if cor < 0.5:
            return "слабая"
        if cor < 0.75:
            return "средняя"
        return "сильная"

    corrs["значимость"] = corrs["corrs"].transform(signigicance)
    return corrs
