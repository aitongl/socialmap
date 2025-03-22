from django.db import models
from django.contrib.auth.models import User
import googlemaps
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    labels = models.CharField(blank=True, max_length=40)
    grade = models.IntegerField(default=0)
    school = models.CharField(blank=True, max_length=40)
    major = models.CharField(blank=True, max_length=40)
    picture = models.FileField(blank=True)
    following = models.ManyToManyField(User, related_name="followers")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=40.4433)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=-79.9436)
    content_type = models.CharField(max_length=50, default="jpeg")

    def save(self, *args, **kwargs):
        if self.labels:
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            geocode_result = gmaps.geocode(self.labels)
            if geocode_result:
                self.latitude = geocode_result[0]['geometry']['location']['lat']
                self.longitude = geocode_result[0]['geometry']['location']['lng']
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'user={self.user.username}, grade={self.grade}'
    
class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="chats_initiated")
    user2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="chats_received")
    start_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_chat_between_users'),
            models.CheckConstraint(
                check=models.Q(user1__lt=models.F('user2')),  # Ensures user1's ID is always smaller than user2
                name='enforce_user_order'
            ),
        ]


class Message(models.Model):
    time = models.DateTimeField()
    content = models.CharField(blank=True, max_length=4000)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)