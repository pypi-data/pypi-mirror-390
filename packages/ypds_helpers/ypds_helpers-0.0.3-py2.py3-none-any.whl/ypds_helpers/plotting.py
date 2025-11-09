# SPDX-FileCopyrightText: 2025-present Anton Popov <a.popov.fizteh@gmail.com>
#
# SPDX-License-Identifier: MIT

from typing import Sequence, Optional, cast
import math

import pandas as pd
import numpy as np
import numpy.typing as npt
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.ticker as ticker

from .data_handling import get_num_cols

def plot_hist(
    df: pd.DataFrame,
    col: str,
    ax: Optional[Axes] = None,
    hue: Optional[str] = None,
    annotate: bool = True,
    kde: bool = False,
    normalize: bool = False,
    **kwargs,
) -> Axes:
    """
    Строит гистрограмму c опциональным разбиением на категории.

    Параметры
    ----------
    - df: Датафрейм с данными
    - col: Название колонки, содержащей данные для построения гистограммы
    - ax: оси, на которых нужно строить гистограмму
    - hue: Наименование опционального столбца для разделения данных
    - annotate: Добавлят подписи к оси Х и заголовок графика
    - normalize: Нормировать гистограмму
    """
    if normalize:
        stat = "probability"
    else:
        stat = "count"

    ax = sns.histplot(
        df,
        x=col,
        hue=hue,
        discrete=pd.api.types.is_integer(df[col]),
        kde=kde,
        kde_kws={"bw_method": 0.6} if kde else None,
        edgecolor="white",
        stat=stat,
        common_norm=False,
        ax=ax,
        **kwargs,
    )
    if normalize:
        ax.set_ylabel("Плотность распределения")
    else:
        ax.set_ylabel("Количество")
    if annotate:
        ax.set_title(f'Гистограмма распределение признака\n"{col}"')
        ax.set_xlabel(col)
    else:
        ax.set_xlabel("")
    return ax


def plot_box(
    df: pd.DataFrame,
    col: str,
    ax: Optional[Axes] = None,
    hue: Optional[str] = None,
    annotate: bool = True,
    **kwargs,
):
    """
    Строит боксплот c опциональным разбиением на категории.

    Параметры
    ----------
    - df: Датафрейм с данными
    - col: Название колонки, содержащей данные для построения боксплота
    - ax: оси, на которых нужно строить боксплот
    - hue: Наименование опционального столбца для разделения данных
    - annotate: Добавлят подписи к оси Х и заголовок графика
    """
    ax = sns.boxplot(df, y=col, hue=hue, ax=ax, **kwargs)
    if annotate:
        ax.set_title(f'Боксплот распределение признака\n"{col}"')
        ax.set_xlabel(col)
    else:
        ax.set_xlabel("")
        ax.set_ylabel("")


def plot_numeric(
    df: pd.DataFrame,
    num_cols: Optional[list[str]] = None,
    title: str = "",
    hue: Optional[str] = None,
    normalize: bool = False,
    kde: bool = True,
    ncols: int = 2,
    scale: float = 2.5,
    **kwargs,
) -> None:
    """
    Функция для построения гистограмм и боксплотов по числовым признакам.

    Параметры:
    ----------
    - df: DataFrame с данными.
    - num_cols: Список числовых признаков для анализа.
    - title: Заголовок для графиков.
    - hue: Опциональный столбец для разделения данных по категориям.
    - normalize: Нормировать гистограмму
    - ncols: Количество столбцов для размещения графиков.
    - scale: Скейлинг фактор, определяющий размер
    """

    if num_cols is None:
        num_cols = get_num_cols(df)
    if len(num_cols) == 1:
        ncols = 1
    nrows = math.ceil(len(num_cols) / ncols)
    if ncols > 1:
        fig = plt.figure(
            layout="constrained", figsize=(scale * ncols * 2, scale * nrows)
        )
    else:
        fig = plt.figure(layout="constrained", figsize=(scale * 4, scale * nrows * 2))
    fig.suptitle(title, fontsize=16)
    subfigs = fig.subfigures(ncols=ncols, nrows=nrows, squeeze=True)
    if isinstance(subfigs, np.ndarray):
        subfigs = cast(list[Figure], subfigs.flatten())
    else:
        subfigs = [subfigs]
    for i, col in enumerate(num_cols):
        axs = subfigs[i].subplots(1, 2)
        if len(title) == 0 and len(num_cols) != 0:
            subfigs[i].suptitle(f"Распределение {col}")
        elif len(num_cols) > 1:
            subfigs[i].suptitle(col)
        plot_hist(
            df, col, axs[0], hue, annotate=False, normalize=normalize, kde=kde, **kwargs
        )
        plot_box(df, col, axs[1], hue, annotate=False, legend=False, gap=0.2, **kwargs)


