# tr-pii-guard

Türkçe metinlerdeki kişisel verileri (TC kimlik no, IBAN, telefon, e-posta, isim, adres) LLM API çağrısından önce tespit edip maskeleyen açık kaynak Python kütüphanesi.

KVKK/GDPR uyumu için, kullanıcı verisini OpenAI/Claude/Gemini gibi servislere göndermeden önce bir güvenlik katmanı sağlar.

## Durum

Erken geliştirme aşamasında.

## Kurulum

```bash
pip install -e .
```

## Kullanım

```python
from tr_pii_guard import redact, restore

masked_text, mapping = redact("TC no 10000000146, telefon 0532 123 45 67.")
# masked_text -> "TC no [TC_NO_1], telefon [TELEFON_1]."

original = restore(masked_text, mapping)
```

Şu an tespit edilen türler: TC kimlik no, IBAN, telefon, e-posta (hepsi checksum/format
doğrulamalı). İsim/adres tespiti (NER) [ROADMAP](ROADMAP.md)'te v0.2 olarak planlı.

## Lisans

MIT
