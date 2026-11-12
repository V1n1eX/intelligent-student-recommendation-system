from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import AcademicProgramme, LearningResource, StudentInterest, StudentProfile
from .recommendation_engine import generate_programme_recommendations, generate_resource_recommendations


class RecommendationSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', email='s@example.com', password='StrongPass123')
        self.profile = StudentProfile.objects.create(
            user=self.user,
            full_name='Student One',
            age=20,
            highest_qualification='secondary',
            academic_background='Mathematics and sciences',
            academic_subjects='Mathematics, Computer Science, Physics',
            preferred_fields='Computer Science, Data Science',
            career_interests='Software engineering, Data analysis',
            learning_style='Visual',
            study_mode='Full-time',
            academic_goals='Become a data scientist',
        )
        self.profile.areas_of_interest.set([
            StudentInterest.objects.create(name='technology'),
            StudentInterest.objects.create(name='data'),
        ])
        self.programme = AcademicProgramme.objects.create(
            name='BSc Computer Science',
            institution='DMI St. John the Baptist University',
            faculty='Engineering',
            academic_field='Computer Science',
            description='Study software engineering and computing theory.',
            required_qualifications='Secondary school certificate',
            required_subjects='Mathematics, Computer Science',
            min_grade_requirements='B',
            programme_duration='4 years',
            study_mode='Full-time',
            career_opportunities='Software Engineer, Data Analyst',
            skills_associated='Programming, Problem Solving',
            interest_tags='technology, coding, software',
            is_active=True,
        )
        self.resource = LearningResource.objects.create(
            title='Python for Data Analysis',
            description='Useful for data analysis and practical coding.',
            subject='Data Science',
            academic_level='Undergraduate',
            category='Course',
            learning_format='Online',
            difficulty_level='Intermediate',
            skills_covered='Python, Data Analysis',
            interest_tags='data, analytics, coding',
            resource_url='https://example.com',
            is_active=True,
        )

    def test_registration_form(self):
        response = self.client.post(reverse('register'), {
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_login_and_dashboard_protection(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='student1', password='StrongPass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_creation_and_editing(self):
        self.client.login(username='student1', password='StrongPass123')
        response = self.client.post(reverse('profile_setup'), {
            'full_name': 'Student One',
            'age': 21,
            'highest_qualification': 'secondary',
            'academic_background': 'STEM',
            'previous_institution': 'Example Academy',
            'academic_subjects': 'Mathematics, Computer Science',
            'subject_grades': 'Mathematics: A, Computer Science: A',
            'preferred_fields': 'Computer Science',
            'career_interests': 'Software engineering',
            'learning_style': 'Visual',
            'study_mode': 'Full-time',
            'academic_goals': 'Career in software engineering',
            'areas_of_interest': [StudentInterest.objects.get_or_create(name='technology')[0].pk],
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.profile_completion, 100.0)

    def test_programme_and_resource_recommendations(self):
        programmes = generate_programme_recommendations(self.profile, AcademicProgramme.objects.filter(is_active=True), limit=5)
        resources = generate_resource_recommendations(self.profile, LearningResource.objects.filter(is_active=True), limit=5)
        self.assertTrue(programmes)
        self.assertTrue(resources)
        self.assertGreater(programmes[0]['score'], 0)

    def test_empty_catalogues(self):
        empty_programmes = generate_programme_recommendations(self.profile, AcademicProgramme.objects.none(), limit=5)
        empty_resources = generate_resource_recommendations(self.profile, LearningResource.objects.none(), limit=5)
        self.assertEqual(empty_programmes, [])
        self.assertEqual(empty_resources, [])

    def test_duplicate_prevention(self):
        self.assertEqual(AcademicProgramme.objects.filter(name='BSc Computer Science').count(), 1)
