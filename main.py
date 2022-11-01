import asyncio
import logging
import os
import sys

from logging.handlers import RotatingFileHandler
from configuration.configuration import ProgramConfiguration
from data_collector.tinkoff_collector import TinkoffCollector
from data_storage.storage_factory import StorageFactory
from invest_api.services.market_data_stream_service import MarketDataStreamService
from observation.observer import Observer

# the configuration file name
CONFIG_FILE = "settings.ini"

logger = logging.getLogger(__name__)


def prepare_logs():
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[RotatingFileHandler('logs/collector.log', maxBytes=100000000, backupCount=10, encoding='utf-8')],
        encoding="utf-8"
    )


async def start_asyncio_trading(observer_worker: Observer, market_data_collector_worker: TinkoffCollector) -> None:
    # Some asyncio MAGIC for Windows OS
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logger.info("Start loop workers for data collection")

    collect_task = asyncio.create_task(market_data_collector_worker.worker())
    observer_task = asyncio.create_task(observer_worker.worker())

    await collect_task
    await observer_task


if __name__ == '__main__':
    prepare_logs()

    logger.info("Data collector has been started")

    try:
        config = ProgramConfiguration(CONFIG_FILE)
        logger.info("Configuration has been loaded")

        logger.info("Load data storage by configuration")
        data_storage = StorageFactory.new_factory(config.storage_type_name, config.storage_settings)

        if data_storage:
            logger.debug("Create data collector")
            market_data_service = MarketDataStreamService(config.tinkoff_token, config.tinkoff_app_name)

            market_data_collector = TinkoffCollector(
                config.tinkoff_token,
                config.tinkoff_app_name,
                data_storage,
                market_data_service,
                config.download_figi,
                config.data_collection_settings,
                config.watcher_settings.delay_between_api_errors_sec
            )

            observer = Observer(config.watcher_settings, market_data_collector)

            asyncio.run(start_asyncio_trading(observer, market_data_collector))

        else:
            logger.info(f"Storage hasn't been found by type name: {config.storage_type_name}")

    except Exception as ex:
        logger.error(f"Error has been occurred: {repr(ex)}")

    logger.info("Data collector has been finished.")
