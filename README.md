# inapp-purchases
Manage in-app purchases for Apple AppStore and Google Play

[![PyPI version](https://badge.fury.io/py/inapp-purchases.svg)](https://badge.fury.io/py/inapp-purchases)
[![Code Health](https://landscape.io/github/adanmauri/inapp-purchases/master/landscape.svg?style=flat)](https://landscape.io/github/adanmauri/inapp-purchases/master)


## Installation
```shell
pip install inapp-purchases
```

## Usage
Currently inapp-purchases supports Google Play and App Store subscription services. But, product purchases is available retrieving raw data.

### Google Play:

```python
from inapp_purchases.google_play import GooglePlayService

service = GooglePlayService(
    service_account_file='service-info.json',
    # or service_account_info='service-info.json'
    package_name='com.package.name'
)

purchase = service.get_subscription_purchase(
    subscription_id='com.subscription.id',
    token='purchase-token'
)
```

### AppStore:

```python
from inapp_purchases.app_store import AppStoreService

service = AppStoreService(
    sandbox=True,
    password='secret-password'
)

purchase = service.get_subscription_purchase(
    receipt_data='receive-hash'
)
```

## Response

```python
{
    'bundle_id': unicode,
    'subscription_id': unicode,
    'purchase_id': unicode,
    'original_purchase_id': unicode,
    'purchase_date_ms': int,
    'original_purchase_date_ms': int,
    'auto_renewing': bool,
    'expires_date_ms': int,
    'country_code': unicode,
    'price_currency_code': unicode,
    'price_amount': float,
    'cancellation_date_ms': int,
    'cancellation_reason': unicode,,
    'payment_state': int,
    'status': unicode,
    'is_active': bool,
    'is_trial_period': bool,
    'expiration_intent': unicode,
}
```

## TODO

- Exceptions
- Google Play products data response (the raw content is returned)
- AppStore products data response (the raw content is returned)
- Get list of products from AppStore
- Tests
- Retrieve more information from the services
- Documentation
- Examples
