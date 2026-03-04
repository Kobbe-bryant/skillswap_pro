from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from skills.models import CustomUser, Skill, Profile, Lesson, Notification


def create_user(username, offers=None):
    user = CustomUser.objects.create_user(username=username, password='pass1234')
    profile = user.profile
    profile.bio = f'Bio for {username}'
    if offers:
        for skill in offers:
            profile.skills_offered.add(skill)
    profile.save()
    return user


class LessonFlowTests(TestCase):
    def setUp(self):
        # create skills
        self.python = Skill.objects.create(name='Python', category='Tech')
        self.guitar = Skill.objects.create(name='Guitar', category='Music')

        # create two users
        self.tutor = create_user('tutor1', offers=[self.python])
        self.learner = create_user('learner1', offers=[self.guitar])

        self.client = Client()

    def test_create_lesson_allowed(self):
        self.client.login(username='tutor1', password='pass1234')
        url = reverse('lesson_create')
        # upload a dummy file and set video url
        file = SimpleUploadedFile('notes.txt', b'These are notes')
        response = self.client.post(url, {
            'title': 'Intro Python',
            'skill': self.python.id,
            'description': 'Learn to code',
            'scheduled_time': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'material_file': file,
            'video_url': 'https://example.com/video'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        lesson = Lesson.objects.get(title='Intro Python')
        self.assertEqual(lesson.tutor, self.tutor)
        self.assertTrue(lesson.material_file.name.startswith('lesson_materials/'))
        self.assertEqual(lesson.video_url, 'https://example.com/video')

    def test_create_lesson_disallowed(self):
        # learner is not offering python
        self.client.login(username='learner1', password='pass1234')
        url = reverse('lesson_create')
        response = self.client.post(url, {
            'title': 'Bad Lesson',
            'skill': self.python.id,
            'description': 'Should fail',
            'scheduled_time': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        }, follow=True)
        # Should not create lesson
        self.assertFalse(Lesson.objects.filter(title='Bad Lesson').exists())
        # form should have an invalid choice error for skill field
        self.assertContains(response, 'Select a valid choice')

    def test_join_creates_notification(self):
        # first create lesson by tutor
        lesson = Lesson.objects.create(
            tutor=self.tutor,
            title='Python 101',
            skill=self.python,
            scheduled_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.client.login(username='learner1', password='pass1234')
        join_url = reverse('lesson_join', args=[lesson.id])
        response = self.client.post(join_url, follow=True)
        self.assertEqual(response.status_code, 200)
        # verify notification for tutor
        note = Notification.objects.filter(user=self.tutor).last()
        self.assertIn('learner1 joined your lesson', note.message)

    def test_simulator_access(self):
        lesson = Lesson.objects.create(
            tutor=self.tutor,
            title='Python 101',
            skill=self.python,
            scheduled_time=timezone.now() + timezone.timedelta(days=1)
        )
        url = reverse('lesson_simulator', args=[lesson.id])
        # tutor can access
        self.client.login(username='tutor1', password='pass1234')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # someone else can't
        self.client.logout()
        outsider = create_user('outsider', offers=[self.guitar])
        self.client.login(username='outsider', password='pass1234')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
        # learner joins then can access
        self.client.logout()
        self.client.login(username='learner1', password='pass1234')
        self.client.post(reverse('lesson_join', args=[lesson.id]))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_file_upload_and_download(self):
        """Test that tutors can upload files and learners can download them."""
        # tutor uploads a lesson with material
        self.client.login(username='tutor1', password='pass1234')
        url = reverse('lesson_create')
        pdf_file = SimpleUploadedFile('lesson.pdf', b'%PDF-1.4 fake pdf content')
        response = self.client.post(url, {
            'title': 'Advanced Python',
            'skill': self.python.id,
            'description': 'Advanced concepts',
            'scheduled_time': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'material_file': pdf_file,
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        lesson = Lesson.objects.get(title='Advanced Python')
        # verify material was uploaded
        self.assertTrue(lesson.material_file)
        self.assertIn('lesson_materials', lesson.material_file.name)
        # learner joins then can access simulator with materials
        self.client.logout()
        self.client.login(username='learner1', password='pass1234')
        self.client.post(reverse('lesson_join', args=[lesson.id]))
        sim_url = reverse('lesson_simulator', args=[lesson.id])
        resp = self.client.get(sim_url)
        # verify file link is in response
        self.assertContains(resp, lesson.material_file.url)
        # verify video link is embedded
        self.assertContains(resp, 'youtube.com/embed')

    def test_video_only_lesson(self):
        """Test lesson with only a video link (no file upload)."""
        self.client.login(username='tutor1', password='pass1234')
        url = reverse('lesson_create')
        response = self.client.post(url, {
            'title': 'Video Lesson',
            'skill': self.python.id,
            'description': 'Video-based teaching',
            'scheduled_time': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'video_url': 'https://www.youtube.com/embed/abc123xyz'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        lesson = Lesson.objects.get(title='Video Lesson')
        self.assertFalse(lesson.material_file)  # no file
        self.assertEqual(lesson.video_url, 'https://www.youtube.com/embed/abc123xyz')

    def test_file_only_lesson(self):
        """Test lesson with only a file upload (no video)."""
        self.client.login(username='tutor1', password='pass1234')
        url = reverse('lesson_create')
        doc_file = SimpleUploadedFile('notes.docx', b'docx content here')
        response = self.client.post(url, {
            'title': 'Document Lesson',
            'skill': self.python.id,
            'description': 'Document-based teaching',
            'scheduled_time': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'material_file': doc_file
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        lesson = Lesson.objects.get(title='Document Lesson')
        self.assertTrue(lesson.material_file)  # file exists
        self.assertFalse(lesson.video_url)  # no video
