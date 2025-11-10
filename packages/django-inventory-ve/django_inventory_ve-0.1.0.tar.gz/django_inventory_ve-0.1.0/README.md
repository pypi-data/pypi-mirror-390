# django-inventory-ve


## Install
```
pip install django-inventory-ve
```

## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "inventory"]
INVENTORY = {"DEFAULT_COST_METHOD": "avg", "AUTO_POST_COGS": True, "AUTO_HOOK_SALES": True}
```

## URLs
```
path("api/inventory/", include("inventory.api.urls"))
```

## Create & Post a Stock Move (IN)
```
POST /api/inventory/moves/
{ "company": 1, "item": 1, "warehouse": 1, "date": "2025-11-09", "currency": "INR",
"type": "in", "qty": "10.000000", "unit_cost": "250.00", "ref": "B-0001" }
```

## Issue Stock (OUT → COGS)
```
POST /api/inventory/moves/
{ "company": 1, "item": 1, "warehouse": 1, "date": "2025-11-09", "currency": "INR",
"type": "out", "qty": "2.000000", "ref": "S-0001" }
```

# settings.py
```
INSTALLED_APPS += ["rest_framework", "finacc", "inventory"]
INVENTORY = {"DEFAULT_COST_METHOD": "avg", "AUTO_POST_COGS": True, "AUTO_HOOK_SALES": True}
```

# urls.py
```
path("api/inventory/", include("inventory.api.urls")),
```
# migrations
```
python manage.py migrate
python manage.py inventory_bootstrap_demo --company=1
```
```
POST /api/inventory/moves/
{ "company":1,"item":1,"warehouse":1,"date":"2025-11-09","currency":"INR",
  "type":"in","qty":"10.000000","unit_cost":"250.00","ref":"B-0001" }
```
```
POST /api/inventory/moves/
{ "company":1,"item":1,"warehouse":1,"date":"2025-11-09","currency":"INR",
  "type":"out","qty":"2.000000","ref":"S-0001" }

```