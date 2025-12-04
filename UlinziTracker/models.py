from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

class Meta:
    app_label = 'UlinziTracker'

# User Profile model
class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('security', 'Security Officer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_regex = RegexValidator(
        regex=r'^\d{10,10}$', 
        message="Phone number must be entered in the format: Up to 10 digits allowed."
    )
    contact_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)  # optional location field

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Signal to create Profile automatically when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Incident/Report model for UlinziTracker
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
    response_time = models.DurationField(blank=True, null=True)  # optional analytics field

    def __str__(self):
        return f"{self.title} ({self.status})"
