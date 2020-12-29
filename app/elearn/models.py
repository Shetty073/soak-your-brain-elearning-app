"""
All user models (College, Customer, Teacher, Student) are extension of the django built-in User model. These models
have a OneToOne relationship with the built-in User model. This means all our users are stored in the Users table but
they are represented by their respective tables (College and Customer table if that User is a customer, Teacher table
if that User is a teacher).
This is the most simple way to work with the django's built-in authentication system.
"""
from django.contrib.auth.models import User
from django.db import models


# Project models
class SybAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)


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
    """
    This is a copy of the College table but this table will exist even if College (customer) deletes his/her account
    """
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
    # TODO: Cross check this model changes with UML diagrams and update the diagrams
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Subject(models.Model):
    # TODO: Cross check this model changes with UML diagrams and update the diagrams
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class CollegeClass(models.Model):
    # TODO: Cross check this model changes with UML diagrams and update the diagrams
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    college_classes = models.ManyToManyField(CollegeClass, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)

    def name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    college_class = models.ForeignKey(CollegeClass, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)

    def name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ClassWorkPost(models.Model):
    college_class = models.ForeignKey(CollegeClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, blank=True)
    title = models.CharField(max_length=256)
    is_assignment = models.BooleanField(default=False)
    is_classtest = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class TextPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.post.title


def user_video_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/videos/filename
    return f'user_{instance.user.id}/videos/{instance.post.id}/{filename}'


class VideoPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    video_url = models.FileField(upload_to=user_video_directory_path)

    def __str__(self):
        return self.post.title


def user_document_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/documents/filename
    return f'user_{instance.user.id}/documents/{instance.post.id}/{filename}'


class DocumentPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    document_url = models.FileField(upload_to=user_document_directory_path)

    def __str__(self):
        return self.post.title


def user_image_directory_path(instance, filename):
    # this will return a file path that is unique for all the users
    # file will be uploaded to MEDIA_ROOT/user_id/images/filename
    return f'user_{instance.user.id}/images/{instance.post.id}/{filename}'


class ImagePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)
    image_url = models.ImageField(upload_to=user_image_directory_path)

    def __str__(self):
        return self.post.title


class YouTubePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    youtube_link = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.post.title


class ArticlePost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    article_link = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.post.title


class PostComment(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)

    def __str__(self):
        return self.post.title


class ClassTestPost(models.Model):
    post = models.ForeignKey(ClassWorkPost, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    class_test_post = models.ForeignKey(ClassTestPost, on_delete=models.CASCADE)
    question = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=256, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.question.question} {self.choice}'
