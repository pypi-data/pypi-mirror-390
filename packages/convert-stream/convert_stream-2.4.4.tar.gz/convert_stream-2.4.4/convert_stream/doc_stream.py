#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com pdfs e imagens
"""
from __future__ import annotations
from convert_stream.mod_types.modules import (
    DEFAULT_LIB_PDF, DEFAULT_LIB_IMAGE, DEFAULT_LIB_PDF_TO_IMG, DEFAULT_LIB_IMAGE_TO_PDF,
)
from convert_stream.mod_types.enums import LibPDF, LibImage, LibPdfToImage
from convert_stream.pdf.pdf_page import PageDocumentPdf
from convert_stream.image.img_object import ImageObject, CollectionImages
from convert_stream.pdf.pdf_document import DocumentPdf, CollectionPagePdf
from convert_stream.pdf.image_to_pdf import LibImageToPdf, ConvertImageToPdf
from convert_stream.pdf.pdf_to_image import ConvertPdfToImages
from soup_files import File, Directory, ProgressBarAdapter


class ImageStream(CollectionImages):

    def __init__(self, images: list[ImageObject]) -> None:
        super().__init__(images)

    def add_image_bytes(self, bt: bytes) -> None:
        im = ImageObject.create_from_bytes(bt)
        self.append(im)


class PdfStream(object):

    def __init__(
                self, *,
                pbar: ProgressBarAdapter = ProgressBarAdapter(),
                lib_pdf: LibPDF = LibPDF.FITZ,
                lib_img: LibImage = LibImage.OPENCV,
                lib_img_to_pdf: LibImageToPdf = LibImageToPdf.IMAGE_TO_PDF_FITZ,
                lib_pdf_to_img: LibPdfToImage = LibPdfToImage.PDF_TO_IMG_FITZ,
                dpi: int = 200,
            ) -> None:
        self.dpi = dpi
        self.progress: ProgressBarAdapter = pbar
        self.collection_pages: CollectionPagePdf = CollectionPagePdf([])
        self.collection_images: CollectionImages = CollectionImages([], lib_img=lib_img)
        self.collection_images.set_pbar(self.progress)
        self.collection_pages.set_pbar(self.progress)
        self.lib_pdf: LibPDF = lib_pdf
        self.lib_img: LibImage = lib_img
        self.lib_img_to_pdf: LibImageToPdf = lib_img_to_pdf
        self.lib_pdf_to_img: LibPdfToImage = lib_pdf_to_img
        self.clear()

    @property
    def convert_pdf_to_images(self) -> ConvertPdfToImages:
        conv = ConvertPdfToImages.create(
            DocumentPdf.create_from_pages(self.collection_pages, lib_pdf=self.lib_pdf),
        )
        conv.set_pbar(self.progress)
        return conv

    @property
    def convert_images_to_pdf(self) -> ConvertImageToPdf:
        _con = ConvertImageToPdf(self.collection_images, lib_img_to_pdf=self.lib_img_to_pdf)
        _con.set_pbar(self.progress)
        return _con

    @property
    def is_empty(self) -> bool:
        return self.collection_pages.is_empty

    def set_land_scape(self):
        self.collection_pages.set_land_scape()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.progress = pbar
        self.collection_pages.set_pbar(pbar)

    def clear(self):
        self.collection_pages.clear()
        self.collection_images.clear()

    def add_page(self, page: PageDocumentPdf) -> None:
        self.collection_pages.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]) -> None:
        self.collection_pages.add_pages(pages)

    def add_file_image(self, f: File) -> None:
        self.collection_images.add_file_image(f)

    def add_files_image(self, files: list[File]) -> None:
        self.collection_images.add_files_image(files)

    def add_image(self, image: ImageObject) -> None:
        self.collection_images.add_image(image)

    def add_images(self, images: list[ImageObject]) -> None:
        self.collection_images.add_images(images)

    def add_file_pdf(self, f: File) -> None:
        self.collection_pages.add_file_pdf(f, lib_pdf=self.lib_pdf)

    def add_files_pdf(self, files: list[File]) -> None:
        self.collection_pages.add_files_pdf(files, lib_pdf=self.lib_pdf)

    def add_document(self, doc: DocumentPdf) -> None:
        self.collection_pages.add_document(doc)

    def add_directory_pdf(self, src_dir: Directory, max_files: int = 4000) -> None:
        self.collection_pages.add_directory_pdf(src_dir, max_files=max_files)

    def add_directory_image(self, src_dir: Directory, max_files: int = 4000) -> None:
        self.collection_images.add_directory_images(src_dir, max_files=max_files)

    def to_document(self, *, land_scape: bool = False, a4: bool = False) -> DocumentPdf:
        """
            Converte os documentos adicionados em PdfStream (imagens/pdfs) em
        objeto do tipo DocumentPdf().
        """
        if self.collection_pages.is_empty and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')

        _doc: DocumentPdf = None
        if not self.collection_images.is_empty:
            # Converter as imagens em documento PDF.
            _doc = self.convert_images_to_pdf.to_document(land_scape, a4=a4)
        if not self.collection_pages.is_empty:
            # Converter/Adicionar as páginas PDF ao documento final.
            if _doc is None:
                _doc: DocumentPdf = self.collection_pages.to_document(self.lib_pdf)
            else:
                _doc.add_pages(self.collection_pages)
        return _doc

    def thresold(self, *, land_scape: bool = False, a4: bool = False) -> DocumentPdf:
        if self.collection_images.length == 0:
            images: list[ImageObject] = []
        else:
            images: list[ImageObject] = self.collection_images.copy()

        if not self.collection_pages.is_empty:
            # Converter as páginas PDF em imagens.
            conv_pdf_to_img: ConvertPdfToImages = self.convert_pdf_to_images
            images.extend(
                conv_pdf_to_img.to_images(dpi=self.dpi, lib_image=self.lib_img),
            )
        if len(images) == 0:
            raise ValueError('Adicione imagens para prosseguir!')
        if land_scape:
            for img in images:
                img.set_landscape()
        for i in images:
            i.set_threshold_gray()
        conv_img_to_pdf = ConvertImageToPdf(CollectionImages(images), lib_img_to_pdf=self.lib_img_to_pdf)
        return conv_img_to_pdf.to_document(a4=a4)

    def to_files_images(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                land_scape: bool = False,
            ) -> None:
        if self.collection_pages.is_empty and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')
        self.progress.start()

        image_stream = ImageStream([])
        image_stream.set_pbar(self.progress)
        if not self.collection_images.is_empty:
            image_stream.add_images(self.collection_images)
        if not self.collection_pages.is_empty:
            self.progress.update_text('Processando Imagens')
            # Criar um documento a partir das páginas
            convert_pdf_to_img = self.convert_pdf_to_images
            # Converter as páginas PDF em imagens e adicionar a coleção já existe de imagens.
            _pdf_to_images: list[ImageObject] = convert_pdf_to_img.to_images(dpi=self.dpi, lib_image=self.lib_img)
            image_stream.add_images(_pdf_to_images)
        # Exportar para arquivos.
        image_stream.to_files_image(output_dir, replace=replace, land_scape=land_scape)
        self.progress.stop()

    def to_files_pdf(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                land_scape: bool = False,
                a4: bool = False,
                prefix: str = None,
            ) -> None:
        if self.collection_pages.is_empty and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')
        pages_document = []
        if not self.collection_pages.is_empty:
            pages_document.extend(self.collection_pages)
        if not self.collection_images.is_empty:
            img_to_pdf: ConvertImageToPdf = self.convert_images_to_pdf
            tmp_document = img_to_pdf.to_document(land_scape, a4=a4)
            pages_document.extend(tmp_document.to_pages())
        final_collection = CollectionPagePdf(pages_document)
        if land_scape:
            final_collection.set_land_scape()
        final_collection.to_files_pdf(output_dir, replace=replace, prefix=prefix)


class SplitPdf(object):

    def __init__(self, pages: list[PageDocumentPdf], pbar: ProgressBarAdapter = ProgressBarAdapter()):
        self.pbar: ProgressBarAdapter = pbar
        self.__collection_pages: CollectionPagePdf = CollectionPagePdf(pages)
        self.__collection_pages.set_pbar(self.pbar)

    def is_empty(self) -> bool:
        return self.__collection_pages.is_empty

    def add_pages_pdf(self, pages: list[PageDocumentPdf]) -> None:
        self.__collection_pages.add_pages(pages)

    def export(self, output_dir: Directory, *, replace: bool = False, prefix: str = 'pag') -> None:
        if self.is_empty():
            self.pbar.update_text(f'O Documento está vazio!')
            return
        self.__collection_pages.to_files_pdf(output_dir, replace=replace, prefix=prefix)
        self.__collection_pages.clear()
