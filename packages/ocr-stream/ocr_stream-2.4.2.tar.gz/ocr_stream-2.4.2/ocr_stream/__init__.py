#!/usr/bin/env python3
from __future__ import annotations
from io import BytesIO
from ocr_stream.modules import *
from ocr_stream.bin_tess import BinTesseract, get_path_tesseract_sys
from ocr_stream.ocr import TesseractOcr, TextRecognized
from ocr_stream.recognize import RecognizeImage, RecognizePdf
from convert_stream import DocumentPdf
from convert_stream.image import ImageObject
from sheet_stream.type_utils import HeadValues, HeadCell
from sheet_stream import TableRow, TableDocuments, TableTextKeyWord, VoidAdapter, ColumnsTable
from convert_stream.mod_types import DictTextTable
from convert_stream.text import FindText, FindStrings
import pandas as pd
from soup_files import (
    JsonConvert, ProgressBarAdapter, ABCProgressBar, CreatePbar,
    Directory, File, InputFiles, LibraryDocs
)


def read_image(img: ImageObject, rec: RecognizeImage = RecognizeImage()) -> TextRecognized:
    _txt = rec.image_recognize(img)
    _txt.metadata = img.metadata
    return _txt


def read_images(
            images: list[ImageObject], *,
            rec: RecognizeImage = RecognizeImage(),
            pbar: ProgressBarAdapter = CreatePbar().get()
        ) -> DocumentPdf:
    pbar.start()
    print()
    max_num = len(images)
    pages = []

    for idx, image in enumerate(images):
        pbar.update(
            ((idx + 1) / max_num) * 100,
            f'[OCR Imagem] {idx + 1} / {max_num}',
        )
        out = read_image(image, rec=rec).to_page_pdf()
        pages.append(out)
    tmp_doc = DocumentPdf.create_from_pages(pages)
    pbar.stop()
    return tmp_doc


def read_document(
            document: DocumentPdf, *,
            dpi: int = 200,
            rec: RecognizePdf = RecognizePdf(),
        ) -> DocumentPdf:
    rec.pbar.start()
    return rec.recognize_document(document, dpi=dpi)


