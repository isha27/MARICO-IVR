from django.db import models

# Create your models here.

class maricodata(models.Model):
    retailercode = models.CharField(max_length = 20)
    distcode = models.CharField(max_length = 20)
    skucode = models.CharField(max_length=20)
    phone = models.CharField(max_length = 20) 
    dialled = models.BooleanField(default=False)

