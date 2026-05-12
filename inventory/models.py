from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Warehouse(BaseModel):
    """
    Omborxona. Har bir filialda bir yoki bir nechta ombor bo'lishi mumkin.
    """
    name = models.CharField(max_length=200, verbose_name=_("Omborxona nomi"))
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.CASCADE,
        related_name="warehouses",
        verbose_name=_("Filial")
    )
    address = models.TextField(blank=True, verbose_name=_("Manzil"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faolmi"))
    is_main = models.BooleanField(default=False, verbose_name=_("Asosiy ombormi"))

    class Meta:
        verbose_name = _("Omborxona")
        verbose_name_plural = _("Omborxonalar")

    def __str__(self):
        return f"{self.branch.name} — {self.name}"


class Stock(BaseModel):
    """
    Tovar qoldiqlari. Qaysi omborxonada qancha tovar bor.
    Har bir (warehouse + variant) juftligi uchun bitta yozuv.
    """
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name=_("Omborxona")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="stocks",
        verbose_name=_("Mahsulot varianti")
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3,
        default=0,
        verbose_name=_("Miqdor")
    )
    reserved_quantity = models.DecimalField(
        max_digits=12, decimal_places=3,
        default=0,
        verbose_name=_("Rezerv qilingan miqdor")
    )

    class Meta:
        verbose_name = _("Tovar qoldig'i")
        verbose_name_plural = _("Tovar qoldiqlari")
        unique_together = ["warehouse", "variant"]

    def __str__(self):
        return f"{self.variant} | {self.warehouse}: {self.quantity}"

    @property
    def available_quantity(self):
        """Sotuv uchun mavjud miqdor"""
        return self.quantity - self.reserved_quantity


class Supplier(BaseModel):
    """
    Yetkazib beruvchilar (ta'minotchilar).
    """
    name = models.CharField(max_length=200, verbose_name=_("Kompaniya nomi"))
    contact_person = models.CharField(max_length=200, blank=True, verbose_name=_("Mas'ul shaxs"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Telefon"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Manzil"))
    inn = models.CharField(max_length=20, blank=True, verbose_name=_("INN"))
    notes = models.TextField(blank=True, verbose_name=_("Izoh"))

    # Balans (qarzdorlik)
    balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Balans (musbat = bizga qarzdor, manfiy = biz qarzdormiz)")
    )

    class Meta:
        verbose_name = _("Yetkazib beruvchi")
        verbose_name_plural = _("Yetkazib beruvchilar")

    def __str__(self):
        return self.name


class PurchaseOrder(BaseModel):
    """
    Tovar kirim buyurtmasi (Yetkazib beruvchidan tovar qabul qilish).
    """
    class Status(models.TextChoices):
        DRAFT = "draft", _("Qoralama")
        ORDERED = "ordered", _("Buyurtma berildi")
        PARTIALLY_RECEIVED = "partially_received", _("Qisman qabul qilindi")
        RECEIVED = "received", _("To'liq qabul qilindi")
        CANCELLED = "cancelled", _("Bekor qilindi")

    order_number = models.CharField(max_length=50, unique=True, verbose_name=_("Buyurtma raqami"))
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchase_orders",
        verbose_name=_("Yetkazib beruvchi")
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchase_orders",
        verbose_name=_("Omborxona")
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Holat")
    )
    order_date = models.DateField(verbose_name=_("Buyurtma sanasi"))
    expected_date = models.DateField(null=True, blank=True, verbose_name=_("Kutilgan kelish sanasi"))
    received_date = models.DateField(null=True, blank=True, verbose_name=_("Qabul qilingan sana"))

    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Jami summa")
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("To'langan summa")
    )
    notes = models.TextField(blank=True, verbose_name=_("Izoh"))
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchase_orders",
        verbose_name=_("Kim yaratdi")
    )

    class Meta:
        verbose_name = _("Kirim buyurtmasi")
        verbose_name_plural = _("Kirim buyurtmalari")
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.order_number} — {self.supplier}"

    @property
    def debt_amount(self):
        return self.total_amount - self.paid_amount


class PurchaseOrderItem(BaseModel):
    """
    Kirim buyurtmasidagi har bir tovar qatori.
    """
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Buyurtma")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="purchase_items",
        verbose_name=_("Mahsulot")
    )
    ordered_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        verbose_name=_("Buyurtma qilingan miqdor")
    )
    received_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=0,
        verbose_name=_("Qabul qilingan miqdor")
    )
    cost_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name=_("Tannarx (kirim narxi)")
    )
    selling_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name=_("Sotuv narxi")
    )

    class Meta:
        verbose_name = _("Kirim qatori")
        verbose_name_plural = _("Kirim qatorlari")

    def __str__(self):
        return f"{self.variant} x {self.ordered_quantity}"

    @property
    def total_cost(self):
        return self.received_quantity * self.cost_price


