"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Oleg Eremenko
email: eremenko.oleg26@gmail.com



Skript pro stažení a export výsledků voleb do Poslanecké sněmovny ČR 2017 z portálu volby.cz.

Na základě zadané URL územního celku (např. okresu) stáhne pro každou obec:
- kód obce
- název obce
- voliči v seznamu
- vydané obálky
- platné hlasy
- počet hlasů pro každou politickou stranu

Data jsou následně uložena do CSV souboru s odpovídající hlavičkou.

Spuštění:
    python main.py "https://www.volby.cz/pls/ps2017nss/ps32?..." vystup_okres.csv
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
from typing import List, Tuple

def validate_arguments(args: List[str]) -> bool:
    """
    Ověří, zda jsou zadané argumenty správné:
    - musí být zadány přesně 2 argumenty (URL a výstupní CSV soubor)
    - URL musí odkazovat na stránku územního celku na volby.cz
    - výstupní soubor musí končit na .csv

    :param args: Argumenty ze sys.argv
    :return: True pokud jsou validní, jinak False
    """
    if len(args) != 3:
        print("❌ Zadejte přesně dva argumenty: <URL> <název_souboru.csv>")
        return False
    if not args[1].startswith("https://www.volby.cz/pls/ps2017nss/ps3"):
        print("❌ První argument musí být platný odkaz na stránku územního celku z volby.cz.")
        return False
    if not args[2].endswith(".csv"):
        print("❌ Druhý argument musí být název CSV souboru končící na .csv")
        return False
    return True

def get_soup(url: str) -> BeautifulSoup:
    """
    Načte a zpracuje HTML obsah z dané URL pomocí knihovny BeautifulSoup.

    :param url: URL adresa stránky
    :return: Parsed HTML jako BeautifulSoup objekt
    """
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def get_obec_links(soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str, str]]:
    """
    Najde všechny odkazy na stránky jednotlivých obcí v územním celku.

    :param soup: HTML hlavní stránky územního celku
    :param base_url: Základní URL pro doplnění relativních odkazů
    :return: Seznam trojic (odkaz na obec, kód obce, název obce)
    """
    results = []
    for row in soup.find_all('tr'):
        cislo_td = row.find('td', class_='cislo')
        name_td = row.find('td', class_='overflow_name')
        if cislo_td and name_td:
            a = cislo_td.find('a')
            if a and a.get('href'):
                full_url = urljoin(base_url, a['href'])
                code = a.text.strip()
                name = name_td.text.strip()
                results.append((full_url, code, name))
    return results

def get_party_names(soup: BeautifulSoup) -> List[str]:
    """
    Získá názvy všech politických stran z jedné stránky obce.

    :param soup: HTML stránky jedné obce
    :return: Seznam názvů stran v pořadí, v jakém jsou uvedeny
    """
    names = []
    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            name_td = tr.find('td', class_='overflow_name')
            if name_td:
                names.append(name_td.text.strip())
    return names

def parse_obec_data(url: str) -> List[str]:
    """
    Načte volební výsledky pro jednu obec:
    - počet registrovaných voličů
    - počet vydaných obálek
    - počet platných hlasů
    - počet platných hlasů pro každou politickou stranu

    :param url: URL stránky konkrétní obce
    :return: Seznam hodnot v pořadí: [voliči, obálky, platné, hlasy pro strany...]
    """
    soup = get_soup(url)

    volici = soup.find('td', headers="sa2").text.strip().replace('\xa0', '')
    obalky = soup.find('td', headers="sa3").text.strip().replace('\xa0', '')
    platne = soup.find('td', headers="sa6").text.strip().replace('\xa0', '')

    hlasy = []

    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            name_td = tr.find('td', class_='overflow_name')
            if not name_td:
                continue

            vote_td = None
            for td in tr.find_all('td', class_='cislo'):
                headers = td.get('headers', '')
                if isinstance(headers, str):
                    headers = headers.split()
                if any(h.endswith('sa2') for h in headers):
                    vote_td = td
                    break

            if vote_td:
                vote = vote_td.text.strip().replace('\xa0', '')
                hlasy.append(vote)
            else:
                hlasy.append('') 

    return [volici, obalky, platne] + hlasy

def save_to_csv(filename: str, header: List[str], data: List[List[str]]) -> None:
    """
    Uloží výsledky do CSV souboru.

    :param filename: Název výstupního souboru
    :param header: Hlavička CSV souboru (seznam názvů sloupců)
    :param data: Vlastní datová část CSV (seznam řádků)
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

def main():
    """
    Hlavní řídicí funkce skriptu.
    - Zpracuje argumenty
    - Načte seznam obcí
    - Získá názvy stran z první obce
    - Získá a zpracuje data pro každou obec
    - Výsledky uloží do CSV
    """
    if not validate_arguments(sys.argv):
        return

    url = sys.argv[1]
    output_file = sys.argv[2]

    print("🔄 Načítám hlavní stránku...")
    main_soup = get_soup(url)
    obec_infos = get_obec_links(main_soup, url)

    if not obec_infos:
        print("❌ Žádné obce nebyly nalezeny.")
        return

    print("📋 Načítám názvy stran z první obce...")
    first_obec_soup = get_soup(obec_infos[0][0])
    party_names = get_party_names(first_obec_soup)
    header = ["code", "location", "registered", "envelopes", "valid"] + party_names

    data = []
    for i, (link, code, name) in enumerate(obec_infos, 1):
        print(f"📥 {i}/{len(obec_infos)} Zpracovávám: {name}")
        row = parse_obec_data(link)
        full_row = [code, name] + row
        data.append(full_row)

    save_to_csv(output_file, header, data)
    print(f"✅ Hotovo! Výsledky byly uloženy do souboru: {output_file}")

if __name__ == "__main__":
    main()
