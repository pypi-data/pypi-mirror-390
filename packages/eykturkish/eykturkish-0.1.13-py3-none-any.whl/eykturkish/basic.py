import sys,os
def girdi(nedenilcek = ">>"):
    return input(nedenilcek)
def crosscls():
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")
def baslik(yazi):
    print(fr"----- {yazi} -----")
def ehe(): # öylesine, eğlence için
    print("ehe")
def satirbasi():
    print("\r")
def renkmodunuac():
    os.system('')
def bossatir(sayi: 1):
    for i in range(sayi):
        print()
