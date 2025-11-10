#!/usr/bin/env python3

import pandas as pd
from soup_files import File, ProgressBarAdapter, CreatePbar


def save_data(
            data: pd.DataFrame, *,
            file: File,
            index: bool = False,
            pbar: ProgressBarAdapter = CreatePbar().get(),
        ):
    pbar.start()
    pbar.update(0, f'Salvando: {file.basename()}')
    try:
        if file.is_csv():
            data.to_csv(file.absolute(), index=index)
        elif file.is_excel():
            data.to_excel(file.absolute(), index=index)
        elif '.ods' in file.extension():
            data.to_excel(file.absolute(), index=index, engine='odf')
    except Exception as err:
        pbar.update_text(f'Erro: {err}')
    else:
        print()
        pbar.update(100, 'OK')
    finally:
        pbar.stop()

