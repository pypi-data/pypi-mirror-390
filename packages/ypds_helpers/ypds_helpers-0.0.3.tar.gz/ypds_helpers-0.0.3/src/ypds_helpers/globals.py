# SPDX-FileCopyrightText: 2025-present Anton Popov <a.popov.fizteh@gmail.com>
#
# SPDX-License-Identifier: MIT

from sklearn.model_selection import GridSearchCV
import pandas as pd

translator = {}
models: pd.DataFrame = pd.DataFrame()
scores: dict[str, float] = {}