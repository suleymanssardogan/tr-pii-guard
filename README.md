# tr-pii-guard

[![CI](https://github.com/suleymanssardogan/tr-pii-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/suleymanssardogan/tr-pii-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tr-pii-guard.svg)](https://pypi.org/project/tr-pii-guard/)

Türkçe metinlerdeki kişisel verileri (TC kimlik no, IBAN, telefon, e-posta, isim, adres) tespit
eden açık kaynak Python kütüphanesi. İki kullanım alanı:

- **LLM güvenlik katmanı:** KVKK/GDPR uyumu için, kullanıcı verisini OpenAI/Claude/Gemini gibi
  servislere göndermeden önce maskele/geri eşle.
- **KVKK veri ihlali etki özeti:** Bir sızma dökümünü tarayıp, bildirim kararı öncesi hızlı,
  açıklanabilir bir risk değerlendirmesi çıkar.

**[Canlı demo](https://suleymanssardogan.github.io/tr-pii-guard/)** — kurulum gerekmez, tamamen tarayıcında çalışır.

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

Şu an tespit edilen türler: TC kimlik no, IBAN, Vergi Kimlik Numarası (VKN), telefon, e-posta,
araç plakası (hepsi checksum/format doğrulamalı), ve API key/secrets (OpenAI, Anthropic, AWS,
GitHub, Google, Slack, Stripe, npm, PyPI, Twilio, SendGrid + PEM private key/sertifika blokları
— bilinen, prefix'li/yapısal formatlar; Azure bilerek hariç, sabit bir prefix'i olmadığı için
güvenli regex yazılamıyor). Doğruluk ölçümü (precision/recall) için [BENCHMARK.md](BENCHMARK.md)'e bak.

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

```python
# Daha yüksek recall istersen (daha çok yanlış pozitif riskiyle) eşiği düşür
redact(text, use_ner=True, ner_min_score=0.5)
```

Varsayılan `ner_min_score=0.8`, düşük güvenli (genelde hatalı) tahminleri eler — gerçek
precision/recall etkisi için [BENCHMARK.md](BENCHMARK.md)'e bak.

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

### KVKK veri ihlali etki özeti

```python
from tr_pii_guard import breach_report

breach_report("TC no 10000000146, telefon 0532 123 45 67.")
# -> {"counts": {"TC_NO": 1, "TELEFON": 1}, "risk_level": "yüksek",
#     "reason": "TC kimlik no, başka bir iletişim/finansal/kimlik bilgisiyle..."}
```

```bash
tr-pii-guard breach-report sizma_dokumu.txt
tr-pii-guard breach-report sizma_klasoru/        # dizin verirsen tüm dosyaları tarar, toplar
tr-pii-guard breach-report musteriler.csv        # .csv ise sütun sütun tarar (ör. "tc_no: 5000")
tr-pii-guard breach-report sizma_dokumu.txt --format json   # dashboard/ticket sistemine bağla
```

Bir veri dökümünü/leak dosyasını (ya da gerçek sızmalarda olduğu gibi, çok dosyalı bir klasörü
ya da CSV exportunu) tarar, PII tiplerini sayar ve bilinen **tip kombinasyonlarına** dayalı (örn.
TC no + telefon birlikte = yüksek risk) açıklanabilir bir risk seviyesi verir — KVKK'ya 72 saat
içinde bildirim kararı öncesi hızlı bir ilk değerlendirme için. `.csv` dosyaları sütun sütun
taranır (gerçek sızmalar çoğu zaman düz metin değil, yapılandırılmış export olur) — her sütun
ayrı bir kaynak olarak raporlanır, hangi alanın (ör. `tc_no` sütunu) PII içerdiği netleşir.
Python'dan çoklu dosya için `breach_report_many()`.

**Bu bir hukuki tavsiye aracı değildir.** Sadece desteklenen genel nitelikli PII türlerine (TC no,
IBAN, telefon, e-posta, opsiyonel isim) bakar; KVKK m.6 kapsamındaki **özel nitelikli veriyi**
(sağlık, din, etnik köken vb.) bilerek tespit etmez — anahtar kelime tabanlı tahmin yanlış negatif
riski taşır, bu da gerçek hukuki sonuç doğurabilir. Bildirim kararı için hukuk/uyum ekibine danış.

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

## Diğer seçeneklerle karşılaştırma

En yakın muadil [wardcat](https://pypi.org/project/wardcat/) — dürüst bir karşılaştırma:

| Özellik | tr-pii-guard | wardcat |
|---|---|---|
| TC no/IBAN checksum doğrulama | ✅ | ✅ |
| Vergi No (VKN) checksum doğrulama | ✅ | ✅ (wardcat'in listesinde "Vergi No" var) |
| Araç plakası tespiti | ✅ | ✅ (wardcat'in listesinde "plates" var) |
| Çoklu ülke desteği | ❌ (bilerek — hedef Türk kullanıcı) | ✅ (TR, US, UK, ES, FR, NL, PL) |
| Secrets tespiti (API key + PEM blok) | ✅ (11 sağlayıcı + PEM) | ✅ (~12 sağlayıcı + PEM) |
| Aksiyon sayısı | 2 (redact, hash) | 6 (warn/hash/redact/mask/tokenize/surrogate) |
| KVKK veri ihlali etki özeti (`breach_report`) | ✅ | ❌ |
| MCP server | ✅ | ✅ |
| Streaming yanıtta bölünen placeholder desteği | ✅ | Belirtilmemiş; 500KB üstü girdide hata veriyor |
| Kurulumsuz canlı demo | ✅ ([dene](https://suleymanssardogan.github.io/tr-pii-guard/)) | ❌ |
| Yayınlanmış precision/recall sayıları | ✅ ([BENCHMARK.md](BENCHMARK.md)) | Benchmark var ama sayfada sayı yok |

(Microsoft Presidio da genel amaçlı bir alternatif ama TC no için hazır bir recognizer'ı yok —
elle eklemen gerekiyor.)

Kapsamda geride olduğumuz yerler var — amacımız her alanda rekabet etmek değil, Türk kullanıcı
için dar ama şeffaf/test edilmiş bir seçenek olmak.

## Bilinen sınırlamalar

- **Yanlış pozitif tercih edilir:** Rastgele bir 11 haneli sayı TC no checksum'ını
  tutarlı bir şekilde geçebilir (~%1 ihtimal) ve maskelenir. Bilinçli bir tercih —
  bir gizlilik aracında fazla maskelemek, PII'yi kaçırmaktan daha güvenli.
- **`+`/`00` olmadan yazılan "90" ülke kodu** (`"90 532 123 45 67"`) tek bir telefon
  olarak tanınmaz; ama numaranın kendisi (`532 123 45 67`) yine de maskelenir —
  dışarıda kalan sadece ülke kodu, kişisel veri değil.
- Telefon alan kodu aralığı `[2-5]xx`'e sabit; nadir/özel numara formatları kaçabilir.
- **VERGI_NO ile TELEFON örtüşebilir:** her ikisi de 10 haneli, bazı rastgele sayılar
  her iki formatı da sağlayabilir (TC no/IBAN'daki checksum rastlantısallığıyla aynı
  kategori). Çakışan aralıkta `redact()` VERGI_NO'yu önceliklendirir (checksum
  doğrulamalı olduğu için); ikisi de maskelendiği için pratik bir sorun oluşturmaz.
- **Plaka tespiti** taksi/konsolosluk gibi özel seri kurallarını ayırmaz; il kodu+harf/rakam
  formatına uyan rastgele kodlar (ör. ürün/parti numaraları) yanlış pozitif verebilir.
- **NER (`use_ner=True`), nadir/yabancı/kurgusal özel isimlerde zayıflıyor** — gerçek Wikipedia
  cümleleriyle yapılan dış doğrulamada recall 0.64'e düşüyor (günlük isimlerde ~0.93-1.00'e karşı).
  Sebep subword tokenization kesilmesi (`"Lichtenthal"` → `"Li"` gibi). `find_names()`'in
  varsayılan `min_score=0.8` eşiği bu kırık parçaların çoğunu eliyor (precision'ı 0.60→0.72'ye
  çıkarıyor) ama bir miktar recall'dan ödün veriyor; daha yüksek recall istersen
  `ner_min_score` düşür. Bkz. [BENCHMARK.md](BENCHMARK.md).

## Lisans

MIT
