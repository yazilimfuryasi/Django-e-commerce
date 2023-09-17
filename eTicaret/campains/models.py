from django.db import models

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    discount_rate = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
    