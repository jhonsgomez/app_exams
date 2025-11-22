from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.core.validators import MinLengthValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("first_name", "Super")
        extra_fields.setdefault("last_name", "Admin")
        extra_fields.setdefault("role_id", 1)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    last_name = models.CharField(
        max_length=255, validators=[MinLengthValidator(2)], blank=True, null=True
    )

    email = models.EmailField(unique=True)

    role = models.ForeignKey(
        "app.Role",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    institution = models.ForeignKey(
        "app.Institution",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    academic_department = models.ForeignKey(
        "app.AcademicDepartment",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    group = models.ForeignKey(
        "app.Group",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    document_type = models.ForeignKey(
        "app.DocumentType",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    document_number = models.CharField(
        max_length=30, validators=[MinLengthValidator(4)], blank=True, null=True
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    semester = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "app_users"

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    def is_super_admin(self):
        return self.role.name == "super_admin" if self.role else False

    def is_admin(self):
        return (
            self.role.name == "admin" or self.role.name == "super_admin"
            if self.role
            else False
        )

    def is_student(self):
        return self.role.name == "student" if self.role else False
