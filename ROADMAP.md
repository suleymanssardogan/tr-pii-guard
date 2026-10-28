# Roadmap

## v0.1 — Çekirdek redaksiyon (şu anki hedef)
- [x] Proje iskeleti (paket, lisans, test altyapısı)
- [x] TC no regex + checksum doğrulama
- [x] Telefon regex
- [x] IBAN regex + checksum doğrulama
- [x] E-posta regex detector
- [x] `redact(text) -> (masked_text, mapping)` — tüm detector'ları birleştiren tek API
- [x] `restore(masked_text, mapping) -> text` — geri eşleme
- [x] Çakışan eşleşmeleri çözme (aynı aralığı birden fazla detector yakalarsa en güvenilir eşleşmeyi seç)

## v0.2 — İsim/adres tespiti (NER)
- [x] Mevcut açık kaynak Türkçe NER modelini entegre et (PERSON/LOCATION) — `redact(text, use_ner=True)`
- [x] Ağır ML bağımlılığı istemeyenler için "sadece regex" modu (`use_ner=False` varsayılan; `transformers`/`torch` yoksa açık hata mesajıyla yönlendirir)
- [ ] Küçük bir Türkçe test korpusu üzerinde precision/recall ölçümü — `transformers`/`torch` bu ortamda kurulu değil (GB'larca indirme), gerçek model doğrulaması kurulduğunda yapılmalı

## v0.3 — Geliştirici deneyimi & paketleme
- [x] Temiz public API + özel pattern eklenebilen plugin arayüzü (`register_detector`)
- [x] CLI aracı (`tr-pii-guard scan dosya.txt`)
- [x] PyPI'a yayınlama — https://pypi.org/project/tr-pii-guard/0.1.0/
- [x] README'de kurulum rozeti

## v0.4 — LLM pipeline entegrasyonu (asıl değer önermesi)
- [ ] OpenAI/Anthropic çağrısını sarmalayan örnek middleware (prompt'u redakte et, cevabı geri eşle)
- [ ] Redakte edilecek PII tiplerini seçebilme (config)
- [ ] Ayarlanabilir hassasiyet (false positive/negative dengesi)

## v0.5 — Açık kaynak hijyeni & topluluk
- [ ] CI (GitHub Actions: lint + pytest)
- [ ] CONTRIBUTING.md
- [ ] Repo'yu public yap
- [ ] İlk gerçek kullanıcı/issue toplama

## Stretch (kapsam dışı tutulabilir)
- [ ] Semantic cache / LLM maliyet raporu modülü
- [ ] İngilizce PII desteği

---

**Öncelik mantığı:** v0.1–v0.3 bir demo/hiring-ready sürüm için zorunlu. v0.4–v0.5 projeyi "gerçek kullanılan açık kaynak araç" yapan farklar. Stretch bölümü zaman kalırsa.
