"""
All user models (College, Customer, Teacher, Student) are extension of the django built-in User model. These models
have a OneToOne relationship with the built-in User model. This means all our users are stored in the Users table but
they are represented by their respective tables (College and Customer table if that User is a customer, Teacher table
if that User is a teacher).
This is the most simple way to work with the django's built-in authentication system.
"""
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class College(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    phone_no = models.CharField(max_length=13)
    card_info = models.CharField(max_length=16)

    def __str__(self):
        return self.first_name


class Customer(models.Model):
    college = models.OneToOneField(College, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.college.first_name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)

    def __str__(self):
        return self.first_name


class ClassName(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    class_name = models.ForeignKey(ClassName, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)

    def __str__(self):
        return self.first_name


class Subject(models.Model):
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ClassWork(models.Model):
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
