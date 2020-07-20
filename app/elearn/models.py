from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class College(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False)
    email = models.EmailField(max_length=256, null=False)
    phone_no = models.CharField(max_length=13, null=False)
    card_info = models.CharField(max_length=16, null=False)

    def __str__(self):
        return self.name


class Customer(models.Model):
    college = models.OneToOneField(College, on_delete=models.SET_NULL)

    def __str__(self):
        return self.college.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False)
    email = models.EmailField(max_length=256, null=False)

    def __str__(self):
        return self.name


class ClassName(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    department = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    class_name = models.ForeignKey(ClassName, on_delete=models.SET_NULL)
    name = models.CharField(max_length=256, null=False)
    email = models.EmailField(max_length=256, null=False)

    def __str__(self):
        return self.name


class Subject(models.Model):
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False)

    def __str__(self):
        return self.name


class ClassWork(models.Model):
    class_name = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=False)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
