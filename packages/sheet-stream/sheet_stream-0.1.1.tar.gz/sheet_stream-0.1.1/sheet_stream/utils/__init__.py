#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from soup_files import ProgressBarAdapter, ABCProgressBar


class VoidPBar(ABCProgressBar):

    def __init__(self):
        super().__init__()

    def set_percent(self, percent: float):
        pass

    def set_text(self, text: str):
        pass


class VoidAdapter(ProgressBarAdapter):

    def __init__(self, progress_bar: ABCProgressBar = VoidPBar()):
        super().__init__()
        self.pbar_implement: ABCProgressBar = progress_bar

    def get_current_percent(self) -> float:
        pass

    def update_text(self, text: str = "-"):
        pass

    def update_percent(self, percent: float = 0):
        pass

    def update(self, percent: float, status: str = "-"):
        pass

    def start(self):
        self.pbar_implement.start()

    def stop(self):
        self.pbar_implement.stop()


