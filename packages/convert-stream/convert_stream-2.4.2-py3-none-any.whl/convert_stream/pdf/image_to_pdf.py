#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Módulo para trabalhar com imagens
"""

from __future__ import annotations
from io import BytesIO
from soup_files import File, Directory, ProgressBarAdapter
from abc import ABC, abstractmethod
from convert_stream.mod_types.enums import LibImageToPdf
from convert_stream.mod_types.modules import (
    MOD_CANVAS, DEFAULT_LIB_IMAGE_TO_PDF, canvas, letter, ImageReader
)
from convert_stream.pdf import DocumentPdf
from convert_stream.pdf.pdf_page import fitz
from convert_stream.image.img_object import MOD_IMG_PIL, Image, ImageObject, CollectionImages


class ABCConvertImageToPdf(ABC):

    def __init__(self, collection_images: CollectionImages):
        self.collection_images: CollectionImages = collection_images
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()

    @abstractmethod
    def set_pbar(self, p: ProgressBarAdapter):
        pass

    @abstractmethod
    def to_document(self, land_scape: bool = True, a4: bool = False) -> DocumentPdf:
        pass

    @abstractmethod
    def to_file_pdf(self, output_file: File, *, land_scape: bool = True, a4: bool = False) -> None:
        pass


class ImplementImageToPdfCanvas(ABCConvertImageToPdf):

    def __init__(self, collection_images: CollectionImages):
        super().__init__(collection_images)

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p
        self.collection_images.set_pbar(p)

    def to_document(self, land_scape: bool = True, a4: bool = False) -> DocumentPdf:
        if not MOD_CANVAS:
            raise RuntimeError("A biblioteca 'reportlab' não está disponível.")

        if self.collection_images.is_empty:
            raise ValueError("A lista de imagens não pode estar vazia.")

        buffer = BytesIO()
        max_num: int = self.collection_images.length
        self.pbar.start()
        if land_scape:
            self.collection_images.set_land_scape()

        # Lógica para determinar o tamanho inicial da página
        first_img_obj = self.collection_images[0]
        first_img_width, first_img_height = first_img_obj.get_dimensions()

        if a4:
            # Se for A4, o tamanho da página é fixo desde o início
            c = canvas.Canvas(buffer, pagesize=letter)
        else:
            # Se não for A4, o canvas é inicializado com as dimensões da primeira imagem
            c = canvas.Canvas(buffer, pagesize=(first_img_width, first_img_height))

        # Processa a primeira imagem
        self.pbar.update(
            (1 / max_num) * 100,
            f'Adicionando imagem ao Documento [1 de {max_num}]'
        )
        img_bytes: BytesIO = first_img_obj.to_bytes()
        img_bytes.seek(0)
        img_reader = ImageReader(img_bytes)

        if a4:
            # Lógica de redimensionamento e centralização para A4
            page_width, page_height = letter
            scale_factor = min(page_width / first_img_width, page_height / first_img_height)
            scaled_width = first_img_width * scale_factor
            scaled_height = first_img_height * scale_factor
            x_pos = (page_width - scaled_width) / 2
            y_pos = (page_height - scaled_height) / 2
            c.drawImage(img_reader, x_pos, y_pos, width=scaled_width, height=scaled_height)
        else:
            # Desenha a imagem preenchendo a página que já tem o tamanho correto
            c.drawImage(img_reader, 0, 0, width=first_img_width, height=first_img_height)

        # Processa as imagens restantes
        for num, img_obj in enumerate(self.collection_images[1:], 1):

            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Adicionando imagem ao Documento [{num + 1} de {max_num}]'
            )
            img_bytes = img_obj.to_bytes()
            img_bytes.seek(0)
            img_reader = ImageReader(img_bytes)
            img_width, img_height = img_obj.get_dimensions()
            # Cria nova página
            c.showPage()

            if a4:
                # O tamanho da página é fixo, apenas desenha a imagem centralizada e redimensionada
                page_width, page_height = letter
                scale_factor = min(page_width / img_width, page_height / img_height)
                scaled_width = img_width * scale_factor
                scaled_height = img_height * scale_factor
                x_pos = (page_width - scaled_width) / 2
                y_pos = (page_height - scaled_height) / 2
                c.drawImage(img_reader, x_pos, y_pos, width=scaled_width, height=scaled_height)
            else:
                # Ajusta o tamanho da nova página para as dimensões da imagem atual
                c.setPageSize((img_width, img_height))
                c.drawImage(img_reader, 0, 0, width=img_width, height=img_height)

        c.save()
        buffer.seek(0)
        self.pbar.stop()
        return DocumentPdf.create_from_bytes(buffer)

    def to_file_pdf(self, output_file: File, *, land_scape: bool = True, a4: bool = False) -> None:
        self.to_document(land_scape=land_scape, a4=a4).to_file(output_file)


class ImplementImageToPdfPil(ABCConvertImageToPdf):
    """
        Classe para converter uma lista de ImageObject em um DocumentPdf
        usando a biblioteca Pillow (PIL).
    """

    def __init__(self, collection_images: CollectionImages):
        super().__init__(collection_images)

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p
        self.collection_images.set_pbar(p)

    def to_document(self, land_scape: bool = True, a4: bool = False) -> DocumentPdf:
        if not MOD_IMG_PIL:
            raise RuntimeError("A biblioteca 'Pillow' não está disponível.")

        if self.collection_images:
            raise ValueError("A lista de imagens não pode estar vazia.")

        if land_scape:
            self.collection_images.set_land_scape()

        pil_images_to_save = []
        if a4:
            # Obtém as dimensões da página A4 em píxels
            # Usando uma resolução de 100 DPI para consistência
            page_width, page_height = letter  # Padrão do reportlab
            page_size = (int(page_width), int(page_height))

            self.pbar.start()
            max_num = self.collection_images.length
            for num, img_obj in enumerate(self.collection_images):
                self.pbar.update(
                    ((num + 1) / max_num) * 100,
                    f'Redimensionando e ajustando imagem para A4 [{num + 1} de {max_num}]'
                )
                original_pil_image = img_obj.to_pil()
                img_width, img_height = original_pil_image.size

                # Calcula o fator de escala para ajustar a imagem à página, mantendo a proporção
                scale_factor = min(page_size[0] / img_width, page_size[1] / img_height)
                scaled_width = int(img_width * scale_factor)
                scaled_height = int(img_height * scale_factor)

                # Redimensiona a imagem
                resized_image = original_pil_image.resize(
                    (scaled_width, scaled_height), Image.Resampling.LANCZOS
                )

                # Criar imagem de fundo branca com o tamanho A4
                new_image = Image.new('RGB', page_size, 'white')

                # Centraliza a imagem redimensionada na nova imagem
                x_pos = (page_size[0] - scaled_width) // 2
                y_pos = (page_size[1] - scaled_height) // 2
                new_image.paste(resized_image, (x_pos, y_pos))

                pil_images_to_save.append(new_image)
            self.pbar.stop()
        else:
            # Para a4 = False, não precisa redimensionar. Pillow ajusta o tamanho da página.
            pil_images_to_save = [img.to_pil() for img in self.collection_images]

        buffer = BytesIO()
        try:
            first_image_pil = pil_images_to_save[0]
            other_images_pil = pil_images_to_save[1:]

            first_image_pil.save(
                buffer,
                'PDF',
                resolution=140.0,
                save_all=True,
                append_images=other_images_pil
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao criar o PDF com Pillow: {e}") from e

        buffer.seek(0)
        return DocumentPdf.create_from_bytes(buffer)

    def to_file_pdf(self, output_file: File, *, land_scape: bool = True, a4: bool = False) -> None:
        self.to_document(land_scape=land_scape, a4=a4).to_file(output_file)


class ImplementImageToPdfFitz(ABCConvertImageToPdf):
    """
        Classe para converter uma lista de ImageObject em um DocumentPdf
        usando a biblioteca PyMuPDF (fitz).
    """

    def __init__(self, collection_images: CollectionImages):
        super().__init__(collection_images)

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p
        self.collection_images.set_pbar(p)

    def to_document(self, land_scape: bool = True, a4: bool = False) -> DocumentPdf:
        max_num: int = self.collection_images.length
        if max_num == 0:
            raise ValueError('Adicione imagens para prosseguir')
        self.pbar.start()
        self.pbar.update(0, f'Convertendo {max_num} imagens em Documento PDF')
        buffer = BytesIO()
        doc = fitz.open()  # Cria um novo documento PDF vazio

        for num, img_obj in enumerate(self.collection_images):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Convertendo: [{num + 1} de {max_num}]'
            )
            if land_scape:
                img_obj.set_landscape()

            # Converte a imagem para bytes
            img_bytes_obj = img_obj.to_bytes()
            # Obtém as dimensões da imagem e da página
            img_width, img_height = img_obj.get_dimensions()

            # Adiciona uma nova página ao documento
            if a4:
                page = doc.new_page()
            else:
                page = doc.new_page(width=img_width, height=img_height)

            # Cria um retângulo que preenche a página
            rect = page.rect
            page_width, page_height = rect.width, rect.height

            # Calcula o fator de escala para ajustar a imagem à página
            scale_factor_w = page_width / img_width
            scale_factor_h = page_height / img_height
            scale_factor = min(scale_factor_w, scale_factor_h)

            # Ajusta o retângulo de inserção para centralizar a imagem
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor
            x0 = (page_width - scaled_width) / 2
            y0 = (page_height - scaled_height) / 2

            # Insere a imagem no retângulo calculado
            page.insert_image(
                fitz.Rect(x0, y0, x0 + scaled_width, y0 + scaled_height),
                stream=img_bytes_obj
            )

        # Salva o documento no buffer de memória
        doc.save(buffer)
        doc.close()
        buffer.seek(0)
        self.pbar.update(100, 'Conversão concluída')
        print()
        self.pbar.stop()
        return DocumentPdf.create_from_bytes(buffer)

    def to_file_pdf(self, output_file: File, *, land_scape: bool = True, a4: bool = False) -> None:
        self.to_document(land_scape=land_scape).to_file(output_file)


class ConvertImageToPdf(object):
    """
        Classe com padrão ADAPTER para converter Imagens em documento(s) PDF.
    """

    def __init__(
            self,
            collection_images: CollectionImages, *,
            lib_img_to_pdf: LibImageToPdf = LibImageToPdf.IMAGE_TO_PDF_FITZ
    ):
        if lib_img_to_pdf == LibImageToPdf.IMAGE_TO_PDF_CANVAS:
            self.convert: ABCConvertImageToPdf = ImplementImageToPdfCanvas(collection_images)
        elif lib_img_to_pdf == LibImageToPdf.IMAGE_TO_PDF_PIL:
            self.convert: ABCConvertImageToPdf = ImplementImageToPdfPil(collection_images)
        elif lib_img_to_pdf == LibImageToPdf.IMAGE_TO_PDF_FITZ:
            self.convert: ABCConvertImageToPdf = ImplementImageToPdfFitz(collection_images)
        else:
            raise NotImplementedError()

        self._count: int = 0

    @property
    def is_null(self) -> bool:
        return self.convert.collection_images.is_empty

    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.convert.pbar

    def set_pbar(self, p: ProgressBarAdapter):
        self.convert.set_pbar(p)

    def add_file(self, file: File) -> None:
        self.convert.collection_images.add_file_image(file)

    def add_files(self, files: list[File]) -> None:
        self.convert.collection_images.add_files_image(files)

    def add_image(self, image: ImageObject) -> None:
        self.convert.collection_images.add_image(image)

    def add_images(self, images: list[ImageObject]) -> None:
        self.convert.collection_images.add_images(images)

    def add_directory(self, src_dir: Directory, max_files: int = 4000) -> None:
        self.convert.collection_images.add_directory_images(src_dir, max_files=max_files)

    def to_document(self, land_scape: bool = True, *, a4: bool = False) -> DocumentPdf:
        return self.convert.to_document(land_scape, a4=a4)

    def to_file_pdf(self, output_file: File, *, land_scape: bool = True, a4: bool = False) -> None:
        self.convert.to_file_pdf(output_file, land_scape=land_scape, a4=a4)

    def set_gausian_blur(self, sigma: float = 0.8) -> None:
        self.convert.collection_images.set_gausian_blur(sigma)

    def set_land_scape(self):
        self.convert.collection_images.set_land_scape()
