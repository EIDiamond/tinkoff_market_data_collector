import datetime
import logging

from tinkoff.invest import Client, TradingSchedule

from invest_api.invest_error_decorators import invest_error_logging, invest_api_retry

__all__ = ("InstrumentService")

logger = logging.getLogger(__name__)


class InstrumentService:
    """
    The class encapsulate tinkoff instruments api
    """
    __MOEX_EXCHANGE_NAME = "MOEX"

    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    def moex_today_trading_schedule(self) -> (bool, datetime, datetime):
        """
        :return: Information about trading day status, datetime trading day start, datetime trading day end
        (both on today)
        """
        for schedule in self.__trading_schedules(
                exchange=self.__MOEX_EXCHANGE_NAME,
                _from=datetime.datetime.utcnow(),
                _to=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        ):
            for day in schedule.days:
                if day.date.date() == datetime.date.today():
                    logger.info(f"MOEX today schedule: {day}")
                    return day.is_trading_day, day.start_time, day.end_time

        return False, datetime.datetime.utcnow(), datetime.datetime.utcnow()

    @invest_api_retry()
    @invest_error_logging
    def __trading_schedules(
            self,
            exchange: str,
            _from: datetime,
            _to: datetime
    ) -> list[TradingSchedule]:
        result = []

        with Client(self.__token, app_name=self.__app_name) as client:
            logger.debug(f"Trading Schedules for exchange: {exchange}, from: {_from}, to: {_to}")

            for schedule in client.instruments.trading_schedules(
                    exchange=exchange,
                    from_=_from,
                    to=_to
            ).exchanges:
                logger.debug(f"{schedule}")
                result.append(schedule)

        return result
