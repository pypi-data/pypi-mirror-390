#!/usr/bin/env python3
from __future__ import annotations

import os.path
from abc import abstractmethod, ABC
from typing import Union
from pandas import DataFrame
from soup_files import File
from convert_stream import DocumentPdf, PageDocumentPdf, DictTextTable
from convert_stream.mod_types.modules import DEFAULT_LIB_IMAGE, LibImage
from convert_stream.image import ImageObject
from sheet_stream.type_utils import MetaDataFile
from ocr_stream.modules import (
    LibOcr, DEFAULT_LIB_OCR, pytesseract, pyocr, easyocr
)
from ocr_stream.bin_tess import BinTesseract

import cv2
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


class TextRecognized(object):
    """
        Recebe os bytes de uma página PDF reconhecida de imagem
    e exporta para vários tipos de dados.
    """

    def __init__(self, bytes_recognized: bytes):
        self.metadata: MetaDataFile = MetaDataFile()
        self.bytes_recognized: bytes = bytes_recognized
        self.__text_document: str | None = None

        self.list_bad_char: list[str] = [
            ':', ',', ';', '$', '=',
            '!', '}', '{', '(', ')',
            '|', '\\', '‘', '*'
            '¢', '“', '\'', '¢', '"',
            '#', '.', '<', '?', '>',
            '»', '@', '+', '[', ']',
            '%', '~', '¥', '♀',
        ]

    @property
    def is_empty(self) -> bool:
        txt = self.to_string()
        if (txt is None) or (txt == '') or (txt == 'nas'):
            return True
        return False

    def to_string(self) -> str | None:
        if self.__text_document is None:
            _pages: list[PageDocumentPdf] = self.to_document().to_pages()
            content: str = ''
            txt_page: str
            for page in _pages:
                txt_page = page.to_string()
                if (txt_page is None) or (txt_page == '') or (txt_page == 'nas'):
                    continue
                if content == '':
                    content = txt_page
                    continue
                content = f'{content}\n{txt_page}'
            self.__text_document = content
        return self.__text_document

    def to_page_pdf(self) -> PageDocumentPdf:
        doc = self.to_document()
        return doc.to_pages()[0]

    def to_document(self) -> DocumentPdf:
        tmp_doc = DocumentPdf(BytesIO(self.bytes_recognized))
        tmp_doc.metadata.file_path = self.metadata.file_path
        tmp_doc.metadata.dir_path = self.metadata.dir_path
        return tmp_doc

    def to_dict(self, separator: str = '\n') -> DictTextTable:
        return self.to_page_pdf().to_dict(separator=separator)

    def to_dataframe(self, separator='\n') -> DataFrame:
        return DataFrame.from_dict(self.to_dict(separator=separator))


class ABCOcrTesseract(ABC):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        if not bin_tess.exists():
            raise FileNotFoundError('tesseract binary not found')
        self.bin_tess: BinTesseract = bin_tess
        self.lang: str = lang
        self.tess_data_dir: str = tess_data_dir
        self.current_library: LibOcr = DEFAULT_LIB_OCR

    @abstractmethod
    def to_string(self, img: Union[File, ImageObject]) -> str:
        pass

    @abstractmethod
    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        pass


