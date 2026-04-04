# 5. Diskuze, závěry a doporučení

## 5.1 Shrnutí klíčových zjištění

| # | Zjištění | KPI | Business question |
|---|---------|-----|-------------------|
| 1 | **GDR vykazuje silnou sezónnost** — v letních měsících klesá pod 60 %, v zimě se blíží 90–95 %. Solární panely pokrývají značnou část spotřeby pouze od dubna do září. | GDR | Jak moc jsou domácnosti závislé na síťové elektřině? |
| 2 | **Večerní špička (18:00–21:00) generuje nejvyšší net load** — denní profil spotřeby potvrzuje tvar kachní křivky (duck curve). Solární výroba v těchto hodinách je nulová, celá spotřeba jde ze sítě. | PLC | Jaké jsou náklady ve špičce a jak se liší podle sezóny? |
| 3 | **Oblačnost negativně koreluje se solární výrobou** — Pearsonova korelace potvrzuje inverzní vztah. Dny s oblačností nad 80 % mají solární výrobu blízkou nule bez ohledu na sezónu. | GDR | Jaké meteorologické faktory nejvíce ovlivňují solární pokrytí? |
| 4 | **Data ze senzorů obsahují ~5 % výpadků a ~0,5 % extrémních outlierů** — DQS kolísá v čase, ale průměrně se drží nad 90 %. Outliery ve spotřebě dosahují 5–15násobku normálních hodnot. | DQS | Jak spolehlivá jsou data ze senzorů? |
| 5 | **Peak Load Cost (PLC) je vysoce variabilní** — distribuce denních nákladů ve špičce má pravý chvost (skewness), což znamená, že existují dny s extrémně vysokou spotřebou ve špičce. | PLC | Lze identifikovat dny s nadprůměrnými náklady? |

## 5.2 Limity vlastního řešení

### Kvalita a pokrytí dat
- **Syntetická smart meter data:** Spotřeba a solární výroba jsou generovány z matematických modelů — nezachycují reálné vzorce chování domácností (např. vliv ceny elektřiny na chování, klimatizace v létě, dovolené).
- **Jedna lokalita:** Meteorologická data pokrývají pouze Prahu. Výsledky nelze automaticky přenést na jiné regiony s odlišným klimatem.
- **Časový rozsah 1 rok:** Nemůžeme posoudit meziroční trendy ani vliv extrémních klimatických událostí.
- **Absence reálných tarifů:** PLC používá zjednodušenou fixní cenu 5 CZK/kWh; reálná tarifní struktura je dynamická a závisí na distribuční oblasti.

### Bias a přenositelnost
- **Uniformní domácnosti:** Všechny domácnosti sdílejí stejný denní profil (liší se jen škálou). Reálná populace má heterogenní vzorce spotřeby (single vs. rodina, home office vs. dojíždění).
- **Rovnoměrné outliery:** Šum je náhodně rozložený v čase. V praxi bývají výpadky korelované (celá oblast, konkrétní výrobní série senzorů).
- **Chybí sociodemografická data:** Bez informací o typu domácnosti, počtu osob nebo velikosti panelů nelze segmentovat smysluplně.

### Technická omezení
- **DuckDB jako lokální řešení:** Pro 1000 domácností (8,76M řádků) je výkon dostatečný. Při škálování na statisíce domácností by bylo nutné přejít na distribuované řešení (Spark, cloud DWH).
- **INNER JOIN:** Záznamy bez shody v timestamp byly vyloučeny — při reálném nasazení je nutné řešit časové posuny a různou granularitu zdrojů.
- **Statická EDA:** Notebook nepodporuje interaktivní filtrování; pro operativní monitoring je nutný dashboard (Tableau, Grafana).

## 5.3 Budoucnost a AI

### Kde dává smysl automatizace
- **Automatická detekce anomálií:** ML model (Isolation Forest, autoencoder) pro real-time detekci vadných senzorů namísto statického IQR prahu.
- **Predikce spotřeby:** Časové řady (Prophet, LSTM) pro předpověď net load na další den/týden — umožní optimalizaci nákupu elektřiny.
- **Dynamické KPI prahy:** Adaptivní nastavení cílových hodnot GDR a PLC podle sezóny a počasí místo fixních ročních cílů.
- **Automatizovaný ETL pipeline:** Orchestrace (Airflow, Prefect) pro denní načítání dat z API, validaci kvality a aktualizaci dashboardu.

### Rizika a kontrolní mechanismy
- **Riziko přeučení na syntetických datech:** Modely trénované na generovaných datech nemusí fungovat na reálných — nutná validace na pilotním vzorku reálných domácností.
- **Bias v doporučeních:** Pokud model systematicky podhodnocuje spotřebu určitého segmentu, může vést k chybným tarifním doporučením.
- **Black-box modely:** Pro regulované odvětví (energetika) je důležitá vysvětlitelnost — preferovat interpretovatelné modely nebo SHAP hodnoty.
- **Kontrolní mechanismy:** Monitoring driftu vstupních dat (data drift detection), pravidelný audit KPI vs. realita, human-in-the-loop pro klíčová rozhodnutí.

---

# 6. Metodika a postup

## 6.1 Workflow

### Postup práce
1. **Definice zadání a KPI** — Na základě požadavků předmětu a konzultací jsme definovali fiktivní firmu EcoHome a.s. a tři měřitelná KPI (GDR, PLC, DQS).
2. **Získání dat** — Reálná meteorologická data stažena z Open-Meteo Archive API (Praha, 2023, hodinová granularita). Syntetická smart meter data vygenerována skriptem `generate_data.py`.
3. **Integrace do DuckDB** — Oba zdroje načteny do lokální DuckDB databáze, propojeny přes `timestamp` (INNER JOIN), vytvořen analytický pohled `v_net_load`.
4. **EDA v Jupyter** — Systematická analýza podle šablony předmětu (sekce 1–8): orientace v datech, kvalita, feature engineering, 6 vizualizací navázaných na KPI.
5. **Vizualizace a dashboard** — Klíčové grafy exportovány jako PNG. Dashboard v Tableau pro interaktivní průzkum.
6. **Dokumentace** — Průvodní HTML dokument, prezentace, tento soubor.

