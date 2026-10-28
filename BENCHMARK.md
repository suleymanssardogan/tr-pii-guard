# Doğruluk Ölçümü

`benchmarks/corpus.py`'daki 18 cümlelik, elle etiketlenmiş küçük Türkçe test setinde ölçüldü.
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

## Not

- Telefon'daki 1 yanlış pozitif bilinçli olarak test setine eklendi: `4455667788` gibi, alan
  kodu aralığına ([2-5]xx) denk gelen rastgele 10 haneli bir referans kodu telefon zannediliyor.
  README'deki "Bilinen sınırlamalar" bölümünde de belirtilmiştir.
- TC no/IBAN'da yanlış pozitif riski var ama bu küçük sette rastlanmadı (checksum rastlantısallığı
  istatistiksel olarak ~%1 ihtimalli, 18 örnekte görülmesi beklenmiyordu).
- NER (isim/adres) tespiti bu ölçüme dahil değil — `transformers`/`torch` gerektirdiği için bu
  depoda indirilip test edilmedi (bkz. ROADMAP.md).
- Katkıda bulunmak isteyenler `benchmarks/corpus.py`'a yeni etiketli örnek ekleyebilir.
