from django.db import models
from datetime import date

class Product(models.Model):
    version = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    left_resistance_characteristic_uuid = models.CharField(max_length=50,default="87654321-4321-4321-4321-abcdef987654")
    right_resistance_characteristic_uuid = models.CharField(max_length=50,default="87654321-4321-4321-4321-abcdef987654")
    stop_characteristic_uuid = models.CharField(max_length=50,default="87654321-4321-4321-4321-abcdef987654")
    service_uuid = models.CharField(max_length=50,default="12345678-1234-1234-1234-123456789abc")
    # starts or stops the exercise
    exercise_initialize_uuid = models.CharField(max_length=50,default="12345678-1234-1234-1234-123456789abc")


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
    fitness_goal = models.CharField(max_length=30,default="undecided")
    def get_age(self):
        today = date.today()
        born = self.date_of_birth
        try: # handles the case where the birthday is today
            birthday_this_year = born.replace(year=today.year)
        except ValueError: # handles Feb 29th birthdays
            birthday_this_year = born.replace(year=today.year, day=born.day-1)
        if birthday_this_year > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year
    def get_bmi(self):
        return # TODO
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
    duration = models.FloatField()
    reps = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    errors = models.PositiveSmallIntegerField()