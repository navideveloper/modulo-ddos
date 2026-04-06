# 🚀 Modulo DDOS (Async Network Tester)

Oddiy va tezkor **async network tester**. Serverga bir nechta so‘rov yuborib, javob vaqtini (latency), status kodlarni va xatoliklarni tahlil qiladi.

---

## 📦 O‘rnatish (Installation)

Avval kerakli kutubxonalarni o‘rnatib oling:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Foydalanish (Usage)

Quyidagi buyruq orqali ishga tushirasiz:

```powershell
python .\main.py --ip=127.0.0.1 --port=80 --requests=1000
```

---

## 📌 Parametrlar

| Parametr     | Tavsif                                       |
| ------------ | -------------------------------------------- |
| `--ip`       | Maqsad IP manzil                             |
| `--port`     | Port (default: 80)                           |
| `--requests` | Yuboriladigan so‘rovlar soni                 |
| `--output`   | Natijani saqlash fayli (default: result.csv) |

---

## 📊 Natija

Dastur ishlagandan so‘ng:

* Terminalda live log chiqadi
* Natijalar `.csv` faylga saqlanadi

CSV ichida:

* request_id
* timestamp
* latency
* bytes_sent
* http_status
* outcome
* error_type

---

## ⚠️ Ogohlantirish

Bu dastur faqat:

* test qilish
* o‘rganish
* o‘z serveringizni tekshirish

uchun mo‘ljallangan.

Begona serverlarga ruxsatsiz ishlatish tavsiya etilmaydi ❗

---

## 👨‍💻 Muallif

**Qudratillo Salohiddinov**

---
