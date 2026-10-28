# Doğruluk Ölçümü

`benchmarks/corpus.py`'daki 20 cümlelik, elle etiketlenmiş küçük Türkçe test setinde ölçüldü.
Bu **büyük, istatistiksel olarak kapsamlı bir benchmark değil** — dürüst, küçük bir örnek:
gerçek formatları, bozuk checksum'lı "sahte" PII'leri, ve detector'ların kaçırabileceği bilinen
tuzakları (PII gibi görünen ama olmayan sayılar) bilerek içeriyor.

Çalıştırmak için: `python3 benchmarks/run.py`

## Sonuçlar (regex detector'lar, NER hariç)

| Tip      | TP | FP | FN | Precision | Recall |
|----------|----|----|----|-----------|--------|
| TC no    | 3  | 0  | 0  | 1.00      | 1.00   |
| IBAN     | 3  | 0  | 0  | 1.00      | 1.00   |
| Telefon  | 7  | 1  | 0  | 0.88      | 1.00   |
| E-posta  | 3  | 0  | 0  | 1.00      | 1.00   |

## Sonuçlar (NER — isim/konum, `pip install tr-pii-guard[ner]` sonrası)

| Tip        | TP | FP | FN | Precision | Recall |
|------------|----|----|----|-----------|--------|
| İsim/konum | 5  | 3  | 0  | 0.62      | 1.00   |

**Bilinen, tutarlı bir yanlış pozitif deseni:** 3 yanlış pozitifin üçü de aynı sebepten —
NER modeli, bir e-posta adresinin local-part'ındaki isim parçasını (`ahmet.yilmaz@...` içindeki
`"yilmaz"`) ayrı bir kişi ismi zannediyor. **Ama bu `redact(use_ner=True)` çağrısında hiçbir zaman
sızmıyor:** overlap-çözümleme mantığı EPOSTA'nın daha uzun eşleşmesini seçip bu parçayı eler
(`tests/test_ner.py::test_redact_use_ner_does_not_leak_name_fragment_from_email` ile doğrulandı).
Risk sadece `find_names()`'i tek başına, `redact()` dışında kullanırsan geçerli.

## Performans

`benchmarks/run.py` ayrıca `redact()`'i bu makinede 3600 kez çalıştırıp ortalama süreyi ölçer:

- **~0.006 ms / çağrı** (yaklaşık 8.5M karakter/saniye) — regex+checksum tabanlı tespit,
  üretim trafiğinde sorun oluşturmayacak kadar hızlı. ([ClickHouse'un guardrail latency
  tablosunda](https://clickhouse.com/resources/engineering/llm-guardrails) "regex/schema"
  kategorisi "sub-millisecond" olarak sınıflandırılıyor — bizim ölçümümüz bu kategoriyle uyumlu.)
- NER (`use_ner=True`) açıldığında gerçek bir model inference'ı çalıştığı için bu rakamlar
  geçerli değil; o mod milisaniyeler-onlarca milisaniye mertebesinde olması beklenir.

## Not

- Telefon'daki 1 yanlış pozitif bilinçli olarak test setine eklendi: `4455667788` gibi, alan
  kodu aralığına ([2-5]xx) denk gelen rastgele 10 haneli bir referans kodu telefon zannediliyor.
  README'deki "Bilinen sınırlamalar" bölümünde de belirtilmiştir.
- TC no/IBAN'da yanlış pozitif riski var ama bu küçük sette rastlanmadı (checksum rastlantısallığı
  istatistiksel olarak ~%1 ihtimalli, 20 örnekte görülmesi beklenmiyordu).
- NER sayıları `transformers`/`torch` kurulduktan sonra gerçekten ölçüldü (artık varsayımsal
  değil) — ama bu ağırlıklar CI'da kurulmuyor (indirme maliyeti), bu yüzden sadece yerel olarak
  doğrulandı, her push'ta otomatik ölçülmüyor.
- Katkıda bulunmak isteyenler `benchmarks/corpus.py`'a yeni etiketli örnek ekleyebilir.
