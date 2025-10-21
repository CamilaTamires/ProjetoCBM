import io
import qrcode
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse
from .models import Equipment

@receiver(post_save, sender=Equipment)
def generate_equipment_qr(sender, instance, created, **kwargs):
    # gera no create, ou no edit se ainda não tiver QR
    if not created and instance.qr_code_image:
        return

    # monte a URL absoluta para o detalhe do equipamento:
    # ex.: http://127.0.0.1:8000/api/equipment/2/
    base = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
    detail_path = reverse('equipment-detail', kwargs={'pk': instance.pk})
    data = f"{base}{detail_path}"

    # gera imagem PNG
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    instance.qr_code_image.save(
        f"equipment_{instance.id}.png",
        ContentFile(buf.read()),
        save=False
    )
    instance.save(update_fields=['qr_code_image'])
