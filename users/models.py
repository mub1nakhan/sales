from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Branch(BaseModel):
    """
    Do'kon / Filial modeli.
    Bir kompaniyada bir nechta filial bo'lishi mumkin.
    """
    name = models.CharField(max_length=200, verbose_name=_("Filial nomi"))
    address = models.TextField(verbose_name=_("Manzil"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Telefon"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faolmi"))

    # Joylashuv (ixtiyoriy)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = _("Filial")
        verbose_name_plural = _("Filiallar")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(BaseModel):
    """
    Xodim rollari: Direktor, Menejer, Kassir, Sotuvchi, Omborchi va h.k.
    """
    class RoleType(models.TextChoices):
        OWNER = "owner", _("Egasi")
        DIRECTOR = "director", _("Direktor")
        MANAGER = "manager", _("Menejer")
        CASHIER = "cashier", _("Kassir")
        SELLER = "seller", _("Sotuvchi")
        WAREHOUSE_KEEPER = "warehouse_keeper", _("Omborchi")
        ACCOUNTANT = "accountant", _("Buxgalter")

    name = models.CharField(max_length=100, verbose_name=_("Rol nomi"))
    role_type = models.CharField(
        max_length=30,
        choices=RoleType.choices,
        default=RoleType.SELLER,
        verbose_name=_("Rol turi")
    )

    # Ruxsatlar (permissions)
    can_view_reports = models.BooleanField(default=False, verbose_name=_("Hisobotlarni ko'rish"))
    can_manage_products = models.BooleanField(default=False, verbose_name=_("Mahsulotlarni boshqarish"))
    can_manage_inventory = models.BooleanField(default=False, verbose_name=_("Omborni boshqarish"))
    can_manage_users = models.BooleanField(default=False, verbose_name=_("Xodimlarni boshqarish"))
    can_view_finance = models.BooleanField(default=False, verbose_name=_("Moliyani ko'rish"))
    can_manage_finance = models.BooleanField(default=False, verbose_name=_("Moliyani boshqarish"))
    can_make_sales = models.BooleanField(default=True, verbose_name=_("Sotuv qilish"))
    can_give_discount = models.BooleanField(default=False, verbose_name=_("Chegirma berish"))
    can_view_cost_price = models.BooleanField(default=False, verbose_name=_("Tannarxni ko'rish"))
    can_manage_customers = models.BooleanField(default=False, verbose_name=_("Mijozlarni boshqarish"))

    class Meta:
        verbose_name = _("Rol")
        verbose_name_plural = _("Rollar")

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):
    """
    Kengaytirilgan foydalanuvchi modeli.
    AbstractUser dan meros olamiz (username, password, email va h.k. tayyor).
    """
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Telefon"))
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name=_("Rasm"))
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name=_("Rol")
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name=_("Filial")
    )
    salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name=_("Oylik maosh")
    )
    # Bonus tizimi
    sales_bonus_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name=_("Savdo bonusi (%)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Faolmi"))

    # created_at va updated_at BaseModel dan keladi,
    # lekin AbstractUser da ham mavjud — shuning uchun override qilamiz
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Qo'shilgan sana"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Yangilangan sana"))

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    @property
    def full_name(self):
        return self.get_full_name() or self.username


class SalesTarget(BaseModel):
    """
    Sotuvchi / Filial uchun savdo rejasi (Plan).
    Masalan: bu oy 50 million so'm savdo qilish kerak.
    """
    class PeriodType(models.TextChoices):
        DAILY = "daily", _("Kunlik")
        WEEKLY = "weekly", _("Haftalik")
        MONTHLY = "monthly", _("Oylik")
        QUARTERLY = "quarterly", _("Kvartallik")
        YEARLY = "yearly", _("Yillik")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="targets",
        verbose_name=_("Xodim")
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="targets",
        verbose_name=_("Filial")
    )
    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
        default=PeriodType.MONTHLY,
        verbose_name=_("Davr turi")
    )
    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name=_("Reja summasi")
    )
    start_date = models.DateField(verbose_name=_("Boshlanish sanasi"))
    end_date = models.DateField(verbose_name=_("Tugash sanasi"))
    notes = models.TextField(blank=True, verbose_name=_("Izoh"))

    class Meta:
        verbose_name = _("Savdo rejasi")
        verbose_name_plural = _("Savdo rejalari")

    def __str__(self):
        target = self.user or self.branch
        return f"{target} — {self.target_amount} ({self.get_period_type_display()})"