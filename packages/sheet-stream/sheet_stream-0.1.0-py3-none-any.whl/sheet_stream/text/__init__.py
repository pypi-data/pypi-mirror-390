#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .date import ConvertStringDate, fmt_col_to_date

BAD_STRING_CHARS: list[str] = [
    ':', ',', ';', '$', '=', '!', '}', '{', '(', ')', '|', '\\', '‘', '*', '¢', '“',
    "'", '¢', '"', '#', '<', '?', '>', '»', '@', '+', '[', ']', '%', '~', '¥',
    '«', '°', '¢', '”', '&', '/', '®', '£', '"'
]

# Criação do Mapa de Tradução (Translator)
# str.maketrans() recebe uma string (ou lista unida em string) de caracteres a serem
# removidos e mapeia todos para None.
# **É crucial gerar este mapa UMA VEZ fora da função para otimização.**
BAD_CHARS_TRANSLATOR = str.maketrans('', '', "".join(BAD_STRING_CHARS))


def clean_string(input_string: str) -> str:
    """
    Remove todos os caracteres listados em BAD_STRING_CHARS da string de entrada.

    Args:
        input_string: A string a ser limpa.

    Returns:
        Uma nova string com os caracteres indesejados removidos.
    """
    # O método translate() usa o mapa pré-compilado para remover os caracteres de forma muito rápida.
    return input_string.translate(BAD_CHARS_TRANSLATOR)


