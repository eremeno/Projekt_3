# **Tretí projekt na Python Akademii od Engeta.**

## Popis projektu
Tento projekt slouží ke extrahování výsledků z parlamentních voleb v roce 2017. Odkaz k prohlédnutí nyjdete zde.

## Instalace knihoven
Knihovny, které jsou použity v kodu jsou uložene v souboru requiments.txt. 
Pro instalaci doporučuji použít nové virtuální prostředí a s nainstalovaným manažerem spustit následovně:
```
pip3 --version
pip install -r requirements.txt
```


## Spuštění projektu
Spuštění souboru `main.py` v rámci přík. řadku požaduje dva povinné argumenty.
```
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?..." vystup_okres.csv
```

## Ukázka projektu
Výsledky hlasování pro okres Beroun:
1. argument: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102
2. argument: vysledky_beroun.csv 

Spuštění programu:
paython main.py https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102 vysledky_beroun.csv

Průběh stahování:
Stahuji data z vybraneho URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102
Ukladam do souboru: vysledky_beroun.csv
Okoncuji main.py

Výstup: vysledky_beroun.csv
