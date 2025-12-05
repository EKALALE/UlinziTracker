from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

# ---------------------------
# User Profile model
# ---------------------------
class Profile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('authority', 'Authority'),
        ('officer', 'Officer'),
        ('chief', 'Area Chief'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        app_label = 'UlinziTracker'


# Signal to create Profile automatically when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ---------------------------
# Incident/Report model
# ---------------------------
class Incident(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    )

    CATEGORY_CHOICES = (
        ('suspicious_activity', 'Suspicious Activity'),
        ('emergency', 'Emergency'),
        ('disturbance', 'Neighborhood Disturbance'),
        ('other', 'Other'),
    )

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    location = models.CharField(max_length=200, blank=True, null=True)
    time_reported = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_time = models.DurationField(blank=True, null=True)

    # Multimedia fields
    image = models.ImageField(upload_to='incident_images/', blank=True, null=True)
    video = models.FileField(upload_to='incident_videos/', blank=True, null=True)
    audio = models.FileField(upload_to='incident_audio/', blank=True, null=True)
    document = models.FileField(upload_to='incident_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    class Meta:
        app_label = 'UlinziTracker'
