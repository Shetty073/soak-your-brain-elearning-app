"""
All user models (College, Customer, Teacher, Student) are extension of the django built-in User model. These models
have a OneToOne relationship with the built-in User model. This means all our users are stored in the Users table but
they are represented by their respective tables (College and Customer table if that User is a customer, Teacher table
if that User is a teacher).
This is the most simple way to work with the django's built-in authentication system.
"""
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Plan(models.Model):
    name = models.CharField(max_length=256)
    price_per_month = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_year = models.DecimalField(max_digits=6, decimal_places=2)
    upcoming_price_per_month = models.FloatField(null=True, blank=True)
    upcoming_price_per_year = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class College(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan_subscribed = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    college_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=256, unique=True)
    phone_no = models.CharField(max_length=13)
    card_info = models.CharField(max_length=16)
    signup_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.college_name


class Customer(models.Model):
    '''
    This is a copy of the College table but this table will exist even if College (customer) deletes his/her account
    '''
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    plan_subscribed = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    college_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=256, unique=True)
    phone_no = models.CharField(max_length=13)
    signup_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.college_name


class Department(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CollegeClass(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    college_classes = models.ManyToManyField(CollegeClass, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    college_class = models.ForeignKey(CollegeClass, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subject(models.Model):
    college_class = models.ForeignKey(CollegeClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ClassWork(models.Model):
    college_class = models.ForeignKey(CollegeClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
