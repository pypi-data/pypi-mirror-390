#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from sheet_stream.type_utils import MetaDataFile

from convert_stream import CollectionImages
from soup_files import Directory, ProgressBarAdapter, CreatePbar
from convert_stream.mod_types.enums import LibPdfToImage
from convert_stream.mod_types.modules import DEFAULT_LIB_PDF_TO_IMG, DEFAULT_LIB_IMAGE, LibPDF
from convert_stream.image.img_object import ImageObject, LibImage
from convert_stream.pdf.pdf_document import DocumentPdf


try:
    import fitz
    MOD_FITZ = True
except ImportError:
    try:
        import pymupdf as fitz
        from pymupdf import Page, Pixmap
        MOD_FITZ = True
    except ImportError:
        fitz = object
        fitz.Page = object
        fitz.TextPage = object
        Page = object
        Pixmap = object


class ABCConvertPdf(ABC):

    def __init__(self, document: DocumentPdf):
        self.document: DocumentPdf = document
        self.lib_pdf_to_image: LibPdfToImage = DEFAULT_LIB_PDF_TO_IMG
        self.pbar: ProgressBarAdapter = CreatePbar().get()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.pbar = pbar

    @abstractmethod
    def to_images(
                self, *,
                dpi: int = 150,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> list[ImageObject]:
        """
            Converte as páginas PDF do documento em lista de objetos imagem ImageObject

        :param dpi: DPI do documento, resolução da renderização.
        :param lib_image: Biblioteca para manipular imagens PIL/OpenCv
        """
        pass

    @abstractmethod
    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            gaussian_filter: bool = False,
            dpi: int = 300,
            lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        """
            Converte todas as páginas do documento em objeto de imagem e salva no disco
        em formato de imagem PNG.
        """
        pass


class ImplementConvertPdfFitz(ABCConvertPdf):

    def __init__(self, document: DocumentPdf):
        super().__init__(document)
        self.lib_pdf_to_image: LibPdfToImage = LibPdfToImage.PDF_TO_IMG_FITZ

    def __get_pages(self) -> list[Page]:
        pages = self.document.to_pages()
        fitz_pages = []
        for p in pages:
            fitz_pages.append(p.implement_page_pdf.mod_page)
        return fitz_pages

    def to_images(
                self, *,
                dpi: int = 200,
                lib_image: LibImage = LibImage.PIL
            ) -> list[ImageObject]:
        """
            Converte um Documento em lista de objetos ImageObject.
        """
        images: list[ImageObject] = []
        _metadata: MetaDataFile = self.document.metadata

        pages_fitz: list[Page] = self.__get_pages()
        _count = len(pages_fitz)
        for n, pg in enumerate(pages_fitz):
            self.pbar.update(
                ((n+1)/_count) * 100,
                f'[Documento para Imagens]: página {n+1}/{_count}'
            )
            pix: Pixmap = pg.get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes('png', jpg_quality=100),
                lib_image=LibImage.PIL,
            )
            img.metadata.name = _metadata.name
            img.metadata.file_path = _metadata.file_path
            images.append(img)
        return images

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                gaussian_filter: bool = False,
                dpi: int = 300,
                lib_image: LibImage = LibImage.PIL
            ) -> None:
        pages_fitz: list[Page] = self.__get_pages()
        _count = len(pages_fitz)
        for n, pg in enumerate(pages_fitz):
            self.pbar.update(
                ((n + 1) / _count) * 100,
                f'[Documento para arquivos de imagens]: {n + 1}/{_count}'
            )
            out_file = output_dir.join_file(f'pag-{n+1}.png')
            if not replace:
                if out_file.exists():
                    self.pbar.update_text(f'Pulando: {out_file.basename()}')
                    continue
            pix: Pixmap = pg.get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes('png', jpg_quality=100),
                lib_image=LibImage.PIL,
            )
            img.to_file(out_file)
        print()


class ConvertPdfToImages(object):

    def __init__(self, mod_conv_to_img: ABCConvertPdf | DocumentPdf):
        if isinstance(mod_conv_to_img, ABCConvertPdf):
            self.mod_convert_to_image: ABCConvertPdf = mod_conv_to_img
        elif isinstance(mod_conv_to_img, ImplementConvertPdfFitz):
            self.mod_convert_to_image: ABCConvertPdf = mod_conv_to_img
        elif isinstance(mod_conv_to_img, DocumentPdf):
            self.mod_convert_to_image = ImplementConvertPdfFitz(mod_conv_to_img)
        else:
            raise NotImplementedError()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.mod_convert_to_image.set_pbar(pbar)

    def to_images(
                self, *,
                dpi: int = 300,
                lib_image: LibImage = LibImage.PIL,
            ) -> list[ImageObject]:
        return self.mod_convert_to_image.to_images(dpi=dpi, lib_image=lib_image)

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                gaussian_filter: bool = False,
                dpi: int = 300,
                lib_image: LibImage = LibImage.PIL,
            ) -> None:
        self.mod_convert_to_image.to_files_image(
            dpi=dpi,
            lib_image=lib_image,
            replace=replace,
            output_dir=output_dir,
            gaussian_filter=gaussian_filter
        )

    def inner_images(self) -> CollectionImages:
        """
            Extrair imagens embutidas nas páginas PDF.
        """
        # doc = Document(stream=page_bytes, filetype="pdf")
        collection_imgs: CollectionImages = CollectionImages([])
        tmp_doc: fitz.Document
        if self.mod_convert_to_image.document.lib_pdf == LibPDF.FITZ:
            tmp_doc: fitz.Document = self.mod_convert_to_image.document.get_real_document()
        elif self.mod_convert_to_image.document.lib_pdf == LibPDF.PYPDF:
            tmp_doc = fitz.Document(
                stream=self.mod_convert_to_image.document.to_bytes().getvalue(), filetype="pdf"
            )
        else:
            raise NotImplementedError()

        page: fitz.Page
        for num, page in enumerate(tmp_doc):
            # Extrair imagens embutidas na página
            images_list: list = page.get_images(full=True)
            for img in images_list:
                try:
                    # Referência do objeto da imagem
                    xref = img[0]
                    # Extrair imagem
                    base_image = tmp_doc.extract_image(xref)
                    # Bytes da imagem
                    image_bytes = base_image["image"]
                    # Extensão (jpg, png, etc.)
                    #image_ext = base_image["ext"]
                except Exception as e:
                    print(e)
                else:
                    img = ImageObject(image_bytes)
                    collection_imgs.append(img)
        return collection_imgs

    @classmethod
    def create(cls, doc: DocumentPdf) -> ConvertPdfToImages:
        _mod = ImplementConvertPdfFitz(doc)
        return cls(_mod)
