from django.db import models
from django.utils.translation import gettext_lazy as _
 
 
class TimeStampedModel(models.Model):
    """
    Barcha modellarda bo'ladigan created_at va updated_at maydonlari.
    Boshqa modellar shu classdan meros oladi.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Yangilangan vaqt"))
 
    class Meta:
        abstract = True
 
 
class SoftDeleteModel(models.Model):
    """
    O'chirish o'rniga is_deleted=True qo'yish (Soft Delete).
    Ma'lumotlar hech qachon yo'qolmaydi, faqat yashiriladi.
    """
    is_deleted = models.BooleanField(default=False, verbose_name=_("O'chirilganmi"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("O'chirilgan vaqt"))
 
    class Meta:
        abstract = True
 
 
class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Asosiy base model — barcha modellar shu classdan meros oladi.
    """
    class Meta:
        abstract = True
 