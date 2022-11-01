import abc
import datetime

__all__ = ("IObservableDataCollector")


class IObservableDataCollector(abc.ABC):
    @abc.abstractmethod
    def last_event_time(self) -> datetime:
        pass

    @abc.abstractmethod
    def is_collection_in_progress(self) -> bool:
        pass

    @abc.abstractmethod
    def restart(self) -> None:
        pass
    