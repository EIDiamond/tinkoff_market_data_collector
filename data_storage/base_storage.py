import abc

from tinkoff.invest import MarketDataResponse

__all__ = ("IStorage")


class IStorage(abc.ABC):
    @abc.abstractmethod
    def save(self, market_data: MarketDataResponse) -> None:
        pass
