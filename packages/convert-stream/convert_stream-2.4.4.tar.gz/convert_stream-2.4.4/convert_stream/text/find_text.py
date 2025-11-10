#!/usr/bin/env python3
from __future__ import annotations
from sheet_stream import ArrayString, contains, find_index, find_all_index


class FindText(object):
    """
        Filtrar palavras/strings em textos longos
    """
    def __init__(self, text_value: str, separator: str = ' '):
        """

        :param text_value: texto bruto a ser filtrado
        :param separator: separador de texto a ser usado durante o filtro
        :type  text_value: str
        :type  separator: str
        :return: None
        """
        self.array: ArrayString = ArrayString(text_value.split(separator))
        self.separator: str = separator

    @property
    def is_null(self) -> bool:
        return self.array.is_empty

    def contains(self, text: str, *, iqual: bool = False, case: bool = True) -> bool:
        return self.array.contains(text, iqual=iqual, case=case)

    def find_index(self, text: str, *, iqual: bool = False, case: bool = True) -> int | None:
        return self.array.find_index(text, iqual=iqual, case=case)

    def get_index(self, num: int) -> str | None:
        return self.array.get(num)

    def to_array(self) -> ArrayString:
        return ArrayString(self.array)

    def find(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find_text(text, iqual=iqual, case=case)

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> list[str]:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find_all(text, iqual=iqual, case=case)


class FindStrings(object):

    def __init__(self, key_words: list[str]):
        self.key_words: list[str] = key_words

    def find_all(self, values: list[str], *, iqual: bool = False, case: bool = True) -> ArrayString:
        final_values = ArrayString([])
        ignore_idx: list[int] = []

        for txt in self.key_words:
            all_idx: list[int] = find_all_index(txt, values, iqual=iqual, case=case)
            if len(all_idx) > 0:
                for i in all_idx:
                    if not i in ignore_idx:
                        final_values.append(values[i])
                        ignore_idx.append(i)
        return final_values
