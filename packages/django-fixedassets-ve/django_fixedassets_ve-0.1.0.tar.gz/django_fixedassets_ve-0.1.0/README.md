## 📖 README (Quickstart excerpt)

# django-fixedassets-ve

## Install
```
pip install django-fixedassets-ve
```
## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "fixedassets"]
FIXEDASSETS = {"AUTO_POST": True}
```
## URLs
```
path("api/fa/", include("fixedassets.api.urls"))
```
## Create Asset & Post Acquisition
```
POST /api/fa/assets/
{ "company":1, "category":1, "code":"FA-0002", "name":"Printer", "purchase_date":"2025-11-01", "currency":"INR", "cost":"30000.00" }

POST /api/fa/acquisitions/
{ "asset": 2, "date": "2025-11-01", "memo":"Capex" }
```
## Post Monthly Depreciation
```
POST /api/fa/depreciations/
{ "schedule": 1, "date":"2025-11-30", "amount":"1500.00" }
```
## Revaluation / Impairment / Disposal
```
POST /api/fa/revaluations/  |  /impairments/  |  /disposals/
```


 