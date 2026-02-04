from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
import os

# 画像保存先を動的に決定する関数
def user_preview_path(instance, filename):
    now = timezone.now().strftime('%Y%m%d_%H%M%S')
    base, ext = os.path.splitext(filename)
    new_filename = f"{now}_{base}{ext}"
    return f'uploads/previews/user_{instance.user.id}/{new_filename}'

# --- 1. ユーザーモデル管理 ---
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# --- 2. User テーブル ---
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.nickname if self.nickname else self.email

# --- 3. Token テーブル ---
class Token(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    jwt_token = models.TextField()
    expires_at = models.DateTimeField()
    is_logged_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# --- 4. Vehicle テーブル (子モデルより先に書く) ---
class Vehicle(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # ここに name_en を追加して、1つにまとめます
    name_en = models.CharField(max_length=100, default="Rocky")
    base_image_path = models.ImageField(upload_to="uploads/vehicles/")

    def __str__(self):
        return self.name

# --- 5. Color テーブル ---
class Color(models.Model):
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/colors/')
    rotation_image_folder = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"

# --- 6. Wheel テーブル ---
class Wheel(models.Model):
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/wheels/')

# --- 7. Bumper テーブル ---
class Bumper(models.Model):
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/bumpers/')

# --- 8. Light テーブル ---
class Light(models.Model):
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/lights/')

# --- 9. Aero テーブル ---
class Aero(models.Model):
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/aeros/')

# --- 10. SavedCustom テーブル ---
class SavedCustom(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, blank=True)
    wheel = models.ForeignKey(Wheel, on_delete=models.PROTECT, null=True, blank=True)
    bumper = models.ForeignKey(Bumper, on_delete=models.PROTECT, null=True, blank=True)
    light = models.ForeignKey(Light, on_delete=models.PROTECT, null=True, blank=True)
    aero = models.ForeignKey(Aero, on_delete=models.PROTECT, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    display_mode = models.BooleanField(default=False)
    preview_image_url = models.CharField(max_length=255, blank=True, default="")
    saved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"Custom {self.id} by {self.user}"