from django.core.management.base import BaseCommand
from django.utils import timezone
from skills.models import CustomUser, Skill, Profile, SwapRequest, Rating, Lesson
import random

class Command(BaseCommand):
    help = 'Load sample data into the SkillSwap database'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')

        # Create skills
        skill_data = [
            ('Python', 'Tech'),
            ('JavaScript', 'Tech'),
            ('React', 'Tech'),
            ('Django', 'Tech'),
            ('Data Science', 'Tech'),
            ('Machine Learning', 'Tech'),
            ('Web Design', 'Tech'),
            ('Photography', 'Arts'),
            ('Painting', 'Arts'),
            ('Graphic Design', 'Arts'),
            ('Digital Drawing', 'Arts'),
            ('Sculpture', 'Arts'),
            ('Spanish', 'Languages'),
            ('French', 'Languages'),
            ('German', 'Languages'),
            ('Mandarin', 'Languages'),
            ('Piano', 'Music'),
            ('Guitar', 'Music'),
            ('Singing', 'Music'),
            ('Yoga', 'Fitness'),
            ('Weight Training', 'Fitness'),
            ('Running', 'Fitness'),
            ('Pilates', 'Fitness'),
        ]

        skills = {}
        for skill_name, category in skill_data:
            skill, _ = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category}
            )
            skills[skill_name] = skill
        
        self.stdout.write(f'Created {len(skills)} skills')

        # Create 20 sample users
        sample_users = [
            {
                'username': 'alice_smith',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'bio': 'Full-stack developer passionate about open source. Love learning new technologies!',
                'offers': ['Python', 'Django', 'Web Design'],
                'wants': ['Spanish', 'Photography'],
            },
            {
                'username': 'bob_jones',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Jones',
                'bio': 'Frontend specialist with 5 years experience in React and modern JavaScript.',
                'offers': ['JavaScript', 'React'],
                'wants': ['Machine Learning', 'German'],
            },
            {
                'username': 'carol_williams',
                'email': 'carol@example.com',
                'first_name': 'Carol',
                'last_name': 'Williams',
                'bio': 'Data scientist exploring the world of AI and ML. Enthusiastic about teaching!',
                'offers': ['Data Science', 'Machine Learning', 'Python'],
                'wants': ['Piano', 'Photography'],
            },
            {
                'username': 'david_brown',
                'email': 'david@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'bio': 'Professional photographer and digital artist. Always excited to share my passion!',
                'offers': ['Photography', 'Digital Drawing', 'Graphic Design'],
                'wants': ['Python', 'Guitar'],
            },
            {
                'username': 'emma_davis',
                'email': 'emma@example.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'bio': 'Yoga instructor and fitness enthusiast. Let\'s grow together!',
                'offers': ['Yoga', 'Pilates', 'Running'],
                'wants': ['French', 'React'],
            },
            {
                'username': 'frank_miller',
                'email': 'frank@example.com',
                'first_name': 'Frank',
                'last_name': 'Miller',
                'bio': 'Software architect with expertise in scalable systems and best practices.',
                'offers': ['Django', 'Python', 'Web Design'],
                'wants': ['Singing', 'Spanish'],
            },
            {
                'username': 'grace_wilson',
                'email': 'grace@example.com',
                'first_name': 'Grace',
                'last_name': 'Wilson',
                'bio': 'Artist and painter. Inspiring creativity in others is my mission!',
                'offers': ['Painting', 'Graphic Design', 'Digital Drawing'],
                'wants': ['Python', 'JavaScript'],
            },
            {
                'username': 'henry_moore',
                'email': 'henry@example.com',
                'first_name': 'Henry',
                'last_name': 'Moore',
                'bio': 'Music teacher specializing in classical and contemporary styles.',
                'offers': ['Piano', 'Guitar', 'Singing'],
                'wants': ['Web Design', 'Mandarin'],
            },
            {
                'username': 'iris_taylor',
                'email': 'iris@example.com',
                'first_name': 'Iris',
                'last_name': 'Taylor',
                'bio': 'Language enthusiast fluent in 4 languages. Love cultural exchange!',
                'offers': ['Spanish', 'French', 'German'],
                'wants': ['React', 'Photography'],
            },
            {
                'username': 'jack_anderson',
                'email': 'jack@example.com',
                'first_name': 'Jack',
                'last_name': 'Anderson',
                'bio': 'Fitness coach and personal trainer. Your health is my passion!',
                'offers': ['Weight Training', 'Running', 'Yoga'],
                'wants': ['Python', 'Piano'],
            },
            {
                'username': 'kate_thomas',
                'email': 'kate@example.com',
                'first_name': 'Kate',
                'last_name': 'Thomas',
                'bio': 'Full-stack developer and tech mentor. Helping others learn is rewarding!',
                'offers': ['JavaScript', 'React', 'Python'],
                'wants': ['Painting', 'Mandarin'],
            },
            {
                'username': 'leo_jackson',
                'email': 'leo@example.com',
                'first_name': 'Leo',
                'last_name': 'Jackson',
                'bio': 'Web designer with an eye for detail and user experience.',
                'offers': ['Web Design', 'Graphic Design', 'Digital Drawing'],
                'wants': ['Django', 'Guitar'],
            },
            {
                'username': 'mia_white',
                'email': 'mia@example.com',
                'first_name': 'Mia',
                'last_name': 'White',
                'bio': 'Machine learning engineer passionate about AI and its applications.',
                'offers': ['Machine Learning', 'Data Science', 'Python'],
                'wants': ['Singing', 'French'],
            },
            {
                'username': 'noah_harris',
                'email': 'noah@example.com',
                'first_name': 'Noah',
                'last_name': 'Harris',
                'bio': 'Backend specialist focusing on scalability and performance.',
                'offers': ['Django', 'Python', 'Data Science'],
                'wants': ['Photography', 'Spanish'],
            },
            {
                'username': 'oliver_martin',
                'email': 'oliver@example.com',
                'first_name': 'Oliver',
                'last_name': 'Martin',
                'bio': 'Artist exploring multiple mediums. Always learning something new!',
                'offers': ['Painting', 'Sculpture', 'Digital Drawing'],
                'wants': ['React', 'Mandarin'],
            },
            {
                'username': 'patricia_lee',
                'email': 'patricia@example.com',
                'first_name': 'Patricia',
                'last_name': 'Lee',
                'bio': 'Language teacher with a love for cultural diversity and exchange.',
                'offers': ['Mandarin', 'Spanish', 'French'],
                'wants': ['Web Design', 'Yoga'],
            },
            {
                'username': 'quentin_perez',
                'email': 'quentin@example.com',
                'first_name': 'Quentin',
                'last_name': 'Perez',
                'bio': 'Frontend developer specializing in UI/UX and modern frameworks.',
                'offers': ['React', 'JavaScript', 'Web Design'],
                'wants': ['Piano', 'German'],
            },
            {
                'username': 'rachel_clark',
                'email': 'rachel@example.com',
                'first_name': 'Rachel',
                'last_name': 'Clark',
                'bio': 'Photographer capturing moments and stories. Let\'s collaborate!',
                'offers': ['Photography', 'Graphic Design', 'Web Design'],
                'wants': ['Machine Learning', 'Singing'],
            },
            {
                'username': 'samuel_rodriguez',
                'email': 'samuel@example.com',
                'first_name': 'Samuel',
                'last_name': 'Rodriguez',
                'bio': 'Fitness enthusiast and wellness coach. Transform your life today!',
                'offers': ['Weight Training', 'Pilates', 'Running'],
                'wants': ['JavaScript', 'Painting'],
            },
            {
                'username': 'tessa_garcia',
                'email': 'tessa@example.com',
                'first_name': 'Tessa',
                'last_name': 'Garcia',
                'bio': 'Musician and composer passionate about sharing the joy of music!',
                'offers': ['Guitar', 'Singing', 'Piano'],
                'wants': ['Python', 'French'],
            },
        ]

        created_users = []
        for user_data in sample_users:
            username = user_data.pop('username')
            email = user_data.pop('email')
            first_name = user_data.pop('first_name')
            last_name = user_data.pop('last_name')
            bio = user_data.pop('bio')
            offers = user_data.pop('offers')
            wants = user_data.pop('wants')

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                user = CustomUser(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='USER',
                )
                user.set_password('password123')
                user.save()
                created_users.append(user)

            # Update profile
            profile = user.profile
            profile.bio = bio
            profile.save()

            # Add skills
            for skill_name in offers:
                profile.skills_offered.add(skills[skill_name])
            for skill_name in wants:
                profile.skills_wanted.add(skills[skill_name])

        self.stdout.write(f'Created {len(created_users)} users')

        # Create some swap requests and ratings
        all_users = list(CustomUser.objects.all())
        if len(all_users) >= 2:
            for i in range(5):
                sender = all_users[i % len(all_users)]
                receiver = all_users[(i + 1) % len(all_users)]
                
                if sender != receiver:
                    sender_skills = sender.profile.skills_offered.all()
                    receiver_skills = receiver.profile.skills_offered.all()
                    
                    if sender_skills.exists() and receiver_skills.exists():
                        # Only create if one doesn't already exist
                        existing = SwapRequest.objects.filter(
                            sender=sender, 
                            receiver=receiver
                        ).first()
                        
                        if not existing:
                            swap = SwapRequest.objects.create(
                                sender=sender,
                                receiver=receiver,
                                skill_offering=sender_skills.first(),
                                skill_wanting=receiver_skills.first(),
                                status='Accepted',
                            )

        # Add a few sample lessons for demonstration
        lessons_data = [
            {
                'tutor': all_users[0],
                'title': 'Intro to Python',
                'skill': skills['Python'],
                'description': 'Learn the basics of Python programming.',
                'scheduled_time': timezone.now() + timezone.timedelta(days=1),
                'status': 'Scheduled'
            },
            {
                'tutor': all_users[3],
                'title': 'Photography 101',
                'skill': skills['Photography'],
                'description': 'Beginner photography tips and tricks.',
                'scheduled_time': timezone.now() + timezone.timedelta(days=2),
                'status': 'Scheduled'
            },
        ]
        for ld in lessons_data:
            Lesson.objects.get_or_create(
                title=ld['title'],
                tutor=ld['tutor'],
                skill=ld['skill'],
                defaults={
                    'description': ld['description'],
                    'scheduled_time': ld['scheduled_time'],
                    'status': ld['status'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
