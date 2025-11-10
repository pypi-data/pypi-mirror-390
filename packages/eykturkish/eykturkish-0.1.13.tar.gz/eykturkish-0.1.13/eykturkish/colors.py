import os; os.system('')
from typing import Tuple
RENKSIFIRLA   = "\033[0m"
KALIN     = "\033[1m"
SOLUK = "\033[2m"
ITALIK    = "\033[3m"
ALTCIZGILI = "\033[4m"
YANIPSONEN = "\033[5m"
SIYAH          = "\033[30m"
KIRMIZI        = "\033[31m"
YESIL          = "\033[32m"
SARI           = "\033[33m"
MAVI           = "\033[34m"
MOR            = "\033[35m"
CAMGOBEGI      = "\033[36m"
BEYAZ          = "\033[37m"
PARLAK_SIYAH   = "\033[90m"
PARLAK_KIRMIZI = "\033[91m"
PARLAK_YESIL   = "\033[92m"
PARLAK_SARI    = "\033[93m"
PARLAK_MAVI    = "\033[94m"
PARLAK_MOR     = "\033[95m"
PARLAK_CAMGOBEGI = "\033[96m"
PARLAK_BEYAZ   = "\033[97m"
def renkliyazdir(renk,yazi):
    print(renk,yazi,RENKSIFIRLA)
def truecolorcode(rgb: Tuple[int, int, int]) -> str:
    """
    Bir RGB üçlüsünden (255, 105, 180) True Color ANSI kodunu oluşturur.
    """
    r, g, b = rgb
    # \033[38;2;<R>;<G>;<B>m formatı.
    return f"\033[38;2;{r};{g};{b}m"
