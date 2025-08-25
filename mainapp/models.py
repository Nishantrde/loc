from django.db import models

# Create your models here.
class LocationReport(models.Model):
    timestamp = models.DateTimeField(null=True, blank=True)
    provider = models.CharField(max_length=64, blank=True, null=True)
    # coords and address are JSONField so you can inspect nested objects easily
    coords = models.JSONField(null=True, blank=True)
    address = models.JSONField(null=True, blank=True)
    raw = models.JSONField(null=True, blank=True)   # raw reverse-geocode response
    reverse_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider or 'unknown'} @ {self.timestamp or self.created_at}"

