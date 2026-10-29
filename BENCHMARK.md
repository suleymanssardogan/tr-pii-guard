# Doğruluk Ölçümü

`benchmarks/corpus.py`'daki 70 cümlelik, elle etiketlenmiş Türkçe test setinde ölçüldü.
Bu **büyük, istatistiksel olarak kapsamlı bir endüstri benchmark'ı değil** — ama ilk sürümdeki
23 cümlelik sanity-check'ten daha ciddi bir örnek: her PII tipi için birden fazla gerçek format
(telefon için 10 farklı yazım şekli gibi), bozuk checksum'lı "sahte" PII'ler, detector'ların
kaçırabileceği bilinen tuzaklar (PII gibi görünen ama olmayan sayılar), key-şekilli olmayan
secret distractor'ları (UUID, hash, base64), ve ~10 tamamen temiz cümle (yanlış pozitif oranını
ölçmek için) bilerek içeriyor. Her checksum-geçerli TC no/IBAN gerçekten üretilip
`_is_valid_tc_no`/`_is_valid_iban` ile doğrulandı, tahmin edilmedi.

Çalıştırmak için: `python3 benchmarks/run.py`

## Sonuçlar (regex detector'lar, NER hariç)

| Tip      | TP | FP | FN | Precision | Recall |
|----------|----|----|----|-----------|--------|
| TC no    | 9  | 0  | 0  | 1.00      | 1.00   |
| IBAN     | 7  | 0  | 0  | 1.00      | 1.00   |
| Telefon  | 12 | 3  | 0  | 0.80      | 1.00   |
| E-posta  | 7  | 0  | 0  | 1.00      | 1.00   |
| API key  | 6  | 0  | 0  | 1.00      | 1.00   |

## Sonuçlar (NER — isim/konum, `pip install tr-pii-guard[ner]` sonrası)

`find_names()` artık bir `min_score` eşiği uyguluyor (varsayılan 0.8) — aşağıdaki sayılar bu
filtre açıkken/kapalıyken:

| Filtre                        | TP | FP | FN | Precision | Recall |
|--------------------------------|----|----|----|-----------|--------|
| `min_score=0.0` (eski davranış) | 15 | 4  | 0  | 0.79      | 1.00   |
| `min_score=0.8` (varsayılan)    | 14 | 0  | 1  | **1.00**  | 0.93   |

**Kök sebep analizi:** Eski haliyle 4 yanlış pozitifin dördü de aynı sebepten geliyordu — NER
modeli, bir e-posta adresinin local-part'ındaki isim parçasını (`ahmet.yilmaz@...` içindeki
`"yilmaz"` gibi) ayrı bir kişi ismi zannediyordu. Bu hatalı tahminlerin güven skorunu (0.54-0.78)
doğru örneklerin skoruyla (0.88-1.00) karşılaştırınca net bir ayrım bulduk ve `min_score=0.8`
varsayılanını buna göre seçtik — bu **değer tahmin edilmedi, gerçek ölçümle belirlendi.**

Bu **ücretsiz bir kazanım değil, gerçek bir precision/recall ödünleşmesi:** bazı düşük güvenli
ama doğru tahminler de (ör. gürültülü bağlamda "Ahmet") eşik altında kalıp kaçırılabiliyor —
`min_score=0.0` ile eski (daha yüksek recall, daha düşük precision) davranışa dönülebilir.
`redact(use_ner=True)` çağrısında bu FP'ler zaten overlap-çözümlemesiyle sızmıyordu
(`tests/test_ner.py::test_redact_use_ner_does_not_leak_name_fragment_from_email`), ama
`find_names()`'i tek başına kullananlar için gerçek bir iyileştirme.

## Dış doğrulama (NER, gerçek Wikipedia cümleleri)

