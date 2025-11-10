import string
temp = 0
def ayikla(metin: str) -> str:
    izinlichrs = set(string.printable + "!'^+%&/()=?_;,:. çöşiğü ÇÖŞİĞÜ-,*-+,0123456789\\ "); return "".join(ch for ch in metin if ch in izinlichrs)

def turkce_karakterleri_ascii_yap(metin: str) -> str:
    """
    Türkçe karakterleri ASCII eşdeğerleriyle değiştirir.

    Örnek: "ışİğüç" -> "isIguc"

    Args:
        metin (str): Dönüştürülecek metin.

    Returns:
        str: ASCII'ye dönüştürülmüş metin.
    """
    turkce_karakterler = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'U': 'U', 'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }
    
    yeni_metin = ""
    for karakter in metin:
        yeni_metin += turkce_karakterler.get(karakter, karakter)
    
    return yeni_metin

def guvenlichr(sayi):
    global temp
    """
    Güvenleştirilmiş chr


    Args:
        sayi (int): Sayı


    Returns:
        str: Karakter
    """
    try:
        temp = chr(sayi)
    except:
        try:
            temp = chr(sayi - 5)
        except:
            try:
                temp = chr(sayi + 5)
            except:
                return None
    return str(temp)
def guvenliord(karakter: str):
    global temp
    """
    Güvenleştirilmiş ord


    Args:
        karakter (str): Chr ile yada başka bişi ile üretilmiş harf


    Returns:
        int: Karakter ordu
    """
    karakter = karakter.replace(" ","")
    if karakter.isnumeric():
        return "sayı ord edilemez!"
    try:
        temp = ord(str(karakter))
    except:
        try:
          temp = ord(str(karakter[0]))
        except:
            return None
    return temp
def boom(hata, neden = ""):
    raise hata(neden)
def buyuk_harflere_cevir(metin: str) -> str:
    """
    Verilen metnin tamamını Türkçe büyük harflere dönüştürür.
    
    Args:
        metin (str): Dönüştürülecek metin.
        
    Returns:
        str: Büyük harflere dönüştürülmüş metin.
    """
    return metin.upper()

def kucuk_harflere_cevir(metin: str) -> str:
    """
    Verilen metnin tamamını Türkçe küçük harflere dönüştürür.

    Args:
        metin (str): Dönüştürülecek metin.

    Returns:
        str: Küçük harflere dönüştürülmüş metin.
    """
    return metin.lower()
def temizlevekucult(metin):
    global temp
    temp = kucuk_harflere_cevir(metin).replace(" ","").encode()
    return temp
def guvenliprint(metin = "Hello World"): # neden sen varsın plus varken
    try:
        print(metin)
    except:
        print("Guvenliprint hatası!")

def guvenliprintplus(metin = "Hello World", hizli = False):
    try:
        print(metin,flush=hizli)
    except:
        try:
            print(ayikla(metin) + " - Ayıklanarak yazıldı.", flush=hizli)
        except:
            print("guvenliprintplus hatası!")