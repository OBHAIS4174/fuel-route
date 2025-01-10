from django.db import models

class FuelStation(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    price_per_gallon = models.FloatField()

    def __str__(self):
        return f"{self.city}, {self.state}: ${self.price_per_gallon}"
