# Stalker

[English](README.md) · **Türkçe**

Hızlı bilgi toplama için küçük bir terminal OSINT aracı:

| Araç | Ne yapar |
|---|---|
| **IP Sorgulama** | Herhangi bir genel IPv4 / IPv6 adresi için konum, internet sağlayıcı / ASN, saat dilimi ve harita bağlantıları |
| **IP Adresimi Göster** | Genel IPv4 ve IPv6 adresiniz |
| **Telefon Numarası Bilgisi** | Ülke / bölge, operatör, saat dilimi, numara türü ve tüm standart formatlar. Tamamen çevrimdışı çalışır |
| **Kullanıcı Adı Arama** | 35 siteyi paralel olarak kontrol eder ve *bulundu / yok / belirsiz* olarak raporlar |

Arayüzün tamamı (menü, sonuçlar, yardım ve hata mesajları) **Türkçe ve İngilizce** olarak kullanılabilir.

## Kurulum

**Python 3.8+** gerekir. Windows, Linux, macOS ve Termux'ta çalışır.

```bash
git clone https://github.com/xkudcobi/stalker.git
cd stalker
pip install -r requirements.txt
python -m stalker
```

Ya da komut olarak kurun:

```bash
pip install .
stalker
```

<details>
<summary>Termux / Debian kurulumu</summary>

```bash
# Termux
pkg install git python
# Debian / Ubuntu / Kali
sudo apt install git python3 python3-pip
```
</details>

## Kullanım

### Etkileşimli menü

`python -m stalker` (veya `stalker`) komutunu argümansız çalıştırın:

```
  [1] IP Sorgulama
  [2] IP Adresimi Göster
  [3] Telefon Numarası Bilgisi
  [4] Kullanıcı Adı Arama
  [5] Dil: Türkçe (switch to English)
  [0] Çıkış
```

Her sorgudan sonra sonuçları `results/<tür>-<tarih>.json` dosyasına kaydedebilirsiniz.

### Komut satırı

```bash
stalker ip 8.8.8.8                 # bir IP adresini sorgula
stalker ip                         # kendi IP adresini sorgula
stalker myip                       # genel IPv4 / IPv6 adresini göster
stalker phone +905321234567        # telefon numarası bilgisi
stalker phone 02125551234 -r TR    # ülke kodu olmayan numara + varsayılan bölge
stalker user johndoe               # kullanıcı adı arama
stalker user johndoe --found-only  # yalnızca bulunan siteleri listele
```

Her komutta kullanılabilen seçenekler:

| Seçenek | Açıklama |
|---|---|
| `--lang en\|tr` | Arayüz dili |
| `--json` | Sonuçları JSON olarak yazdır (betikler için kullanışlı) |
| `-o DOSYA` | Sonuçları ayrıca bir JSON dosyasına kaydet |
| `--timeout SN` | İstek başına zaman aşımı (varsayılan 10) |
| `--no-color` | Renkleri kapat (`NO_COLOR` değişkeni de desteklenir) |

### Dil

Dil şu sırayla belirlenir: `--lang` parametresi → `STALKER_LANG` ortam değişkeni → menüde son yapılan seçim → sistem dili. Menüden seçilen dil `~/.config/stalker/config.json` dosyasında saklanır.

## Sonuçlar ne kadar doğru?

- **IP Sorgulama** [ipwho.is](https://ipwho.is) servisini kullanır, ulaşılamazsa [ip-api.com](https://ip-api.com)'a geçer. IP konumu yaklaşıktır: genellikle bir kişinin değil, internet sağlayıcısının konumunu gösterir.
- **Telefon Numarası Bilgisi** Google'ın [libphonenumber](https://github.com/google/libphonenumber) verisini kullanır. Bu bilgi *numaranın* kendisini tanımlar (nerede ve hangi operatöre tahsis edildiği). Bir telefonun konumunu bulamaz. Taşınan numaralarda ilk operatör görünebilir.
- **Kullanıcı Adı Arama** yalnızca site net bir yanıt verdiğinde *BULUNDU* der. Otomatik kontrolü engelleyen veya giriş isteyen siteler, elle doğrulayabilmeniz için bağlantısıyla birlikte *BELİRSİZ* olarak gösterilir.

## Geliştirme

```bash
python -m unittest discover -s tests
```

Testler çevrimdışı çalışır. Diğer kontrollerin yanında her metnin iki dilde de aynı yer tutucularla tanımlı olduğunu doğrular.

Kullanıcı adı aramasına site eklemek, [`stalker/core/username.py`](stalker/core/username.py) dosyasına tek bir `Site(...)` satırı eklemekten ibarettir.

## Sorumluluk reddi

Bu araç eğitim, yetkili güvenlik testleri ve kendi dijital ayak izinizi incelemek içindir. Yalnızca sorgulama izniniz olan veriler üzerinde kullanın ve size uygulanan yasalara uyun. Kötüye kullanımdan geliştiriciler sorumlu değildir.

## Lisans

[MIT](LICENSE)
