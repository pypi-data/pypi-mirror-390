#!/usr/bin/env python3

from __future__ import annotations

import os.path
import pandas as pd
from soup_files import File
from sheet_stream.erros import *
from sheet_stream.type_utils.enums import ColumnsTable, LibSheet
from sheet_stream.type_utils.metadata_file import MetaDataFile, MetaDataItem, get_hash_from_bytes


def contains(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> bool:
    """
        Verificar se um texto existe em lista de strings.
    """
    if case:
        if iqual:
            for x in values:
                if text == x:
                    return True
        else:
            for x in values:
                if text in x:
                    return True
    else:
        if iqual:
            for x in values:
                if text.upper() == x.upper():
                    return True
        else:
            for x in values:
                if text.upper() in x.upper():
                    return True
    return False


def find_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> int | None:
    """
        Verificar se um texto existe em lista de ‘strings’ se existir, retorna o índice da posição
    do texto na lista.
    """
    _idx: int | None = None
    if case:
        if iqual:
            for num, x in enumerate(values):
                if text == x:
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text in x:
                    _idx = num
                    break
    else:
        if iqual:
            for num, x in enumerate(values):
                if text.upper() == x.upper():
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text.upper() in x.upper():
                    _idx = num
                    break
    return _idx


def find_all_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> list[int]:
    """

    """
    items: list[int] = ListItems([])
    if iqual:
        for num, i in enumerate(values):
            if case:
                if i == text:
                    items.append(num)
            else:
                if text.lower() == i.lower():
                    items.append(num)
    else:
        for num, i in enumerate(values):
            if case:
                if text in i:
                    items.append(num)
            else:
                if text.lower() in i.lower():
                    items.append(num)
    return items


class ListItems(list):

    def __init__(self, items: list):
        super().__init__(items)

    @property
    def length(self) -> int:
        return len(self)

    @property
    def is_empty(self) -> bool:
        return self.length == 0

    def get(self, idx: int):
        return self[idx]


class ListString(ListItems):

    def __init__(self, items: list[str]):
        super().__init__(items)

    def contains(self, item: str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def find_index(self, item: str, *, case: bool = True, iqual: bool = False) -> int | None:
        return find_index(item, self, case=case, iqual=iqual)

    def find_all_index(self, item: str, *, case: bool = True, iqual: bool = False) -> list[int]:
        return find_all_index(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> str:
        return self[idx]

    def add_item(self, i: str):
        if isinstance(i, str):
            self.append(i)

    def add_items(self, items: list[str]):
        for item in items:
            self.add_item(item)


class ArrayString(ListString):
    """
        Classe para filtrar e manipular lista de strings.
    """

    def __init__(self, items: list[str]):
        super().__init__(items)

    def get_next_string(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a próxima string se existir, se não retorna None.
        """
        next_idx: int | None = self.get_next_index(text, iqual=iqual, case=case)
        return None if next_idx is None else self[next_idx]

    def get_next_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        next_idx: int | None = self.get_next_index(text, iqual=iqual, case=case)
        return ListString([]) if next_idx is None else ListString(self[next_idx:])

    def get_next_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _idx: int | None = self.find_index(text, iqual=iqual, case=case)
        if _idx is None:
            return None
        if _idx < 0:
            return None
        if _idx >= self.length - 1:
            return None
        return _idx + 1

    def get_back_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _final_idx: int | None = self.find_index(text, iqual=iqual, case=case)
        if _final_idx is None:
            return None
        if _final_idx <= 0:
            return None
        return _final_idx - 1

    def get_back_string(self, text: str, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a string anterior se existir, se não retorna None.
        """
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return None if _idx is None else self[_idx]

    def get_back_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return ListString([]) if _idx is None else ListString(self[:_idx])

    def get(self, idx: int) -> str:
        return self[idx]

    def find_text(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if (text is None) or (text == ""):
            raise ValueError(f'{__class__.__name__}: text is None')
        idx_item = self.find_index(text, iqual=iqual, case=case)
        return None if idx_item is None else self[idx_item]

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> ListString:
        list_idx: list[int] = find_all_index(text, self, case=case, iqual=iqual)
        if len(list_idx) == 0:
            return ListString([])

        new_values = ListString([])
        for idx in list_idx:
            new_values.append(self[idx])
        return new_values

    def count(self, text: str, *, iqual: bool = False, case: bool = True) -> int:
        count: int = 0
        if iqual:
            for i in self:
                if case:
                    if i == text:
                        count += 1
                else:
                    if text.lower() == i.lower():
                        count += 1
        else:
            for i in self:
                if case:
                    if text in i:
                        count += 1
                else:
                    if text.lower() in i.lower():
                        count += 1
        return count


class HeadCell(str):

    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class HeadValues(ListString):

    def __init__(self, head_items: list[HeadCell]):
        super().__init__(head_items)

    def contains(self, item: HeadCell | str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> HeadCell:
        return self[idx]

    def add_item(self, i: HeadCell | str):
        if isinstance(i, str):
            self.append(HeadCell(i))
        else:
            self.append(i)


class ListColumnBody(ArrayString):
    """
        Lista de strings nomeada para representar os dados da coluna de uma tabela.
    """

    def __init__(self, col_name: HeadCell | str, col_body: list[str]):
        super().__init__(col_body)
        if isinstance(col_name, str):
            col_name = HeadCell(col_name)
        self.col_name: HeadCell = col_name

    def __repr__(self):
        return f'{__class__.__name__}\nName: {self.col_name}\nValues:{super().__repr__()}'


class TableRow(ArrayString):
    """
        Lista de strings nomeada para representar os dados de uma linha de tabela.
    """

    def __init__(self, row_index: HeadCell | str, col_body: list[str]):
        super().__init__(col_body)
        if isinstance(row_index, str):
            row_index = HeadCell(row_index)
        self.row_index: HeadCell = row_index


class TableTextKeyWord(dict):
    """
    Dicionário com strings que apontam para listas de strings.
    """
    def __init__(self, body_list: list[ListColumnBody]):
        local_args: dict[HeadCell, ListColumnBody] = {}
        self.header: HeadValues = HeadValues([])
        if len(body_list) == 0:
            super().__init__(local_args)
        else:
            max_num: int = len(body_list[0])
            col: ListColumnBody
            for col in body_list:
                current_num: int = len(col)
                if current_num > max_num:
                    raise ListTableLargeError(
                        f'Coluna {col.col_name} excedeu o tamanho máximo da tabela -> {max_num}'
                    )
                elif current_num < max_num:
                    raise ListTableShortError(
                        f'Coluna {col.col_name} é menor que o tamanho minimo da tabela -> {max_num}'
                    )
                local_args[col.col_name] = col
                self.header.add_item(col.col_name)
            super().__init__(local_args)

    @property
    def length(self) -> int:
        if self.header.length == 0:
            return 0
        return len(self[self.header[0]])

    def contains(self, value: str, *, case: bool = True, iqual: bool = False) -> bool:
        cols = self.header
        element: ListColumnBody
        for c in cols:
            element = self[c]
            if element.contains(value, case=case, iqual=iqual):
                return True
        return False

    def set_column(self, col: ListColumnBody):
        """
        Adiciona ou atualiza uma coluna de tabela.
        """
        if col.length > self.length:
            raise ListTableLargeError(
                f'Coluna {col.col_name} excedeu o tamanho máximo da tabela'
            )
        elif col.length < self.length:
            raise ListTableShortError(
                f'Coluna {col.col_name} é menor que o tamanho minimo da tabela'
            )
        self[col.col_name] = col
        self.header.add_item(col.col_name)

    def get_column(self, col_name: str | HeadCell) -> ListColumnBody:
        if isinstance(col_name, str):
            col_name = HeadCell(col_name)
        return self[col_name]

    def get_row(self, idx: int) -> TableRow:
        _row: ArrayString = ArrayString([])
        _cols: HeadValues = self.header
        for c in _cols:
            _row.append(self[c][idx])
        return TableRow(f'{idx}', _row)

    def add_row(self, row: TableRow):
        _num_row = row.length
        _num_tb = self.length
        _cols = self.header
        if _num_row > _num_tb:
            raise RowLargeError()
        elif _num_row < _num_tb:
            raise RowShortError()

        for n, line in enumerate(row):
            self[_cols[n]].append(line)

    def update_row(self, row: TableRow):
        _num_row = row.length
        _num_tb = self.length
        _cols = self.header
        if _num_row > _num_tb:
            raise RowLargeError()
        elif _num_row < _num_tb:
            raise RowShortError()

        update_idx = int(row.row_index)
        for n, line in enumerate(row):
            self[_cols[n]][update_idx] = line


class TableDocuments(TableTextKeyWord):

    default_columns: list[ListColumnBody] = [
        ListColumnBody(ColumnsTable.KEY, ListString([])),
        ListColumnBody(ColumnsTable.NUM_PAGE, ListString([])),
        ListColumnBody(ColumnsTable.NUM_LINE, ListString([])),
        ListColumnBody(ColumnsTable.TEXT, ListString([])),
        ListColumnBody(ColumnsTable.FILE_NAME, ListString([])),
        ListColumnBody(ColumnsTable.FILETYPE, ListString([])),
        ListColumnBody(ColumnsTable.FILE_PATH, ListString([])),
        ListColumnBody(ColumnsTable.DIR, ListString([])),
    ]

    def __init__(self, body_list: list[ListColumnBody]):
        super().__init__(body_list)

    @property
    def columns(self) -> HeadValues:
        _cols = list(self.keys())
        return HeadValues([HeadCell(x) for x in _cols])

    def to_data(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self)

    @classmethod
    def create_void_dict(cls) -> TableDocuments:
        _default: list[ListColumnBody] = [
            ListColumnBody(ColumnsTable.KEY, ListString([])),
            ListColumnBody(ColumnsTable.NUM_PAGE, ListString([])),
            ListColumnBody(ColumnsTable.NUM_LINE, ListString([])),
            ListColumnBody(ColumnsTable.TEXT, ListString([])),
            ListColumnBody(ColumnsTable.FILE_NAME, ListString([])),
            ListColumnBody(ColumnsTable.FILETYPE, ListString([])),
            ListColumnBody(ColumnsTable.FILE_PATH, ListString([])),
            ListColumnBody(ColumnsTable.DIR, ListString([])),
        ]
        return cls(_default)

    @classmethod
    def create_void_df(cls) -> pd.DataFrame:
        return pd.DataFrame.from_dict(cls.create_void_dict())

    @classmethod
    def create_from_values(
                cls,
                values: list[str], *,
                page_num: str = 'nan',
                file_path: str = 'nan',
                dir_path: str = 'nan',
                file_type: str = 'nan',
            ) -> TableDocuments:
        max_num = len(values)
        if max_num < 1:
            return cls.create_void_dict()

        _items = [
            ListColumnBody(
                ColumnsTable.KEY, ListString([f'{x}' for x in range(0, max_num)])
            ),
            ListColumnBody(
                ColumnsTable.NUM_PAGE, ListString([page_num] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.NUM_LINE, ListString([f'{x+1}' for x in range(0, max_num)])
            ),
            ListColumnBody(
                ColumnsTable.TEXT, ListString(values)
            ),
            ListColumnBody(
                ColumnsTable.FILE_NAME, ListString([os.path.basename(file_path)] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.FILETYPE, ListString([file_type] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.FILE_PATH, ListString([file_path] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.DIR, ListString([dir_path] * max_num)
            ),
        ]
        return cls(_items)

    @classmethod
    def create_from_file_text(cls, file: File) -> TableDocuments:
        if not isinstance(file, File):
            return cls.create_void_dict()

        try:
            with open(file.absolute(), 'rt') as f:
                lines = ListString(f.readlines())
        except Exception as e:
            print(e)
            return cls.create_void_dict()
        else:
            return cls.create_from_values(
                lines,
                file_type=file.extension(),
                file_path=file.absolute(),
                dir_path=file.dirname(),
            )


def concat_table_documents(list_map: list[TableDocuments]) -> TableDocuments:
    if len(list_map) < 1:
        return TableDocuments.create_void_dict()
    _columns: HeadValues = list_map[0].columns
    list_values: list[ListColumnBody] = []
    text_table: TableDocuments
    col: ListColumnBody
    i: HeadCell

    for i in _columns:
        list_values.append(
            ListColumnBody(i, ListString([]))
        )
    for text_table in list_map:
        for col in list_values:
            col.extend(
                text_table[col.col_name]
            )
    return TableDocuments(list_values)


__all__ = [
    'contains', 'concat_table_documents', 'find_index', 'find_all_index',
    'ListItems', 'ListString', 'ArrayString', 'HeadCell', 'HeadValues',
    'ListColumnBody', 'TableRow', 'TableTextKeyWord', 'TableDocuments',
    'MetaDataItem', 'MetaDataFile', 'get_hash_from_bytes', 'LibSheet'
]





