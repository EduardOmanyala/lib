from django.core.management.base import BaseCommand
from questions.models import Course, Subject


class Command(BaseCommand):
    help = 'Populate the database with courses and subjects'

    def handle(self, *args, **options):
        self.stdout.write('Creating courses and subjects...')

        # Create courses
        courses_data = [
            {'code': 'kcse', 'name': 'KCSE'},
            {'code': 'cpa', 'name': 'CPA/CPS'},
            {'code': 'kmtc', 'name': 'KMTC'},
            {'code': 'acca', 'name': 'ACCA'},
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={'name': course_data['name']}
            )
            if created:
                self.stdout.write(f'Created course: {course.name}')
            else:
                self.stdout.write(f'Course already exists: {course.name}')

        # Create subjects for each course
        subjects_data = {
            'kcse': [
                'Mathematics', 'Physics', 'Chemistry', 'Biology',
                'English', 'Kiswahili', 'History', 'Geography',
                'Computer Studies', 'Business Studies', 'Agriculture'
            ],
            'cpa': [
                'Financial Accounting', 'Auditing'
            ],
            'kmtc': [
                'Nursing', 'Clinical Medicine', 'Pharmacy'
            ],
            'acca': [
                'Financial Accounting', 'Management Accounting', 'Audit & Assurance'
            ]
        }

        for course_code, subject_names in subjects_data.items():
            try:
                course = Course.objects.get(code=course_code)
                for subject_name in subject_names:
                    # Create a unique code for each subject
                    subject_code = f"{course_code}_{subject_name.lower().replace(' ', '_')}"
                    
                    subject, created = Subject.objects.get_or_create(
                        code=subject_code,
                        defaults={
                            'name': subject_name,
                            'course': course
                        }
                    )
                    if created:
                        self.stdout.write(f'Created subject: {subject.name} for {course.name}')
                    else:
                        self.stdout.write(f'Subject already exists: {subject.name} for {course.name}')
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Course {course_code} not found'))

        self.stdout.write(self.style.SUCCESS('Successfully populated courses and subjects'))
