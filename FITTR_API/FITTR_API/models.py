from django.db import models


class Product(models.Model):
    version = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    resistance_characteristic_uuid = models.CharField(max_length=50,default="87654321-4321-4321-4321-abcdef987654")
    stop_characteristic_uuid = models.CharField(max_length=50,default="87654321-4321-4321-4321-abcdef987654")
    service_uuid = models.CharField(max_length=50,default="12345678-1234-1234-1234-123456789abc")


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    weight = models.SmallIntegerField()
    height = models.SmallIntegerField()
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    product_id = models.ForeignKey(Product,
                                   to_field='id',
                                   on_delete=models.CASCADE) # Deletes the user if the related product is deleted
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'FITTR_API'


class ExerciseSession(models.Model):
    product_id = models.ForeignKey(
        Product,
        to_field='id',
        on_delete=models.DO_NOTHING,  # Do nothing to Product when ExerciseSession is deleted
    )
    user_id = models.ForeignKey(
        User,
        to_field='id',
        on_delete=models.DO_NOTHING,  # Do nothing to User when ExerciseSession is deleted
    )
    exercise_type = models.CharField(max_length=20)
    duration = models.PositiveSmallIntegerField()
    reps = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    errors = models.PositiveSmallIntegerField()