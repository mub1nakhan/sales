# Sales Management API — Hujjatlar

**Versiya:** 1.0.0  
**Base URL:** `http://localhost:8000`

---

## Swagger UI (Interaktiv hujjatlar)

| URL | Tavsif |
|-----|--------|
| `/api/docs/` | Swagger UI — brauzerda sinab ko'rish |
| `/api/redoc/` | ReDoc UI — o'qish uchun qulay |
| `/api/schema/` | OpenAPI 3.0 schema (YAML/JSON) |

---

## Autentifikatsiya

Barcha himoyalangan endpointlar uchun `Authorization` sarlavhasi talab qilinadi:

```
Authorization: Bearer <access_token>
```

### Auth Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| `POST` | `/api/auth/register/` | Ro'yxatdan o'tish |
| `POST` | `/api/auth/login/` | Kirish — token olish |
| `POST` | `/api/auth/logout/` | Chiqish — tokenni bekor qilish |
| `POST` | `/api/auth/token/refresh/` | Access tokenni yangilash |

#### Register — `POST /api/auth/register/`
```json
{
  "username": "ali_valiyev",
  "password": "parol123",
  "password_confirm": "parol123",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "phone": "+998901234567",
  "email": "ali@example.com"
}
```

#### Login — `POST /api/auth/login/`
```json
{ "username": "ali_valiyev", "password": "parol123" }
```
**Javob:**
```json
{
  "user": { "id": 1, "username": "ali_valiyev", ... },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

#### Logout — `POST /api/auth/logout/`
```json
{ "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..." }
```

#### Token yangilash — `POST /api/auth/token/refresh/`
```json
{ "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..." }
```

---

## API Endpointlar

### Foydalanuvchilar (Users)

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET` | `/api/branches/` | Filiallar ro'yxati |
| `POST` | `/api/branches/` | Yangi filial |
| `GET/PUT/PATCH/DELETE` | `/api/branches/{id}/` | Filial CRUD |
| `GET` | `/api/roles/` | Rollar ro'yxati |
| `POST` | `/api/roles/` | Yangi rol |
| `GET/PUT/PATCH/DELETE` | `/api/roles/{id}/` | Rol CRUD |
| `GET` | `/api/users/` | Foydalanuvchilar ro'yxati |
| `POST` | `/api/users/` | Yangi foydalanuvchi |
| `GET` | `/api/users/me/` | Joriy foydalanuvchi |
| `POST` | `/api/users/{id}/change-password/` | Parol o'zgartirish |
| `GET/PUT/PATCH/DELETE` | `/api/users/{id}/` | Foydalanuvchi CRUD |
| `GET` | `/api/sales-targets/` | Savdo rejalari |
| `POST` | `/api/sales-targets/` | Yangi savdo rejasi |

**Filter parametrlar:**
- `GET /api/users/?branch=1&role=2&is_active=true&search=Ali`
- `GET /api/branches/?is_active=true&search=Chilonzor`

---

### Mahsulotlar (Products)

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET/POST` | `/api/categories/` | Kategoriyalar |
| `GET` | `/api/categories/?parent=root` | Faqat asosiy kategoriyalar |
| `GET` | `/api/categories/{id}/children/` | Ichki kategoriyalar |
| `GET/POST` | `/api/brands/` | Brendlar |
| `GET/POST` | `/api/units/` | O'lchov birliklari |
| `GET/POST` | `/api/product-attributes/` | Mahsulot xususiyatlari |
| `GET/POST` | `/api/products/` | Mahsulotlar |
| `GET` | `/api/products/{id}/variants/` | Mahsulot variantlari |
| `GET/POST` | `/api/product-variants/` | Variantlar (barcode/SKU bo'yicha) |
| `GET/POST` | `/api/price-lists/` | Narxlar ro'yxati |

**Filter parametrlar:**
- `GET /api/products/?category=1&brand=2&is_active=true&search=ko'ylak`
- `GET /api/product-variants/?product=1&barcode=12345678`

---

