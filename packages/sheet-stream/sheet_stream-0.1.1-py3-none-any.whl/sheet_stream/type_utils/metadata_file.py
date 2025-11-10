from __future__ import annotations
from io import BytesIO
from soup_files import File
from hashlib import md5 as md5_hash


def get_hash_from_bytes(bt: BytesIO | bytes) -> str:
    if isinstance(bt, BytesIO):
        return md5_hash(bt.getvalue()).hexdigest().upper()
    elif isinstance(bt, bytes):
        return md5_hash(bt).hexdigest().upper()
    else:
        raise TypeError(f"Unsupported type {type(bt)}")


class MetaDataItem(str):

    def __init__(self, text: str = 'nan'):
        super().__init__()
        self.text: str = text

    @property
    def is_empty(self) -> bool:
        return self.text == 'nan'


class MetaDataFile(object):

    def __init__(
                self, *,
                file_path: MetaDataItem = None,
                dir_path: MetaDataItem = None,
                name: MetaDataItem = None,
                md5: MetaDataItem = None,
                size: MetaDataItem = None,
                extension: MetaDataItem = None,
                origin_src: MetaDataItem = None,
            ):

        self.file_path: MetaDataItem = file_path if file_path is not None else MetaDataItem()
        self.dir_path: MetaDataItem = dir_path if dir_path is not None else MetaDataItem()
        self.name: MetaDataItem = name if name is not None else MetaDataItem()
        self.md5: MetaDataItem = md5 if md5 is not None else MetaDataItem()
        self.size: MetaDataItem = size if size is not None else MetaDataItem()
        self.extension: MetaDataItem = extension if extension is not None else MetaDataItem()
        self.origin_src: MetaDataItem = origin_src if origin_src is not None else MetaDataItem()

    def __repr__(self):
        return f'{__class__.__name__}: {self.to_dict()}'

    def to_dict(self) -> dict[str, str | None]:
        return {
            'file_path': self.file_path if not self.file_path.is_empty else None,
            'dir_path': self.dir_path if not self.dir_path.is_empty else None,
            'name': self.name if not self.name.is_empty else None,
            'md5': self.md5 if not self.md5.is_empty else None,
            'size': self.size if not self.size.is_empty else None,
            'extension': self.extension if not self.extension.is_empty else None,
            'origin_src': self.origin_src if not self.origin_src.is_empty else None,
        }

    @classmethod
    def create_metadata(cls, file: str | File) -> MetaDataFile:
        if isinstance(file, str):
            file = File(file)

        if isinstance(file, File):
            mt = cls(
                file_path=MetaDataItem(file.absolute()),
                dir_path=MetaDataItem(file.dirname()),
                extension=MetaDataItem(file.extension()),
                origin_src=MetaDataItem('file'),
                name=MetaDataItem(file.name()),
            )
            if file.exists():
                mt.size = MetaDataItem(file.size())
                mt.md5 = MetaDataItem(file.md5())
        elif isinstance(file, bytes):
            mt = cls(
                origin_src=MetaDataItem('bytes'),
                name=MetaDataItem(get_hash_from_bytes(file)),
            )
            mt.md5 = mt.name
        elif isinstance(file, BytesIO):
            mt = cls(
                origin_src=MetaDataItem('bytes'),
                name=MetaDataItem(get_hash_from_bytes(file)),
            )
            mt.md5 = mt.name
        else:
            raise ValueError()
        return mt

