from django.db import models

class Acquisition(models.Model):
    asset = models.OneToOneField("fixedassets.Asset", on_delete=models.CASCADE, related_name="acquisition")
    date = models.DateField()
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)

class Revaluation(models.Model):
    asset = models.ForeignKey("fixedassets.Asset", on_delete=models.CASCADE, related_name="revaluations")
    date = models.DateField()
    increase_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    decrease_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)

class Impairment(models.Model):
    asset = models.ForeignKey("fixedassets.Asset", on_delete=models.CASCADE, related_name="impairments")
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)

class Disposal(models.Model):
    asset = models.OneToOneField("fixedassets.Asset", on_delete=models.CASCADE, related_name="disposal")
    date = models.DateField()
    proceeds = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)