# tr-pii-guard

[![CI](https://github.com/suleymanssardogan/tr-pii-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/suleymanssardogan/tr-pii-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tr-pii-guard.svg)](https://pypi.org/project/tr-pii-guard/)

Türkçe metinlerdeki kişisel verileri (TC kimlik no, IBAN, telefon, e-posta, isim, adres) LLM API çağrısından önce tespit edip maskeleyen açık kaynak Python kütüphanesi.

KVKK/GDPR uyumu için, kullanıcı verisini OpenAI/Claude/Gemini gibi servislere göndermeden önce bir güvenlik katmanı sağlar.

## Durum

Erken geliştirme aşamasında.

## Kurulum

```bash
pip install tr-pii-guard
```

## Kullanım

```python
from tr_pii_guard import redact, restore

masked_text, mapping = redact("TC no 10000000146, telefon 0532 123 45 67.")
# masked_text -> "TC no [TC_NO_1], telefon [TELEFON_1]."

original = restore(masked_text, mapping)
```

Şu an tespit edilen türler: TC kimlik no, IBAN, telefon, e-posta (hepsi checksum/format
doğrulamalı). Doğruluk ölçümü (precision/recall) için [BENCHMARK.md](BENCHMARK.md)'e bak.

> ⚠️ **`mapping` ham PII değerlerini içerir.** Audit/metrik için `mapping`'i olduğu gibi loglama —
> tam da maskelemeye çalıştığın veriyi log dosyasına yazmış olursun. Güvenle loglanabilecek,
> sadece tip bazında sayı veren bir özet için `summary(mapping)` kullan:
>
> ```python
> from tr_pii_guard import summary
> summary(mapping)  # -> {"TC_NO": 1, "TELEFON": 1}  (ham değer yok)
> ```

### İsim/adres tespiti (opsiyonel, NER)

```bash
pip install tr-pii-guard[ner]
```

```python
masked_text, mapping = redact("Ahmet Yılmaz İstanbul'a gitti.", use_ner=True)
```

`use_ner` varsayılan olarak kapalı — temel paket `transformers`/`torch` indirmeden çalışır.
Ekstra kurulu değilken `use_ner=True` çağrılırsa açık bir hata mesajıyla uyarır.

### Komut satırı

```bash
tr-pii-guard scan dosya.txt
```

### LLM çağrısını koruma altına alma

```python
from tr_pii_guard import protect

def call_openai(prompt: str) -> str:
    return openai_client.responses.create(model="gpt-4o-mini", input=prompt).output_text

reply = protect(call_openai, "TC no 10000000146 ile siparişimi sorgula.")
```

`protect` hiçbir LLM SDK'sını import etmez — `llm_call` metin alıp metin döndüren herhangi bir
fonksiyon olabilir (OpenAI, Claude, yerel bir model, ne olursa). Aynı `use_ner`/`types`/`strict`
argümanlarını `redact()`'teki gibi kabul eder.

### Geri dönüşümsüz pseudonimleştirme (hash)

```python
from tr_pii_guard import hash_pii

hash_pii("TC no 10000000146.", salt="projene-özel-bir-tuz")
# -> "TC no [TC_NO_265c9160683d]."
```

`redact()`/`restore()` tersinirdir (orijinal değeri geri çıkarabilirsin); `hash_pii` tersinmez —
aynı değer + aynı salt her zaman aynı hash'i üretir (kayıtları eşlemek için kullanışlı), ama
orijinal değer bir daha asla okunamaz. Analytics/log gibi orijinali gerektirmeyen senaryolar için.

### Streaming LLM yanıtları

```python
from tr_pii_guard import protect_stream

def call_openai_stream(prompt: str):
    for event in openai_client.responses.create(model="gpt-4o-mini", input=prompt, stream=True):
        if event.type == "response.output_text.delta":
            yield event.delta

for piece in protect_stream(call_openai_stream, "TC no 10000000146 ile siparişimi sorgula."):
    print(piece, end="", flush=True)
```

`llm_call` bir metin parçaları (chunk) iterable'ı döndürmeli. `[TC_NO_1]` gibi bir placeholder iki
chunk arasına bölünse bile (`"[TC_NO"` + `"_1]"` gibi) doğru şekilde geri eşlenir — sadece
placeholder'ın tamamlanmasını beklemek için gereken kadar buffer tutulur, gerisi hemen akar.

### MCP server (AI agent'lara doğrudan araç olarak)

```bash
pip install tr-pii-guard[mcp]
tr-pii-guard-mcp
```

Claude Code gibi bir MCP client'ın config'ine ekleyerek `redact_text`, `restore_text`,
`hash_pii_text` araçlarını doğrudan agent'a sunar — agent kendi başına PII maskeleyebilir,
geri eşleyebilir ya da hash'leyebilir, Python kodu yazmana gerek kalmadan.

### Kapsamı/hassasiyeti ayarlama

```python
# Sadece TC no ve IBAN'ı maskele
redact(text, types=["TC_NO", "IBAN"])

# Checksum doğrulamasını atla, daha fazla aday yakala (daha çok yanlış pozitif riskiyle)
redact(text, strict=False)
```

### Özel detector ekleme

```python
import re
from tr_pii_guard import register_detector

register_detector("CALISAN_ID", lambda text: list(re.finditer(r"EMP-\d{5}", text)))
```

## Bilinen sınırlamalar

- **Yanlış pozitif tercih edilir:** Rastgele bir 11 haneli sayı TC no checksum'ını
  tutarlı bir şekilde geçebilir (~%1 ihtimal) ve maskelenir. Bilinçli bir tercih —
  bir gizlilik aracında fazla maskelemek, PII'yi kaçırmaktan daha güvenli.
- **`+`/`00` olmadan yazılan "90" ülke kodu** (`"90 532 123 45 67"`) tek bir telefon
  olarak tanınmaz; ama numaranın kendisi (`532 123 45 67`) yine de maskelenir —
  dışarıda kalan sadece ülke kodu, kişisel veri değil.
- Telefon alan kodu aralığı `[2-5]xx`'e sabit; nadir/özel numara formatları kaçabilir.

## Lisans

MIT