class IPytesseract(ABCOcrTesseract):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        super().__init__(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        self.current_library: LibOcr = LibOcr.PYTESSERACT
        self._MOD_TESS: pytesseract = pytesseract
        self._MOD_TESS.tesseract_cmd = self.bin_tess.get_tesseract().absolute()

    def __get_tess_dir_config(self) -> str | None:
        """
        https://github.com/h/pytesseract

        Example config: r'--tessdata-dir "C:\Program Files (x86)\Tesseract-OCR\tessdata"'
        tessdata_dir_config = r'--tessdata-dir <replace_with_your_tessdata_dir_path>'
        It's important to add double quotes around the dir path.
        """
        # Caminho para os dados de idioma, por, eng etc...
        # os.environ["TESSDATA_PREFIX"] = self.tess_data_dir.absolute()
        if self.tess_data_dir is None:
            return ''
        if not os.path.exists(self.tess_data_dir):
            return ''
        return r'--tessdata-dir "{}"'.format(self.tess_data_dir)

    def to_string(self, img: Union[File, ImageObject]) -> str:
        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()
        else:
            raise NotImplementedError()

        if self.lang is None:
            return self._MOD_TESS.image_to_string(_im, config=self.__get_tess_dir_config())
        else:
            return self._MOD_TESS.image_to_string(_im, lang=self.lang, config=self.__get_tess_dir_config())

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:

        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()
        else:
            raise NotImplementedError()
        bt = self._MOD_TESS.image_to_pdf_or_hocr(
            _im,
            lang=self.lang,
            config=self.__get_tess_dir_config()
        )
        return TextRecognized(bt)


# ======================================================================#
# Modulo easyocr
# ======================================================================#
class IEasyOcr(ABCOcrTesseract):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = 'pt', tess_data_dir: str = None):
        super().__init__(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        self.reader: easyocr.Reader = easyocr.Reader([self.lang], gpu=True)

    def to_string(self, img: Union[File, ImageObject]) -> str:
        if isinstance(img, File):
            img = ImageObject(img)
        result = self.reader.readtext(img.to_opencv())
        text = '\n'.join([res[1] for res in result])
        return text

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:

        # 1️⃣ Converter o objeto de entrada para imagem OpenCV
        if isinstance(img, File):
            img = ImageObject(img)
        img_cv = img.to_opencv()
        img_h, img_w = img_cv.shape[:2]

        # 2️⃣ Reconhecer o texto com EasyOCR
        results: list = self.reader.readtext(img_cv)

        # 3️⃣ Converter a imagem para PDF (imagem de fundo)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=(img_w, img_h))

        # Desenha a imagem original como fundo
        img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        pdf.drawImage(ImageReader(img_pil), 0, 0, width=img_w, height=img_h)

        # 4️⃣ Adiciona o texto OCR como camada "invisível" sobre a imagem
        pdf.setFont("Helvetica", 8)
        pdf.setFillColorRGB(1, 1, 1, alpha=0)  # texto invisível

        for (bbox, text, conf) in results:
            if not text.strip():
                continue
            # Coordenadas do bounding box (EasyOCR retorna 4 pontos)
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox

            # Média da posição vertical
            avg_y = (y1 + y2 + y3 + y4) / 4

            # Posição invertida (PDF tem origem no canto inferior esquerdo)
            y_pdf = img_h - avg_y

            # Largura estimada
            text_width = abs(x2 - x1)
            pdf.drawString(x1, y_pdf, text)

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        # 5️⃣ Retorna como TextRecognized (bytes do PDF com texto embutido)
        text_rec = TextRecognized(buffer.read())
        text_rec.metadata = img.metadata if hasattr(img, "metadata") else MetaDataFile()
        return text_rec


# ======================================================================#
# Modulo OCR pyocr
# ======================================================================#

class IPyOcr(ABCOcrTesseract):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        super().__init__(bin_tess, lang=lang, tess_data_dir=tess_data_dir)

        self.current_library: LibOcr = LibOcr.PYOCR
        pyocr_modules: list = pyocr.get_available_tools()
        if len(pyocr_modules) == 0:
            raise ValueError(f"{__class__.__name__} No OCR tool found")
        # The tools are returned in the recommended order of usage
        self._pyOcr = pyocr_modules[0]
        langs: list[str] = self._pyOcr.get_available_languages()
        if lang in langs:
            self.lang = lang
        else:
            self.lang = langs[0]
        print(f"Will use tool {self._pyOcr.get_name()}")

    def to_string(self, img: Union[File, ImageObject]) -> str:
        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()

        return self._pyOcr.to_string(
            _im,
            lang=self.lang,
            builder=pyocr.builders.TextBuilder()
        )

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        raise NotImplementedError(f'{__class__.__name__} método não implementado')


class TesseractOcr(object):

    def __init__(self, mod_ocr: ABCOcrTesseract):
        self.mod_ocr: ABCOcrTesseract = mod_ocr

    def to_string(self, img: Union[File, ImageObject]) -> str:
        return self.mod_ocr.to_string(img)

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        return self.mod_ocr.to_reconize(img)

    @classmethod
    def create(
                cls,
                bin_tess: BinTesseract, *,
                lang: str = None,
                tess_data_dir: str = None,
                lib_ocr: LibOcr = DEFAULT_LIB_OCR,
            ) -> TesseractOcr:
        if lib_ocr == LibOcr.PYTESSERACT:
            md = IPytesseract(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        elif lib_ocr == LibOcr.PYOCR:
            md = IPyOcr(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        elif lib_ocr == LibOcr.EASYOCR:
            if lang is None:
                lang = 'pt'
            md = IEasyOcr(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        else:
            raise ValueError(f'{lib_ocr} is not supported')
        return cls(md)


__all__ = ['TesseractOcr', 'TextRecognized']