class StockTransfer(BaseModel):
    """
    Omborxonalar o'rtasida tovar ko'chirish (Transfer).
    Masalan: Chilonzor filiali → Yunusobod filiali.
    """
    class Status(models.TextChoices):
        PENDING = "pending", _("Kutilmoqda")
        IN_TRANSIT = "in_transit", _("Yo'lda")
        COMPLETED = "completed", _("Yakunlandi")
        CANCELLED = "cancelled", _("Bekor qilindi")

    transfer_number = models.CharField(max_length=50, unique=True, verbose_name=_("Transfer raqami"))
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
        verbose_name=_("Qayerdan")
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
        verbose_name=_("Qayerga")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Holat")
    )
    transfer_date = models.DateField(verbose_name=_("Ko'chirish sanasi"))
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_transfers",
        verbose_name=_("Kim yaratdi")
    )

    class Meta:
        verbose_name = _("Tovar ko'chirish")
        verbose_name_plural = _("Tovar ko'chirishlar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.transfer_number}: {self.from_warehouse} → {self.to_warehouse}"


class StockTransferItem(BaseModel):
    """
    Transfer qatorlari.
    """
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Transfer")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        verbose_name=_("Mahsulot")
    )
    requested_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        verbose_name=_("So'ralgan miqdor")
    )
    sent_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=0,
        verbose_name=_("Yuborilgan miqdor")
    )
    received_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=0,
        verbose_name=_("Qabul qilingan miqdor")
    )

    class Meta:
        verbose_name = _("Transfer qatori")
        verbose_name_plural = _("Transfer qatorlari")

    def __str__(self):
        return f"{self.variant} x {self.requested_quantity}"


class Inventory(BaseModel):
    """
    Inventarizatsiya (Reviziya) — omborlarda tovar sanash.
    """
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", _("Jarayonda")
        COMPLETED = "completed", _("Yakunlandi")
        CANCELLED = "cancelled", _("Bekor qilindi")

    inventory_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventories",
        verbose_name=_("Omborxona")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Boshlangan vaqt"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Yakunlangan vaqt"))
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventories"
    )

    class Meta:
        verbose_name = _("Inventarizatsiya")
        verbose_name_plural = _("Inventarizatsiyalar")
        ordering = ["-started_at"]

    def __str__(self):
        return f"#{self.inventory_number} — {self.warehouse}"


class InventoryItem(BaseModel):
    """
    Inventarizatsiya qatorlari: tizim miqdori vs haqiqiy miqdor.
    """
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="items"
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE
    )
    system_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        verbose_name=_("Tizim miqdori")
    )
    actual_quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        verbose_name=_("Haqiqiy miqdor")
    )
    difference = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=0,
        verbose_name=_("Farq")
    )

    class Meta:
        verbose_name = _("Inventarizatsiya qatori")
        verbose_name_plural = _("Inventarizatsiya qatorlari")

    def save(self, *args, **kwargs):
        self.difference = self.actual_quantity - self.system_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant}: tizim={self.system_quantity}, haqiqiy={self.actual_quantity}"


class WriteOff(BaseModel):
    """
    Tovarni hisobdan chiqarish (buzilgan, o'g'irlangan, yo'qolgan).
    """
    class Reason(models.TextChoices):
        DAMAGED = "damaged", _("Shikastlangan")
        EXPIRED = "expired", _("Muddati o'tgan")
        STOLEN = "stolen", _("O'g'irlangan")
        LOST = "lost", _("Yo'qolgan")
        OTHER = "other", _("Boshqa")

    write_off_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="write_offs",
        verbose_name=_("Omborxona")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        verbose_name=_("Mahsulot")
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_("Miqdor"))
    reason = models.CharField(
        max_length=20,
        choices=Reason.choices,
        default=Reason.OTHER,
        verbose_name=_("Sabab")
    )
    description = models.TextField(blank=True, verbose_name=_("Batafsil izoh"))
    total_loss = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Jami zarar summasi")
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="write_offs"
    )

    class Meta:
        verbose_name = _("Hisobdan chiqarish")
        verbose_name_plural = _("Hisobdan chiqarishlar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.write_off_number} — {self.variant}: {self.quantity}"