class SearchableTextImage(object):
    """

    return {
            ColumnsTable.KEY.value: ColumnBody(ColumnsTable.KEY.value, ListString([])),
            ColumnsTable.NUM_PAGE.value: ColumnBody(ColumnsTable.NUM_PAGE.value, ListString([])),
            ColumnsTable.NUM_LINE.value: ColumnBody(ColumnsTable.NUM_LINE.value, ListString([])),
            ColumnsTable.TEXT.value: ColumnBody(ColumnsTable.TEXT.value, ListString([])),
            ColumnsTable.FILE_NAME.value: ColumnBody(ColumnsTable.FILE_NAME.value, ListString([])),
            ColumnsTable.FILETYPE.value: ColumnBody(ColumnsTable.FILETYPE.value, ListString([])),
            ColumnsTable.FILE_PATH.value: ColumnBody(ColumnsTable.FILE_PATH.value, ListString([])),
            ColumnsTable.DIR.value: ColumnBody(ColumnsTable.DIR.value, ListString([])),
        }
    """
    def __init__(self, silent: bool = False):
        self.silent = silent
        self.elements: DictTextTable = DictTextTable.create_void_dict()

    def __repr__(self):
        return f'SearchableTextPdf: {self.elements}'

    @property
    def length(self) -> int:
        return len(self.elements[ColumnsTable.TEXT.value])

    def is_empty(self) -> bool:
        return len(self.elements[ColumnsTable.TEXT.value]) == 0

    @property
    def columns(self) -> HeadValues:
        return HeadValues([HeadCell(x) for x in list(self.elements.keys())])

    @property
    def first(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        cols = self.columns
        _first = {}
        for c in cols:
            _first[c] = self.elements[c][0]
        return _first

    @property
    def last(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        if self.is_empty():
            return {}
        cols = self.columns
        _last = {}
        for c in cols:
            _last[c] = self.elements[c][-1]
        return _last

    def get_item(self, idx: int) -> dict[str, str]:
        _current_item = {}
        cols = self.columns
        try:
            for col in cols:
                _current_item[col] = self.elements[col][idx]
        except Exception as err:
            if not self.silent:
                print(err)
            return _current_item
        else:
            return _current_item

    def add_line(self, line: dict[str, str]) -> None:
        cols: HeadValues = self.columns
        cols_line: HeadValues = HeadValues([HeadCell(y) for y in list(line.keys())])
        for col in cols:
            if cols_line.contains(col, case=True, iqual=True):
                self.elements[col].append(line[col])

    def clear(self) -> None:
        for _k in self.elements.keys():
            self.elements[_k].clear()

    def to_string(self) -> str:
        """
            Retorna o texto da coluna TEXT em formato de string
        ou 'nas' em caso de erro nas = Not a String
        """
        try:
            return ' '.join(self.elements[ColumnsTable.TEXT.value])
        except Exception as e:
            print(e)
            return 'nas'

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.elements)

    def to_file_json(self, file: File):
        """Exporta os dados da busca para um arquivo JSON"""
        dt = JsonConvert.from_dict(self.elements).to_json_data()
        dt.to_file(file)

    def to_file_excel(self, file: File):
        """Exporta os dados da busca para um arquivo .XLSX"""
        self.to_data_frame().to_excel(file.absolute(), index=False)


class ImageFinder(object):
    """
        Classe para Filtrar texto em Imagens
    """

    def __init__(self):
        self.docs_collection: dict[str, ImageObject] = {}
        self.recognize: RecognizeImage = RecognizeImage()
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()

    def is_empty(self) -> bool:
        return len(self.docs_collection) == 0

    def clear(self) -> None:
        self.docs_collection.clear()

    def add_image(self, img: File | bytes | BytesIO | str | ImageObject) -> None:
        if isinstance(img, File):
            img = ImageObject(img)
        elif isinstance(img, ImageObject):
            pass
        elif isinstance(img, bytes):
            img = ImageObject(img)
        elif isinstance(img, str):
            img = ImageObject(img)
        elif isinstance(img, BytesIO):
            img = ImageObject(img)

        if not img.metadata.file_path.is_empty:
            self.docs_collection[img.metadata.file_path] = img
        else:
            self.docs_collection[img.metadata.name] = img

    def add_images(self, images: list[File] | list[ImageObject] | list[bytes] | list[BytesIO]) -> None:
        for f in images:
            self.add_image(f)

    def add_directory_images(self, dir_pdf: Directory) -> None:
        files = InputFiles(dir_pdf).get_files(file_type=LibraryDocs.IMAGE)
        if len(files) > 0:
            self.add_images(files)

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
            ) -> SearchableTextImage:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        _searchable = SearchableTextImage(silent)
        if self.is_empty():
            return _searchable

        total_num: int = len(self.docs_collection.keys())
        for n, file_key in enumerate(self.docs_collection.keys()):
            self.pbar.update(
                ((n + 1) / total_num) * 100,
                f'[PESQUISANDO]: {n+1}/{total_num}',
            )

            current_img: ImageObject = self.docs_collection[file_key]
            txt_in_img = self.recognize.image_to_string(current_img)
            if (txt_in_img == '') or (txt_in_img is None):
                self.pbar.update_text(f'ERRO: {n+1} {current_img.metadata.name}')
                continue
            try:
                fd = FindText(txt_in_img, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text: str | None = fd.get_index(idx)
            except Exception as err:
                print(f'{__class__.__name__} {err}')
            else:
                new_line: dict[str, str] = {
                    ColumnsTable.KEY: f'{idx}',
                    ColumnsTable.NUM_PAGE: 'nan',
                    ColumnsTable.NUM_LINE: f'{idx + 1}',
                    ColumnsTable.TEXT: math_text,
                    ColumnsTable.FILE_NAME: current_img.metadata.file_path,
                    ColumnsTable.FILETYPE: current_img.metadata.extension,
                    ColumnsTable.FILE_PATH: current_img.metadata.dir_path,
                    ColumnsTable.DIR: current_img.metadata.dir_path,
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
            ) -> SearchableTextImage:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        _searchable = SearchableTextImage(silent)
        if self.is_empty():
            return _searchable

        total_num: int = len(self.docs_collection.keys())
        for n, file_key in enumerate(self.docs_collection.keys()):
            self.pbar.update(
                ((n + 1) / total_num) * 100,
                f'[PESQUISANDO]: {n + 1}/{total_num}',
            )

            current_img: ImageObject = self.docs_collection[file_key]
            txt_in_img = self.recognize.image_to_string(current_img)
            if (txt_in_img == '') or (txt_in_img is None):
                self.pbar.update_text(f'ERRO: {n + 1} {current_img.metadata.name}')
                continue
            try:
                fd = FindText(txt_in_img, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text: str | None = fd.get_index(idx)
            except Exception as err:
                print(f'{__class__.__name__} {err}')
            else:
                new_line: dict[str, str] = {
                    ColumnsTable.KEY: f'{idx}',
                    ColumnsTable.NUM_PAGE: 'nan',
                    ColumnsTable.NUM_LINE: f'{idx + 1}',
                    ColumnsTable.TEXT: math_text,
                    ColumnsTable.FILE_NAME: current_img.metadata.file_path,
                    ColumnsTable.FILETYPE: current_img.metadata.extension,
                    ColumnsTable.FILE_PATH: current_img.metadata.dir_path,
                    ColumnsTable.DIR: current_img.metadata.dir_path,
                }
                _searchable.add_line(new_line)
        return _searchable


__all__ = [
    'ImageFinder', 'SearchableTextImage', 'read_images',
    'read_document', 'RecognizeImage', 'RecognizePdf', 'LibOcr',
]
