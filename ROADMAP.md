# Roadmap

## v0.1 — Çekirdek redaksiyon (şu anki hedef)
- [x] Proje iskeleti (paket, lisans, test altyapısı)
- [x] TC no regex + checksum doğrulama
- [x] Telefon regex
- [x] IBAN regex + checksum doğrulama
- [ ] E-posta regex detector
- [ ] `redact(text) -> (masked_text, mapping)` — tüm detector'ları birleştiren tek API
- [ ] `restore(masked_text, mapping) -> text` — geri eşleme
- [ ] Çakışan eşleşmeleri çözme (aynı aralığı birden fazla detector yakalarsa en güvenilir eşleşmeyi seç)

## v0.2 — İsim/adres tespiti (NER)
- [ ] Mevcut açık kaynak Türkçe NER modelini entegre et (PERSON/LOCATION)
- [ ] Ağır ML bağımlılığı istemeyenler için "sadece regex" modu (`pip install tr-pii-guard[ner]` opsiyonel ekstra)
- [ ] Küçük bir Türkçe test korpusu üzerinde precision/recall ölçümü

## v0.3 — Geliştirici deneyimi & paketleme
- [ ] Temiz public API + özel pattern eklenebilen plugin arayüzü
- [ ] CLI aracı (`tr-pii-guard scan dosya.txt`)
- [ ] PyPI'a yayınlama
- [ ] README'de gerçek kullanım örnekleri + rozetler

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
