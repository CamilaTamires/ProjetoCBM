from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Personalizando os campos que aparecem no formulário de edição do usuário
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'cpf', 'cargo')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login',)}),
    )

    # Personalizando os campos para o formulário de criação de novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'cpf', 'cargo', 'password1', 'password2'),
        }),
    )

    # Personalizando como os usuários serão listados no painel do admin
    list_display = ('email', 'nome', 'cpf', 'cargo', 'is_staff')

    # Permitir busca por email, nome, cpf e cargo
    search_fields = ('email', 'nome', 'cpf', 'cargo')

    # Ordenar a lista de usuários por email
    ordering = ('email',)
