import asyncio
import datetime
import logging

from tinkoff.invest import MarketDataResponse

from configuration.settings import DataCollectionSettings
from data_storage.base_storage import IStorage
from invest_api.services.instrument_service import InstrumentService
from invest_api.services.market_data_stream_service import MarketDataStreamService
from observation.observable import IObservableDataCollector

__all__ = ("TinkoffCollector")

logger = logging.getLogger(__name__)


class TinkoffCollector(IObservableDataCollector):
    """
    The class encapsulate market data collection process
    """

    def __init__(
            self,
            token: str,
            app_name: str,
            storage: IStorage,
            market_data_stream_service: MarketDataStreamService,
            download_figi: list[str],
            data_collection_settings: DataCollectionSettings,
            api_errors_delay: int
    ) -> None:
        self.__token = token
        self.__app_name = app_name

        self.__storage = storage

        self.__last_event: datetime = None
        self.__collections_progress = False

        self.__market_data_stream_service = market_data_stream_service

        self.__download_figi = download_figi
        self.__data_collection_settings = data_collection_settings

        self.__api_errors_delay = api_errors_delay

    async def worker(self) -> None:
        logger.info("Start every day data collecting")

        while True:
            logger.info("Check trading schedule on today")

            try:
                is_trading_day, start_time, end_time = InstrumentService(
                    self.__token,
                    self.__app_name
                ).moex_today_trading_schedule()
                # for tests purposes
                # is_trading_day, start_time, end_time = \
                #    True, \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=5), \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=1)

                if is_trading_day and datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) < end_time:
                    logger.info(f"Today is trading day. Data collection will start after {start_time}")

                    await TinkoffCollector.__sleep_to(start_time)

                    while datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) < end_time:
                        try:
                            await self.__collect_data()
                        except Exception as ex:
                            logger.info(f"Collect error: {repr(ex)}")
                            logger.info(f"Try again after {self.__api_errors_delay} seconds")
                            await asyncio.sleep(self.__api_errors_delay)

                else:
                    logger.info("Nothing to collect today")

                    if is_trading_day:
                        logger.info("Trade session was over")
                    else:
                        logger.info("Today is not trading day")
            except Exception as ex:
                logger.error(f"Start data collection today error: {repr(ex)}")

            logger.info("Sleep to next morning")
            await TinkoffCollector.__sleep_to_next_morning()

    async def __collect_data(self) -> None:
        logger.info(f"Trading day has been started")

        self.__update_collection_status(True)

        try:
            async for marketdata in self.__market_data_stream_service.start_async_candles_stream(
                    self.__download_figi,
                    self.__data_collection_settings
            ):
                self.__update_last_event(marketdata)
                self.__storage.save(marketdata)
        finally:
            self.__update_collection_status(False)

        logger.info(f"Trading day has been finished")

    def __update_last_event(self, market_data: MarketDataResponse) -> None:
        if market_data.candle:
            if (not self.__last_event) or self.__last_event < market_data.candle.time:
                self.__last_event = market_data.candle.time
        elif market_data.trade:
            if (not self.__last_event) or self.__last_event < market_data.trade.time:
                self.__last_event = market_data.trade.time
        elif market_data.last_price:
            if (not self.__last_event) or self.__last_event < market_data.last_price.time:
                self.__last_event = market_data.last_price.time

    def last_event_time(self) -> datetime:
        return self.__last_event

    def __update_collection_status(self, status: bool) -> None:
        self.__collections_progress = status
        self.__last_event = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) if status else None

    def is_collection_in_progress(self) -> bool:
        return self.__collections_progress

    def restart(self) -> None:
        if self.is_collection_in_progress():
            logger.info(f"Restart required. Stopping stream. ")
            self.__market_data_stream_service.stop_candles_stream()

    @staticmethod
    async def __sleep_to_next_morning() -> None:
        future = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        next_time = datetime.datetime(year=future.year, month=future.month, day=future.day,
                                      hour=6, minute=0, tzinfo=datetime.timezone.utc)

        await TinkoffCollector.__sleep_to(next_time)

    @staticmethod
    async def __sleep_to(next_time: datetime) -> None:
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        logger.debug(f"Sleep from {now} to {next_time}")
        total_seconds = (next_time - now).total_seconds()

        if total_seconds > 0:
            await asyncio.sleep(total_seconds)
