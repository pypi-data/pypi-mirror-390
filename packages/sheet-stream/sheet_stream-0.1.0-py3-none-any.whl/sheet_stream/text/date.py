#!/usr/bin/env python3
from __future__ import annotations
from datetime import datetime
import pandas as pd
from sheet_stream.type_utils.enums import LibDate


class ConvertStringDate(object):
    def __init__(self):
        """
            Converter vários formatos de datas.
        """

        self.date_valid_formats = (
            '%d-%m-%Y',  # Exemplo: 11-01-2025
            '%d/%m/%y',
            '%d-%m-%y',
            '%Y/%m/%d',  # Exemplo: 2025/01/11
            '%d/%m/%Y',  # Exemplo: 11/01/2025
            '%Y-%m-%d',  # Exemplo: 2025-01-11
            '%d %B %Y',  # Exemplo: 11 Janeiro 2025
            '%b %d, %Y',  # Exemplo: Jan 11, 2025
            '%A, %d %B %Y',  # Exemplo: Sábado, 11 Janeiro 2025
            '%H:%M:%S',  # Exemplo: 08:35:00
            '%H:%M',  # Exemplo: 08:35
            '%I:%M %p',  # Exemplo: 08:35 AM
            '%Y-%m-%d %H:%M:%S',  # Exemplo: 2025-01-11 08:35:00
            '%Y-%m-%dT%H:%M:%S',  # Exemplo: 2025-01-11T08:35:00 (Formato ISO 8601)
            '%Y%m%dT%H%M%S',  # Exemplo: 20250111T083500 (Formato compactado)
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",  # ISO-like
            "%Y-%m-%dT%H:%M:%S.%f"
        )

        self.date_valid_times_tamp = (
            '%Y-%m-%d %H:%M:%S',  # Exemplo: 2025-01-11 08:35:00
            '%Y-%m-%dT%H:%M:%S',  # Exemplo: 2025-01-11T08:35:00 (Formato ISO 8601)
            '%Y%m%dT%H%M%S',  # Exemplo: 20250111T083500 (Formato compactado)
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",  # ISO-like
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f"
        )

        # Dicionário de mapeamento de nomes de meses em português para inglês
        self.date_month_pt_to_eng = {
            'Janeiro': 'January',
            'Fevereiro': 'February',
            'Março': 'March',
            'Abril': 'April',
            'Maio': 'May',
            'Junho': 'June',
            'Julho': 'July',
            'Agosto': 'August',
            'Setembro': 'September',
            'Outubro': 'October',
            'Novembro': 'November',
            'Dezembro': 'December',
        }

        # Mapeamento dos meses em português para números
        self.month_to_number = {
            "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
            "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
            "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
        }

    def is_valid_date(self, date_str: str) -> bool:
        """
            Verificar se uma string é uma data válida
        """
        if (date_str is None) or (date_str == ''):
            return False

        # Tentar conversão com formatos tradicionais.
        date_str = date_str.strip()
        for fmt in self.date_valid_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except:
                pass

        # Tentar a conversão com datas por extenso em português.
        # Sexta-feira, 25 de abril de 2025
        if ('de' in date_str) and (',' in date_str):
            date_str = date_str.split(',')[1].strip()
            date_str = date_str.replace(' ', '-').replace('de', '').replace('--', '-').strip()

        if '-' in date_str:
            for _key in self.month_to_number.keys():
                if _key.lower() in date_str.lower():
                    new = self.date_pt_d_m_y_to_date(date_str)
                    if new is not None:
                        return True

        if self.date_pt_d_m_y_to_date(date_str) is not None:
            return True
        if self.is_timestamp(date_str):
            return True
        if ',' in date_str:
            try:
                # Sábado, 11 Janeiro 2025
                date_str = self.date_pt_week_d_m_y_to_date(date_str)
            except:
                pass
            else:
                return True
        return False

    def is_timestamp(self, d: object) -> bool:
        """
            Verifica se o objeto atual é timestamp
        """
        if isinstance(d, pd.Timestamp):
            return True
        for current_format in self.date_valid_times_tamp:
            try:
                datetime.strptime(d, current_format)
                return True
            except:
                pass
        return False

    def date_pt_week_d_m_y_to_date(self, date_string: str, fmt: LibDate = LibDate.DMY) -> str | None:
        """
            Converte uma data escrita por extenso em data string nos padrões python.
        Ex: Domingo, 12 Janeiro 2025 -> 12/01/2025
        """
        # Remover o dia da semana da string
        if not ',' in date_string:
            return None

        date_string = date_string.split(", ")[1]
        date_string = date_string.strip()
        # Formato da data sem o dia da semana
        current_data_fmt = '%d %B %Y' # 12 Janeiro 2025

        # Substituir o nome do mês em português pelo nome em inglês
        for pt_mes, en_mes in self.date_month_pt_to_eng.items():
            date_string = date_string.replace(pt_mes, en_mes)

        # Converter a string para um objeto datetime
        to_datetime = datetime.strptime(date_string, current_data_fmt)

        # Formatando o objeto datetime para o formato desejado "dia/mês/ANO" ou
        # outro definido em fmt
        return to_datetime.strftime(fmt)

    def date_pt_d_m_y_to_date(self, data_str_br: str, *, fmt: LibDate = LibDate.DMY) -> str | None:
        """
        Converte uma data no padrão 25-abril-2025 para o padrão 25/04/2025 (ou outro definido em fmt).

        """
        # Divide a string e substitui o mês pelo número correspondente
        if not '-' in data_str_br:
            return None

        try:
            dia, mes, ano = data_str_br.split("-")
            mes_num = self.month_to_number[mes.lower()]  # Converte o mês para número (maio=5, junho=6, ...)
            data_formatada = f"{dia}/{mes_num}/{ano}"  # Formata para o padrão dd/mm/yyyy
            # Converte para um objeto datetime
            return datetime.strptime(data_formatada, fmt).strftime(fmt)  # "%d/%m/%Y" ...
        except Exception as e:
            return None

    def convert_date(self, date_str: str, *, fmt: LibDate = LibDate.DMY) -> str | None:
        """
            Converter uma data em string para um formato qualquer.
        """
        if not self.is_valid_date(date_str):
            return None

        if ('de' in date_str) and (',' in date_str):
            # Sexta-feira, 25 de abril de 2025
            date_str = date_str.split(',')[1].strip()
            date_str = date_str.replace(' ', '-').replace('de', '').replace('--', '-').strip()
        if '-' in date_str:
            for _key in self.month_to_number.keys():
                if _key.lower() in date_str.lower():
                    new = self.date_pt_d_m_y_to_date(date_str)
                    if new is not None:
                        return new

        for current_format in self.date_valid_formats:
            try:
                date_obj = datetime.strptime(date_str, current_format)
            except:
                pass
            else:
                return date_obj.strftime('{}'.format(fmt.value))
        return None

    def convert_timestamp(self, ts: str, *, fmt: LibDate = LibDate.DMY) -> str | None:
        """
            Converter uma data em string timestamp para um formato qualquer.
        """
        if not self.is_timestamp(ts):
            return None

        for current_format in self.date_valid_times_tamp:
            try:
                date_timestamp: datetime = datetime.strptime(ts, current_format)
            except:
                pass
            else:
                # Converter datetime para string no formato recebido via parâmetro.
                return date_timestamp.strftime(fmt)
        return None


