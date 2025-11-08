from django.apps import apps
from magnet_data.currencies.currency_pair import CurrencyPair
from magnet_data.currencies.enums import CurrencyAcronyms
from magnet_data.holidays.enums import Countries
from magnet_data import utils
import datetime


class Currencies(CurrencyAcronyms):
    @staticmethod
    def get_pair(base_currency: str, counter_currency: str) -> CurrencyPair:
        """
        Returns a CurrencyPair object
        """
        return CurrencyPair(
            base_currency=base_currency,
            counter_currency=counter_currency
        )


class Holidays(Countries):
    def __init__(self):
        self.cls = apps.get_model(
            app_label='magnet_data',
            model_name='Holiday'
        )
        self.reset_cache()

    def reset_cache(self):
        self.last_updated = {}

    def update(self, country_code: str, year):
        """
        Update values stored in the database with what the api returned
        """
        now = datetime.datetime.now()
        threshold = now - datetime.timedelta(1)
        if (
            self.last_updated.get(year) is None
            or self.last_updated.get(year) < threshold
        ):
            self.last_updated[year] = now
            self.cls.update_holidays(country_code=country_code.upper(), year=year)

    def is_workday(self, date, country_code: str) -> bool:
        """
        Alias for Holidays.get_next_business_day for backwards compatibility
        """
        return self.is_business_day(date, country_code)

    def is_business_day(self, date, country_code: str) -> bool:
        """
        Returns True if the given date is not Saturday, Sunday, or
        Holiday
        Keyword arguments:
            from_date -- date to check
            country-code -- ISO 3166 country code
        """
        self.update(country_code, date.year)
        if date.weekday() == 5:  # Saturday
            return False

        if date.weekday() == 6:  # Sunday
            return False

        return not self.cls.objects.filter(
            date=date,
            country_code=country_code.upper(),
        ).exists()

    def get_next_working_day(self,
                             country_code: str,
                             working_days: int = 1,
                             from_date: datetime.date = None,
                             step: int = 1):
        """
        Alias for Holidays.get_next_business_day for backwards compatibility
        """
        return self.get_next_business_day(country_code, working_days, from_date, step)

    def get_next_business_day(self,
                              country_code: str,
                              business_days_count: int = 1,
                              from_date: datetime.date = None,
                              step: int = 1) -> datetime.date:
        """
        Returns the next date that is a working day.
        Keyword arguments:
            country-code -- ISO 3166 country code
            business_days_count -- number of business days to count (default 1)
            from_date -- date to start counting from (default today)
            step -- the amount by which the index increases. (default 1)
        """
        if from_date is None:
            from_date = utils.today()

        last_updated_year = from_date.year

        self.update(country_code, year=last_updated_year)

        final_date = from_date

        while business_days_count > 0:
            final_date += datetime.timedelta(days=step)

            if last_updated_year != final_date.year:
                last_updated_year = final_date.year
                self.update(country_code, year=last_updated_year)

            if self.is_workday(date=final_date, country_code=country_code):
                business_days_count -= 1

        return final_date

    def get_holidays_count_during_weekdays(self,
                                           country_code: str,
                                           start_date: datetime.date,
                                           end_date: datetime.date) -> int:
        """
        Returns the number of holidays between two dates, not considering
        saturdays and sundays
        Keyword arguments:
            country-code -- ISO 3166 country code
            start_date -- date to start counting from
            end_date -- date where to stop counting
        """
        for year in range(start_date.year, end_date.year + 1):
            self.update(country_code, year)

        days = 0

        holidays_dates = self.cls.objects.filter(
            date__range=[start_date, end_date],
            country_code=country_code.upper(),
        ).values_list('date', flat=True)

        for date in holidays_dates:
            if date.weekday() not in (5, 6):  # not in sunday or saturday
                days += 1

        return days

    def get_business_days_count(self, country_code: str,
                                start_date: datetime.date,
                                end_date: datetime.date) -> int:
        """
        Returns the number of businesss days between two dates
        Keyword arguments:
            country-code -- ISO 3166 country code
            start_date -- date to start counting from
            end_date -- date where to stop counting
        """
        for year in range(start_date.year, end_date.year + 1):
            self.update(country_code, year)

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        delta = (end_date - start_date).days + 1
        full_weeks, remaining_days = divmod(delta, 7)
        business_days = full_weeks * 5

        for i in range(remaining_days):
            if (start_date.weekday() + i) % 7 < 5:
                business_days += 1

        # get holidays
        holidays_count = self.get_holidays_count_during_weekdays(
            country_code=country_code,
            start_date=start_date,
            end_date=end_date
        )

        return business_days - holidays_count


class MagnetDataClient:
    def __init__(self) -> None:
        super().__init__()
        self.currencies = Currencies()
        self.holidays = Holidays()
