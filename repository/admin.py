from django.contrib import admin
from . import models

admin.site.register(models.Account)
admin.site.register(models.CourseCategory)
admin.site.register(models.CourseSubCategory)
admin.site.register(models.DegreeCourse)
admin.site.register(models.Course)
admin.site.register(models.Teacher)
admin.site.register(models.Scholarship)
admin.site.register(models.CourseDetail)
admin.site.register(models.PricePolicy)

