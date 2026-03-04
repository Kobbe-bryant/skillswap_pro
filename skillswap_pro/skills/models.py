from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('USER', 'Regular User'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('Tech', 'Technology'),
        ('Arts', 'Arts'),
        ('Languages', 'Languages'),
        ('Music', 'Music'),
        ('Fitness', 'Fitness'),
        ('Other', 'Other'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Tech'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Skills'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True, max_length=500)
    skills_offered = models.ManyToManyField(
        Skill,
        related_name='offered_by',
        blank=True
    )
    skills_wanted = models.ManyToManyField(
        Skill,
        related_name='wanted_by',
        blank=True
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"


class SwapRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    )
    
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )
    skill_offering = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        related_name='offered_in_swaps'
    )
    skill_wanting = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        related_name='wanted_in_swaps'
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('sender', 'receiver', 'skill_offering', 'skill_wanting')
        verbose_name_plural = 'Swap Requests'

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} | {self.get_status_display()}"


class Rating(models.Model):
    """Rating given after a swap is completed."""
    swap = models.OneToOneField(
        SwapRequest,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    rater = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ratings_given'
    )
    ratee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='ratings_received'
    )
    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return f"Rating {self.score} from {self.rater.username} to {self.ratee.username}"


class Notification(models.Model):
    """Simple notification model for user events."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}..."


class Lesson(models.Model):
    """A scheduled lesson or simulated teaching session.

    Tutors create lessons associated with a Skill. Learners can join lessons and
    later access a simple simulator page where the tutor can upload or display
    lesson content. This is a placeholder for a more complex interactive
    experience.
    """
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    tutor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='lessons_given'
    )
    title = models.CharField(max_length=200)
    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lessons'
    )
    description = models.TextField(blank=True, null=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )
    # optional materials for the lesson
    material_file = models.FileField(
        upload_to='lesson_materials/',
        blank=True,
        null=True
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text='Link to an external video or embed (e.g. YouTube)'
    )
    learners = models.ManyToManyField(
        CustomUser,
        related_name='lessons_taken',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']
        verbose_name_plural = 'Lessons'

    def __str__(self):
        return f"{self.title} by {self.tutor.username}"

