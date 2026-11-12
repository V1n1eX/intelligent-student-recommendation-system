from django.contrib.auth.models import User
from django.db import models


class StudentInterest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    QUALIFICATION_CHOICES = [
        ('secondary', 'Secondary School / Certificate'),
        ('diploma', 'Diploma / Certificate'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    highest_qualification = models.CharField(max_length=30, choices=QUALIFICATION_CHOICES, default='secondary', blank=True)
    academic_background = models.CharField(max_length=255, blank=True)
    previous_institution = models.CharField(max_length=150, blank=True)
    academic_subjects = models.CharField(max_length=255, blank=True)
    subject_grades = models.CharField(max_length=255, blank=True)
    areas_of_interest = models.ManyToManyField(StudentInterest, blank=True)
    preferred_fields = models.CharField(max_length=255, blank=True)
    career_interests = models.CharField(max_length=255, blank=True)
    learning_style = models.CharField(max_length=50, blank=True)
    study_mode = models.CharField(max_length=50, blank=True)
    academic_goals = models.TextField(blank=True)
    profile_completion = models.FloatField(default=0.0)

    def get_interest_names(self):
        return [interest.name for interest in self.areas_of_interest.all()]

    def update_profile_completion(self):
        fields = [
            self.full_name,
            self.age,
            self.highest_qualification,
            self.academic_background,
            self.previous_institution,
            self.academic_subjects,
            self.subject_grades,
            self.preferred_fields,
            self.career_interests,
            self.learning_style,
            self.study_mode,
            self.academic_goals,
        ]
        total = len(fields) + 1
        completed = sum(1 for value in fields if value not in (None, '', []))
        if self.pk is not None and self.areas_of_interest.exists():
            completed += 1
        self.profile_completion = round((completed / total) * 100, 2)
        return self.profile_completion

    def save(self, *args, **kwargs):
        self.update_profile_completion()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.username


class AcademicProgramme(models.Model):
    name = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    faculty = models.CharField(max_length=200, blank=True)
    academic_field = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    required_qualifications = models.TextField(blank=True)
    required_subjects = models.CharField(max_length=255, blank=True)
    min_grade_requirements = models.CharField(max_length=200, blank=True)
    programme_duration = models.CharField(max_length=100, blank=True)
    study_mode = models.CharField(max_length=50, blank=True)
    career_opportunities = models.CharField(max_length=255, blank=True)
    skills_associated = models.CharField(max_length=255, blank=True)
    interest_tags = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LearningResource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=150, blank=True)
    academic_level = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=80, blank=True)
    learning_format = models.CharField(max_length=80, blank=True)
    difficulty_level = models.CharField(max_length=80, blank=True)
    skills_covered = models.CharField(max_length=255, blank=True)
    interest_tags = models.CharField(max_length=255, blank=True)
    resource_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class RecommendationHistory(models.Model):
    RECOMMENDATION_TYPES = [
        ('programme', 'Programme'),
        ('resource', 'Resource'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendation_history')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    recommendation_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} - {self.recommendation_type}'
