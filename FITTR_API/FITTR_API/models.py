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
    heartbeat_uuid = models.CharField(max_length=50,default="e429a327-c1a4-4a25-956e-f3d632bdd63a")

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
        height_meters = self.height/100
        return self.weight/(height_meters**2)
    def get_bmr(self):
        if self.gender.lower() == 'male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.get_age())
        elif self.gender.lower() == 'female':
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.get_age())
        else:
            bmr = 0  # Default to 0 if gender is not specified correctly
        return bmr
    def get_bmi_description(self):
        bmi = self.get_bmi()
        if bmi < 18.5:
            return f"Underweight (BMI: {bmi:.2f})"
        elif 18.5 <= bmi < 22.9:
            return f"Normal weight (BMI: {bmi:.2f})"
        elif 23 <= bmi < 27.4:
            return f"Overweight (BMI: {bmi:.2f})"
        else:
            return f"Obese (BMI: {bmi:.2f})"
    def get_bmr_description(self):
        bmr = self.get_bmr()
        if bmr == 0: return "Undefined bmr. Do not use bmr value as context"
        if bmr < 1200:
            return f"Below optimal BMR (BMR: {bmr:.2f})"
        elif 1200 <= bmr < 1800:
            return f"Optimal BMR (BMR: {bmr:.2f})"
        else:
            return f"Above optimal BMR (BMR: {bmr:.2f})"
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