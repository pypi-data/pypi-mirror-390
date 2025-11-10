#!/usr/bin/env python3
from enum import Enum


class ColumnsTable(Enum):
    """
        Classe enum para padronizar os nomes das tabelas geradas por este módulo.
    """

    NUM_LINE = 'LINHA'
    NUM_PAGE = 'PÁGINA'
    TEXT = 'TEXTO'
    FILE_PATH = 'ARQUIVO'
    FILE_NAME = 'NOME_ARQUIVO'
    DIR = 'PASTA'
    FILETYPE = 'TIPO_ARQUIVO'
    KEY = 'KEY'

    @classmethod
    def to_list(cls) -> list[str]:
        return [
            cls.NUM_LINE.value,
            cls.NUM_PAGE.value,
            cls.TEXT.value,
            cls.FILE_PATH.value,
            cls.FILE_NAME.value,
            cls.FILETYPE.value,
            cls.DIR.value,
            cls.KEY.value,
        ]


class LibPdfToImage(Enum):
    """Enumerar as bibliotecas externas que convertem PDF em imagem"""
    PDF_TO_IMG_FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImageToPdf(Enum):

    IMAGE_TO_PDF_FITZ = 'fitz'
    IMAGE_TO_PDF_CANVAS = 'canvas'
    IMAGE_TO_PDF_PIL = 'pil'
    NOT_IMPLEMENTED = 'null'


class LibPDF(Enum):

    PYPDF = 'pypdf'
    FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImage(Enum):

    PIL = 'pil'
    OPENCV = 'opencv'
    NOT_IMPLEMENTED = 'null'


class RotationAngle(Enum):

    ROTATION_90 = 90
    ROTATION_180 = 180
    ROTATION_270 = 270
