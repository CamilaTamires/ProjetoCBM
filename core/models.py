from django.db import models
from django.contrib.auth.models import AbstractUser
import qrcode
from io import BytesIO
from django.core.files import File

# 1. Modelo de usuário
class User(AbstractUser):
    ROLE_CHOICES = [
        ('coordenador', 'Coordenador'),
        ('tecnico', 'Técnico'),
        ('solicitante', 'Solicitante'),
    ]

    cpf = models.CharField(max_length=11, unique=True)  # CPF
    cargo = models.CharField(max_length=100, choices=ROLE_CHOICES, default='solicitante')
    nome = models.CharField(max_length=100)  # Adicionando o campo nome aqui

    def __str__(self):
        return f"{self.nome} ({self.email})"  # Acessando o nome diretamente

# 2. Modelo de Ativo (equipamento)
class Ativo(models.Model):
    nome = models.CharField(max_length=255)  # Nome do ativo (ex: computador, impressora)
    local = models.CharField(max_length=255)  # Local onde o ativo está (ex: sala 101)
    numero_serie = models.CharField(max_length=100, unique=True)  # Número de série do ativo
    qrcode = models.ImageField(upload_to='ativos/qrcodes/', blank=True, null=True)  # QR Code gerado

    # Relacionamento com o usuário
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ativos")

    def gerar_qrcode(self):
        """Gera um QR Code para o ativo com base no número de série"""
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(self.numero_serie)
        qr.make(fit=True)

        # Criar a imagem do QR code em memória
        img = qr.make_image(fill='black', back_color='white')

        # Salvar o QR Code como arquivo de imagem
        qr_code_io = BytesIO()
        img.save(qr_code_io, 'PNG')
        qr_code_io.seek(0)

        # Atribuir o QR Code ao campo 'qrcode' como um arquivo
        self.qrcode.save(f"{self.numero_serie}_qrcode.png", File(qr_code_io), save=False)
        self.save()

    def save(self, *args, **kwargs):
        # Gerar o QR Code automaticamente ao salvar o ativo
        if not self.qrcode:  # Só gerar o QR Code se ele ainda não existir
            self.gerar_qrcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.numero_serie}"
