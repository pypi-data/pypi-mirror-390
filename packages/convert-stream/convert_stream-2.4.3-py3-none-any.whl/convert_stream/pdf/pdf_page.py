#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd

from convert_stream.mod_types.enums import LibPDF
from convert_stream.mod_types.table_types import (
    DictTextTable, ListString
)
from convert_stream.mod_types.modules import (
    ModPagePdf, PageObject, fitz
)
from sheet_stream.type_utils import MetaDataFile
from convert_stream.text.find_text import FindText, ArrayString


class ABCPagePdf(ABC):

    def __init__(self, mod_page: ModPagePdf, page_number: int):
        if page_number < 1:
            raise ValueError('page_number must be >= 1')
        self.mod_page: ModPagePdf = mod_page
        self.lib_pdf: LibPDF = LibPDF.NOT_IMPLEMENTED
        self.number_page: int = page_number
        self.metadata: MetaDataFile = MetaDataFile()

    @abstractmethod
    def get_width(self) -> float:
        pass

    @abstractmethod
    def get_height(self) -> float:
        pass

    @abstractmethod
    def extract_box(self):
        pass

    @abstractmethod
    def set_land_scape(self):
        pass

    @abstractmethod
    def is_land_scape(self) -> bool:
        pass

    @abstractmethod
    def set_rotation(self, num: int):
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass

    @classmethod
    def create_from_pypdf(cls, page: PageObject, number: int) -> ABCPagePdf:
        pass

    @classmethod
    def create_from_fitz(cls, page: fitz.Page, number: int) -> ABCPagePdf:
        pass


class ImplementPypdf(ABCPagePdf):

    def __init__(self, mod_page: ModPagePdf, page_number: int):
        super().__init__(mod_page, page_number)
        self.lib_pdf: LibPDF = LibPDF.PYPDF
        self.number_page: int = page_number
        self.mod_page: ModPagePdf = mod_page

    def set_rotation(self, num: int):
        try:
            self.mod_page.rotate(90)
        except Exception as e:
            print(e)

    def get_width(self) -> float:
        try:
            # mediaBox retorna RectangleObject
            return float(self.mod_page.mediabox.width)
        except Exception:
            return 0

    def get_height(self) -> float:
        try:
            return float(self.mod_page.mediabox.height)
        except Exception:
            return 0

    def set_land_scape(self):
        if self.is_land_scape():
            return
        try:
            # rotacionar para 90° (paisagem)
            self.mod_page.rotate(90)
        except Exception:
            pass

    def is_land_scape(self) -> bool:
        try:
            return self.get_width() > self.get_height()
        except Exception as err:
            print(f'Error: {err}')
            return False

    def extract_box(self):
        raise NotImplementedError()

    def to_string(self) -> str:
        try:
            t = self.mod_page.extract_text()
        except Exception as e:
            print(f'{__class__.__name__} {e}')
            return 'nas'
        else:
            if t is None:
                return 'nas'
            return t

    @classmethod
    def create_from_pypdf(cls, page: PageObject, number: int) -> ImplementPypdf:
        return cls(page, number)


class ImplementFitz(ABCPagePdf):

    def __init__(self, mod_page: ModPagePdf, page_number: int):
        super().__init__(mod_page, page_number)
        self.lib_pdf: LibPDF = LibPDF.FITZ
        self.number_page: int = page_number

    def set_rotation(self, num: int):
        try:
            self.mod_page.set_rotation(num)
        except Exception as e:
            print(e)

    def get_width(self) -> float:
        try:
            rect = self.mod_page.rect  # fitz.Rect
            return float(rect.width)
        except Exception:
            return 0

    def get_height(self) -> float:
        try:
            rect = self.mod_page.rect
            return float(rect.height)
        except Exception:
            return 0

    def set_land_scape(self):
        if self.is_land_scape():
            return
        try:
            # Rotaciona para 90 graus
            self.mod_page.set_rotation(-90)
        except Exception:
            pass

    def is_land_scape(self) -> bool:
        try:
            return self.get_width() > self.get_height()
        except Exception:
            return False

    def extract_box(self) -> fitz.TextPage:
        return self.mod_page.get_textpage()

    def to_string(self) -> str:
        try:
            text = self.mod_page.get_textpage().extractTEXT()
        except:
            return 'nas'
        else:
            if text is None:
                return 'nas'
            return text

    @classmethod
    def create_from_fitz(cls, page: fitz.Page, number: int) -> ABCPagePdf:
        return cls(page, number)


class PageDocumentPdf(object):

    def __init__(self, page_pdf: ABCPagePdf):
        self.implement_page_pdf: ABCPagePdf = page_pdf
        self.lib_pdf: LibPDF = page_pdf.lib_pdf

    @property
    def metadata(self) -> MetaDataFile:
        return self.implement_page_pdf.metadata

    @metadata.setter
    def metadata(self, metadata: MetaDataFile):
        self.implement_page_pdf.metadata = metadata

    def __repr__(self) -> str:
        return self.to_string()

    def __eq__(self, other: PageDocumentPdf) -> bool:
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(f'{self.number_page}_{self.to_string()}')

    @property
    def number_page(self) -> int:
        return self.implement_page_pdf.number_page

    @number_page.setter
    def number_page(self, num: int):
        self.implement_page_pdf.number_page = num

    def extract_box(self) -> fitz.TextPage:
        return self.implement_page_pdf.extract_box()

    def to_string(self) -> str:
        return self.implement_page_pdf.to_string()

    def to_list(self, separator: str = '\n') -> list[str]:
        txt = self.implement_page_pdf.to_string()
        if (txt is None) or (txt == 'nas'):
            return ListString([])
        return ListString(txt.split(separator))

    def to_dict(self, separator: str = '\n') -> DictTextTable:
        _values = self.to_list(separator)
        return DictTextTable.create_from_values(
            _values, page_num=f'{self.number_page}', file_type='.pdf'
        )

    def to_map(self, separator: str = '\n') -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.to_dict(separator=separator)).astype('str')

    def to_array(self, separator: str = '\n') -> ArrayString:
        return ArrayString(self.to_list(separator=separator))

    def find(self, text: str, *, separator: str = '\n', iqual: bool = False, case: bool = False) -> str | None:
        fd = FindText(self.to_string(), separator=separator)
        return fd.find(text, iqual=iqual, case=case)

    def find_all(self, text: str, *, separator: str = '\n', iqual: bool = False, case: bool = True) -> list[str]:
        fd = FindText(self.to_string(), separator=separator)
        return fd.find_all(text, iqual=iqual, case=case)

    def get_width(self) -> float:
        return self.implement_page_pdf.get_width()

    def get_height(self) -> float:
        return self.implement_page_pdf.get_height()

    def set_land_scape(self):
        self.implement_page_pdf.set_land_scape()

    def is_land_scape(self) -> bool:
        return self.implement_page_pdf.is_land_scape()

    def set_rotation(self, num: int):
        self.implement_page_pdf.set_rotation(num)

    @classmethod
    def create_from_page_pypdf(cls, page: PageObject, number: int) -> PageDocumentPdf:
        return cls(ImplementPypdf(page, number))

    @classmethod
    def create_from_page_fitz(cls, page: fitz.Page, number: int) -> PageDocumentPdf:
        if page is None:
            raise ValueError(f'fitz.Page não pode ser None')
        return cls(ImplementFitz(page, number))
