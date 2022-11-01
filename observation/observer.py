import asyncio
import datetime
import logging

from configuration.settings import WatcherSettings
from observation.observable import IObservableDataCollector

__all__ = ("Observer")

logger = logging.getLogger(__name__)


class Observer:
    """
    The class handles data collection status to struggle with API hangs
    """
    def __init__(self, settings: WatcherSettings, data_collector: IObservableDataCollector) -> None:
        self.__settings = settings
        self.__data_collector = data_collector

    async def worker(self) -> None:
        while True:
            # logger.debug("Check current data collection status")

            if self.__data_collector.is_collection_in_progress() and self.__data_collector.last_event_time():
                now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

                last_event_total_seconds_delay = (now - self.__data_collector.last_event_time()).total_seconds()

                logger.debug(f"Status check! Current delay is {last_event_total_seconds_delay}")

                if last_event_total_seconds_delay > self.__settings.max_sec_api_silence:
                    self.__data_collector.restart()

            await asyncio.sleep(self.__settings.max_sec_api_silence)
