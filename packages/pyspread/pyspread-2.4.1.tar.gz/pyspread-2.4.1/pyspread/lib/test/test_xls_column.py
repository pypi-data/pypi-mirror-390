# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

Tests for `xlsx.py`

"""

from contextlib import contextmanager
from pathlib import Path
import pytest
import sys

ORIGIN_PATH = Path(__file__).parent.parent.parent


@contextmanager
def insert_path(path):
    sys.path.insert(0, ORIGIN_PATH)
    yield
    sys.path.pop(0)


with insert_path(ORIGIN_PATH):
    from lib.xls_column import xls_column


test_params_excel_column = (
    (0, "A"),
    (1, "B"),
    (2, "C"),
    (23, "X"),
    (24, "Y"),
    (25, "Z"),
    (26, "AA"),
    (650, "YA"),
    (651, "YB"),
    (701, "ZZ"),
    (702, "AAA"),
    (703, "AAB"),
    (16383, "XFD"),
    (2**100+1, "BKOWAWZZAERONYJCMBBOJR"),
)


@pytest.mark.parametrize("column, result", test_params_excel_column)
def test_excel_column(column, result):
    """pytest for `excel_column`"""

    assert xls_column(column) == result
