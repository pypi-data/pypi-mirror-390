#!/usr/bin/env python
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

Tools for converting Excel style column names

**Provides**

 * :func:`xls_column`


"""


def xls_column(column: int) -> str:
    """Converts column number to Excel like column name in A, B, C notation

    The Excel like notationis created for arbitrary numbers.
    Limitations of Excel implementations are not taken into account.

    :param column: Column number starting with 0
    :return: String with Excel like column

    """

    if column < 0:
        raise ValueError(f"Column number {column} is negative.")

    start_char = 65
    base = 26
    result = ""

    while True:
        if result:
            column -= 1  # subsequent digits start with `A` instead of `@`

        result += chr(start_char + int(column % base))
        column //= base

        if not column:
            break

    return result[::-1]