def plot_cats(
    df: pd.DataFrame,
    cat_cols: Optional[list[str]] = None,
    hue: Optional[str] = None,
    title: str = "",
    ncols: int = 2,
    max_cats: int = 10,
    max_cats_alias: str = "all_other",
    **kwargs,
) -> None:
    """
    Функция для построения графиков распределения категориальных признаков.

    Параметры:
    ----------
    - df: DataFrame с данными.
    - cat_cols: Список категориальных признаков для анализа.
    - hue: Название категориального признака, по которому будут группирвоаться значения.
    - title: Заголовок для графиков.
    - ncols: Количество столбцов для размещения графиков.
    - max_cats: Максимальное количество категорий. Более мелкие категории будут
    объединены в одну категорию.
    - max_cats_alias: Назкание категории, которая обхединяет более мелкие категории.
    """

    if cat_cols is None:
        cat_cols = df.select_dtypes([object, "category"]).columns.to_list()
    if len(cat_cols) == 0:
        return
    scale = 3
    nrows = math.ceil(len(cat_cols) / ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(scale * ncols * 2, scale * nrows))
    fig.suptitle(title, fontsize=16)
    fig.set_layout_engine("constrained")
    try:
        axs = cast(Sequence[Axes], axs.flatten())
    except AttributeError:
        axs = cast(Sequence[Axes], [axs])
    for i, col in enumerate(cat_cols):

        if hue is not None:
            data = (
                df.groupby(hue)[col]
                .value_counts(normalize=True, ascending=False)
                .reset_index()
            )
            if data.shape[0] > max_cats:
                data.iloc[max_cats] = data.iloc[max_cats:].sum()
                data = data.iloc[: max_cats + 1]
                data = data.rename(index={data.index[max_cats]: max_cats_alias})
            sns.barplot(
                data,
                x=data.columns.difference([col, hue])[0],
                y=col,
                hue=hue,
                ax=axs[i],
                orient="y",
                **kwargs,
            )
            for container in axs[i].containers:
                axs[i].bar_label(
                    container, label_type="edge", padding=3, fmt=lambda x: f"{x:.0%}"  # type: ignore
                )
                x_min, x_max = axs[i].get_xlim()
                axs[i].set_xlim(x_min, x_max + (x_max - x_min) * 0.05)
        else:
            data = df[col].value_counts(ascending=False)
            if data.shape[0] > max_cats:
                data.iloc[max_cats] = data.iloc[max_cats:].sum()
                data = data.iloc[: max_cats + 1]
                data = data.rename(index={data.index[max_cats]: max_cats_alias})
            sns.barplot(data, ax=axs[i], orient="h", color="#8ebad9", **kwargs)  # type: ignore
            axs[i].bar_label(
                axs[i].containers[0],  # type: ignore
                label_type="edge",
                padding=5,
                fmt=lambda x: f"{int(x)} ({x/data.sum():.0%})",
            )
            x_min, x_max = axs[i].get_xlim()
            axs[i].set_xlim(x_min, x_max + (x_max - x_min) * 0.25)
        if len(cat_cols) > 1:
            axs[i].set_title(f"Распределение {col}", fontsize=14)
        axs[i].set_xlabel("")
        axs[i].set_ylabel("")
        axs[i].xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
    # Удалим лишние оси
    for i in range(len(cat_cols), nrows * ncols):
        axs[i].remove()

def show_residues(y_true: npt.ArrayLike, y_pred: npt.ArrayLike, title: str = "", **kwargs):
    """
    Строит графики распределения остатков

    Параметры
    --------
    - y_true: Истинные значения
    - y_pred: Предсказанные значения
    - title: Опциональный общий заголовок для всего изображения
    """
    data = pd.DataFrame()
    data["истина"] = y_true
    data["предсказание"] = y_pred
    data["остатки"] = data["предсказание"] - data["истина"]
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    if len(title):
        fig.suptitle(title)
    plot_hist(data, col="остатки", ax=axs[0], **kwargs)
    sns.scatterplot(data, x="истина", y="остатки", ax=axs[1], **kwargs)
    _ = axs[1].set_title(
        "Диаграмма рассеяния остатков\nв зависимости от истинных значений"
    )
    fig.tight_layout()