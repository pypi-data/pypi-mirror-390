

class InvalidFileSheetError(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class InvalidFileCsvError(InvalidFileSheetError):

    def __init__(self, *args):
        super().__init__(*args)


class InvalidFileExcelError(InvalidFileSheetError):

    def __init__(self, *args):
        super().__init__(*args)


class InvalidFileOdsError(InvalidFileSheetError):

    def __init__(self, *args):
        super().__init__(*args)


class ListTableError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ListTableLargeError(ListTableError):

    def __init__(self, *args):
        super().__init__(*args)


class ListTableShortError(ListTableError):

    def __init__(self, *args):
        super().__init__(*args)


class RowLargeError(ListTableError):

    def __init__(self, *args):
        pass


class RowShortError(ListTableError):

    def __init__(self, *args):
        pass
