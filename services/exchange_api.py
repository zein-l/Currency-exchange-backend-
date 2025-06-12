import requests
from datetime import date, timedelta
import pandas as pd

# Live & historical rates via frankfurter.app (no key)
def get_live_rates(source='USD', currencies=None):
    if not currencies:
        currencies = ['EUR','GBP','CAD','JPY','USD']
    resp = requests.get(
        'https://api.frankfurter.app/latest',
        params={'from':source,'to':','.join(currencies)}
    )
    data = resp.json()
    if 'rates' not in data:
        raise Exception('Unexpected response from Frankfurter')
    quotes = {source+k: v for k,v in data['rates'].items()}
    return {
        'success':   True,
        'timestamp': data['date'],
        'source':    source,
        'quotes':    quotes
    }

def get_historical_rates(source='USD', currency='EUR', days=7):
    end   = date.today()
    start = end - timedelta(days=days)
    url   = f'https://api.frankfurter.app/{start.isoformat()}..{end.isoformat()}'
    resp  = requests.get(url, params={'from':source,'to':currency})
    data  = resp.json()
    if 'rates' not in data:
        raise Exception('Unexpected structure from Frankfurter')
    rates = {
        d: {f'{source}{currency}': v[currency]}
        for d,v in data['rates'].items()
    }
    return {
        'source':     source,
        'currency':   currency,
        'start_date': str(start),
        'end_date':   str(end),
        'rates':      rates
    }

def get_margin_info(currency='EUR', source='USD', margin_percent=2.0):
    data = get_live_rates(source=source, currencies=[currency])
    rate = data['quotes'][source+currency]
    return {
        'base':          source,
        'currency':      currency,
        'official_rate': rate,
        'platform_rate': round(rate*(1 + margin_percent/100),6),
        'markup_percent': margin_percent
    }

def get_historical_rates_df(source='USD', currency='EUR', days=7):
    raw = get_historical_rates(source, currency, days)
    records = [
        {'date': d, 'rate': v[f'{source}{currency}']}
        for d,v in raw['rates'].items()
    ]
    df = pd.DataFrame(records)
    if df.empty:
        return df
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date').reset_index(drop=True)
