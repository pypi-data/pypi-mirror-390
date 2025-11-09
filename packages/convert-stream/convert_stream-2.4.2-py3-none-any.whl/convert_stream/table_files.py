#!/usr/bin/env python3

from __future__ import annotations
from io import BytesIO
from soup_files import File, Directory, InputFiles, LibraryDocs

from convert_stream import PageDocumentPdf
from convert_stream.text.find_text import FindText
from convert_stream.pdf.pdf_document import SearchableTextPdf, DocumentPdf
from convert_stream.mod_types.table_types import ColumnsTable
from convert_stream.image import ImageObject


class PdfFinder(object):
    """
        Classe para Filtrar texto em Imagens
    """

    def __init__(self):
        self.docs_collection: dict[str, DocumentPdf] = {}

    def is_empty(self) -> bool:
        return len(self.docs_collection) == 0

    def clear(self) -> None:
        self.docs_collection.clear()

    def add_document(self, document: File | bytes | BytesIO | str | DocumentPdf) -> None:
        if isinstance(document, File):
            document = DocumentPdf(document)
        elif isinstance(document, DocumentPdf):
            pass
        elif isinstance(document, bytes):
            document = DocumentPdf(BytesIO(document))
        elif isinstance(document, str):
            document = ImageObject(document)
        elif isinstance(document, BytesIO):
            document = DocumentPdf(document)

        if not document.metadata.file_path.is_empty:
            self.docs_collection[document.metadata.file_path] = document
        else:
            self.docs_collection[document.metadata.name] = document

    def add_documents(self, documents: list[File] | list[DocumentPdf] | list[bytes] | list[BytesIO]) -> None:
        for _doc in documents:
            self.add_document(_doc)

    def add_directory_pdf(self, dir_pdf: Directory) -> None:
        files = InputFiles(dir_pdf).get_files(file_type=LibraryDocs.PDF)
        if len(files) > 0:
            self.add_documents(files)

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for n, file_key in enumerate(self.docs_collection.keys()):
            temp_doc: DocumentPdf = self.docs_collection[file_key]
            pages_pdf: list[PageDocumentPdf] = temp_doc.to_pages()
            for pg in pages_pdf:
                text_page: str = pg.to_string()

                if (text_page == '') or (text_page is None) or (text_page == 'nas'):
                    continue
                try:
                    fd = FindText(text_page, separator=separator)
                    idx = fd.find_index(text, iqual=iqual, case=case)
                    if idx is None:
                        continue
                    math_text: str | None = fd.get_index(idx)
                except Exception as err:
                    print(f'{__class__.__name__} {err}')
                else:
                    file_path = temp_doc.metadata.file_path
                    file_name = temp_doc.metadata.name
                    dir_path = temp_doc.metadata.dir_path
                    file_type = temp_doc.metadata.extension

                    new_line: dict[str, str] = {
                        ColumnsTable.KEY: f'{idx}',
                        ColumnsTable.NUM_PAGE: 'nan',
                        ColumnsTable.NUM_LINE: f'{idx + 1}',
                        ColumnsTable.TEXT: math_text,
                        ColumnsTable.FILE_NAME: file_name,
                        ColumnsTable.FILETYPE: file_type,
                        ColumnsTable.FILE_PATH: file_path,
                        ColumnsTable.DIR: dir_path,
                    }
                    _searchable.add_line(new_line)
                    return _searchable
        return _searchable

    def find_all(
                self, text: str,
                separator: str = '\n',
                iqual: bool = False,
                case: bool = False,
                silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for n, file_key in enumerate(self.docs_collection.keys()):
            temp_doc: DocumentPdf = self.docs_collection[file_key]
            pages_pdf: list[PageDocumentPdf] = temp_doc.to_pages()
            for pg in pages_pdf:
                text_page: str = pg.to_string()

                if (text_page == '') or (text_page is None) or (text_page == 'nas'):
                    continue
                try:
                    fd = FindText(text_page, separator=separator)
                    idx = fd.find_index(text, iqual=iqual, case=case)
                    if idx is None:
                        continue
                    math_text: str | None = fd.get_index(idx)
                except Exception as err:
                    print(f'{__class__.__name__} {err}')
                else:
                    file_path = temp_doc.metadata.file_path
                    file_name = temp_doc.metadata.name
                    dir_path = temp_doc.metadata.dir_path
                    file_type = temp_doc.metadata.extension

                    new_line: dict[str, str] = {
                        ColumnsTable.KEY: f'{idx}',
                        ColumnsTable.NUM_PAGE: 'nan',
                        ColumnsTable.NUM_LINE: f'{idx + 1}',
                        ColumnsTable.TEXT: math_text,
                        ColumnsTable.FILE_NAME: file_name,
                        ColumnsTable.FILETYPE: file_type,
                        ColumnsTable.FILE_PATH: file_path,
                        ColumnsTable.DIR: dir_path,
                    }
                    _searchable.add_line(new_line)
        return _searchable
