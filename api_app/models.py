from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# --- 1. ユーザーモデル管理 ---
# AbstractBaseUser 継承
class MyUserManager(BaseUserManager):
    
    # ユーザー作成（Emailとパスワードのみ）
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # パスワードをハッシュ化
        user.save(using=self._db)
        return user
    
    #管理者作成
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

        

# --- ここからインデントを修正 (クラスはネストしない) ---

# --- 2. User テーブル ---
class User(AbstractBaseUser,PermissionsMixin):
    # user_idは(AutoField)
    
    # メール
    email = models.EmailField(unique=True)

    # ニックネーム
    nickname = models.CharField(max_length=100, blank=True, null=True)

    # 登録日時
    created_at = models.DateTimeField(auto_now_add=True)

    # ログイン設定
    is_active = models.BooleanField(default=True)

    #管理者
    is_staff = models.BooleanField(default=False)

    # UserManager　紐付け
    objects = MyUserManager()
    
    # ログインIDとして 'email' を指定
    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = []

    def __str__(self):
        # 表示名をニックネームにする（nullの場合email表記）
        return self.nickname if self.nickname else self.email


# --- 3. Token テーブル ---
class Token(models.Model):
    # token_id : INT {PK} (自動)

    # user_id 外部キー(FK)
    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,
        # ユーザ削除時にToken削除
        on_delete=models.CASCADE 
    )

    # jwt_token
    jwt_token = models.TextField()

    # expires_at
    expires_at = models.DateTimeField()

    is_logged_in = models.BooleanField(default=False)

    # created_at
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # ★ 修正: Tokne -> Token
        return f"Token for {self.user}"

# --- 4. Vehicle テーブル ---
class Vehicle(models.Model):
    # vehicle_id INT {PK} （自動）
    name = models.CharField(max_length=255, unique=True)
    
    base_image_path = models.ImageField(upload_to="uploads/vehicles/")

    def __str__(self):
        return self.name

# --- 5. Color テーブル ---
class Color(models.Model):
    # color_id INT {PK} （自動）
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.ImageField(upload_to='uploads/colors/')
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"

# --- 6. Wheel テーブル ---
class Wheel(models.Model):
    # wheel_id INT {PK} （自動）
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    image_url = models.ImageField(upload_to='uploads/wheels/')
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"

# --- 7. Bumper テーブル ---
class Bumper(models.Model):
    # bumper_id INT {PK} （自動）
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image_url = models.ImageField(upload_to='uploads/bumpers/')
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"

# --- 8. Light テーブル ---
class Light(models.Model):
    # light_id : INT {PK} （自動）
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image_url = models.ImageField(upload_to='uploads/lights/')
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"

# --- 9. Aero テーブル ---
class Aero(models.Model):
    # aero_id : INT {PK} （自動）
    name = models.CharField(max_length=255)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image_url = models.ImageField(upload_to='uploads/aeros/')
    
    def __str__(self):
        return f"{self.name} (for {self.vehicle.name})"


# --- 10. SavedCustom テーブル ---
class SavedCustom(models.Model):
    # custom_id : INT {PK} （自動）
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # パーツごとのテーブル
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    wheel = models.ForeignKey(Wheel, on_delete=models.PROTECT)
    bumper = models.ForeignKey(Bumper, on_delete=models.PROTECT)
    light = models.ForeignKey(Light, on_delete=models.PROTECT)
    aero = models.ForeignKey(Aero, on_delete=models.PROTECT)

    # total_price
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # display_mode
    display_mode = models.BooleanField(default=False)

    # preview_image_url : VARCHAR (ImageField)
    preview_image_url = models.ImageField(upload_to='uploads/previews/')

    # saved_at : DATETIME
    saved_at = models.DateTimeField(auto_now_add=True)

    # is_favorite : BOOLEAN (★お気に入り機能)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return f"Custom {self.id} by {self.user}"