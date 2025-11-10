from django.core.management.base import BaseCommand
from finacc.models.company import Company
from finacc.models.accounts import Account
from fixedassets.models.asset import AssetCategory, Asset
from fixedassets.models.config import FAAccountMapping

class Command(BaseCommand):
    help = "Create FA categories, a sample asset and account mapping"

    def add_arguments(self, parser):
        parser.add_argument("--company", type=int, required=True)

    def handle(self, *args, **opts):
        c = Company.objects.get(id=opts["company"])
        cat, _ = AssetCategory.objects.get_or_create(company=c, name="Computers", defaults={"depreciation_method":"slm", "useful_life_years":3, "residual_value":1000})
        Asset.objects.get_or_create(company=c, category=cat, code="FA-0001", defaults={"name":"Laptop", "purchase_date":"2025-04-01", "currency":"INR", "cost":60000, "book_value":60000})
        def acc(code): return Account.objects.get(company=c, code=code)
        FAAccountMapping.objects.get_or_create(company=c, defaults={
            "asset_account": acc("1500"),
            "accum_depr_account": acc("1590"),
            "depr_expense_account": acc("6100"),
            "gain_loss_account": acc("7100"),
        })
        self.stdout.write(self.style.SUCCESS("Fixed Assets demo ready"))