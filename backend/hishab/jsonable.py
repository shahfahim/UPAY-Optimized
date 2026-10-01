"""Convert engine results (dataclasses, numpy, dates) to plain JSON types."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime

import numpy as np
import pandas as pd


def jsonable(x):
    if is_dataclass(x) and not isinstance(x, type):
        x = asdict(x)
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items() if not isinstance(v, pd.DataFrame)}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, pd.DataFrame):
        return None
    return x
