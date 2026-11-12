from django.contrib import admin

from .models import AcademicProgramme, LearningResource, RecommendationHistory, StudentInterest, StudentProfile


admin.site.register(StudentInterest)
admin.site.register(StudentProfile)
admin.site.register(AcademicProgramme)
admin.site.register(LearningResource)
admin.site.register(RecommendationHistory)
