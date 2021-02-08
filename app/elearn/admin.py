from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Plan)
admin.site.register(models.College)
admin.site.register(models.Invoice)
admin.site.register(models.Teacher)
admin.site.register(models.Department)
admin.site.register(models.CollegeClass)
admin.site.register(models.Student)
admin.site.register(models.Subject)
admin.site.register(models.ClassWorkPost)
admin.site.register(models.TextPost)
admin.site.register(models.VideoPost)
admin.site.register(models.DocumentPost)
admin.site.register(models.ImagePost)
admin.site.register(models.YouTubePost)
admin.site.register(models.ArticlePost)
admin.site.register(models.PostComment)
admin.site.register(models.CommentReply)
admin.site.register(models.ClassTestPost)
admin.site.register(models.Question)
admin.site.register(models.Choice)
admin.site.register(models.StudentChoice)
admin.site.register(models.ClassTestSolution)
admin.site.register(models.AssignmentSolution)
