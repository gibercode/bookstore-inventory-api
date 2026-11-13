import re
from decimal import ROUND_HALF_UP, Decimal

import requests
from django.conf import settings
from django.core.cache import cache

CURRENCY_CODE = re.compile(r'[A-Z]{3}')
CENTS = Decimal('0.01')


class ExchangeRateError(Exception):
    """The exchange rate provider failed or returned something unusable."""


class UnknownCurrencyError(ExchangeRateError):
    """The currency code is malformed or not offered by the provider."""


class ExchangeRateService:
    """Client for exchangerate-api.com (v4 `latest` endpoint).

    Rates are cached because the provider only refreshes them once a day.
    """

    def __init__(self, base_url=None, timeout=None, cache_ttl=None):
        self.base_url = (base_url or settings.EXCHANGE_RATE_API_URL).rstrip('/')
        self.timeout = timeout or settings.EXCHANGE_RATE_TIMEOUT
        self.cache_ttl = settings.EXCHANGE_RATE_CACHE_TTL if cache_ttl is None else cache_ttl

    def get_rates(self, base='USD'):
        """Return {currency_code: Decimal rate} for one unit of `base`."""
        base = self._normalize(base)
        key = f'exchange_rates:{base}'

        rates = cache.get(key)
        if rates is None:
            rates = self._fetch_rates(base)
            cache.set(key, rates, self.cache_ttl)
        return rates

    def get_rate(self, currency, base='USD'):
        currency = self._normalize(currency)
        rates = self.get_rates(base)
        try:
            return rates[currency]
        except KeyError:
            raise UnknownCurrencyError(f'Currency "{currency}" is not supported.')

    def get_local_rate(self):
        """USD -> local currency (settings.LOCAL_CURRENCY, VES by default)."""
        return self.get_rate(settings.LOCAL_CURRENCY)

    def convert_to_local(self, amount_usd):
        return self.convert(amount_usd, settings.LOCAL_CURRENCY)

    def convert(self, amount, to_currency, base='USD'):
        """Convert `amount` of `base` into `to_currency`, rounded to cents."""
        rate = self.get_rate(to_currency, base)
        return (Decimal(str(amount)) * rate).quantize(CENTS, rounding=ROUND_HALF_UP)

    def _fetch_rates(self, base):
        try:
            response = requests.get(f'{self.base_url}/{base}', timeout=self.timeout)
        except requests.RequestException as exc:
            raise ExchangeRateError(f'Could not reach the exchange rate provider: {exc}')

        if response.status_code == 404:
            raise UnknownCurrencyError(f'Currency "{base}" is not supported.')
        if not response.ok:
            raise ExchangeRateError(
                f'Exchange rate provider answered with status {response.status_code}.'
            )

        try:
            return dict(response.json(parse_float=Decimal)['rates'])
        except (ValueError, KeyError, TypeError):
            raise ExchangeRateError('Exchange rate provider returned an unexpected payload.')

    @staticmethod
    def _normalize(code):
        code = str(code).strip().upper()
        if not CURRENCY_CODE.fullmatch(code):
            raise UnknownCurrencyError(f'"{code}" is not a valid 3-letter currency code.')
        return code
