import calendar
import locale
from datetime import datetime

from aiogram.types import User

from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    "Always returns ru_RU locale for consistent Russian language support"
    return "ru_RU"


class GenericCalendar:

    def __init__(
        self,
        locale: str = None,  # оставляем для обратной совместимости
        cancel_btn: str = None,
        today_btn: str = None,
        show_alerts: bool = False,
    ) -> None:
        """Initialize calendar with Russian language by default

        Parameters:
        locale (str): Ignored, always uses Russian
        cancel_btn (str): label for button Cancel to cancel date input
        today_btn (str): label for button Today to set calendar back to todays date
        show_alerts (bool): defines how the date range error would shown (defaults to False)
        """
        self._labels = CalendarLabels()

        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if today_btn:
            self._labels.today_caption = today_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts

    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'Дата должна быть позже {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts,
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'Дата должна быть раньше {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts,
            )
            return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date
