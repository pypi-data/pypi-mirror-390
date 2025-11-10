from django.db import models

class DepreciationSchedule(models.Model):
    asset = models.OneToOneField("fixedassets.Asset", on_delete=models.CASCADE, related_name="schedule")
    start_date = models.DateField()
    frequency = models.CharField(max_length=8, default="monthly")

class DepreciationLine(models.Model):
    schedule = models.ForeignKey(DepreciationSchedule, on_delete=models.CASCADE, related_name="lines")
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    posted_entry_id = models.IntegerField(null=True, blank=True)
    is_posted = models.BooleanField(default=False)