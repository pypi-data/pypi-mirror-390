#!/usr/bin/env python3

from __future__ import annotations
from sheet_stream import (
    ColumnsTable, ListString, ListItems, ListColumnBody, ArrayString, TableDocuments, TableRow, TableTextKeyWord
)
from sheet_stream.type_utils import HeadCell


class ColumnBody(ListColumnBody):

    def __init__(self, col_name: HeadCell | str, col_body: list[str]):
        super().__init__(col_name, col_body)


class DictTextTable(TableDocuments):

    def __init__(self, body_list: list[ListColumnBody]):
        super().__init__(body_list)
