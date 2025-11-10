# django-purchase


## Install
```
pip install django-purchase
```


## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "purchase"]
```


## URLs
```
path("api/purchase/", include("purchase.api.urls"))
```


## Create & Post a Bill
```
POST /api/purchase/bills/
{ "company": 1, "vendor": 1, "number": "B-0001", "date": "2025-11-09", "currency": "INR",
"is_tax_inclusive": false, "lines": [ {"item": 1, "qty": 1, "rate": "1000.00", "tax": 1} ] }

```



# settings.py
```
INSTALLED_APPS += ["rest_framework", "finacc", "purchase"]
PURCHASE = {
  "AUTO_POST_BILL": True,
  "AUTO_POST_VENDORCREDIT": True,
  "AUTO_POST_PAYMENT": True,
  "AUTO_POST_SUPPLIER_REFUND": True,
}
```

# urls.py
```
path("api/purchase/", include("purchase.api.urls")),
```
# migration
```
python manage.py migrate
python manage.py purchase_bootstrap_demo --company=1
```

### Create & post a Bill (API)
```
POST /api/purchase/bills/
{
  "company": 1, "vendor": 1, "number": "B-0001",
  "date": "2025-11-09", "currency": "INR",
  "is_tax_inclusive": false,
  "lines": [{"item": 1, "qty": 1, "rate": "1000.00", "tax": 1}]
}
```