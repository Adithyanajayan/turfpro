

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.db import models
from datetime import time
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    def create_user(self, email, phone = None, password = None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, phone = None, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, phone, password, **extra_fields)
    


class CustomUser(AbstractBaseUser,PermissionsMixin):
    
    phone = models.CharField(max_length=10,unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=[('player', 'Player'), ('owner', 'Owner'), ('admin', 'admin')],default='player')
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "first_name", "last_name"]

    objects = UserManager()


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
    is_approved = models.BooleanField(default=False)

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
    
    STATUS_CHOICES =[('enabled','Enabled'),('disabled','Disabled')] 
    
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='enabled')
    
    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

class Rating(models.Model):
    turf = models.ForeignKey(Turf_details, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # rating 1–5

    class Meta:
        unique_together = ('turf', 'user')
    
    def toggle_status(self):
        self.status = 'disabled' if self.status == 'enabled' else 'enabled'
        self.save()
        return self.status
    
    
    
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    turf = models.ForeignKey(Turf_details, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    STATUS_CHOICES =[('pending','pending'),('confirmed','confirmed'),('incomplete', 'Incomplete'),('completed','completed')] 
    
    
    status = models.CharField(choices=STATUS_CHOICES,default='pending',max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    

    def __str__(self):
        return f"{self.user.username} booked {self.turf.name} on {self.date}"
    
    def update_status(self):
        
        from datetime import date
        today = date.today()

        if self.date <= today :
            if self.status == 'confirmed':
                self.status = 'completed'
            elif self.status == 'pending':
                self.status = 'incomplete'
            self.save()
    @property
    def duration_hours(self):
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return max(duration.total_seconds() / 3600, 0)   
   
    @property
    def total_price(self):
        return self.duration_hours * float(self.turf.price)



class Bill(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='bill')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill for {self.booking}"


    
class Cancelled_booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cancelled_bookings')
    turf = models.ForeignKey(Turf_details, on_delete=models.CASCADE, related_name='cancelled_bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    

    
    status = models.CharField(max_length=10,default='cancelled',editable=False)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    
    

    def __str__(self):
        return f"{self.user.username} booked {self.turf.name} on {self.date}"
    @property
    def duration_hours(self):
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = end - start
        return duration.total_seconds() / 3600
    @property
    def total_price(self):
        return self.duration_hours * float(self.turf.price)





