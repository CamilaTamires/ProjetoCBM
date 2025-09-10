from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError


# -------------------------
# Validador de CPF (básico)
# -------------------------
def validar_cpf(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError('O CPF deve conter 11 dígitos numéricos.')


# -------------------------
# Gerenciador de usuários
# -------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, nome, cpf, cargo, password=None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório")
        email = self.normalize_email(email)
        validate_email(email)
        user = self.model(email=email, nome=nome, cpf=cpf, cargo=cargo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, cpf, cargo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome, cpf, cargo, password, **extra_fields)


# -------------------------
# Modelo do usuário
# -------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('coordenador', 'coordenador'),
        ('tecnico', 'Técnico'),
        ('solicitante', 'Solicitante'),
    ]

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True, validators=[validar_cpf])
    cargo = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='solicitante')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf', 'cargo']

    def __str__(self):
        return f"{self.nome} ({self.email})"
