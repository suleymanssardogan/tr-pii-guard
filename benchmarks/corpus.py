"""Small, hand-labeled Turkish test corpus for measuring detector precision/recall.

Not a large statistically rigorous benchmark -- a transparent, honest sample
covering common formats plus a few deliberately tricky distractors (invalid
checksums, PII-shaped non-PII numbers) so the false-positive/negative rate is
visible rather than hidden. See benchmarks/run.py and BENCHMARK.md.

Each case lists the exact substrings each detector SHOULD return for `text`.
An empty list means "nothing of this type should be found here".
"""

CASES = [
    {
        "text": "Müşteri TC no 10000000146 ile kayıtlı.",
        "tc_no": ["10000000146"],
        "iban": [],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "TC kimlik numaram 12345678950, lütfen kontrol edin.",
        "tc_no": ["12345678950"],
        "iban": [],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "Sipariş numarası 12345678901 ile takip edebilirsiniz.",
        "tc_no": [],  # bozuk checksum, TC no DEĞİL
        "iban": [],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "Fatura tutarı 98765432199 TL oldu.",
        "tc_no": [],  # bozuk checksum, TC no DEĞİL
        "iban": [],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "IBAN'ım TR33 0006 1005 1978 6457 8413 26, ödeme yapabilirsiniz.",
        "tc_no": [],
        "iban": ["TR33 0006 1005 1978 6457 8413 26"],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "Hesap no TR630012345678901234567890 şeklindedir.",
        "tc_no": [],
        "iban": ["TR630012345678901234567890"],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "IBAN TR33 0006 1005 1978 6457 8413 27 yanlış görünüyor.",
        "tc_no": [],
        "iban": [],  # son hane bozuk, geçerli IBAN DEĞİL
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "Beni 0532 123 45 67 numarasından arayabilirsiniz.",
        "tc_no": [],
        "iban": [],
        "telefon": ["0532 123 45 67"],
        "eposta": [],
    },
    {
        "text": "+90 212 444 55 66 müşteri hizmetleri hattı.",
        "tc_no": [],
        "iban": [],
        "telefon": ["+90 212 444 55 66"],
        "eposta": [],
    },
    {
        "text": "Acil durumda (0532)1234567 numarasını kullanın.",
        "tc_no": [],
        "iban": [],
        "telefon": ["(0532)1234567"],
        "eposta": [],
    },
    {
        "text": "Ofis telefonu: 0212-444-5566",
        "tc_no": [],
        "iban": [],
        "telefon": ["0212-444-5566"],
        "eposta": [],
    },
    {
        "text": "Numaram 5321234567, kaydedin.",
        "tc_no": [],
        "iban": [],
        "telefon": ["5321234567"],
        "eposta": [],
    },
    {
        "text": "E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": ["ahmet.yilmaz@example.com"],
    },
    {
        "text": "İletişim: ayse.demir+is@sirket.com.tr adresinden ulaşın.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": ["ayse.demir+is@sirket.com.tr"],
    },
    {
        "text": "Bugün hava çok güzel, dışarı çıkalım.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
    },
    {
        "text": "Fiyat 150 TL, kargo 3 gün sürer.",
        "tc_no": [],
        "iban": [],
        "telefon": [],
        "eposta": [],
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
    },
    {
        # Bilinen sınırlama: rastgele 10 haneli, telefon GİBİ görünen bir referans
        # kodu -- alan kodu aralığı [2-5]xx'e denk gelirse yanlış pozitif verir.
        "text": "Rastgele referans kodu: 4455667788",
        "tc_no": [],
        "iban": [],
        "telefon": [],  # gerçek telefon DEĞİL -- detector'ın yanlış pozitif verip vermediğini ölçer
        "eposta": [],
    },
]