### Sotuvlar (Billz)

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET/POST` | `/api/customer-groups/` | Mijoz guruhlari |
| `GET/POST` | `/api/customers/` | Mijozlar |
| `GET` | `/api/customers/{id}/sales/` | Mijoz sotuvlari tarixi |
| `GET/POST` | `/api/cash-registers/` | Kassalar |
| `GET/POST` | `/api/cash-sessions/` | Kassa smenalari |
| `POST` | `/api/cash-sessions/{id}/close/` | Smenani yopish |
| `GET` | `/api/cash-sessions/{id}/summary/` | Smena hisoboti |
| `GET/POST` | `/api/sales/` | Sotuvlar |
| `POST` | `/api/sales/{id}/complete/` | Sotuvni yakunlash |
| `POST` | `/api/sales/{id}/cancel/` | Sotuvni bekor qilish |
| `GET` | `/api/sales/{id}/returns/` | Sotuv qaytarishlari |
| `GET/POST` | `/api/payment-methods/` | To'lov usullari |
| `GET/POST` | `/api/expense-categories/` | Xarajat turlari |
| `GET/POST` | `/api/expenses/` | Xarajatlar |
| `GET/POST` | `/api/cash-movements/` | Kassa harakatlari |

**Filter parametrlar:**
- `GET /api/sales/?branch=1&seller=2&status=completed&date_from=2025-01-01&date_to=2025-12-31`
- `GET /api/customers/?group=1&search=Aliyev`

**Smena yopish:**
```json
{ "closing_balance": 500000, "notes": "Kunlik yopilish" }
```

---

### Inventar (Inventory)

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET/POST` | `/api/warehouses/` | Omborxonalar |
| `GET` | `/api/stocks/` | Tovar qoldiqlari (faqat o'qish) |
| `GET` | `/api/stocks/low-stock/` | Kam qolgan tovarlar |
| `GET` | `/api/stocks/out-of-stock/` | Tugagan tovarlar |
| `GET/POST` | `/api/suppliers/` | Yetkazib beruvchilar |
| `GET/POST` | `/api/purchase-orders/` | Kirim buyurtmalari |
| `POST` | `/api/purchase-orders/{id}/receive/` | Tovarni qabul qilish |
| `POST` | `/api/purchase-orders/{id}/cancel/` | Buyurtmani bekor qilish |
| `GET/POST` | `/api/stock-transfers/` | Tovar ko'chirishlar |
| `POST` | `/api/stock-transfers/{id}/complete/` | Transferni yakunlash |
| `GET/POST` | `/api/inventories/` | Inventarizatsiya |
| `POST` | `/api/inventories/{id}/complete/` | Inventarizatsiyani yakunlash |
| `GET/POST` | `/api/write-offs/` | Hisobdan chiqarishlar |

**Filter parametrlar:**
- `GET /api/stocks/?warehouse=1&search=Nike`
- `GET /api/purchase-orders/?supplier=1&status=draft`

---

## Umumiy Filter Parametrlar

Barcha ViewSet larda qo'llab-quvvatlanadigan umumiy parametrlar:

| Parametr | Turi | Tavsif |
|----------|------|--------|
| `search` | string | Matn bo'yicha qidirish |
| `is_active` | boolean | `true` yoki `false` |
| `date_from` | date | `YYYY-MM-DD` formatida boshlanish sanasi |
| `date_to` | date | `YYYY-MM-DD` formatida tugash sanasi |

---

## HTTP Status Kodlar

| Kod | Ma'nosi |
|-----|---------|
| `200` | OK — Muvaffaqiyatli |
| `201` | Created — Yaratildi |
| `204` | No Content — O'chirildi |
| `400` | Bad Request — Noto'g'ri so'rov |
| `401` | Unauthorized — Token kerak |
| `403` | Forbidden — Ruxsat yo'q |
| `404` | Not Found — Topilmadi |

---

## Token muddatlari

| Token | Muddat |
|-------|--------|
| `access` | 1 soat |
| `refresh` | 7 kun |

Access token muddati tugaganda `refresh` token bilan yangilanadi.  
`ROTATE_REFRESH_TOKENS = True` — har yangilanishda yangi refresh token ham beriladi.
