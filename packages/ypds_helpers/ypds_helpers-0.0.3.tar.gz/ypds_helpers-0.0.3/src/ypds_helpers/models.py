# SPDX-FileCopyrightText: 2025-present Anton Popov <a.popov.fizteh@gmail.com>
#
# SPDX-License-Identifier: MIT

from functools import partial
from typing import Literal, Union, Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import FunctionTransformer, StandardScaler, OrdinalEncoder
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import numpy.typing as npt

from .globals import translator, models
from .helpers import dispmay_item


def make_num_sanitizer(min_val: np.number, max_val: np.number) -> FunctionTransformer:
    """
    Создаёт трансформер, который заполняет все значения, выходящие за
    указанный диапазон значениями np.nan
    """

    def coerce_num_vals(data: np.ndarray, min_val: np.number, max_val: np.number):
        data = data.astype("float")
        data[data < min_val] = np.nan
        data[data > max_val] = np.nan
        return data

    return FunctionTransformer(
        func=coerce_num_vals,
        validate=True,
        kw_args={"min_val": min_val, "max_val": max_val},
        feature_names_out="one-to-one",
    )


def make_typo_corrector(correct_vals: list[str]) -> FunctionTransformer:
    """
    Простой корректировщик опечаток.

    Считает расстояния Хэмминга между словами и корректирует одиночную опечатку.
    """

    def correct_typo(word: Union[str, float], correct_vals: list[str]):
        if isinstance(word, (int, float)):
            return np.nan

        hamming_vals = {}
        for value in correct_vals:
            if len(word) != len(value):
                hamming_vals[value] = np.inf
            else:
                hamming_vals[value] = sum(ch1 != ch2 for ch1, ch2 in zip(word, value))

        min_dist = min(hamming_vals.values())
        if min_dist == 0:
            return word
        if min_dist == 1:
            for key, val in hamming_vals.items():
                if val == 1:
                    return key
        return np.nan

    vect = np.vectorize(
        partial(correct_typo, correct_vals=correct_vals), otypes=[object]
    )
    return FunctionTransformer(func=vect, feature_names_out="one-to-one")


def make_num_processor(min_val: np.number, max_val: np.number) -> Pipeline:
    """
    Создаёт препроцессор для численных данных.
    """
    return Pipeline(
        [
            ("sanitizer", make_num_sanitizer(min_val, max_val)),
            ("imputer", IterativeImputer()),
            ("num_scaler", StandardScaler()),
        ]
    )


# Предвижу, что возможно эта чусть будет помечена как ошибка во время ревью
# Я сознательно не стал использовать imputer перед кодированием, так как не
# вижу в нём смысла. Пропуски и неизвестные категории будут закодированы
# ординал энкодером как пропуски (np.nan), после чего IterativeImputer заполнит
# их подходящими значениями, поэтому я не понимаю зачем использовать imputer
# 2 раза (до и после энкодера).
def make_ord_processor(categories: list[str]) -> Pipeline:
    """
    Создаёт препроцессор для категориальных данных,
    которые будут кодироваться с помощью OrdinalEncoder.
    """
    return Pipeline(
        [
            ("typo_corrector", make_typo_corrector(categories)),
            (
                "ord_encoder",
                OrdinalEncoder(
                    categories=[categories],
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                ),
            ),
            ("imputer", IterativeImputer()),
            ("rounder", FunctionTransformer(np.round, feature_names_out="one-to-one")),
        ]
    )


def make_num_ord_processor(min_val: np.number, max_val: np.number) -> Pipeline:
    """
    Создаёт препроцессор для численных данных, которые по сути являются
    категориальными (аналог make_ord_processor).
    """

    return Pipeline(
        [
            ("sanitizer", make_num_sanitizer(min_val, max_val)),
            ("imputer", IterativeImputer()),
            ("rounder", FunctionTransformer(np.round, feature_names_out="one-to-one")),
        ]
    )


def show_search_result(search: GridSearchCV, n_results: int = 10) -> pd.DataFrame:
    """
    Возвращает датафрйем с основными результатами поиска по сетке.
    """
    df = pd.DataFrame(search.cv_results_)
    report_cols = [
        "rank_test_score",
        "mean_test_score",
        "mean_fit_time",
        "mean_score_time",
    ]
    report_cols.extend([col for col in df.columns if col.startswith("param_")])
    return df[report_cols].sort_values(by="rank_test_score").head(n_results).round(4)


def evaluate_params(grid: GridSearchCV):
    """
    Выводит максимальное значение метрики качества для значений гиперпараметров
    """
    df = pd.DataFrame(grid.cv_results_)
    params = [col for col in df.columns if col.startswith("param_")]

    for param in params:
        dispmay_item(
            df[[param, "mean_test_score", "rank_test_score"]]
            .groupby(param, sort=False)
            .agg({"mean_test_score": "max", "rank_test_score": "min"})
            .sort_values(by="mean_test_score", ascending=False)
            .head(10)
            .round(4)
        )


def grid_search(
    pipeline: Pipeline,
    grid: Union[list, dict],
    X_train: pd.DataFrame,
    y_train: Union[pd.DataFrame, np.ndarray],
    model: str,
    scoring: Union[Callable, str] = 'roc_auc',
    cv_method: Union[TimeSeriesSplit, int, None] = None,
    n_jobs: int = -1,
) -> None:
    """
    Осуществляет поиск по сетке, выводит и сохраняет результаты.
    """


    gs_kwargs = {
        "scoring": scoring,
        "cv": cv_method if cv_method else 5,
        "n_jobs": n_jobs,
        "verbose": 1,
    }
    grid_search_result = GridSearchCV(pipeline, grid, **gs_kwargs).fit(X_train, y_train)
    result = show_search_result(grid_search_result)
    dispmay_item(result)
    cols = ["mean_test_score", "mean_fit_time", "mean_score_time"]
    best_result = result.loc[result["rank_test_score"] == 1, cols].iloc[0].copy()
    models.loc[model, cols] = best_result
    translator.update(
        {
            "mean_test_score": "Ср. результат",
            "mean_fit_time": "Ср. длительность обучения",
            "mean_score_time": "Ср. длительность предсказания",
            "model": "Модель",
        }
    )
    models.at[model, "model"] = grid_search_result.best_estimator_
    models.sort_values("mean_test_score", ascending=False, inplace=True)
