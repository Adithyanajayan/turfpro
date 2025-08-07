

from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import time

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=[('player', 'Player'), ('owner', 'Owner')])

    def __str__(self):
        return self.username


class SportType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Turf_details(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='turf')
    name = models.CharField(max_length=20,unique='true')
    location = models.CharField(max_length=50)
    price = models.CharField(max_length=5)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    sport_types = models.ManyToManyField(SportType, related_name='turf')
    image = models.ImageField(upload_to='turf_images/', null=True, blank=True)
    length = models.FloatField(null=True, blank=True)  
    width = models.FloatField(null=True, blank=True)  
    has_floodlight = models.BooleanField(default=False)
    has_drinking_water = models.BooleanField(default=False)

    PLAYER_CAPACITY_CHOICES = [
        ('5', "5's"),
        ('7', "7's"),
        ('11', "11's"),
    ]
    player_capacity = models.CharField(
        max_length=2,
        choices=PLAYER_CAPACITY_CHOICES,
        null=True,
        blank=True
    )

    extra_features = models.TextField(
        null=True,
        blank=True,
        help_text="Any other features not listed above"
    )

    
    
    
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    turf = models.ForeignKey(Turf_details, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_confirmed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} booked {self.turf.name} on {self.date}"

    def duration_hours(self):
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600


class Bill(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='bill')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill for {self.booking}"



class Schedule(models.Model):
    turf = models.ForeignKey(Turf_details, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedule')

    class Meta:
        unique_together = ('turf', 'date', 'start_time', 'end_time')

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.turf.name} on {self.date} from {self.start_time} to {self.end_time} - {status}"


