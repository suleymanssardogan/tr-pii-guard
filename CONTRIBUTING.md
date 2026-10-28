# Katkıda Bulunma

1. Fork'la, bir branch aç.
2. `pip install -e .` ile kur.
3. Değişikliğini yap, **bir test ekle** (yeni bir detector, bir regex düzeltmesi, bir API
   değişikliği — hepsi küçük bir testle gelsin).
4. Göndermeden önce:
   ```bash
   python -m ruff check src tests
   python -m pytest tests/ -q
   ```
5. PR aç; ne değiştiğini ve neden değiştirdiğini kısaca açıkla.

## Yeni bir PII tipi eklemek

`src/tr_pii_guard/detectors.py`'a `find_<tip>(text) -> list[re.Match]` şeklinde bir fonksiyon
ekle, `redactor.py`'daki `_base_detectors`'a kaydet, `tests/test_detectors.py`'a geçerli/geçersiz
örnek testleri ekle. Format + checksum/doğrulama varsa (TC no, IBAN gibi) ikisini ayrı tut:
regex formatı yakalasın, ayrı bir `_is_valid_...` fonksiyonu doğrulasın.
