from django.db import models


class Product(models.Model):
    version = models.CharField(max_length=10)

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.SmallIntegerField()
    email = models.EmailField()
    password = models.CharField(max_length=50)
    weight = models.SmallIntegerField()
    height = models.SmallIntegerField()
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    product_id = models.ForeignKey(Product,
                                   to_field='id',
                                   on_delete=models.CASCADE) # Deletes the user if the related product is deleted
    class Meta:
        app_label = 'FITTR_API'