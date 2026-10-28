# tr-pii-guard

Türkçe metinlerdeki kişisel verileri (TC kimlik no, IBAN, telefon, e-posta, isim, adres) LLM API çağrısından önce tespit edip maskeleyen açık kaynak Python kütüphanesi.

KVKK/GDPR uyumu için, kullanıcı verisini OpenAI/Claude/Gemini gibi servislere göndermeden önce bir güvenlik katmanı sağlar.

## Durum

Erken geliştirme aşamasında.

## Kurulum

```bash
pip install -e .
```

## Kullanım (planlanan API)

```python
from tr_pii_guard import redact

masked_text, mapping = redact("Adım Ahmet Yılmaz, TC no 12345678901.")
# masked_text -> "Adım [İSİM], TC no [TC_NO]."
```

## Lisans

MIT
