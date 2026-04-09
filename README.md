# 🚀 Modulo DDoS

**Modulo DDoS** — bu Python va PycURL asosida yaratilgan yuqori tezlikdagi stress-test vositasi. U HTTP serverlarining yuklanishga chidamliligini sinash uchun mo'ljallangan.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey)

---

## ⚡ Xususiyatlari

- **Yuqori tezlik** – Bir vaqtning o'zida 800 tagacha ulanish
- **HTTP Pipelining** – So'rovlar navbatini optimallashtirish
- **Real-vaqt statistikasi** – Har bir so'rov holati va kechikish vaqti
- **CSV hisobot** – Barcha natijalarni faylga saqlash
- **Rangli interfeys** – Terminalda qulay kuzatish imkoniyati

---

## 📦 O'rnatish

```bash
# Repositoriyani klonlash
git clone https://github.com/username/modulo-ddos.git
cd modulo-ddos
pip install pycurl certifi colorama
```

## 🔧 Foydalanish
```bash
python modulo.py --ip <IP-manzil> --port <PORT> --requests <SONI> --output <FAYL>
```
| Parametr   | Tavsif              | Standart     |
|------------|---------------------|--------------|
| --ip       | Nishon IP manzili   | Majburiy     |
| --port     | Nishon porti        | 80           |
| --requests | So'rovlar soni      | 100          |
| --output   | CSV hisobot fayli   | result.csv   |

# Misol
```bash
python modulo.py --ip 192.168.1.1 --port 8080 --requests 1000 --output test.csv
```