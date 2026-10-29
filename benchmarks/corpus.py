"""Small, hand-labeled Turkish test corpus for measuring detector precision/recall.

Not a large statistically rigorous benchmark -- a transparent, honest sample
covering common formats plus a few deliberately tricky distractors (invalid
checksums, PII-shaped non-PII numbers) so the false-positive/negative rate is
visible rather than hidden. See benchmarks/run.py and BENCHMARK.md.

Each case lists the exact substrings each detector SHOULD return for `text`.
An empty list means "nothing of this type should be found here".
"""

# Fake API key fixtures built via concatenation (not literal secret-shaped
# strings in source) so scanners/push-protection don't mistake these for
# real leaked credentials.
_FAKE_OPENAI_KEY = "sk-proj-" + "abcdefghijklmnopqrstuvwxyz1234567890"
_FAKE_AWS_KEY = "AKIA" + "IOSFODNN7EXAMPLE"  # AWS's own public documentation example

CASES = [
    {
        "text": "Müşteri TC no 10000000146 ile kayıtlı.",
        "tc_no": ["10000000146"],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "TC kimlik numaram 12345678950, lütfen kontrol edin.",
        "tc_no": ["12345678950"],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Sipariş numarası 12345678901 ile takip edebilirsiniz.",
        "tc_no": [],  # bozuk checksum, TC no DEĞİL
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Fatura tutarı 98765432199 TL oldu.",
        "tc_no": [],  # bozuk checksum, TC no DEĞİL
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "IBAN'ım TR33 0006 1005 1978 6457 8413 26, ödeme yapabilirsiniz.",
        "tc_no": [],
        "iban": ["TR33 0006 1005 1978 6457 8413 26"],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Hesap no TR630012345678901234567890 şeklindedir.",
        "tc_no": [],
        "iban": ["TR630012345678901234567890"],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "IBAN TR33 0006 1005 1978 6457 8413 27 yanlış görünüyor.",
        "tc_no": [],
        "iban": [],  # son hane bozuk, geçerli IBAN DEĞİL
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Beni 0532 123 45 67 numarasından arayabilirsiniz.",
        "tc_no": [],
        "iban": [],
        "telefon": ["0532 123 45 67"],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "+90 212 444 55 66 müşteri hizmetleri hattı.",
        "tc_no": [],
        "iban": [],
        "telefon": ["+90 212 444 55 66"],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Acil durumda (0532)1234567 numarasını kullanın.",
        "tc_no": [],
        "iban": [],
        "telefon": ["(0532)1234567"],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Ofis telefonu: 0212-444-5566",
        "tc_no": [],
        "iban": [],
        "telefon": ["0212-444-5566"],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Numaram 5321234567, kaydedin.",
        "tc_no": [],
        "iban": [],
        "telefon": ["5321234567"],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": ["ahmet.yilmaz@example.com"],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "İletişim: ayse.demir+is@sirket.com.tr adresinden ulaşın.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": ["ayse.demir+is@sirket.com.tr"],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Bugün hava çok güzel, dışarı çıkalım.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Fiyat 150 TL, kargo 3 gün sürer.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": (
            "Merhaba, ben Ahmet. Siparişim gelmedi, acil arayın: (0532)1234567 "
            "ya da 0212-444-5566. Mail: ahmet.yilmaz+siparis@gmail.com "
            "TCKN'm 10000000146, IBAN'ım TR330006100519786457841326 (boşluksuz)."
        ),
        "tc_no": ["10000000146"],
        "iban": ["TR330006100519786457841326"],
        "telefon": ["(0532)1234567", "0212-444-5566"],
        "eposta": ["ahmet.yilmaz+siparis@gmail.com"],
        # NER modeli burada "Ahmet"ı doğru buluyor, ama bilinen bir sınırlama:
        # e-posta'nın local-part'ındaki ".yilmaz" kısmını da isim zannedip
        # yanlış pozitif veriyor (overlap-çözümlemesi bunu redact()'te eler,
        # ama find_names() tek başına kullanılırsa görülür -- bu yüzden
        # burada BEKLENEN listesine eklemiyoruz, FP olarak ölçülsün).
        "isim": ["Ahmet"],
        "api_key": [],
    },
    {
        # Bilinen sınırlama: rastgele 10 haneli, telefon GİBİ görünen bir referans
        # kodu -- alan kodu aralığı [2-5]xx'e denk gelirse yanlış pozitif verir.
        "text": "Rastgele referans kodu: 4455667788",
        "tc_no": [],
        "iban": [],
        "telefon": [],  # gerçek telefon DEĞİL -- detector'ın yanlış pozitif verip vermediğini ölçer
        "eposta": [],
        "isim": [],
        "api_key": [],
    },
    {
        "text": "Ahmet Yılmaz İstanbul'da oturuyor.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": ["Ahmet Yılmaz", "İstanbul"],
        "api_key": [],
    },
    {
        "text": "Ayşe Kaya, Ankara'dan geldi.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": ["Ayşe Kaya", "Ankara"],
        "api_key": [],
    },
    {
        "text": f"Config dosyasına yanlışlıkla {_FAKE_OPENAI_KEY} yazılmış.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [_FAKE_OPENAI_KEY],
    },
    {
        "text": f"AWS access key: {_FAKE_AWS_KEY} (AWS'nin kendi resmi örnek anahtarı).",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
        "isim": [],
        "api_key": [_FAKE_AWS_KEY],
    },
]
