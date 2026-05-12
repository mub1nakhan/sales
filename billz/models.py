from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


# ═══════════════════════════════════════════════
#  MIJOZLAR (CRM)
# ═══════════════════════════════════════════════

class CustomerGroup(BaseModel):
    """
    Mijoz guruhlari: Oddiy, VIP, Do'stlar va h.k.
    Har bir guruh uchun alohida chegirma yoki narx belgilash mumkin.
    """
    name = models.CharField(max_length=200, verbose_name=_("Guruh nomi"))
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name=_("Chegirma (%)")
    )
    cashback_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name=_("Keshbek (%)")
    )
    price_list = models.ForeignKey(
        "products.PriceList",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("Narxlar ro'yxati")
    )
    color = models.CharField(max_length=20, default="#3498db", verbose_name=_("Rang (interfeys uchun)"))

    class Meta:
        verbose_name = _("Mijoz guruhi")
        verbose_name_plural = _("Mijoz guruhlari")

    def __str__(self):
        return self.name


class Customer(BaseModel):
    """
    Mijoz (xaridor) modeli.
    """
    class Gender(models.TextChoices):
        MALE = "male", _("Erkak")
        FEMALE = "female", _("Ayol")
        OTHER = "other", _("Boshqa")

    first_name = models.CharField(max_length=100, verbose_name=_("Ism"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("Familiya"))
    phone = models.CharField(max_length=20, db_index=True, verbose_name=_("Telefon"))
    phone2 = models.CharField(max_length=20, blank=True, verbose_name=_("Qo'shimcha telefon"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    birthday = models.DateField(null=True, blank=True, verbose_name=_("Tug'ilgan kun"))
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        verbose_name=_("Jinsi")
    )
    address = models.TextField(blank=True, verbose_name=_("Manzil"))
    group = models.ForeignKey(
        CustomerGroup,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="customers",
        verbose_name=_("Guruh")
    )
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="customers",
        verbose_name=_("Birlamchi filial")
    )
    notes = models.TextField(blank=True, verbose_name=_("Izoh"))

    # Moliya
    balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Balans (musbat = bizga qarzdor, manfiy = biz qarzdormiz)")
    )
    total_purchases = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Jami xaridlar summasi")
    )
    bonus_points = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name=_("Bonus ballar")
    )

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_customers"
    )

    class Meta:
        verbose_name = _("Mijoz")
        verbose_name_plural = _("Mijozlar")
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


# ═══════════════════════════════════════════════
#  KASSA VA SMENA
# ═══════════════════════════════════════════════

class CashRegister(BaseModel):
    """
    Kassa apparati / nuqtasi.
    """
    name = models.CharField(max_length=100, verbose_name=_("Kassa nomi"))
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.CASCADE,
        related_name="cash_registers",
        verbose_name=_("Filial")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Kassa")
        verbose_name_plural = _("Kassalar")

    def __str__(self):
        return f"{self.branch.name} — {self.name}"


class CashSession(BaseModel):
    """
    Kassa smenasi. Kassir smena ochadi va yopadi.
    """
    class Status(models.TextChoices):
        OPEN = "open", _("Ochiq")
        CLOSED = "closed", _("Yopiq")

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Kassa")
    )
    cashier = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cash_sessions",
        verbose_name=_("Kassir")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_("Holat")
    )
    opening_balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Ochilish balansi")
    )
    closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Yopilish balansi")
    )
    opened_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ochilgan vaqt"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Yopilgan vaqt"))
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Kassa smenasi")
        verbose_name_plural = _("Kassa smenalari")
        ordering = ["-opened_at"]

    def __str__(self):
        return f"{self.cash_register} | {self.cashier} | {self.opened_at.date()}"


# ═══════════════════════════════════════════════
#  SOTUV (SAVDO)
# ═══════════════════════════════════════════════

class Sale(BaseModel):
    """
    Sotuv hujjati (Chek).
    """
    class Status(models.TextChoices):
        DRAFT = "draft", _("Qoralama (savatcha)")
        COMPLETED = "completed", _("Yakunlangan")
        RETURNED = "returned", _("Qaytarilgan")
        PARTIALLY_RETURNED = "partially_returned", _("Qisman qaytarilgan")
        CANCELLED = "cancelled", _("Bekor qilindi")

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", _("To'lanmagan")
        PARTIAL = "partial", _("Qisman to'langan")
        PAID = "paid", _("To'langan")
        OVERPAID = "overpaid", _("Ortiqcha to'langan")

    receipt_number = models.CharField(max_length=50, unique=True, verbose_name=_("Chek raqami"))
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales",
        verbose_name=_("Filial")
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales",
        verbose_name=_("Omborxona")
    )
    cash_session = models.ForeignKey(
        CashSession,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sales",
        verbose_name=_("Smena")
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sales",
        verbose_name=_("Mijoz")
    )
    seller = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales",
        verbose_name=_("Sotuvchi")
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Holat")
    )
    payment_status = models.CharField(
        max_length=15,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name=_("To'lov holati")
    )

    # Summalar
    subtotal = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Jami (chegirmadan oldin)")
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Chegirma summasi")
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name=_("Chegirma (%)")
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Jami to'lov summasi")
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("To'langan summa")
    )
    change_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Qaytim pul")
    )
    bonus_used = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name=_("Ishlatilgan bonus")
    )
    bonus_earned = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name=_("Ishlangan bonus")
    )

    sale_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Sotuv sanasi"))
    notes = models.TextField(blank=True)

    # Rezerv (layaway) — muayyan vaqtga ajratib qo'yish
    is_layaway = models.BooleanField(default=False, verbose_name=_("Rezervmi"))
    layaway_until = models.DateField(null=True, blank=True, verbose_name=_("Qachongacha ajratilgan"))

    class Meta:
        verbose_name = _("Sotuv")
        verbose_name_plural = _("Sotuvlar")
        ordering = ["-sale_date"]

    def __str__(self):
        return f"#{self.receipt_number} — {self.total_amount} so'm"

    @property
    def debt_amount(self):
        return self.total_amount - self.paid_amount

    @property
    def profit(self):
        return sum(item.profit for item in self.items.all())


