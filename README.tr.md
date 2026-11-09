# tr-itn

**Konuşma tanıma (ASR) çıktısındaki Türkçe sayıları yazı biçimine çevirir.**
`"iki bin yirmi altı"` → `2026`, `"yüzde on sekiz"` → `%18`, `"on dört otuz"` → `14:30`.
Ekler Türkçenin ünlü uyumuna göre yazılır: `"on dörtte"` → `14'te`, `"yüz elli liraya"` →
`150 TL'ye`, `"üç kilometreye"` → `3 km'ye`.

Saf Python 3.10+; **çalışma zamanında sıfır bağımlılık**. Windows, macOS ve Linux'ta aynı
şekilde çalışır.

```
$ echo "toplantı iki kasım iki bin yirmi altı saat on dört otuzda" | tr-itn
toplantı 2 Kasım 2026 saat 14:30'da
```

## Neden var?

Konuşma tanıma modelleri sayılar konusunda anlaşamıyor: kimi `14:30` yazıyor, kimi
`"on dört otuz"`. Altyazı, toplantı dökümü ve sesli bot hatlarının tek bir yazı biçimine
ihtiyacı var. Türkçede iş yalnızca sözcükleri birleştirmek değil: ek, son sözcüğün sesine göre
gelir (`"dörtte"` → `4'te`, ama `"altıda"` → `6'da`).

Bu işin bilinen aracı NVIDIA NeMo-text-processing; Pynini/OpenFST ister ve tekerlek paketi
yalnızca Linux x86_64 için var. `tr-itn` bağımlılıksız alternatif: `pip install tr-itn`,
tek satır import, derleyici yok, çalışırken ağ yok.

## Kurulum

```bash
pip install tr-itn
```

Başka hiçbir şey kurulmaz; paket yalnızca standart kütüphaneyi kullanır.

## 30 saniyelik örnek

```bash
$ tr-itn --explain <<< "yüzde on sekiz kdv"
%18 kdv

kural         güven   girdi -> çıktı
yuzde         0.98    yüzde on sekiz -> %18
```

```python
>>> from tr_itn import cevir, acikla
>>> cevir("toplantı iki kasım iki bin yirmi altı saat on dört otuzda")
"toplantı 2 Kasım 2026 saat 14:30'da"
>>> cevir("yüz elli liraya iki bin dolar")
"150 TL'ye $2000"
>>> acikla("üçüncü")[0].kural
'sira'
```

## Neleri çevirir?

| Kural | Konuşma | Yazı |
| --- | --- | --- |
| kardinal | `iki bin yirmi altı` | `2026` |
| kardinal + ek | `otuzunda`, `dörtte` | `30'unda`, `4'te` |
| ondalık | `üç virgül sıfır beş` | `3,05` |
| yüzde | `yüzde on sekiz kdv` | `%18 kdv` |
| sıra sayısı | `yüz elli üçüncü`, `ikincisi` | `153.`, `2'ncisi` |
| saat | `saat on dört otuz`, `on dört otuzda` | `saat 14:30`, `14:30'da` |
| saat (buçuk/çeyrek) | `saat üç buçuk`, `saat üç çeyrek` | `saat 3:30`, `saat 3:15` |
| tarih | `iki kasım iki bin yirmi altı` | `2 Kasım 2026` |
| tarih + ek | `iki kasımda`, `iki bin yirmi altı yılında` | `2 Kasım'da`, `2026 yılında` |
| para | `yüz elli lira`, `iki bin dolar` | `150 TL`, `$2000` |
| para + ek | `yüz elli liraya` | `150 TL'ye` |
| birim | `üç kilometreye`, `yirmi beş derece` | `3 km'ye`, `25°` |
| rakam dizisi | `sıfır beş üç iki …` ("telefon"/"numara" sonrası) | `0532…` |

Kapsam dışı: noktalama ve büyük harf geri getirme, kelime hatası düzeltme, sayıdan yazıya
çevirme (o başka bir proje).

## Belirsizlik siyaseti: emin değilse dönüştürmez

Türkçede sayı sözleri gündelik sözcüklerle çakışır. Bu yüzden varsayılan davranış temkinlidir
ve her karar açıklanabilir:

