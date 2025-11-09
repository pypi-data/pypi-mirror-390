#!/usr/bin/env python3
from __future__ import annotations
import os
from shutil import which
from soup_files import File, KERNEL_TYPE


def __get_path_tesseract_unix() -> File | None:
    out = which('tesseract')
    if out is None:
        return None
    return File(out)


def __get_path_tesseract_windows() -> File | None:
    out = which('tesseract.exe')
    if out is None:
        if os.path.isfile("C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"):
            return File("C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe")
        return None
    return File(out)


def get_path_tesseract_sys() -> File | None:
    if KERNEL_TYPE == 'Windows':
        return __get_path_tesseract_windows()
    return __get_path_tesseract_unix()


class BinTesseract(object):
    """
        Fornece o caminho absoluto do tesseract instalado no sistema, se
    disponível. Você pode usar um binário alternativo, basta informar
    o caminho do binário desejado no construtor.
    """
    _instance = None  # Atributo de classe para armazenar a instância singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BinTesseract, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: File = None):
        # Garante que __init__ não será executado mais de uma vez
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True
        self.__tess_data_dir = None
        self.__lang = None
        if path is not None:
            self.__path_tesseract: File = path
        else:
            self.__path_tesseract = get_path_tesseract_sys()

    def set_tesseract(self, path: File):
        if not isinstance(path, File):
            return
        self.__path_tesseract = path

    def get_tesseract(self) -> File | None:
        return self.__path_tesseract

    def set_lang(self, lang: str):
        if not isinstance(lang, str):
            return
        self.__lang = lang

    def get_lang(self):
        return self.__lang

    def set_tessdata_dir(self, tessdata_dir: str):
        if not isinstance(tessdata_dir, str):
            return
        self.__tess_data_dir = tessdata_dir

    def get_tessdata_dir(self) -> str | None:
        if self.__tess_data_dir is not None:
            return self.__tess_data_dir
        try:
            if KERNEL_TYPE == 'Windows':
                if os.path.exists("C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"):
                    self.__tess_data_dir = "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"
            elif KERNEL_TYPE == 'Linux':
                if os.path.exists('/usr/share/tesseract-ocr/5/tessdata'):
                    self.__tess_data_dir = '/usr/share/tesseract-ocr/5/tessdata'
        except Exception as err:
            print(err)
        return self.__tess_data_dir

    def exists(self) -> bool:
        """Verifica se o binário tesseract existe"""
        if self.__path_tesseract is None:
            return False
        return self.__path_tesseract.exists()


__all__ = ['BinTesseract', 'get_path_tesseract_sys']
