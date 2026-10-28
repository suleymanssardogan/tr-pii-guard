"""KVKK-odaklı veri ihlali etki özeti.

Bu bir hukuki tavsiye aracı DEĞİLDİR -- sadece hangi PII türlerinin tespit
edildiğine ve bunların bilinen kombinasyonlarına dayalı, açıklanabilir,
kural tabanlı bir teknik özet üretir. KVKK bildirim kararı için hukuk/uyum
ekibine danışılmalıdır.

Kurallar KVKK m.6 (özel nitelikli veri) kapsamına GİRMEZ -- sağlık, din,
etnik köken gibi kategoriler anahtar kelimeyle güvenilir tespit edilemez
(yanlış negatif riski çok yüksek), bu yüzden bilerek kapsam dışı tutuldu.
"""

from __future__ import annotations

from .redactor import redact, summary


def _assess_risk(counts: dict[str, int]) -> tuple[str, str]:
    tc_no = counts.get("TC_NO", 0)
    iban = counts.get("IBAN", 0)
    telefon = counts.get("TELEFON", 0)
    eposta = counts.get("EPOSTA", 0)
    isim = counts.get("ISIM", 0)

    if tc_no and (telefon or eposta or iban or isim):
        return (
            "yüksek",
            (
                "TC kimlik no, başka bir iletişim/finansal/kimlik bilgisiyle birlikte "
                "bulundu — kimlik hırsızlığı riski yüksek."
            ),
        )
    if iban:
        return "yüksek", "IBAN (finansal veri) tespit edildi."
    if tc_no:
        return "orta", "Sadece TC kimlik no tespit edildi, başka bağlam bilgisi yok."
    if telefon or eposta or isim:
        return (
            "düşük",
            "Sadece iletişim/isim bilgisi tespit edildi, kimlik numarası veya finansal veri yok.",
        )
    return "yok", "Taranan metinde desteklenen PII türlerinden hiçbiri bulunamadı."


def breach_report(
    text: str,
    use_ner: bool = False,
    types: list[str] | None = None,
    strict: bool = True,
) -> dict:
    """Metindeki PII'yi tarar, tip bazında sayım yapar ve PII tip
    kombinasyonlarına dayalı açıklanabilir bir risk seviyesi döndürür.

    Dönen dict, `summary()` gibi ham PII değeri İÇERMEZ -- loglanabilir/
    paylaşılabilir. Risk seviyeleri: "yüksek", "orta", "düşük", "yok".

    KVKK m.6 özel nitelikli veri (sağlık, din, vb.) tespiti kapsam dışıdır.
    """
    _, mapping = redact(text, use_ner=use_ner, types=types, strict=strict)
    counts = summary(mapping)
    risk_level, reason = _assess_risk(counts)
    return {"counts": counts, "risk_level": risk_level, "reason": reason}
