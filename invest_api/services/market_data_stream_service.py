import logging
from typing import Generator

from tinkoff.invest import AsyncClient, CandleInstrument, SubscriptionInterval, TradeInstrument, \
    MarketDataResponse, LastPriceInstrument
from tinkoff.invest.market_data_stream.async_market_data_stream_manager import AsyncMarketDataStreamManager

from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry
from configuration.settings import DataCollectionSettings


__all__ = ("MarketDataStreamService")

logger = logging.getLogger(__name__)


class MarketDataStreamService:
    """
    The class encapsulate tinkoff market data stream (gRPC) service api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

        self.__stream: AsyncMarketDataStreamManager = None

    @invest_api_retry()
    @invest_error_logging
    async def start_async_candles_stream(
            self,
            figies: list[str],
            settings: DataCollectionSettings
    ) -> Generator[MarketDataResponse, None, None]:
        """
        The method starts async gRPC stream and return required responses
        """
        logger.debug(f"Starting market data async stream")

        async with AsyncClient(self.__token, app_name=self.__app_name) as client:
            self.__stream = client.create_market_data_stream()

            if settings.candles:
                logger.info(f"Subscribe candles: {figies}")
                self.__stream.candles.subscribe(
                    [
                        CandleInstrument(
                            figi=figi,
                            interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE
                        )
                        for figi in figies
                    ]
                )

            if settings.trades:
                logger.info(f"Subscribe trades: {figies}")
                self.__stream.trades.subscribe(
                    [
                        TradeInstrument(
                            figi=figi
                        )
                        for figi in figies
                    ]
                )

            if settings.last_price:
                logger.info(f"Subscribe last_price: {figies}")
                self.__stream.last_price.subscribe(
                    [
                        LastPriceInstrument(
                            figi=figi
                        )
                        for figi in figies
                    ]
                )

            async for market_data in self.__stream:
                logger.debug(f"market_data: {market_data}")

                if (settings.candles and market_data.candle) \
                        or (settings.trades and market_data.trade) \
                        or (settings.last_price and market_data.last_price):
                    yield market_data

    def stop_candles_stream(self) -> None:
        if self.__stream:
            logger.info(f"Stopping candles stream")

            self.__stream.stop()
