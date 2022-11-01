from typing import Optional

from data_storage.base_storage import IStorage
from data_storage.files_csv.csv_data_storage import CSVDataStorage

__all__ = ("StorageFactory")


class StorageFactory:
    """
    Fabric for storages. Put here a new storage class.
    """
    @staticmethod
    def new_factory(storage_type: str, *args, **kwargs) -> Optional[IStorage]:
        match storage_type:
            case "FILES_CSV":
                return CSVDataStorage(*args, **kwargs)
            case _:
                return None
