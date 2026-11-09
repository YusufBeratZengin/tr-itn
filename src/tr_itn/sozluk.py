"""Türkçe konuşma diline ait sabit sözlükler.

Bu modül yalnızca veri tutar; kural yoktur. Tüm anahtarlar küçük harflidir ve
Türkçe küçük harf kurallarına göre yazılmıştır ("İ" -> "i", "I" -> "ı").
"""

from __future__ import annotations

# --- Kardinal sayı sözleri ---------------------------------------------------

BIRLER: dict[str, int] = {
    "sıfır": 0,
    "bir": 1,
    "iki": 2,
    "üç": 3,
    "dört": 4,
    "beş": 5,
    "altı": 6,
    "yedi": 7,
    "sekiz": 8,
    "dokuz": 9,
}

ONLAR: dict[str, int] = {
    "on": 10,
    "yirmi": 20,
    "otuz": 30,
    "kırk": 40,
    "elli": 50,
    "altmış": 60,
    "yetmiş": 70,
    "seksen": 80,
    "doksan": 90,
}

YUZ = "yüz"

OLCEKLER: dict[str, int] = {
    "bin": 1_000,
    "milyon": 1_000_000,
    "milyar": 1_000_000_000,
    "trilyon": 1_000_000_000_000,
}

SAYI_SOZLERI: frozenset[str] = frozenset(
    set(BIRLER) | set(ONLAR) | {YUZ} | set(OLCEKLER)
)

# Sayı olmayan ama sayı sözüne benzeyen (ek almış) biçimler. Bunlar asla
# dönüştürülmez; `onun` -> "10'un" gibi yanlış dönüşümleri engeller.
SAYI_GIBI_TUZAKLAR: frozenset[str] = frozenset(
    {
        # "o" adılının çekimleri
        "onun", "onu", "ona", "onda", "ondan", "onunla", "onlarla",
        "onlar", "onlara", "onları", "onlardan", "onların", "onlarca",
        # "bir" adılı ve belirsizlik biçimleri
        "biri", "birini", "birine", "birinin", "birinde", "birinden",
        "birileri", "birilerini", "birimize", "biriniz", "birisi",
        "birim", "birimi", "birimin", "birimler", "birimleri",
        # "yüz" (surat) çekimleri
        "yüzü", "yüzün", "yüzüne", "yüzünü", "yüzünde", "yüzünden",
        "yüzler", "yüzleri", "yüzlerce", "yüzüyle", "yüzüme",
        # deyimleşmiş ikilemeler
        "yüzyüze", "ikinci el",  # çok sözcüklü olduğu için ayrıca bağlam kuralında
    }
)

# Deyimsel ikilemeler: dönüşüm yapılmaz.
IKILEMELER: tuple[tuple[str, ...], ...] = (
    ("yüz", "yüz"),
    ("üç", "aşağı", "beş", "yukarı"),
    ("bin", "bir", "gece"),
    ("bir", "iki"),
    ("iki", "üç"),
    ("üç", "beş"),
    ("beş", "on"),
)

# --- Sıra sayıları -----------------------------------------------------------

# Kök -> sıra eki üretimi `sayi.sira_eki` içinde yapılır; burada yalnızca
# özel (düzensiz) biçimler tutulur.
SIRA_OZEL: dict[str, int] = {
    "sıfırıncı": 0,
    "birinci": 1,
    "ikinci": 2,
    "üçüncü": 3,
    "dördüncü": 4,
    "beşinci": 5,
    "altıncı": 6,
    "yedinci": 7,
    "sekizinci": 8,
    "dokuzuncu": 9,
    "onuncu": 10,
    "yirminci": 20,
    "otuzuncu": 30,
    "kırkıncı": 40,
    "ellinci": 50,
    "altmışıncı": 60,
    "yetmişinci": 70,
    "sekseninci": 80,
    "doksanıncı": 90,
    "yüzüncü": 100,
    "bininci": 1_000,
    "milyonuncu": 1_000_000,
    "milyarıncı": 1_000_000_000,
}

# Sıra sayısından sonra gelen iyelik ekleri ("birincisi", "üçüncüsü").
SIRA_FAZLA_EKLER: frozenset[str] = frozenset(
    {"i", "si", "ü", "sü", "ıncı", "inci", "nci", "ncı"}
)

# --- Tarih -------------------------------------------------------------------

AYLAR: dict[str, int] = {
    "ocak": 1,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "ağustos": 8,
    "eylül": 9,
    "ekim": 10,
    "kasım": 11,
    "aralık": 12,
}

AY_ADLARI: dict[int, str] = {
    1: "Ocak",
    2: "Şubat",
    3: "Mart",
    4: "Nisan",
    5: "Mayıs",
    6: "Haziran",
    7: "Temmuz",
    8: "Ağustos",
    9: "Eylül",
    10: "Ekim",
    11: "Kasım",
    12: "Aralık",
}

YIL_IPUCLARI: tuple[str, ...] = ("yıl", "yılı", "yılında", "yılından", "yıllarında", "senesinde", "senesi")

