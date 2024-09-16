import uuid

from django.db import models

from users.managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, PermissionsMixin, UserManager, Permission
from django.utils.translation import gettext_lazy as _



# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            'Returns True if the user account is currently active. '
        )
    )

    class Status(models.TextChoices):
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        LOCKED = 'locked'
    username = models.CharField(
        max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    date_joined = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=Status.choices, default=Status.ACTIVE)
    user_role = models.CharField(max_length=20, choices=[
        ('normal_user', 'Normal User'), ('admin', 'Admin'),
        ('farmer', 'Farmer'), ('partner', 'Partner')], default='normal_user')
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    objects = CustomUserManager()


class UserProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
        OTHER = 'other'
    full_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True, blank=True)
    profile_image = models.CharField(null=True, blank=True)
    address = models.CharField(null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=10, choices=Gender.choices)
    phone = models.CharField(unique=True, null=True, blank=True, max_length=15)
    user_profile_percentage = models.IntegerField(default=0, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        required_fields = [
            self.full_name,
            self.phone,
            self.dob,
            self.address,
            self.gender
        ]
        all_filled = all(field for field in required_fields)
        if all_filled:
            self.is_verified = True
        # Calculate profile completion percentage
        total_fields = len(required_fields)
        filled_fields = sum(1 for field in required_fields if field)
        self.user_profile_percentage = (filled_fields / total_fields) * 100 if total_fields else 0
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"


class FarmerProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
        OTHER = 'other'
    full_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    address = models.CharField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    gender = models.CharField(null=True, blank=True, max_length=10, choices=Gender.choices)
    profile_image = models.CharField(null=True, blank=True)
    farm_name = models.CharField(max_length=255, blank=True)
    farm_location = models.CharField(max_length=255, blank=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    farm_size_acres = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    primary_crop = models.CharField(max_length=100, blank=True)
    livestock_count = models.PositiveIntegerField(blank=True, null=True)
    organic_certification = models.BooleanField(default=False)
    farm_description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    farmer_profile_percentage = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        required_fields = [
            self.full_name,
            self.phone,
            self.dob,
            self.address,
        ]
        all_filled = all(field for field in required_fields)
        if all_filled:
            self.is_verified = True
        # Calculate profile completion percentage
        total_fields = len(required_fields)
        filled_fields = sum(1 for field in required_fields if field)
        self.farmer_profile_percentage = (filled_fields / total_fields) * 100 if total_fields else 0
        super(FarmerProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"Farmer Profile of {self.user.username}"


class PartnerProfile(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    profile_image = models.CharField(null=True, blank=True)
    delivery_area = models.CharField(max_length=255, blank=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    delivery_ratings = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    delivery_history = models.PositiveIntegerField(blank=True, null=True)
    delivery_capacity = models.PositiveIntegerField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True)
    available_for_delivery = models.BooleanField(default=True)
    estimated_delivery_days= models.IntegerField(default=0, null=True, blank=True)
    delivery_charge = models.IntegerField(default=0, null=True,blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    partner_profile_percentage = models.IntegerField(default=0, null=True, blank=True)
    address = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        required_fields = [
            self.full_name,
            self.phone,
            self.delivery_charge,
            self.estimated_delivery_days,
            self.delivery_area
        ]
        all_filled = all(field for field in required_fields)
        if all_filled:
            self.is_verified = True
        # Calculate profile completion percentage
        total_fields = len(required_fields)
        filled_fields = sum(1 for field in required_fields if field)
        self.partner_profile_percentage = (filled_fields / total_fields) * 100 if total_fields else 0
        super(PartnerProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"Partner Profile of {self.user.username}"