class SaleItem(BaseModel):
    """
    Sotuv qatori — har bir sotilgan mahsulot.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Sotuv")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="sale_items",
        verbose_name=_("Mahsulot")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=3,
        verbose_name=_("Miqdor")
    )
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name=_("Birlik narxi")
    )
    cost_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Tannarx (hisobot uchun)")
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0,
        verbose_name=_("Chegirma (%)")
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Chegirma summasi")
    )
    total_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name=_("Jami narxi")
    )

    class Meta:
        verbose_name = _("Sotuv qatori")
        verbose_name_plural = _("Sotuv qatorlari")

    def __str__(self):
        return f"{self.variant} x {self.quantity} = {self.total_price}"

    @property
    def profit(self):
        return (self.unit_price - self.cost_price) * self.quantity


class SaleReturn(BaseModel):
    """
    Tovar qaytarish.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="returns",
        verbose_name=_("Asl sotuv")
    )
    return_number = models.CharField(max_length=50, unique=True)
    cashier = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sale_returns"
    )
    reason = models.TextField(blank=True, verbose_name=_("Qaytarish sababi"))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    refund_method = models.CharField(
        max_length=20,
        choices=[("cash", "Naqd"), ("card", "Karta"), ("balance", "Balansga")],
        default="cash",
        verbose_name=_("Qaytarish usuli")
    )

    class Meta:
        verbose_name = _("Qaytarish")
        verbose_name_plural = _("Qaytarishlar")
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.return_number}"


class SaleReturnItem(BaseModel):
    """
    Qaytarish qatorlari.
    """
    sale_return = models.ForeignKey(
        SaleReturn, on_delete=models.CASCADE, related_name="items"
    )
    sale_item = models.ForeignKey(
        SaleItem, on_delete=models.CASCADE, related_name="return_items"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _("Qaytarish qatori")
        verbose_name_plural = _("Qaytarish qatorlari")


# ═══════════════════════════════════════════════
#  TO'LOV TURLARI
# ═══════════════════════════════════════════════

class PaymentMethod(BaseModel):
    """
    To'lov usullari: Naqd, Karta (Visa/HUMO), UZCARD, Click, Payme, Nasiya va h.k.
    """
    name = models.CharField(max_length=100, verbose_name=_("To'lov usuli nomi"))
    is_cash = models.BooleanField(default=False, verbose_name=_("Naqd pulmi"))
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _("To'lov usuli")
        verbose_name_plural = _("To'lov usullari")
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Payment(BaseModel):
    """
    To'lov tranzaksiyasi. Har bir to'lov turi uchun alohida yozuv.
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Sotuv")
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("To'lov usuli")
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Summa"))
    reference = models.CharField(max_length=100, blank=True, verbose_name=_("Havola (transaction ID)"))
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("To'lov")
        verbose_name_plural = _("To'lovlar")

    def __str__(self):
        return f"{self.payment_method}: {self.amount}"


# ═══════════════════════════════════════════════
#  MOLIYA
# ═══════════════════════════════════════════════

class ExpenseCategory(BaseModel):
    """
    Xarajat turlari: Ijara, Ish haqi, Transport, Kommunal xizmatlar va h.k.
    """
    name = models.CharField(max_length=200, verbose_name=_("Xarajat turi"))
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="children"
    )
    icon = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=20, default="#e74c3c")

    class Meta:
        verbose_name = _("Xarajat turi")
        verbose_name_plural = _("Xarajat turlari")

    def __str__(self):
        return self.name


class Expense(BaseModel):
    """
    Xarajat yozuvi.
    """
    branch = models.ForeignKey(
        "users.Branch",
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name=_("Filial")
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="expenses",
        verbose_name=_("Xarajat turi")
    )
    cash_session = models.ForeignKey(
        CashSession,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="expenses"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Summa"))
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("To'lov usuli")
    )
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    expense_date = models.DateField(verbose_name=_("Xarajat sanasi"))
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="expenses"
    )
    receipt_image = models.ImageField(
        upload_to="expenses/receipts/",
        null=True, blank=True,
        verbose_name=_("Chek rasmi")
    )

    class Meta:
        verbose_name = _("Xarajat")
        verbose_name_plural = _("Xarajatlar")
        ordering = ["-expense_date"]

    def __str__(self):
        return f"{self.category} — {self.amount} ({self.expense_date})"


class CashMovement(BaseModel):
    """
    Kassa harakatlari — inkassatsiya, kirim, chiqim.
    """
    class MovementType(models.TextChoices):
        INCOME = "income", _("Kirim")
        OUTCOME = "outcome", _("Chiqim")
        COLLECTION = "collection", _("Inkassatsiya")
        TRANSFER = "transfer", _("Kassalar o'rtasida o'tkazma")

    cash_session = models.ForeignKey(
        CashSession,
        on_delete=models.CASCADE,
        related_name="movements"
    )
    movement_type = models.CharField(
        max_length=15,
        choices=MovementType.choices,
        verbose_name=_("Harakat turi")
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cash_movements"
    )

    class Meta:
        verbose_name = _("Kassa harakati")
        verbose_name_plural = _("Kassa harakatlari")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.amount}"