| Girdi | Çıktı | Gerekçe |
| --- | --- | --- |
| `bir gün gelecek` | değişmez | çıplak `bir` açık sayı bağlamı değil |
| `yirmi bir` | `21` | çok sözcüklü sayı içinde |
| `bir lira` | `1 TL` | para bağlamı |
| `ikinci el araba` | değişmez | deyim |
| `yüz yüze` | değişmez | deyim; çıplak `yüz` bağlam ister |
| `onun arabası` | değişmez | adıl, `on` + ek değil |
| `iki üç kişi` | değişmez | sayı değil ("iki üç" yaklaşık) |
| `on dört otuz` | değişmez | `1430` mu, saat mi belli değil |
| `on dört otuzda` | `14:30'da` | bulunma eki saat bağlamı verir |
| `üç buçuk` | değişmez | 3,5 mi 3:30 mu? |
| `üç buçuk kilo` | `3,5 kg` | birim ondalık olduğunu gösterir |

Daha agresif okuma istiyorsanız açıkça seçin:

```python
from tr_itn import cevir, Stil

cevir("bir gün gelecek", Stil(bir_baglami="gevsek"))   # "1 gün gelecek"
cevir("on dört otuz", Stil(saat_kipi=True))            # "14:30"
```

## Üç gerçek senaryo

**1. Altyazı.** ASR'den çıkmış SRT'yi sıra numarasına ve zaman damgasına dokunmadan çevir:

```python
from pathlib import Path
from tr_itn import srt_cevir

p = Path("altyazi.srt")
p.write_text(srt_cevir(p.read_text(encoding="utf-8")), encoding="utf-8")
```

```
1
00:00:01,000 --> 00:00:04,000
toplantı 2 Kasım 2026 saat 14:30'da başlıyor

2
00:00:04,500 --> 00:00:07,000
%18 kdv dahil 150 TL
```

**2. Toplantı dökümü.** Tek komut, kısaltmalar için finans sözlüğüyle:

```bash
$ tr-itn --alan ornekler/alan_finans.json ornekler/toplanti.txt
tr-itn: uyarı: 'tl' yerleşik kuralı eziyor
Merhaba, bugünkü toplantı 2 Kasım 2026 saat 14:30'da başlıyor.
...
```

**3. Sesli komut botu.** İpucu sözcüğünden sonra rakam dizisi (aşağıdaki numara uydurmadır):

```bash
$ echo "telefon sıfır beş üç iki bir iki üç dört beş altı yedi" | tr-itn
telefon 05321234567
```

Yalnız belirli bir kurala göre işlem yapacaksanız `acikla()` ile kural izlerine bakın
(örneğin tutarları alıp saatlere dokunmamak için).

## Komut satırı

```
tr-itn [DOSYA ...] [--explain] [--json]
       [--ondalik {,|.}] [--binlik {yok|nokta|virgul|bosluk}]
       [--para-adi] [--bir {siki|gevsek}] [--saat-kipi] [--rakam-dizisi]
       [--esik N] [--alan DOSYA] [--surum]
```

* Argüman yoksa ya da `-` verilirse stdin okunur; birden çok dosya sırayla işlenir.
* `--explain` kural izini, `--json` ise `{"metin": ..., "kurallar": [...]}` yazar.
* Çıkış kodları: `0` başarı, `1` okunamayan dosya / bozuk sözlük, `2` kullanım hatası.
* Hiçbir kurala uymayan metin olduğu gibi döner; metin hiçbir zaman istisna fırlatmaz.

## Python arayüzü

```python
from tr_itn import cevir, cevir_ayrintili, acikla, Stil, AlanSozlugu, srt_cevir, Akis

cevir(metin, stil=None, alan=None)           -> str
cevir_ayrintili(metin, stil=None, alan=None) -> Sonuc(metin, izler)
acikla(metin, stil=None, alan=None)          -> list[KuralIzi]
```

`KuralIzi` şu alanları taşır: `kural`, `girdi`, `cikti`, `konum` (karakter aralığı),
`guven` (0–1) ve `aciklama`.

### Akış kipi (parça parça ASR)

`Akis`, sondaki sayı ifadesini ve yarım kalmış sözcüğü tamponlar; iki parçaya bölünen sayı
tek sayı olarak çıkar:

```python
>>> a = Akis()
>>> a.besle("toplantı iki bin")
'toplantı '
>>> a.besle(" yirmi altı")
''
>>> a.bitir()
'2026'
```

### Altyazı (SRT / VTT)

Zaman damgaları, sıra numaraları ve `WEBVTT` başlığı korunur; yalnızca metin satırları çevrilir.

```python
from tr_itn import srt_cevir
yeni = srt_cevir(open("altyazi.srt", encoding="utf-8").read())
```

### Alan sözlüğü

JSON (ya da basit `anahtar: değer` YAML) dosyası varsayılanı ezer ve çıktısını sonraki
dönüşümlerden korur. Yerleşik sözcüklerle çakışma sessizce uygulanmaz, bildirilir.

