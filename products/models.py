from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Category(BaseModel):
    """
    Mahsulot kategoriyalari (daraxt struktura - tree).
    Misol: Kiyim → Erkaklar → Ko'ylaklar
    """
    name = models.CharField(max_length=200, verbose_name=_("Kategoriya nomi"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="children",
        verbose_name=_("Ota kategoriya")
    )
    icon = models.CharField(max_length=100, blank=True, verbose_name=_("Ikonka (emoji yoki CSS class)"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Tartib raqami"))

    class Meta:
        verbose_name = _("Kategoriya")
        verbose_name_plural = _("Kategoriyalar")
        ordering = ["sort_order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name


class Brand(BaseModel):
    """
    Brend / Ishlab chiqaruvchi.
    """
    name = models.CharField(max_length=200, verbose_name=_("Brend nomi"))
    logo = models.ImageField(upload_to="brands/", null=True, blank=True, verbose_name=_("Logo"))
    country = models.CharField(max_length=100, blank=True, verbose_name=_("Mamlakat"))

    class Meta:
        verbose_name = _("Brend")
        verbose_name_plural = _("Brendlar")

    def __str__(self):
        return self.name


class Unit(BaseModel):
    """
    O'lchov birliklari: dona, kg, metr, litr va h.k.
    """
    name = models.CharField(max_length=50, verbose_name=_("Nomi"))
    short_name = models.CharField(max_length=10, verbose_name=_("Qisqa nomi"))  # dona, kg, m, l

    class Meta:
        verbose_name = _("O'lchov birligi")
        verbose_name_plural = _("O'lchov birliklari")

    def __str__(self):
        return f"{self.name} ({self.short_name})"


class Product(BaseModel):
    """
    Asosiy mahsulot modeli.
    Har bir mahsulot bir nechta variantga ega bo'lishi mumkin
    (masalan, ko'ylak → S, M, L o'lchamlari).
    """
    name = models.CharField(max_length=300, verbose_name=_("Mahsulot nomi"))
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name=_("Kategoriya")
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name=_("Brend")
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name=_("O'lchov birligi")
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True, verbose_name=_("Asosiy rasm"))

    # Narxlar
    cost_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Tannarx (sotib olish narxi)")
    )
    selling_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Sotuv narxi")
    )
    min_selling_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Minimal sotuv narxi (chegirma chegarasi)")
    )
    wholesale_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0,
        verbose_name=_("Ulgurji narx")
    )

    # Ombor
    min_stock_level = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name=_("Minimal zaxira (signal berish uchun)")
    )

    # Xususiyatlar
    has_variants = models.BooleanField(default=False, verbose_name=_("Variantlari bormi"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faolmi"))
    is_service = models.BooleanField(default=False, verbose_name=_("Xizmat turimi (omborsiz)"))

    class Meta:
        verbose_name = _("Mahsulot")
        verbose_name_plural = _("Mahsulotlar")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def profit_margin(self):
        """Foyda foizi"""
        if self.cost_price and self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0


class ProductAttribute(BaseModel):
    """
    Mahsulot xususiyat turlari: O'lcham, Rang, Material va h.k.
    """
    name = models.CharField(max_length=100, verbose_name=_("Xususiyat nomi"))

    class Meta:
        verbose_name = _("Xususiyat turi")
        verbose_name_plural = _("Xususiyat turlari")

    def __str__(self):
        return self.name


class ProductAttributeValue(BaseModel):
    """
    Xususiyat qiymatlari: S, M, L, XL / Qizil, Ko'k, Yashil va h.k.
    """
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Xususiyat turi")
    )
    value = models.CharField(max_length=100, verbose_name=_("Qiymat"))

    class Meta:
        verbose_name = _("Xususiyat qiymati")
        verbose_name_plural = _("Xususiyat qiymatlari")
        unique_together = ["attribute", "value"]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(BaseModel):
    """
    Mahsulot varianti.
    Masalan: Ko'ylak (M o'lcham, Qizil rang) → alohida SKU va narx.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("Mahsulot")
    )
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU (ichki kod)"))
    barcode = models.CharField(max_length=100, blank=True, db_index=True, verbose_name=_("Shtrix-kod"))
    attributes = models.ManyToManyField(
        ProductAttributeValue,
        blank=True,
        verbose_name=_("Xususiyatlar")
    )

    # Variant uchun alohida narx (bo'sh bo'lsa asosiy mahsulot narxi ishlatiladi)
    cost_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Tannarx")
    )
    selling_price = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Sotuv narxi")
    )
    image = models.ImageField(upload_to="variants/", null=True, blank=True, verbose_name=_("Rasm"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faolmi"))

    class Meta:
        verbose_name = _("Mahsulot varianti")
        verbose_name_plural = _("Mahsulot variantlari")

    def __str__(self):
        attrs = ", ".join([str(a) for a in self.attributes.all()])
        return f"{self.product.name} [{attrs}]" if attrs else self.product.name

    def get_selling_price(self):
        """Variant narxi bo'lmasa, asosiy mahsulot narxini qaytaradi"""
        return self.selling_price or self.product.selling_price

    def get_cost_price(self):
        return self.cost_price or self.product.cost_price


class ProductImage(BaseModel):
    """
    Mahsulot rasmlari (bir nechta rasm bo'lishi mumkin).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Mahsulot")
    )
    image = models.ImageField(upload_to="products/gallery/", verbose_name=_("Rasm"))
    is_main = models.BooleanField(default=False, verbose_name=_("Asosiy rasmmi"))
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Mahsulot rasmi")
        verbose_name_plural = _("Mahsulot rasmlari")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} rasmi"


class PriceList(BaseModel):
    """
    Narxlar ro'yxati.
    Turli mijoz guruhlari yoki filiallar uchun turli narx.
    Masalan: Oddiy narx, VIP narx, Ulgurji narx.
    """
    name = models.CharField(max_length=200, verbose_name=_("Narxlar ro'yxati nomi"))
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False, verbose_name=_("Standart narxmi"))

    class Meta:
        verbose_name = _("Narxlar ro'yxati")
        verbose_name_plural = _("Narxlar ro'yxatlari")

    def __str__(self):
        return self.name


class PriceListItem(BaseModel):
    """
    Narxlar ro'yxatidagi har bir mahsulot narxi.
    """
    price_list = models.ForeignKey(
        PriceList, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="price_list_items"
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Narx"))

    class Meta:
        verbose_name = _("Narxlar ro'yxati elementi")
        verbose_name_plural = _("Narxlar ro'yxati elementlari")
        unique_together = ["price_list", "variant"]

    def __str__(self):
        return f"{self.price_list} — {self.variant}: {self.price}"