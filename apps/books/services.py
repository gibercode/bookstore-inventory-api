import logging
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.utils import timezone

from apps.books.models import Book
from apps.core.services.exchange_rate import CENTS, ExchangeRateError, ExchangeRateService

logger = logging.getLogger(__name__)

SELLING_PRICE_FIELD = Book._meta.get_field('selling_price_local')
MAX_SELLING_PRICE = Decimal(10) ** (SELLING_PRICE_FIELD.max_digits - SELLING_PRICE_FIELD.decimal_places)


class PriceOutOfRangeError(Exception):
    """The calculated price does not fit in Book.selling_price_local."""


def calculate_selling_price(book, rate_service=None):
    """Price a book in the local currency and store it in `selling_price_local`.

    local cost    = cost_usd * (USD -> local currency rate)
                    (a default rate is used if the exchange API fails)
    selling price = local cost + profit margin
    """
    rate_service = rate_service or ExchangeRateService()
    try:
        rate = rate_service.get_local_rate()
        rate_source = 'api'
    except ExchangeRateError:
        logger.warning('Exchange rate API failed, using the default rate', exc_info=True)
        rate = settings.DEFAULT_EXCHANGE_RATE
        rate_source = 'default'
    margin = settings.PROFIT_MARGIN_PERCENTAGE

    cost_local = (book.cost_usd * rate).quantize(CENTS, rounding=ROUND_HALF_UP)
    selling_price = (cost_local * (100 + margin) / 100).quantize(CENTS, rounding=ROUND_HALF_UP)
    if selling_price >= MAX_SELLING_PRICE:
        raise PriceOutOfRangeError('Calculated price is too large to be stored.')

    book.selling_price_local = selling_price
    book.save(update_fields=['selling_price_local', 'updated_at'])

    return {
        'book_id': book.pk,
        'cost_usd': book.cost_usd,
        'exchange_rate': rate,
        'cost_local': cost_local,
        'margin_percentage': margin,
        'selling_price_local': selling_price,
        'currency': settings.LOCAL_CURRENCY,
        'rate_source': rate_source,
        'calculation_timestamp': timezone.now(),
    }
