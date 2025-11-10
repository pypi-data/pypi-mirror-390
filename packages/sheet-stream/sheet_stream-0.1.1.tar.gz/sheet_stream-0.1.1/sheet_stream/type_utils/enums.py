from enum import StrEnum


class LibSheet(StrEnum):

    CSV = 'csv'
    EXCEL = 'excel'
    ODS = 'ods'
    NOT_IMPLEMENTED = 'not_implemented'


class LibDate(StrEnum):
    D_M_Y = '%d-%m-%Y'
    DMY = '%d/%m/%Y'
    dmy = '%d/%m/%y'
    d_m_y = '%d-%m-%y'
    YMD = '%Y/%m/%d'
    Y_M_D = '%Y-%m-%d'


class ColumnsTable(StrEnum):
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