def fmt_col_to_date(
            df: pd.DataFrame,
            nome_coluna: str, *,
            date_fmt: LibDate = LibDate.DMY
        ) -> pd.DataFrame:
    """
    Formata uma coluna específica de um DataFrame como data, preservando valores que não puderem ser convertidos.

    Parâmetros:
        df (pd.DataFrame): DataFrame de entrada.
        nome_coluna (str): Nome da coluna a ser formatada.
        formato (str): Tipo de formatação de data. Pode ser:
            - "dia/mes/ano" → "%d/%m/%Y"
            - "mes/dia/ano" → "%m/%d/%Y"
            - "ano-mes-dia" → "%Y-%m-%d"
            - ou um formato customizado válido do datetime.

    Retorna:
        pd.DataFrame: O mesmo DataFrame, com a coluna formatada.
    """
    # Copia o DataFrame para não modificar o original
    new_df = df.copy().astype('str')

    def try_converter(current_date) -> str:
        """Tenta converter o valor para data, preservando o original se falhar."""
        try:
            _new: str | None = ConvertStringDate().convert_date(current_date, fmt=date_fmt)
        except Exception as e:
            return current_date
        else:
            if _new is not None:
                return _new
            return current_date

    new_df[nome_coluna] = new_df[nome_coluna].apply(try_converter)
    return new_df.astype('str')