El-yapımı korpustaki NER sayısı bizim yazdığımız, kolay/kanonik cümlelerden geliyor
(`"Ahmet Yılmaz İstanbul'da oturuyor."` gibi) — bu, gerçek dünya performansını olduğundan iyi
gösterebilir. Bunu bağımsız şekilde sınamak için **savasy/bert-base-turkish-ner-cased modelinin
eğitiminde kullanılmayan**, halka açık bir veri setini ([turkish-nlp-suite/turkish-wikiNER
test split](https://huggingface.co/datasets/turkish-nlp-suite/turkish-wikiNER), 1000 gerçek
Türkçe Wikipedia cümlesi, cc-by-sa-4.0) indirip çalıştırdık.

Çalıştırmak için: `python3 benchmarks/external_wikiner_eval.py` (`pip install pandas pyarrow`
gerektirir — proje bağımlılığı değil, sadece bu tek script için).

| Yöntem (iyelik eki normalize edilmiş)     | TP  | FP  | FN  | Precision | Recall |
|---------------------------------------------|-----|-----|-----|-----------|--------|
| `min_score=0.0` (eski davranış)              | 846 | 557 | 402 | 0.60      | 0.68   |
| `min_score=0.8` (varsayılan)                 | 796 | 315 | 452 | **0.72**  | 0.64   |

Aynı ödünleşme burada da görünüyor: 1000 gerçek cümlede eşik precision'ı 0.60'tan 0.72'ye
çıkarıyor, recall'u 0.68'den 0.64'e düşürüyor. Daha yüksek recall istersen `min_score`'u
düşür (ör. `redact(text, use_ner=True, ner_min_score=0.5)`).

**Kalan farkın (hâlâ el-yapımı setin altında) asıl sebebi:** nadir/yabancı/kurgusal özel
isimlerde subword tokenization kesilmesi — ör. `"Lichtenthal"` → `"Li"`, `"Jiraiya"` → `"iya"`/
`"J"`, `"shinigami"` → `"sh"`. Model, günlük/yaygın isimlerde güçlü (el-yapımı setteki gibi),
ama alışılmadık/yabancı kökenli özel isimlerde zayıflıyor; `min_score` bu tür kırık/düşük-güvenli
parçaların çoğunu eler ama kategori-karıştırma hatalarını (ör. `"Jiraiya"`'yı %95 güvenle ORG
sanması) düzeltmez — bu **gerçek, somut bir sınırlama**, hand-crafted test setinin tek başına
göstermediği bir şey.

## Performans

`benchmarks/run.py` ayrıca `redact()`'i bu makinede 3600 kez çalıştırıp ortalama süreyi ölçer:

- **~0.006 ms / çağrı** (yaklaşık 7.5M karakter/saniye) — regex+checksum tabanlı tespit,
  üretim trafiğinde sorun oluşturmayacak kadar hızlı. ([ClickHouse'un guardrail latency
  tablosunda](https://clickhouse.com/resources/engineering/llm-guardrails) "regex/schema"
  kategorisi "sub-millisecond" olarak sınıflandırılıyor — bizim ölçümümüz bu kategoriyle uyumlu.)
- NER (`use_ner=True`) açıldığında gerçek bir model inference'ı çalıştığı için bu rakamlar
  geçerli değil; o mod milisaniyeler-onlarca milisaniye mertebesinde olması beklenir.

## Not

- Telefon'daki 3 yanlış pozitif bilinçli olarak test setine eklendi: `4455667788`,
  `3344556677`, `2233445566` gibi, alan kodu aralığına ([2-5]xx) denk gelen rastgele 10
  haneli referans/ürün kodları telefon zannediliyor. README'deki "Bilinen sınırlamalar"
  bölümünde de belirtilmiştir.
- TC no/IBAN'da yanlış pozitif riski var ama bu sette rastlanmadı (checksum rastlantısallığı
  istatistiksel olarak ~%1 ihtimalli).
- API key distractor'ları (UUID, SHA256 hash, rastgele base64) hiçbirini tetiklemedi —
  prefix'li/yapısal format eşleştirmenin false-positive riskini düşük tuttuğunu doğruluyor.
- NER sayıları `transformers`/`torch` kurulduktan sonra gerçekten ölçüldü (varsayımsal değil)
  — ama bu ağırlıklar CI'da kurulmuyor (indirme maliyeti), bu yüzden sadece yerel olarak
  doğrulandı, her push'ta otomatik ölçülmüyor.
- Katkıda bulunmak isteyenler `benchmarks/corpus.py`'a yeni etiketli örnek ekleyebilir.
