from django.db import models

class FAAccountMapping(models.Model):
    company = models.OneToOneField("finacc.Company", on_delete=models.CASCADE)
    asset_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="fa_asset")
    accum_depr_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="fa_accum")
    depr_expense_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="fa_depr_exp")
    gain_loss_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="fa_gain_loss")
    revaluation_reserve = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="fa_reval_res", null=True, blank=True)
