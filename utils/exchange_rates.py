import httpx
import asyncio
from datetime import datetime, timedelta

RATES_CACHE = {}
CACHE_EXPIRY = datetime.now()

async def get_exchange_rates(base_currency="USD"):
    global RATES_CACHE, CACHE_EXPIRY

    base_currency = base_currency.upper()

    if base_currency in RATES_CACHE and datetime.now() < CACHE_EXPIRY:
        return RATES_CACHE[base_currency]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency}")
            if response.status_code == 200:
                data = response.json()
                RATES_CACHE[base_currency] = data.get("rates", {})
                CACHE_EXPIRY = datetime.now() + timedelta(hours=1)
                return RATES_CACHE[base_currency]
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")

    return RATES_CACHE.get(base_currency, {"USD": 1.0, "UZS": 12500, "EUR": 0.9, "RUB": 90.0}) # Fallback

async def convert_currency(amount, from_curr, to_curr):
    if from_curr == to_curr:
        return amount

    rates = await get_exchange_rates(to_curr)
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()

    # rates are relative to to_curr (1 to_curr = rates[X] X)
    # wait, usually it's 1 base = rates[target] target
    # So if base is USD, rates['UZS'] = 12500 means 1 USD = 12500 UZS.

    # We want 1 from_curr in to_curr.
    # If rates are relative to to_curr: 1 to_curr = rates[from_curr] from_curr
    # => 1 from_curr = 1 / rates[from_curr] to_curr

    if from_curr in rates:
        return float(amount) / rates[from_curr]

    # If not directly available, try via USD
    usd_rates = await get_exchange_rates("USD")
    if from_curr in usd_rates and to_curr in usd_rates:
        amount_in_usd = float(amount) / usd_rates[from_curr]
        return amount_in_usd * usd_rates[to_curr]

    return float(amount)
