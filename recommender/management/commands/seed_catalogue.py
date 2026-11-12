import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from recommender.models import AcademicProgramme, LearningResource, StudentInterest


class Command(BaseCommand):
    help = 'Seed the DMI St. John the Baptist University catalogue for programmes and learning resources.'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[3]
        programme_path = base_dir / 'data' / 'programmes.json'
        resource_path = base_dir / 'data' / 'learning_resources.json'

        if not programme_path.exists() or not resource_path.exists():
            raise CommandError('Catalogue data files are missing.')

        try:
            programmes = json.loads(programme_path.read_text(encoding='utf-8'))
            for item in programmes:
                AcademicProgramme.objects.update_or_create(
                    name=item['name'],
                    institution=item['institution'],
                    defaults={
                        'faculty': item.get('faculty', ''),
                        'academic_field': item.get('academic_field', ''),
                        'description': item.get('description', ''),
                        'required_qualifications': item.get('required_qualifications', ''),
                        'required_subjects': ', '.join(item.get('required_subjects', [])),
                        'min_grade_requirements': item.get('min_grade_requirements', ''),
                        'programme_duration': item.get('programme_duration', ''),
                        'study_mode': item.get('study_mode', ''),
                        'career_opportunities': ', '.join(item.get('career_opportunities', [])),
                        'skills_associated': ', '.join(item.get('skills_associated', [])),
                        'interest_tags': ', '.join(item.get('interest_tags', [])),
                        'is_active': item.get('is_active', True),
                    },
                )

            resources = json.loads(resource_path.read_text(encoding='utf-8'))
            for item in resources:
                LearningResource.objects.update_or_create(
                    title=item['title'],
                    subject=item['subject'],
                    defaults={
                        'description': item.get('description', ''),
                        'academic_level': item.get('academic_level', ''),
                        'category': item.get('category', ''),
                        'learning_format': item.get('learning_format', ''),
                        'difficulty_level': item.get('difficulty_level', ''),
                        'skills_covered': ', '.join(item.get('skills_covered', [])),
                        'interest_tags': ', '.join(item.get('interest_tags', [])),
                        'resource_url': item.get('resource_url', ''),
                        'is_active': item.get('is_active', True),
                    },
                )

            for name in ['technology', 'business', 'data', 'research', 'security', 'environment', 'leadership', 'innovation']:
                StudentInterest.objects.get_or_create(name=name)

            self.stdout.write(self.style.SUCCESS('Catalogue seeded successfully.'))
        except Exception as exc:
            raise CommandError(f'Catalogue seeding failed: {exc}')
