#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations

import os.path
from typing import Union
from abc import ABC, abstractmethod
from soup_files import File, Directory, InputFiles, LibraryDocs, ProgressBarAdapter
from io import BytesIO
import numpy as np
from scipy.ndimage import uniform_filter
from sheet_stream.type_utils import get_hash_from_bytes, MetaDataFile, MetaDataItem
from convert_stream.mod_types.enums import LibImage, RotationAngle
from convert_stream.mod_types.table_types import ListItems
from convert_stream.mod_types.modules import (
    MOD_IMG_PIL, ModuleImage, DEFAULT_LIB_IMAGE,
    cv2, MatLike, Image, ImageFilter, LibImage
)


class ABCImageObject(ABC):

    def __init__(self, module_image: ModuleImage) -> None:
        # Dimensões máximas, altere se necessário.
        self.max_size: tuple[int, int] = (1980, 720)
        self.module_image: ModuleImage = module_image
        self.lib_image: LibImage = LibImage.OPENCV
        self.metadata: MetaDataFile = MetaDataFile()

    @property
    def name(self) -> str | None:
        return self.metadata.name if not self.metadata.name.is_empty else None

    @abstractmethod
    def get_dimensions(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def is_landscape(self) -> bool:
        """Verificar se a imagen é do tipo paisagem"""
        pass

    @abstractmethod
    def is_vertical(self) -> bool:
        pass

    @abstractmethod
    def set_landscape(self):
        pass

    @abstractmethod
    def set_vertical(self):
        pass

    @abstractmethod
    def set_rotation(self, angle: RotationAngle) -> None:
        pass

    @abstractmethod
    def set_gausian_blur(self, sigma: float = 0.7):
        pass

    @abstractmethod
    def set_background_blur(self, sigma: float):
        pass

    @abstractmethod
    def set_threshold_black(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        pass

    @abstractmethod
    def set_threshold_gray(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        pass

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> BytesIO:
        pass

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        pass

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        pass


class ImplementOpenCv(ABCImageObject):
    def __init__(self, module_image: ModuleImage) -> None:
        super().__init__(module_image)
        self.lib_image = LibImage.OPENCV

        # Redimensionar se necessário
        dimensions = (self.module_image.shape[1], self.module_image.shape[0])  # (largura, altura)
        if (dimensions[0] > self.max_size[0]) or (dimensions[1] > self.max_size[1]):
            h, w = self.module_image.shape[:2]
            scale = min(self.max_size[0] / w, self.max_size[1] / h)
            new_size = (int(w * scale), int(h * scale))
            self.module_image = cv2.resize(self.module_image, new_size, interpolation=cv2.INTER_LANCZOS4)

    def get_dimensions(self) -> tuple[int, int]:
        height, width = self.module_image.shape[:2]
        return width, height

    def is_landscape(self) -> bool:
        w, h = self.get_dimensions()
        return w > h

    def is_vertical(self) -> bool:
        w, h = self.get_dimensions()
        return h > w

    def set_landscape(self):
        if self.is_vertical():
            #self.set_rotation(RotationAngle.ROTATION_90)
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def set_vertical(self):
        if self.is_landscape():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_rotation(self, angle: RotationAngle) -> None:
        if angle == RotationAngle.ROTATION_90:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == RotationAngle.ROTATION_180:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_180)
        elif angle == RotationAngle.ROTATION_270:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def set_gausian_blur(self, sigma: float = 0.5):
        # Aplica um filtro Gaussiano para reduzir o ruído
        _blurred: MatLike = cv2.GaussianBlur(self.module_image, (3, 3), sigma)
        self.module_image = _blurred

    def set_background_blur(self, sigma: float):
        # 1. Converter para escala de cinza
        gray = cv2.cvtColor(self.module_image, cv2.COLOR_BGR2GRAY)

        # 2. Borramento para capturar apenas o fundo suave
        blur = cv2.GaussianBlur(gray, (0, 0), sigma)

        # 3. Subtração para aumentar contraste do texto
        enhanced = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)

        # 4. Normalizar (clarear fundo, escurecer texto)
        norm = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)

        # 5. Converter de volta para BGR
        self.module_image = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)

    def set_threshold_black(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        nparr = np.frombuffer(self.to_bytes().getvalue(), np.uint8)
        img_opencv: cv2.typing.MatLike = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        # Aplica um filtro Gaussiano para reduzir o ruído
        _blurred: cv2.typing.MatLike = cv2.GaussianBlur(img_opencv, (3, 3), sigma)
        # Aplica binarização adaptativa (texto branco, fundo preto)
        binary: cv2.typing.MatLike = cv2.adaptiveThreshold(
            _blurred,
            max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        self.module_image = cv2.bitwise_not(binary)

    def set_threshold_gray(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        nparr = np.frombuffer(self.to_bytes().getvalue(), np.uint8)
        img_opencv: cv2.typing.MatLike = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Aplica um filtro Gaussiano para reduzir o ruído
        _blurred: cv2.typing.MatLike = cv2.GaussianBlur(img_opencv, (3, 3), sigma)

        # Aplica binarização adaptativa (texto preto, fundo branco)
        binary = cv2.adaptiveThreshold(
            _blurred,
            max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,  # Inverte o texto para ser branco inicialmente
            11,
            2
        )
        self.module_image = cv2.bitwise_not(binary)

    def to_file(self, file: File):
        #print(f'Exportando arquivo: {file.basename()}')
        cv2.imwrite(file.absolute(), self.module_image)

    def to_bytes(self) -> BytesIO:
        # Codifica como PNG em memória
        success, buffer = cv2.imencode(".png", self.module_image)
        if not success:
            raise ValueError("Falha ao converter a imagem para bytes.")
        output = BytesIO(buffer.tobytes())
        return output

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        img = cv2.imread(f.absolute())
        if img is None:
            raise ValueError(f"Não foi possível abrir a imagem: {f.absolute()}")
        im_obj = cls(img)
        im_obj.metadata = MetaDataFile.create_metadata(f)
        return im_obj

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        np_arr = np.frombuffer(bt, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Não foi possível criar a imagem a partir dos bytes fornecidos.")
        bytes_io = BytesIO(bt)
        name: str = get_hash_from_bytes(bytes_io)
        bytes_io.close()
        im_obj = cls(img)
        im_obj.metadata.name = MetaDataItem(name)
        im_obj.metadata.md5 = MetaDataItem(name)
        return im_obj


class ImplementPIL(ABCImageObject):
    def __init__(self, module_image: ModuleImage):
        super().__init__(module_image)
        self.lib_image = LibImage.PIL

        # Redimensionar, se as dimensões estiverem maior que self.max_size.
        if (self.module_image.width > self.max_size[0]) or (self.module_image.height > self.max_size[1]):
            buff_image: BytesIO = BytesIO()
            self.module_image.save(buff_image, format='PNG', optimize=True, quality=90)
            self.module_image = Image.open(buff_image)
            buff_image.seek(0)
            #buff_image.close()
            #del buff_image
            #self.module_image.thumbnail(self.max_size, Image.LANCZOS)

    def get_dimensions(self) -> tuple[int, int]:
        return self.module_image.size  # (width, height)

    def is_landscape(self) -> bool:
        w, h = self.get_dimensions()
        return w > h

    def is_vertical(self) -> bool:
        w, h = self.get_dimensions()
        return h > w

    def set_landscape(self):
        if self.is_vertical():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_vertical(self):
        if self.is_landscape():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_rotation(self, angle: RotationAngle) -> None:
        self.module_image = self.module_image.rotate(
            -angle.value, expand=True
        )  # negativo = sentido horário

    def set_gausian_blur(self, sigma: float = 0.7):
        # 1. Converter para tons de cinza
        gray = self.module_image.convert("L")

        # 2. Borramento
        blur = gray.filter(ImageFilter.GaussianBlur(radius=sigma))

        # 3. Realçar texto combinando original e borrada
        np_gray = np.array(gray, dtype=np.float32)
        np_blur = np.array(blur, dtype=np.float32)
        enhanced = np.clip(1.5 * np_gray - 0.5 * np_blur, 0, 255).astype(np.uint8)

        # 4. Normalização
        min_val, max_val = enhanced.min(), enhanced.max()
        if max_val > min_val:
            enhanced = ((enhanced - min_val) * (255 / (max_val - min_val))).astype(np.uint8)

        # 5. Converter de volta para RGB
        self.module_image = Image.fromarray(enhanced).convert("RGB")

    def set_background_blur(self, sigma: float):
        # Converter para RGBA para preservar transparência
        img = self.module_image.convert("RGBA")

        # Criar versão borrada
        blurred = img.filter(ImageFilter.GaussianBlur(radius=sigma))

        # Criar máscara baseada na luminosidade
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p > 200 else 0).convert("1")

        # Combinar foreground com background borrado
        img.paste(blurred, mask=mask)
        self.module_image = img

    def set_threshold_black(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        img = self.module_image.convert("RGBA")
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p > 200 else 0).convert("1")
        black_bg = Image.new("RGBA", img.size, (0, 0, 0, max_value))
        img.paste(black_bg, mask=mask)
        self.module_image = img

    def set_threshold_gray(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        if not MOD_IMG_PIL:
            raise RuntimeError("PIL não está disponível.")
        # 1. Converte para escala de cinza
        gray_img = self.module_image.convert("L")

        # 2. Detecta o texto usando um threshold adaptativo (via NumPy)
        import numpy as np
        img_np = np.array(gray_img)

        # Parâmetros semelhantes ao adaptiveThreshold do OpenCV
        block_size = 25
        mean = uniform_filter(img_np.astype(np.float32), size=block_size)
        mask_text = (img_np < mean - 15).astype(np.uint8) * 255  # texto=255, fundo=0

        # 3. Máscara do fundo (inverso)
        mask_background = 255 - mask_text
        # 4. Cria fundo cinza claro
        background_np = np.full_like(img_np, max_value, dtype=np.uint8)
        # 5. Texto escuro
        text_dark_value = 30
        text_np = np.full_like(img_np, text_dark_value, dtype=np.uint8)

        # 6. Combina texto escuro com fundo cinza
        combined_np = ((text_np * (mask_text // 255)) +
                       (background_np * (mask_background // 255))).astype(np.uint8)
        # 7. Converte de volta para PIL (BGR → RGB não é necessário, pois estamos em L)
        self.module_image = Image.fromarray(combined_np).convert("RGB")

    def to_file(self, file: File) -> None:
        # Salva no formato original ou detectado pela extensão
        self.module_image.save(file.absolute())

    def to_bytes(self) -> BytesIO:
        buffer = BytesIO()
        # Tenta manter o formato original; se não houver, usa PNG
        fmt = self.module_image.format or "PNG"
        self.module_image.save(buffer, format=fmt)
        buffer.seek(0)
        return buffer

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        img = Image.open(f.absolute())
        im_obj = cls(img)
        im_obj.metadata = MetaDataFile.create_metadata(f)
        return im_obj

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        img = Image.open(BytesIO(bt))
        bytes_io = BytesIO(bt)
        name = get_hash_from_bytes(bytes_io)
        bytes_io.close()
        _obj = cls(img)
        _obj.metadata.name = MetaDataItem(name)
        _obj.metadata.md5 = MetaDataItem(name)
        return _obj


class ImageObject(object):

    def __init__(
                self, img: Union[ABCImageObject, bytes, BytesIO, str, File],
                *, lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        #
        if isinstance(img, ABCImageObject):
            self.img_adapter: ABCImageObject = img
        elif isinstance(img, bytes):
            if lib_image == LibImage.OPENCV:
                self.img_adapter = ImplementOpenCv.create_from_bytes(img)
            elif lib_image == LibImage.PIL:
                self.img_adapter = ImplementPIL.create_from_bytes(img)
            else:
                raise ValueError('Use: PIL ou OPENCV')
        elif isinstance(img, BytesIO):
            img.seek(0)
            if lib_image == LibImage.OPENCV:
                self.img_adapter = ImplementOpenCv.create_from_bytes(img.getvalue())
            elif lib_image == LibImage.PIL:
                self.img_adapter = ImplementPIL.create_from_bytes(img.getvalue())
            else:
                raise ValueError('Use: PIL ou OPENCV')
        elif isinstance(img, File):
            if lib_image == LibImage.OPENCV:
                self.img_adapter = ImplementOpenCv.create_from_file(img)
            elif lib_image == LibImage.PIL:
                self.img_adapter = ImplementPIL.create_from_file(img)
            else:
                raise ValueError('Use: PIL ou OPENCV')
        elif isinstance(img, str):
            if lib_image == LibImage.OPENCV:
                self.img_adapter = ImplementOpenCv.create_from_file(File(img))
            elif lib_image == LibImage.PIL:
                self.img_adapter = ImplementPIL.create_from_file(File(img))
            else:
                raise ValueError('Use: PIL ou OPENCV')
        else:
            raise ValueError('Use: str, bytes, BytesIO, File, OPENCV or PIL')

    @property
    def name(self) -> str:
        return self.img_adapter.name

    @property
    def metadata(self) -> MetaDataFile:
        return self.img_adapter.metadata

    @metadata.setter
    def metadata(self, metadata: MetaDataFile) -> None:
        self.img_adapter.metadata = metadata

    def to_pil(self) -> Image.Image:
        """
        Converte o ImageObject para um objeto PIL.Image.
        """
        # Obtém o stream de bytes da imagem
        image_bytes: BytesIO = self.to_bytes()
        # Cria e retorna um objeto Image do Pillow a partir do stream de bytes
        return Image.open(image_bytes)

    def to_opencv(self) -> MatLike:
        return cv2.imdecode(self.to_numpy(), cv2.IMREAD_COLOR)

    def to_numpy(self) -> np.ndarray:
        bt: BytesIO = self.to_bytes()
        return np.frombuffer(bt.getvalue(), np.uint8)

    def get_dimensions(self) -> tuple[int, int]:
        return self.img_adapter.get_dimensions()

    def is_landscape(self) -> bool:
        return self.img_adapter.is_landscape()

    def is_vertical(self) -> bool:
        return self.img_adapter.is_vertical()

    def set_landscape(self):
        return self.img_adapter.set_landscape()

    def set_vertical(self):
        return self.img_adapter.set_vertical()

    def set_rotation(self, angle: RotationAngle = RotationAngle.ROTATION_90) -> None:
        self.img_adapter.set_rotation(angle)

    def set_gausian_blur(self, sigma: float = 0.5):
        self.img_adapter.set_gausian_blur(sigma)

    def set_background_blur(self, sigma: float):
        self.img_adapter.set_background_blur(sigma)

    def set_threshold_black(self, *, max_value: float = 150, sigma: float = 0.5) -> None:
        self.img_adapter.set_threshold_black(max_value=max_value, sigma=sigma)

    def set_threshold_gray(self, *, max_value: float = 150, sigma: float = 0.5):
        self.img_adapter.set_threshold_gray(max_value=max_value, sigma=sigma)

    def to_file(self, file: File):
        self.img_adapter.to_file(file)

    def to_bytes(self) -> BytesIO:
        return self.img_adapter.to_bytes()

    @classmethod
    def create_from_file(cls, f: File, *, lib_image: LibImage = DEFAULT_LIB_IMAGE) -> ImageObject:
        if lib_image == LibImage.OPENCV:
            _adapter = ImplementOpenCv.create_from_file(f)
            return cls(_adapter)
        elif lib_image == LibImage.PIL:
            _adapter = ImplementPIL.create_from_file(f)
            return cls(_adapter)
        raise ValueError(f'Módulo imagem inválido: {lib_image}')

    @classmethod
    def create_from_bytes(cls, bt: bytes, *, lib_image: LibImage = DEFAULT_LIB_IMAGE) -> ImageObject:

        if lib_image == LibImage.OPENCV:
            _adapter = ImplementOpenCv.create_from_bytes(bt)
            return cls(_adapter)
        elif lib_image == LibImage.PIL:
            _adapter = ImplementPIL.create_from_bytes(bt)
            return cls(_adapter)
        raise ValueError(f'Módulo imagem inválido: {lib_image}')

    @classmethod
    def create_from_pil(cls, pil: ModuleImage) -> ImageObject:
        return cls(ImplementPIL(pil))


class CollectionImages(ListItems):
    
    def __init__(self, images: list[ImageObject], *, lib_img: LibImage = LibImage.OPENCV) -> None:
        """
            Gerir uma lista de Imagens
        :type images: list[ImageObject]
        """
        super().__init__(images)
        self.lib_img: LibImage = lib_img
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()
        self.__count: int = 0

    def clear(self) -> None:
        super().clear()
        self.__count = 0

    def add_image(self, image: ImageObject) -> None:
        self.__count += 1
        self.pbar.update_text(f'Adicionando imagem {self.__count}')
        self.append(image)

    def add_file_image(self, file: File) -> None:
        self.pbar.start()
        self.__count += 1
        self.pbar.update_text(f'Adicionando imagem {self.__count} {file.basename()}')
        im = ImageObject.create_from_file(file, lib_image=self.lib_img)
        self.append(im)
        self.pbar.stop()

    def add_images(self, images: list[ImageObject]) -> None:
        for img in images:
            self.add_image(img)

    def add_files_image(self, files: list[File]) -> None:
        self.pbar.start()
        max_num: int = len(files)
        for num, f in enumerate(files):
            self.pbar.update(
                ((num+1) / max_num) * 100,
                f'Adicionando imagem: [{num+1} de {max_num}]'
            )
            self.append(ImageObject.create_from_file(f, lib_image=self.lib_img))
        self.pbar.stop()

    def add_directory_images(self, d: Directory, max_files: int = 4000) -> None:
        input_files = InputFiles(d, maxFiles=max_files)
        self.add_files_image(input_files.get_files(file_type=LibraryDocs.IMAGE))

    def to_files_image(
                self,
                output_dir: Directory,
                replace: bool = False,
                land_scape: bool = False,
                gaussian_filter: bool = False,
            ) -> None:
        self.pbar.start()
        print()
        output_dir.mkdir()
        max_num = self.length
        img: ImageObject
        for n, img in enumerate(self):
            if img.metadata.file_path is not None:
                filename = f'{os.path.basename(img.metadata.file_path)}-{n}.png'
            else:
                filename = f'{img.metadata.name}-{n}.png'
            file_path = output_dir.join_file(filename)
            if (not replace) and (file_path.exists()):
                self.pbar.update_text(f'[PULANDO]: {file_path.basename()}')
                continue
            self.pbar.update(
                ((n + 1) / max_num) * 100,
                f'Exportando: [{n + 1} de {max_num}] {file_path.absolute()}',
            )
            if land_scape:
                img.set_landscape()
            if gaussian_filter:
                img.set_gausian_blur()
                img.set_threshold_gray()
            try:
                img.to_file(file_path)
            except Exception as e:
                print()
                self.pbar.update_text(f'{e}')
        self.pbar.stop()

    def set_land_scape(self):
        for im in self:
            im.set_landscape()

    def set_gausian_blur(self, sigma: float = 0.8) -> None:
        self.pbar.start()
        max_num: int = self.length
        for _num, im in enumerate(self):
            self.pbar.update(
                ((_num + 1) / max_num) * 100,
                f'Aplicando GausianBlur: [{_num + 1} de {max_num}]'
            )
            im.set_gausian_blur(sigma)
            im.set_threshold_gray()
        print()
        self.pbar.stop()

    def set_pbar(self, p: ProgressBarAdapter) -> None:
        self.pbar = p


class ProcessImageScanner(object):

    def __init__(self, image: ImageObject):
        self.image: ImageObject = image

    def select_doc(self) -> ImageObject | None:
        """
        Detecta e recorta automaticamente a área do documento principal
        (texto ou folha digitalizada) em uma imagem.
        Retorna um novo ImageObject contendo apenas o recorte detectado.
        """
        # Converte para matriz OpenCV
        img_cv: np.ndarray = cv2.imdecode(self.image.to_numpy(), cv2.IMREAD_COLOR)
        if img_cv is None:
            print(f'[NDARRAY] Falha na imagem: {self.image.metadata.name}')
            return None

        # Etapa 1: converter para tons de cinza
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Etapa 2: aplicar blur para suavizar ruídos
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Etapa 3: detecção de bordas
        edges = cv2.Canny(gray_blur, 50, 150)

        # Etapa 4: encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            print(f'[CONTOURS] Falha na imagem: {self.image.metadata.name}')
            return None

        # Etapa 5: selecionar o maior contorno plausível (maior área retangular)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        doc_contour = None

        for c in contours:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            if len(approx) == 4:
                doc_contour = approx
                break

        if doc_contour is None:
            # Caso não encontre um quadrilátero, usa o maior contorno
            doc_contour = contours[0]

        # Etapa 6: criar bounding box e recortar
        x, y, w, h = cv2.boundingRect(doc_contour)
        cropped = img_cv[y:y + h, x:x + w]

        # Evitar recortes muito pequenos (ruído)
        if w < 50 or h < 50:
            return None

        # Etapa 7: converter o recorte em ImageObject
        success, buffer = cv2.imencode(".png", cropped)
        if not success:
            print(f'Falha na imagem: {self.image.metadata.name}')
            return None

        bytes_io = BytesIO(buffer.tobytes())
        new_image = ImageObject(bytes_io, lib_image=LibImage.OPENCV)
        # Herdar metadados originais
        new_image.metadata = self.image.metadata
        new_image.metadata.name = MetaDataItem(f"{self.image.metadata.name}_crop")
        return new_image

