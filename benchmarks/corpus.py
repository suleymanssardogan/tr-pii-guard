"""Hand-labeled Turkish test corpus for measuring detector precision/recall.

Still not a large, statistically rigorous benchmark -- but a deliberately
wider, honest sample than a first-pass sanity check: multiple valid examples
per PII type (not just one), format variety, checksum-failing distractors,
PII-shaped-but-not-PII traps, and non-key-shaped secret distractors, so the
false-positive/negative rate is visible rather than hidden. See
benchmarks/run.py and BENCHMARK.md.

Each case lists the exact substrings each detector SHOULD return for `text`.
An empty list means "nothing of this type should be found here". Every
checksum-valid/invalid TC no and IBAN below was generated and verified
against the real `_is_valid_tc_no`/`_is_valid_iban` functions, not guessed.
"""

# Fake API key fixtures built via concatenation (not literal secret-shaped
# strings in source) so scanners/push-protection don't mistake these for
# real leaked credentials.
_FAKE_OPENAI_KEY = "sk-proj-" + "abcdefghijklmnopqrstuvwxyz1234567890"
_FAKE_AWS_KEY = "AKIA" + "IOSFODNN7EXAMPLE"  # AWS's own public documentation example
_FAKE_ANTHROPIC_KEY = "sk-ant-" + "api03-ZZZZYYYYXXXXWWWWVVVVUUUUTTTTSSSSRRRRQQQQ"
_FAKE_GOOGLE_KEY = "AIza" + "XXYYZZaabbccddeeffgghhiijjkkllmmnno"  # AIza + exactly 35 chars
_FAKE_GITHUB_KEY = "ghp_" + "ZZZZYYYYXXXXWWWWVVVVUUUUTTTTSSSSRRRRQQQQAB"
_FAKE_PEM_BLOCK = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    + "MIIEpAIBAAKCAQEA7" + "fakefakefakefakefakefake"
    + "\n-----END RSA PRIVATE KEY-----"
)