# --- Para --------------------------------------------------------------------

# sözcük -> (sembol, sembol_önde_mi)
PARA_BIRIMLERI: dict[str, tuple[str, bool]] = {
    "lira": ("TL", False),
    "tl": ("TL", False),
    "dolar": ("$", True),
    "euro": ("€", True),
    "avro": ("€", True),
    "sterlin": ("£", True),
    "kuruş": ("kuruş", False),
    "sent": ("sent", False),
}

# --- Birimler ----------------------------------------------------------------

BIRIMLER: dict[str, str] = {
    "milimetre": "mm",
    "santimetre": "cm",
    "metre": "m",
    "kilometre": "km",
    "gram": "g",
    "kilogram": "kg",
    "kilo": "kg",
    "ton": "ton",
    "mililitre": "ml",
    "litre": "l",
    "saniye": "sn",
    "dakika": "dk",
    "saat": "saat",
    "gün": "gün",
    "hafta": "hafta",
    "ay": "ay",
    "yıl": "yıl",
    "derece": "°",
    "adet": "adet",
    "tane": "tane",
    "kişi": "kişi",
    "puan": "puan",
    "sayfa": "sayfa",
    "satır": "satır",
    "kere": "kere",
    "kez": "kez",
    "defa": "defa",
}

# --- Bağlam ipuçları ---------------------------------------------------------

SAAT_IPUCLARI: frozenset[str] = frozenset(
    {"saat", "saatte", "saati", "saatlerde", "toplantı", "toplantıda", "randevu", "randevuya"}
)

PARA_IPUCLARI: frozenset[str] = frozenset(
    {"fiyat", "fiyatı", "ücret", "ücreti", "tutar", "tutarı", "maliyet", "maliyeti", "bütçe", "bütçesi"}
)

SAYI_IPUCLARI: frozenset[str] = frozenset(
    {
        "sayı", "rakam", "numara", "numarası", "kod", "kodu", "sıra",
        "seviye", "puan", "skor", "yüzde", "adet", "toplam",
    }
)

# Telefon / rakam dizisi başlatan sözcükler.
RAKAM_IPUCLARI: frozenset[str] = frozenset(
    {"telefon", "telefonu", "numarayı", "numara", "numarası", "faks", "kod"}
)

# "ikinci el" gibi, sıra sayısından sonra gelince deyim oluşturan sözcükler.
SIRA_ENGEL: dict[str, frozenset[str]] = {
    "2": frozenset({"el"}),
}

#: Saat ifadesinde dakika belirten özel sözcükler.
DAKIKA_ONEKLERI: frozenset[str] = frozenset({"buçuk", "çeyrek"})

# --- Sözcük normalleştirme ---------------------------------------------------

# Girdi metninde geçebilecek ASCII karışıklıkları (ASR çıktısı).
ASCII_DUZELTME: dict[str, str] = {
    "yuzde": "yüzde",
    "yuz": "yüz",
    "uc": "üç",
    "bes": "beş",
    "alti": "altı",
    "dort": "dört",
    "yedi": "yedi",
    "sekiz": "sekiz",
    "dokuz": "dokuz",
    "yirmi": "yirmi",
    "otuz": "otuz",
    "kirk": "kırk",
    "elli": "elli",
    "altmis": "altmış",
    "yetmis": "yetmiş",
    "seksen": "seksen",
    "doksan": "doksan",
    "bin": "bin",
    "milyon": "milyon",
    "milyar": "milyar",
    "kasim": "kasım",
    "subat": "şubat",
    "agustos": "ağustos",
    "eylul": "eylül",
    "aralik": "aralık",
    "haziran": "haziran",
    "nisan": "nisan",
    "mayis": "mayıs",
    "temmuz": "temmuz",
    "ekim": "ekim",
    "ocak": "ocak",
    "mart": "mart",
    "lira": "lira",
    "dolar": "dolar",
    "kurus": "kuruş",
    "derece": "derece",
    "saat": "saat",
    "dakika": "dakika",
    "saniye": "saniye",
    "kilometre": "kilometre",
    "metre": "metre",
    "santimetre": "santimetre",
    "kilogram": "kilogram",
    "gram": "gram",
    "litre": "litre",
}

# --- Sembollerin okunuşu (ek uyumu için) -------------------------------------

#: Yazı biçimi -> okunuş. Ek, yazıya değil okunuşa göre uyumlanır:
#: "liraya" -> "TL'ye" (TL = "te-le").
SEMBOL_OKUNUS: dict[str, str] = {
    "TL": "tele",
    "$": "dolar",
    "€": "euro",
    "£": "sterlin",
    "km": "kilometre",
    "cm": "santimetre",
    "mm": "milimetre",
    "kg": "kilogram",
    "g": "gram",
    "m": "metre",
    "ml": "mililitre",
    "l": "litre",
    "sn": "saniye",
    "dk": "dakika",
    "°": "derece",
}
