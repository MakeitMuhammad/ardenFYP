from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.


#-------------------------------------------------
#User
#-------------------------------------------------
class CustomUser(AbstractUser):
    ACCOUNT_TYPES = [
        ('user', 'User Account'),
        ('expert', 'Expert Account'),
    ]
    
    full_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)

    def __str__(self):
        return f"{self.full_name} ({self.account_type})"
    
#-------------------------------------------------
#Profile
#-------------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    qualification = models.CharField(max_length=100, blank=True)
    last_work_company = models.CharField(max_length=100, blank=True)
    profile_pic_url = models.ImageField(upload_to='pictures/profile/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"
    
#-------------------------------------------------
#socials
#-------------------------------------------------
class SocialLink(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='social_link')
    
    website = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Social Links"
    
#-------------------------------------------------
# Project
#-------------------------------------------------
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.title
    

    
#-------------------------------------------------
# Project Tasks
#-------------------------------------------------
class ProjectTask(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.TextField()
    status = models.CharField(max_length=50, default='pending')


#-------------------------------------------------
#tags
#-------------------------------------------------
class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
       
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
#-------------------------------------------------
# message
#-------------------------------------------------
User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"
    

#-------------------------------------------------
# notifications
#-------------------------------------------------
User = get_user_model()

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.full_name} from {self.sender.full_name}"