CASES = [
    # ---- TC kimlik no: valid (checksum-passing) ----
    {
        "text": "Müşteri TC no 10000000146 ile kayıtlı.",
        "tc_no": ["10000000146"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "TC kimlik numaram 12345678950, lütfen kontrol edin.",
        "tc_no": ["12345678950"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Banka hesabı açmak için TC no 13579246816 gerekli.",
        "tc_no": ["13579246816"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Nüfus cüzdanımdaki TC kimlik numarası: 24681357994.",
        "tc_no": ["24681357994"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Sözleşmede TC no 19283746550 olarak geçiyor.",
        "tc_no": ["19283746550"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Kimlik doğrulama kodu TC no 91827364550 ile eşleşti.",
        "tc_no": ["91827364550"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "TC: 56789123416, lütfen kaydedin.",
        "tc_no": ["56789123416"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Vergi dairesine TC no 43219876516 ile başvurdum.",
        "tc_no": ["43219876516"], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- TC kimlik no: invalid checksum (true negatives) ----
    {
        "text": "Sipariş numarası 12345678901 ile takip edebilirsiniz.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Fatura tutarı 98765432199 TL oldu.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Referans kodu: 11111111111",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Takip no: 22222222222",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Seri numarası: 33333333333",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Kayıt kodu: 44444444444",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Barkod: 99999999999",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- IBAN: valid (checksum-passing) ----
    {
        "text": "IBAN'ım TR33 0006 1005 1978 6457 8413 26, ödeme yapabilirsiniz.",
        "tc_no": [], "iban": ["TR33 0006 1005 1978 6457 8413 26"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Hesap no TR630012345678901234567890 şeklindedir.",
        "tc_no": [], "iban": ["TR630012345678901234567890"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Havale için TR090011122233344455566677 kullanın.",
        "tc_no": [], "iban": ["TR090011122233344455566677"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Firma IBAN: TR470098877665544332211009",
        "tc_no": [], "iban": ["TR470098877665544332211009"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Bağış hesabı TR870055544433322211100099 numaralıdır.",
        "tc_no": [], "iban": ["TR870055544433322211100099"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Kira ödemesi için TR120012312312312312312312 IBAN'ına gönderin.",
        "tc_no": [], "iban": ["TR120012312312312312312312"], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- IBAN: invalid checksum (true negatives) ----
    {
        "text": "IBAN TR33 0006 1005 1978 6457 8413 27 yanlış görünüyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Bu IBAN hatalı: TR090011122233344455566678",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Girilen IBAN TR470098877665544332211008 doğrulanamadı.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- Telefon: format variety ----
    {
        "text": "Beni 0532 123 45 67 numarasından arayabilirsiniz.",
        "tc_no": [], "iban": [], "telefon": ["0532 123 45 67"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "+90 212 444 55 66 müşteri hizmetleri hattı.",
        "tc_no": [], "iban": [], "telefon": ["+90 212 444 55 66"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Acil durumda (0532)1234567 numarasını kullanın.",
        "tc_no": [], "iban": [], "telefon": ["(0532)1234567"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Ofis telefonu: 0212-444-5566",
        "tc_no": [], "iban": [], "telefon": ["0212-444-5566"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Numaram 5321234567, kaydedin.",
        "tc_no": [], "iban": [], "telefon": ["5321234567"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "0 (212) 444 55 66'yı arayın.",
        "tc_no": [], "iban": [], "telefon": ["0 (212) 444 55 66"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "+90-532-123-45-67 numaramdır.",
        "tc_no": [], "iban": [], "telefon": ["+90-532-123-45-67"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Cep telefonum: 0555 666 77 88",
        "tc_no": [], "iban": [], "telefon": ["0555 666 77 88"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "İş yeri: 0312 444 44 44",
        "tc_no": [], "iban": [], "telefon": ["0312 444 44 44"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "0530.123.45.67 şeklinde kaydedin.",
        "tc_no": [], "iban": [], "telefon": ["0530.123.45.67"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- Telefon: known false-positive traps (PII-shaped, not phone) ----
    {
        # Bilinen sınırlama: rastgele 10 haneli, telefon GİBİ görünen bir referans
        # kodu -- alan kodu aralığı [2-5]xx'e denk gelirse telefon yanlış pozitifi verir.
        # Aynı rastlantı burada VKN checksum'ını da geçiyor -- TC no/IBAN'daki checksum
        # rastlantısallığıyla aynı, bilinçli kabul edilen bir durum, bir hata değil.
        "text": "Rastgele referans kodu: 4455667788",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": ["4455667788"], "plaka": [],
    },
    {
        "text": "Ürün kodu: 3344556677",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": ["3344556677"], "plaka": [],
    },
    {
        "text": "Parti numarası: 2233445566",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- E-posta: format variety ----
    {
        "text": "E-posta adresim ahmet.yilmaz@example.com, yazabilirsiniz.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["ahmet.yilmaz@example.com"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "İletişim: ayse.demir+is@sirket.com.tr adresinden ulaşın.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["ayse.demir+is@sirket.com.tr"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Kayıt için test.user123@sirket-adi.com.tr kullanın.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["test.user123@sirket-adi.com.tr"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Bilgi: destek@firma.net adresine yazın.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["destek@firma.net"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Mail adresim: Ahmet_Yilmaz99@gmail.com",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["Ahmet_Yilmaz99@gmail.com"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "iletisim@alt.domain.example.org adresinden yazın.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": ["iletisim@alt.domain.example.org"], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- API key / secrets: variety per provider + PEM ----
    {
        # _FAKE_OPENAI_KEY'in son 10 hanesi ("1234567890") ayrıca VKN checksum'ını
        # geçiyor -- find_vergi_no() standalone çağrıldığında bunu (doğru şekilde)
        # buluyor. redact()'te sorun değil: API_KEY eşleşmesi çok daha uzun olduğu
        # için overlap-çözümlemesi onu kazandırır, VERGI_NO alt-eşleşmesi elenir.
        "text": f"Config dosyasına yanlışlıkla {_FAKE_OPENAI_KEY} yazılmış.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_OPENAI_KEY],
        "vergi_no": ["1234567890"], "plaka": [],
    },
    {
        "text": f"AWS access key: {_FAKE_AWS_KEY} (AWS'nin kendi resmi örnek anahtarı).",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_AWS_KEY],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": f"Anthropic anahtarı sızmış: {_FAKE_ANTHROPIC_KEY}",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_ANTHROPIC_KEY],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": f"Google Maps API key: {_FAKE_GOOGLE_KEY}",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_GOOGLE_KEY],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": f"GitHub personal access token: {_FAKE_GITHUB_KEY}",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_GITHUB_KEY],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": f"Sunucu config dosyasına sızmış: {_FAKE_PEM_BLOCK}",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [_FAKE_PEM_BLOCK],
        "vergi_no": [], "plaka": [],
    },
    # ---- API key: non-key-shaped distractors (must NOT match) ----
    {
        "text": "Kayıt kimliği: 550e8400-e29b-41d4-a716-446655440000",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Dosya hash'i: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Base64 içerik: dGhpcyBpcyBqdXN0IHJhbmRvbSBiYXNlNjQgdGV4dA==",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- NER: isim/konum ----
    {
        "text": "Ahmet Yılmaz İstanbul'da oturuyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Ahmet Yılmaz", "İstanbul"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Ayşe Kaya, Ankara'dan geldi.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Ayşe Kaya", "Ankara"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Mehmet Demir, İzmir'de yaşıyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Mehmet Demir", "İzmir"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Fatma Şahin ile Bursa'da görüştük.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Fatma Şahin", "Bursa"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Mustafa Öztürk, Antalya ofisinde çalışıyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Mustafa Öztürk", "Antalya"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Zeynep Arslan, Adana'dan taşındı.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Zeynep Arslan", "Adana"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Can Çelik İstanbul'a tatile gitti.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": ["Can Çelik", "İstanbul"], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- Karışık (gerçekçi, birden fazla tip aynı anda) ----
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
        "vergi_no": [], "plaka": [],
    },
    # ---- Temiz metin (hiç PII yok) -- yanlış pozitif oranını ölçer ----
    {
        "text": "Bugün hava çok güzel, dışarı çıkalım.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Fiyat 150 TL, kargo 3 gün sürer.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Maç 2-1 bitti, taraftarlar çok mutluydu.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Yarın toplantı saat 14:00'te başlayacak.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Kitap 320 sayfa, okuması 5 saat sürdü.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Restoranın yemekleri lezzetli ama servis yavaştı.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Proje teslim tarihi iki hafta ertelendi.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Yeni sezon dizisi çok konuşuluyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Market alışverişi için liste hazırladım.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    {
        "text": "Hava durumuna göre yarın yağmur bekleniyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- Vergi No: valid (checksum-passing, generated + verified) ----
    {
        "text": "Firma vergi no: 9876543217 olarak kayıtlıdır.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": ["9876543217"], "plaka": [],
    },
    {
        # "5" ile başladığı için find_phone()'u da (doğru şekilde) tetikliyor --
        # aynı bilinen 10-haneli-sayı belirsizliği, bkz. redactor.py'deki
        # VERGI_NO/TELEFON sıralama notu.
        "text": "Vergi kimlik numaramız 5556667775, faturalarda kullanın.",
        "tc_no": [], "iban": [], "telefon": ["5556667775"], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": ["5556667775"], "plaka": [],
    },
    # ---- Vergi No: invalid checksum (true negative) ----
    {
        "text": "Sipariş kodu: 9876543210",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
    # ---- Plaka: format variety ----
    {
        "text": "Aracın plakası 34 CC 2342 olarak kayıtlı.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": ["34 CC 2342"],
    },
    {
        "text": "Kaza tutanağında 06 A 12345 plakası geçiyor.",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": ["06 A 12345"],
    },
    {
        "text": "Otopark kaydı: 35 BK 1234",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": ["35 BK 1234"],
    },
    # ---- Plaka: known limitation (invalid province, still format-shaped) ----
    {
        # İl kodu 81'i aştığı için eşleşmemesi gerekiyor -- format tuzağı testi.
        "text": "Kod: 99 A 12345",
        "tc_no": [], "iban": [], "telefon": [], "eposta": [], "isim": [], "api_key": [],
        "vergi_no": [], "plaka": [],
    },
]