### Replikace výsledků
```bash
# 1. Naklonovat repozitář / rozbalit archiv
# 2. Nainstalovat závislosti
pip install duckdb pandas matplotlib seaborn pyarrow requests

# 3. Vygenerovat data (stáhne počasí z API + vytvoří syntetická data)
python generate_data.py

# 4. Spustit EDA notebook
jupyter notebook EDA_EcoHome.ipynb
# Kernel → Restart & Run All
```

## 6.2 Rozdělení rolí

| Člen týmu | Role | Odpovědnost |
|-----------|------|-------------|
| [Člen 1]  | Data engineer | Získání dat (API, generátor), DuckDB integrace, ETL pipeline |
| [Člen 2]  | Data analyst | EDA, vizualizace, interpretace KPI, Jupyter notebook |
| [Člen 3]  | Architekt & dokumentace | Návrh architektury, HTML dokument, prezentace, data governance |

> **Poznámka:** Doplňte jména a upravte podle skutečného rozdělení práce v týmu.

## 6.3 Nástroje a prostředí

| Nástroj | Verze | Účel |
|---------|-------|------|
| Python | 3.12 | Hlavní programovací jazyk |
| DuckDB | 1.x | Lokální analytická databáze (DWH) |
| Pandas | 3.x | Manipulace s tabulkovými daty |
| Matplotlib | 3.x | Tvorba grafů |
| Seaborn | 0.13+ | Statistické vizualizace |
| Jupyter Notebook | — | Interaktivní prostředí pro EDA |
| Tableau | — | Interaktivní dashboard |
| draw.io | — | Architektonické diagramy |
| Open-Meteo API | Archive v1 | Zdroj reálných meteorologických dat |

**Konvence:**
- Kód komentován česky, každý řádek.
- Názvy sloupců v databázi: `snake_case`, bez diakritiky.
- Grafy: vždy titulek, popsané osy s jednotkami, legenda, mřížka.
- Výstupní soubory grafů: `output/graf_XX_nazev.png`.

## 6.4 AI použití

### Jak bylo AI využito
- **Návrh struktury projektu:** Claude Code pomohl navrhnout architekturu datové platformy, definovat KPI a vytvořit kostru EDA notebooku.
- **Generování kódu:** Kód pro `generate_data.py` (generátor dat) a `EDA_EcoHome.ipynb` (EDA notebook) byl vytvořen s asistencí AI a následně zkontrolován a upraven týmem.
- **Diagramy:** Architektonické diagramy (draw.io XML) vytvořeny s asistencí AI.
- **Konzultace:** AI sloužilo jako konzultant pro otázky ohledně DuckDB SQL, pandas API, vizualizačních best practices a interpretace výsledků.

### Klíčové prompty
1. *„Vygeneruj kód pro Jupyter Notebook EDA podle školní šablony s 6 grafy napojenými na KPI (GDR, PLC, DQS)."*
2. *„Napiš Python skript, který stáhne počasí z Open-Meteo API a vygeneruje syntetická smart meter data s kachní křivkou, korelací s oblačností a záměrným šumem."*
3. *„Navrhni high-level architekturu datové platformy a data lineage diagram ve formátu draw.io XML."*

### Kontrola faktů a ověření
- **Open-Meteo API:** Ověřeno, že API vrací korektní data pro zadané souřadnice a období (porovnání s ČHMÚ).
- **Syntetická data:** Distribuce spotřeby a solární výroby vizuálně porovnány s veřejně dostupnými profily (CEPS, ERÚ).
- **Kód:** Každá buňka notebooku spuštěna a výstupy zkontrolovány manuálně.
- **KPI definice:** Ověřeny proti zadání předmětu a přednáškám.

### Co bylo převzato a jak ověřeno
| Zdroj | Co bylo převzato | Jak ověřeno |
|-------|-----------------|-------------|
| AI (Claude Code) | Kostra kódu, struktury, diagramy | Manuální review, spuštění, úpravy týmem |
| Open-Meteo API | Meteorologická data | Porovnání s ČHMÚ, kontrola rozsahů |
| Přednášky předmětu | Šablona EDA, požadavky na projekt | Přímé porovnání se zadáním |

## 6.5 Zdroje

### Data
- **Open-Meteo Archive API** — https://open-meteo.com/ — historická meteorologická data (CC BY 4.0)
- **Syntetická data** — vlastní generátor `generate_data.py` (popsán v sekci 4 EDA notebooku)

### Dokumentace a nástroje
- **DuckDB dokumentace** — https://duckdb.org/docs/
- **Pandas dokumentace** — https://pandas.pydata.org/docs/
- **Matplotlib dokumentace** — https://matplotlib.org/stable/contents.html
- **Seaborn dokumentace** — https://seaborn.pydata.org/

### Odborné zdroje
- **Duck Curve (kachní křivka)** — California ISO, „What the duck curve tells us about managing a green grid", 2016
- **ČEPS** — https://www.ceps.cz/ — data o české elektrizační soustavě
- **ERÚ (Energetický regulační úřad)** — https://www.eru.cz/ — regulační rámec a tarifní struktury
- **Přednášky a cvičení předmětu** — Zpracování velkých dat, PEF ČZU (materiály v `data-and-info/`)
