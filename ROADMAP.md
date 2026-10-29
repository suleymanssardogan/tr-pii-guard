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
- [x] Küçük bir Türkçe test korpusu üzerinde precision/recall ölçümü — gerçekten kuruldu ve ölçüldü: recall 1.00, precision 0.62 (bkz. BENCHMARK.md, bilinen e-posta local-part yanlış pozitifi)

## v0.3 — Geliştirici deneyimi & paketleme
- [x] Temiz public API + özel pattern eklenebilen plugin arayüzü (`register_detector`)
- [x] CLI aracı (`tr-pii-guard scan dosya.txt`)
- [x] PyPI'a yayınlama — https://pypi.org/project/tr-pii-guard/0.2.0/ (v0.4/v0.5 ile güncel)
- [x] README'de kurulum rozeti

## v0.4 — LLM pipeline entegrasyonu (asıl değer önermesi)
- [x] Herhangi bir LLM çağrısını sarmalayan `protect(llm_call, prompt)` middleware (SDK bağımlılığı yok, metin-içi/metin-dışı herhangi bir fonksiyonla çalışır)
- [x] Redakte edilecek PII tiplerini seçebilme (`redact(text, types=["TC_NO", "IBAN"])`)
- [x] Ayarlanabilir hassasiyet (`redact(text, strict=False)` — checksum doğrulamasını atlayıp daha fazla aday yakalar)

## v0.5 — Açık kaynak hijyeni & topluluk
- [x] CI (GitHub Actions: ruff + pytest, Python 3.9/3.11/3.13 matrix)
- [x] CONTRIBUTING.md
- [x] Repo'yu public yap — https://github.com/suleymanssardogan/tr-pii-guard
- [ ] İlk gerçek kullanıcı/issue toplama — repo public olup paket duyurulduktan sonra organik

## v0.6 — KVKK veri ihlali özelliklerini genişletme
- [x] `breach_report_many()` + `tr-pii-guard breach-report --dir` ile çoklu dosya/dizin taraması (gerçek sızma dökümleri çoğu zaman tek paragraf değil, çok dosyalıdır)
- [x] API key/secrets tespiti (OpenAI, Anthropic, AWS, GitHub, Google, Slack, Stripe — prefix'li, iyi tanımlı formatlar; wardcat'e karşı kapanan bir boşluk)
- [ ] `--format json` çıktısı (dashboard/ticket sistemlerine bağlanabilsin)
- [ ] CSV-farkındalığı (sütun bazlı sayım)

---

**Öncelik mantığı:** v0.1–v0.3 bir demo/hiring-ready sürüm için zorunlu. v0.4–v0.5 projeyi "gerçek kullanılan açık kaynak araç" yapan farklar.