```bash
$ tr-itn --alan ornekler/alan_finans.json ornekler/toplanti.txt
tr-itn: uyarı: 'tl' yerleşik kuralı eziyor
Merhaba, bugünkü toplantı 2 Kasım 2026 saat 14:30'da başlıyor.
Geçen ay %18 KDV dahil 150 TL birim fiyatla 2400 adet sattık.
```

### "Normalize ederek WER" ölçümü

```bash
$ python scripts/wer.py ornekler/wer_ornek.jsonl
kayıt        : 5
WER (ham)    : 1.000
WER (ITN)    : 0.067
fark         : +0.933
```

`ornekler/wer_ornek.jsonl` **uydurma** bir veri kümesidir; yalnızca ölçümü göstermek için var,
benchmark değildir.

## Ayarlar

| Ayar | Varsayılan | Anlamı |
| --- | --- | --- |
| `ondalik_ayirici` | `","` | ondalık ayırıcı (`3,5` / `3.5`) |
| `binlik_ayirici` | `None` | binlik ayırıcı (`2.026`, `2 026`) |
| `para_sembolu` | `True` | `150 TL` / `150 lira` |
| `bir_baglami` | `"siki"` | çıplak `bir` davranışı |
| `saat_kipi` | `False` | iki parçalı sayıları saat oku |
| `rakam_dizisi` | `False` | rakam sözlerini dizgiye çevir |
| `ay_buyuk_harf` | `True` | `2 Kasım` / `2 kasım` |
| `esik` / `ust_sinir` | `0` / `None` | bu sınırların dışındaki sayıları yazı bırak |

## Doğruluk

* `tests/vektorler/*.jsonl` içinde **305 elle doğrulanmış vektör**: 101 sayı, 60 tarih/saat,
  60 para/yüzde/birim, 40 sıra sayısı ve ek, 44 olumsuz kontrol.
* Olumsuz kontrollerde **sıfır yanlış dönüşüm** (`bir gün gelecek`, `ikinci el`, `yüz yüze`,
  `onun`, `on dört otuz`, …).
* **Gidiş-dönüş**: yazıya çevrilen 10.000 rastgele sayı geri çevrildiğinde aynı değeri verir.
* **%94 dal kapsamı**, `mypy --strict` temiz, `ruff` temiz, Linux + Windows + macOS CI.

Ölçüm (bu makine, Linux x86_64, Python 3.14, tek çekirdek):

```
girdi      : 1.00 MiB (966511 karakter)
çıktı      : 586950 karakter
süre       : 1,9–2,0 s (en iyi / 3 tur)
hız        : 0,51–0,52 MiB/s
```

`python scripts/bench.py` ile yeniden üretilebilir.

## Sınırlar (yayına almadan önce okuyun)

* Çıplak `bir` ve çıplak `yüz` varsayılan olarak çevrilmez: `bir lira`, `yüzde yüz`,
  `iki yüz` deyin ya da `bir_baglami="gevsek"` kullanın.
* `saat yirmi beş` → `20:05` okunur; "yirmi beş" saat bağlamı belirsizdir. `"üçü çeyrek geçe"`
  gibi saat deyimleri kapsam dışı.
* `üç virgül beş yüz` → `3,500` olur; ondalık kısım sayı olarak okunur.
* İyelikli tarih biçimleri (`"kasımın üçü"`) olduğu gibi bırakılır.
* `-lık`, `-ce` ekleri, üleştirme sayıları (`birer`, `ikişer`) ve harf harf okunan kısaltmalar
  desteklenmez.
* Metin UTF-8 kabul edilir; geçersiz baytlar (CLI'de) değiştirilir, hata verilmez.
* Kütüphane değer uydurmaz: yazılanı çevirir, gerisini olduğu gibi bırakır.

## Geliştirme

```bash
python -m pip install -e ".[dev]"
bash scripts/check.sh          # ruff + mypy + pytest (%85 kapsam eşiği)
```

`check.sh` yalnızca lint, tip, test ve kapsam eşiğinin hepsi geçtiğinde 0 döner. Temiz bir
klonda betik kendini kurar: `pytest`/`pytest-cov`/`ruff`/`mypy` eksikse yerel `.venv`
oluşturulur, `.[dev]` oraya kurulur ve kontroller o yorumlayıcıyla çalıştırılır. Otomatik
kurulumu kapatmak için `TR_ITN_KURULUM=0` kullanın.

## Lisans

MIT © 2026 YusufBeratZengin. Ayrıntı: [LICENSE](LICENSE).
