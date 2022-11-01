import csv
import datetime
import logging
from pathlib import Path

from tinkoff.invest import MarketDataResponse, Candle, Trade, LastPrice
from tinkoff.invest.utils import quotation_to_decimal

from configuration.settings import StorageSettings
from data_storage.base_storage import IStorage


__all__ = ("CSVDataStorage")

logger = logging.getLogger(__name__)


class CSVDataStorage(IStorage):
    __FILE_NAME = "market_data.csv"

    __CANDLE_TYPE_FOLDER = "candle"
    __TRADE_TYPE_FOLDER = "trade"
    __LAST_PRICE_TYPE_FOLDER = "last_price"

    # Consts to read and parse dict with configuration
    __ROOT_PATH_NAME = "root_path"
    __BUFFER_ROW_SIZE_NAME = "buffer_row_size"

    def __init__(self, settings: StorageSettings) -> None:
        self.__root_path = settings.settings.get(self.__ROOT_PATH_NAME, None)

        self.__buffer_row_size = settings.settings.get(self.__BUFFER_ROW_SIZE_NAME, None)

        if not (self.__root_path and self.__buffer_row_size):
            logger.error(f"Storage init failed: root path is {self.__root_path}, "
                         f"buffer row size is {self.__buffer_row_size}")

            raise Exception(f"CSVDataStorage: All settings must be specified, but some of them is empty")

    def save(self, market_data: MarketDataResponse) -> None:
        try:
            if market_data.candle:
                self.__save_candle(market_data.candle)
            elif market_data.trade:
                self.__save_trade(market_data.trade)
            elif market_data.last_price:
                self.__save_last_price(market_data.last_price)
            else:
                logger.debug(f"Nothing to save")

        except Exception as ex:
            logger.error(f"Error while write market data to file: {repr(ex)}")

    def __save_candle(self, candle: Candle) -> None:
        """
        Headers in candle csv file:
        open, close, high, low, volume, time
        """
        row = [
            quotation_to_decimal(candle.open),
            quotation_to_decimal(candle.close),
            quotation_to_decimal(candle.high),
            quotation_to_decimal(candle.low),
            candle.volume,
            candle.time
        ]

        CSVDataStorage.__write_data_row(
            self.__calculate_file_path(candle.figi, self.__CANDLE_TYPE_FOLDER, candle.time),
            row
        )

    def __save_trade(self, trade: Trade) -> None:
        """
        Headers in trade csv file:
        direction, price, quantity, time
        """
        row = [
            int(trade.direction),
            quotation_to_decimal(trade.price),
            trade.quantity,
            trade.time
        ]

        CSVDataStorage.__write_data_row(
            self.__calculate_file_path(trade.figi, self.__TRADE_TYPE_FOLDER, trade.time),
            row
        )

    def __save_last_price(self, last_price: LastPrice) -> None:
        """
        Headers in last_price csv file:
        price, time
        """
        row = [
            quotation_to_decimal(last_price.price),
            last_price.time
        ]

        CSVDataStorage.__write_data_row(
            self.__calculate_file_path(last_price.figi, self.__LAST_PRICE_TYPE_FOLDER, last_price.time),
            row
        )

    def __calculate_file_path(self, figi: str, type_folder: str, time: datetime) -> str:
        """
        Folder Structure is:
        root_path
            figi
                type_folder
                    year
                        month
                            day
                                {file_name}
        """
        directories = [
            self.__root_path, figi, type_folder, str(time.year), str(time.month), str(time.day)
        ]

        current_dir = None
        for directory in directories:
            current_dir = CSVDataStorage.__check_or_mk_dir(
                current_dir.joinpath(Path(directory)) if current_dir else Path(directory)
            )

        return str(Path(current_dir, self.__FILE_NAME))

    @staticmethod
    def __check_or_mk_dir(directory: Path) -> Path:
        if not directory.exists():
            logger.info(f"Directory doesn't exist: {directory}. Making...")
            directory.mkdir()

        return directory

    @staticmethod
    def __write_data_row(file_name: str, row: list) -> None:
        logger.debug(f"Write to file: {file_name}. Data: {row}")

        with open(file_name, 'a', encoding='UTF8', newline="") as file:
            csv_writer = csv.writer(file)

            # write the data
            csv_writer.writerow(row)

    @staticmethod
    def __write_data_rows(file_name: str, rows: list[list]) -> None:
        logger.debug(f"Write to file: {file_name}. Data: {rows}")

        with open(file_name, 'a', encoding='UTF8', newline="") as file:
            csv_writer = csv.writer(file)

            # write the data
            csv_writer.writerows(rows)
