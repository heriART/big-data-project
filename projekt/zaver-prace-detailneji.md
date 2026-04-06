# Podrobný průvodce prezentací — EcoHome a.s.

> Tento dokument slouží jako podklad pro přípravu prezentace (10–12 min + 5 min diskuze).
> Komentáře ve formátu `>>` označují, co nezapomenout říct nahlas.

---

## SLIDE 1 — Úvod: Kdo jsme a co řešíme

### EcoHome a.s. — fiktivní firma

- Firma poskytující **chytré řízení energií** v domácnostech s fotovoltaickými panely.
- Kombinuje **meteorologická data** s **IoT smart metery** pro optimalizaci spotřeby a maximalizaci využití solární energie.
- Cílová skupina: domácnosti s vlastními solárními panely, které chtějí snížit závislost na síti a ušetřit na špičkových tarifech.

>> **Nezapomeňte říct:** "Firma je fiktivní, ale problém je reálný — s rostoucím počtem domácích FVE v ČR řeší tisíce domácností přesně tyhle otázky. Inspirovali jsme se reálným trendem decentralizace energetiky."

### Proč zrovna tohle téma?

- Energetika je doména bohatá na **senzorová data** (IoT smart metery generují záznamy každou hodinu).
- Kombinace **reálných meteo dat** + **syntetických smart meter dat** umožňuje pokrýt celý datový lifecycle.
- Téma je aktuální — kachní křivka (duck curve), solární boom, dynamické tarify.

>> **Nezapomeňte říct:** "Zvolili jsme energetiku, protože nám umožnila pracovat s časovými řadami, senzory, joinováním dvou různých zdrojů a řešit reálné business otázky — není to jen akademické cvičení."

---

## SLIDE 2 — Business otázky a KPI

### 3 hlavní otázky, na které odpovídáme:

1. **Jak moc jsou domácnosti závislé na síťové elektřině vs. vlastní solární výrobě?**
2. **Jaké jsou náklady ve večerní špičce (18:00–21:00) a jak se liší podle sezóny?**
3. **Jak spolehlivá jsou data ze senzorů smart meterů?**

### 3 KPI — proč právě tyhle?

| KPI | Název | Vzorec | Jednotka | Proč? |
|-----|-------|--------|----------|-------|
| **GDR** | Grid Dependency Ratio | `1 − (solární výroba / spotřeba)` | % | Měří, kolik elektřiny musí domácnost brát ze sítě. Čím nižší, tím víc se soláry vyplatí. |
| **PLC** | Peak Load Cost | `spotřeba ve špičce × cena/kWh` | CZK/den | Špičková elektřina je nejdražší. PLC říká, kolik domácnosti platí v nejhorších hodinách. |
| **DQS** | Data Quality Score | `validní záznamy / celkový počet` | % | Bez kvalitních dat nemůžeme nic měřit. DQS je meta-KPI — říká, jestli můžeme věřit ostatním metrikám. |

>> **Nezapomeňte říct:** "KPI jsme volili tak, aby pokrývala tři dimenze — energetickou efektivitu (GDR), finanční dopad (PLC) a spolehlivost datové infrastruktury (DQS). Každý graf v EDA je napojený minimálně na jedno KPI."

>> **Tip pro diskuzi:** Můžou se zeptat, proč zrovna 5 CZK/kWh. Odpověď: je to zjednodušení — reálná cena závisí na distributorovi a tarifu, ale pro demonstraci konceptu je fixní cena dostatečná.

---

## SLIDE 3 — Data: Odkud a jak?

### Dva zdroje dat:

**1. Reálná meteorologická data (weather)**
- Zdroj: **Open-Meteo Archive API** (licence CC BY 4.0)
- Lokalita: Praha (50.08°N, 14.44°E)
- Období: celý rok 2023, hodinová granularita
- Proměnné: teplota, oblačnost, srážky, vítr, solární iradiace
- **8 760 řádků** (365 dní × 24 hodin)

**2. Syntetická smart meter data (smart_meters)**
- Generováno vlastním skriptem `generate_data.py`
- **1 000 domácností × 8 760 hodin = 8 760 000 řádků**
- Proměnné: timestamp, household_id, spotřeba [kWh], solární výroba [kWh]

>> **Nezapomeňte říct:** "Reálná data jsme stáhli z Open-Meteo API — je to otevřená služba, kterou jsme ověřili porovnáním s daty ČHMÚ. Smart meter data jsou syntetická, protože reálná data z elektroměrů nejsou veřejně dostupná. Ale záměrně jsme do nich zanesli realistické vlastnosti."

### Jak jsou syntetická data vytvořena (a proč tak)?

| Vlastnost | Jak jsme to udělali | Proč |
|-----------|---------------------|------|
| **Kachní křivka** | Denní profil spotřeby: špička 18–21h (2.5×), ranní špička 6–9h (1.5×), noční minimum (0.4×) | Simuluje reálný vzorec spotřeby domácností — večer se vaří, topí, svítí |
| **Sezónnost** | Kosinusová modulace: vyšší spotřeba v zimě | V zimě se víc topí a svítí, v létě méně |
| **Korelace s počasím** | Solární výroba inverzně závisí na oblačnosti z reálných meteo dat | Panely vyrábí míň, když je zataženo — tohle je fyzikální fakt |
| **Variabilita** | Náhodná bazální spotřeba a velikost panelů per domácnost | Ne všechny domácnosti jsou stejné |
| **Šum a výpadky** | ~5 % NaN (výpadky senzorů), ~0.5 % extrémní outliery | Reálné senzory občas vypadnou nebo naměří nesmysl |

>> **Nezapomeňte říct:** "Data nejsou 'příliš hezká' — záměrně jsme zanesli šum, výpadky a outliery, aby EDA měla co řešit. Tohle je důležité, protože v reálu data nikdy nepřijdou čistá."

>> **Pozor na otázku:** "Proč syntetická a ne reálná?" — Reálná smart meter data z českých domácností nejsou veřejně dostupná. Syntetická data nám umožnila kontrolovat, jaké vlastnosti mají, a demonstrovat celý pipeline.

---

## SLIDE 4 — Technická architektura

### Datový tok (pipeline):

```
Open-Meteo API  ──→  real_weather.csv  ──┐
                                          ├──→  DuckDB  ──→  Jupyter notebook  ──→  Grafy + závěry
generate_data.py ──→  smart_meters.parquet ──┘       │
                                               v_net_load (VIEW = JOIN obou tabulek)
```

### Proč DuckDB?

- Lokální analytická databáze — žádný server, žádná konfigurace, jeden soubor `.duckdb`.
- Sloupce orientovaná — ideální pro agregace nad miliony řádků (SUM, AVG, GROUP BY).
- SQL rozhraní — srozumitelné, integrovatelné s Pythonem.

### Struktura databáze:

| Objekt | Typ | Řádků | Klíče |
|--------|-----|-------|-------|
| `weather` | Tabulka | 8 760 | `timestamp` |
| `smart_meters` | Tabulka | 8 760 000 | `timestamp`, `household_id` |
| `v_net_load` | VIEW | 8 760 000 | JOIN přes `timestamp` + výpočet `net_load` |

>> **Nezapomeňte říct:** "View `v_net_load` propojuje počasí a smart metery přes timestamp pomocí INNER JOIN. Přidává sloupec `net_load = spotřeba − solární výroba`, což je klíčová metrika pro PLC."

>> **Tip na otázku o škálování:** "Pro 1000 domácností DuckDB stačí (8.7M řádků se zpracuje za sekundy). Při škálování na statisíce domácností bychom přešli na distribuované řešení — Spark nebo cloud DWH (BigQuery, Snowflake)."

---

## SLIDE 5 — Kvalita dat

### Co jsme zjistili při čištění:

- **Chybějící hodnoty:** ~2.5 % ve spotřebě, ~2.5 % v solární výrobě (záměrně zanesené výpadky senzorů)
- **Outliery:** ~0.5 % extrémních hodnot ve spotřebě (5–15× normální hodnoty)
- **Žádné duplicity:** 0 duplicitních řádků, 0 duplicitních timestamp-household kombinací
- **Žádné záporné hodnoty** ve spotřebě ani solární výrobě
- **Oblačnost:** vše v rozsahu 0–100 %

### Jak jsme detekovali outliery:

- Metoda **IQR (Interquartile Range):** hodnoty mimo `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]`
- Feature `is_valid`: binární příznak, zda je záznam bez NaN a bez outlierů — základ pro DQS

>> **Nezapomeňte říct:** "Kvalita dat je u IoT projektů kritická. My víme, že šum jsme zanesli záměrně — ale v reálu byste tyhle vzorce museli odhalit bez znalosti ground truth. Proto jsme zavedli KPI DQS, které kvalitu sleduje průběžně."

---

## SLIDE 6 — Graf 1: Trend GDR po měsících

**Soubor:** `output/graf_01_gdr_trend.png`

### Co graf ukazuje:
- Line chart: GDR (%) na ose Y, měsíce 2023 na ose X.
- **V zimě (leden, prosinec): GDR ~95–97 %** — domácnosti jsou téměř plně závislé na síti.
- **V létě (červen, červenec): GDR ~47–48 %** — solární panely pokrývají přes polovinu spotřeby.
- Jasný **sezónní tvar "U"** — odpovídá fyzikální realitě (v létě víc slunce).

### Interpretace:
- Solární panely mají smysl především od dubna do září.
- V zimě je potřeba alternativní řešení (baterie, optimalizace spotřeby).
- GDR nikdy neklesne na 0 % — i v létě je spotřeba v noci plně ze sítě.

>> **Nezapomeňte říct:** "Tohle je náš hlavní graf pro KPI GDR. Vidíme, že sezónnost je dominantní faktor. Důležité je, že GDR neklesne na nulu ani v létě — solární panely prostě nevyrábí v noci, takže 100% soběstačnost bez baterií není možná."

>> **Tip:** Zmíňte, že reálný GDR by mohl být ještě variabilnější kvůli chování domácností (dovolené, klimatizace v létě).

---

## SLIDE 7 — Graf 2: Korelace oblačnosti a solární výroby

**Soubor:** `output/graf_02_oblacnost_solar.png`

### Co graf ukazuje:
- Scatter plot: oblačnost (%) na ose X, solární výroba (kWh) na ose Y.
- Barva bodů = solární iradiace (W/m²) — třetí dimenze.
- **Jasný negativní trend:** při nízké oblačnosti (0–20 %) dosahuje solární výroba až 1.6 kWh, při oblačnosti nad 80 % je téměř nulová.
- Body s vysokou iradiací (tmavší/červenější) se koncentrují vlevo dole — nízká oblačnost = vysoká iradiace.

### Interpretace:
- Oblačnost je klíčový prediktor solární výroby (a tedy i GDR).
- Dny se 100% oblačností = téměř nulová výroba bez ohledu na sezónu.
- Pro predikci GDR by stačilo sledovat předpověď oblačnosti.

>> **Nezapomeňte říct:** "Tohle potvrzuje fyzikální očekávání — čím víc mraků, tím míň solární výroby. Barevná škála ukazuje, že to koreluje i se solární iradiací. Pro firmu to znamená: pokud chce předpovídat GDR na další den, stačí jí předpověď oblačnosti."

---

## SLIDE 8 — Graf 3: Kachní křivka (Duck Curve)

**Soubor:** `output/graf_03_kachni_krivka.png`

### Co graf ukazuje:
- Bar chart: průměrný net load (kWh) podle hodiny dne (0–23).
- Barevné kódování: modrá = noc, zelená = ráno, oranžová = odpoledne, **červená = špička 18–21h**.
- **Jasný tvar kachní křivky:**
  - Noc (0–5h): nízký net load (~0.2 kWh) — minimální spotřeba.
  - Ráno (6–8h): ranní špička (~0.6–0.7 kWh) — vstávání, sprchování, vaření.
  - Den (9–17h): pokles net load (~0.25–0.35 kWh) — solární výroba kompenzuje spotřebu.
  - **Večer (18–21h): prudký nárůst na ~1.25–1.30 kWh** — solární výroba = 0, spotřeba na maximu.
  - Pozdní večer (21–23h): pokles na ~0.5 kWh.

### Interpretace:
- Večerní špička je **3–5× vyšší** než denní minimum.
- Právě v těchto hodinách solární panely nevyrábí → celá spotřeba jde ze sítě → nejvyšší náklady.
- Tohle je přesně ten problém, který řeší bateriová úložiště (přesunou přebytek z poledne do večera).

>> **Nezapomeňte říct:** "Kachní křivka je známý fenomén z kalifornské energetiky (California ISO, 2016). Naše data ho perfektně replikují. Červené sloupce ukazují, proč je PLC tak důležité — právě tady domácnosti platí nejvíc a solární panely nepomáhají."

>> **Tip:** Tohle je vizuálně nejsilnější graf. Nechte ho na slidu chvíli, ať si ho diváci prohlédnou.

---

## SLIDE 9 — Graf 4: Distribuce Peak Load Cost

**Soubor:** `output/graf_04_plc_distribuce.png`

### Co graf ukazuje:
- Histogram: denní PLC (CZK) na ose X, počet dní na ose Y.
- Cena: simulovaná **5 CZK/kWh** za špičkovou elektřinu.
- **Průměr: ~19 212 CZK/den** (za všech 1000 domácností).
- **Medián: ~19 168 CZK/den** — blízko průměru, ale distribuce je bimodální.
- Rozptyl: od ~13 000 do ~26 000 CZK/den.

### Interpretace:
- Distribuce **není normální** — má dva „hrboly" (bimodální charakter).
- Levý hrb (~13 000–14 000 CZK): letní dny, kdy je spotřeba nižší.
- Pravý hrb (~23 000–25 000 CZK): zimní dny s vysokou spotřebou.
- Existují extrémní dny s náklady přes 25 000 CZK — na ty je třeba se připravit.

>> **Nezapomeňte říct:** "Průměr a medián jsou si blízké, ale distribuce ukazuje, že existují dva režimy — léto a zima. Pro firmu to znamená: nemůžete plánovat s jedním číslem, musíte počítat se sezónností i u nákladů."

>> **Tip pro diskuzi:** "5 CZK/kWh je zjednodušení. V reálu by PLC záviselo na dynamickém tarifu — špičková cena může být i 8–10 CZK/kWh, takže reálné náklady by byly vyšší."

---

## SLIDE 10 — Graf 5: Outliery ve spotřebě (Box-plot)

**Soubor:** `output/graf_05_outliery_spotreba.png`

### Co graf ukazuje:
- Box-plot: distribuce spotřeby (kWh) podle segmentu denní doby (Noc, Ráno, Odpoledne, Špička).
- **Outliery viditelné jako body nad krabicovými diagramy** — dosahují 15–35 kWh (vs. normální hodnoty 0–2 kWh).
- Nejvíce outlierů je ve **špičce (18–21h)** — kde je spotřeba přirozeně nejvyšší, takže outlier = extrémní výkyv.
- Ráno (6–12h) má také výrazné outliery (až 21 kWh).

### Interpretace:
- Outliery odpovídají záměrně zanesenému šumu (0.5 % řádků × 5–15× normální hodnota).
- V praxi by tyto hodnoty mohly být vadné senzory nebo skutečné anomálie (např. elektrické topení na plný výkon).
- Pro výpočet KPI je nutné outliery filtrovat — jinak zkreslí GDR i PLC.

>> **Nezapomeňte říct:** "Box-plot jasně ukazuje, že outliery existují ve všech segmentech, ale jsou nejextrémnější ve špičce. V reálném nasazení bychom pro detekci použili Isolation Forest nebo autoencoder, ne jen statické IQR prahy."

---

## SLIDE 11 — Graf 6: Vývoj DQS v čase

**Soubor:** `output/graf_06_dqs_vyvoj.png`

### Co graf ukazuje:
- Line chart: DQS (%) na ose Y, týdny roku 2023 na ose X.
- Zelená linka s výplní, červená čárkovaná čára = průměr DQS (~89.5 %).
- **DQS kolísá od ~83 % do ~95 %** — v létě je vyšší, v zimě nižší.
- Tvar připomíná převrácenou verzi GDR grafu — koreluje se sezónností.

### Interpretace:
- Vyšší DQS v létě může být způsobeno tím, že solární výroba je v létě stabilnější (méně NaN).
- V zimě je víc výpadků — to odpovídá realitě (mrazy, sněhové pokrytí senzorů).
- Průměr ~89.5 % je akceptabilní, ale v některých týdnech klesá pod 85 % — to je varovný signál.

>> **Nezapomeňte říct:** "DQS je náš 'meta-KPI' — říká nám, jestli můžeme věřit ostatním metrikám. Pokud DQS klesne pod 85 %, měl by se spustit alert a někdo by měl zkontrolovat senzory."

---

## SLIDE 12 — Graf 7: Spotřeba v logaritmickém měřítku (bonusový graf)

**Soubor:** `output/graf_07_spotreba_log.png`

### Co graf ukazuje:
- Strip/swarm plot: spotřeba v logaritmickém měřítku podle segmentu denní doby.
- Logaritmické měřítko odhaluje strukturu dat, kterou lineární box-plot skrývá.
- Viditelné **vrstvy/klastry** odpovídající různým úrovním spotřeby.

### Proč je tam:
- Doplňuje graf 5 — ukazuje stejná data z jiného pohledu.
- Logaritmická škála lépe odhalí rozdíly v nižších hodnotách a outlierech současně.

>> **Tento graf je bonusový — nemusíte ho v prezentaci podrobně rozebírat, ale můžete na něj odkázat, pokud se někdo zeptá na detaily distribuce.**

---

## SLIDE 13 — Limity a co bychom udělali jinak

### Hlavní limity:

1. **Syntetická data** — nezachycují reálné chování (dovolené, klimatizace, vliv ceny na spotřebu). Všechny domácnosti sdílejí stejný denní profil, liší se jen škálou.
2. **Jedna lokalita** (Praha) — výsledky nelze přenést na jiné regiony (horské vs. nížinné oblasti mají jiný solární potenciál).
3. **1 rok dat** — nemůžeme posoudit meziroční trendy ani extrémní události.
4. **Zjednodušený tarif** — fixní 5 CZK/kWh vs. reálné dynamické tarify.
5. **INNER JOIN** — záznamy bez shody v timestamp byly vyloučeny. V praxi je nutné řešit různou granularitu zdrojů.

### Co bychom udělali jinak / co dál:

- Získat reálná data z pilotního projektu (i 10 domácností by stačilo pro validaci).
- Přidat sociodemografická data pro segmentaci (single vs. rodina, velikost panelů).
- Nasadit ML model pro predikci spotřeby na další den (Prophet, LSTM).
- Vytvořit interaktivní dashboard (Grafana/Tableau) místo statických grafů.
- Automatizovat pipeline (Airflow) pro denní aktualizaci dat.

>> **Nezapomeňte říct:** "Každý projekt má limity a je důležité je přiznat. Syntetická data jsou největší omezení — ale umožnila nám demonstrovat celý workflow od zdroje po insight. V reálném nasazení by prvním krokem byla validace na pilotním vzorku."

---

## SLIDE 14 — Závěr a shrnutí

### Co jsme udělali:
- Navrhli datový produkt pro optimalizaci energetické spotřeby domácností.
- Definovali 3 měřitelná KPI (GDR, PLC, DQS).
- Integrovali 2 datové zdroje (reálná meteo + syntetické smart metery) do DuckDB (8.76M řádků).
- Provedli systematickou EDA s 7 vizualizacemi napojenými na KPI.
- Identifikovali sezónnost, kachní křivku a datové anomálie.

### Klíčové takeaways:
1. Solární panely snižují závislost na síti hlavně **od dubna do září** (GDR klesá ze 97 % na 47 %).
2. Večerní špička (18–21h) je **3–5× dražší** než zbytek dne — bateriové úložiště by mělo největší dopad právě zde.
3. Kvalita senzorových dat je **~90 %** — akceptabilní, ale vyžaduje průběžný monitoring.

>> **Závěrečná věta:** "Ukázali jsme, že i s lokálním DuckDB, Pythonem a Jupyterem lze zpracovat téměř 9 milionů řádků a dostat z nich actionable insights. Klíčem je správná definice KPI a systematická EDA — ne jen grafy, ale interpretace."

---

## Připravené odpovědi na očekávané otázky

**Q: Proč DuckDB a ne PostgreSQL / MySQL?**
> DuckDB je analytická databáze optimalizovaná pro OLAP dotazy (agregace, GROUP BY). Nepotřebuje server, je v jednom souboru a pro naše objemy dat (8.7M řádků) je rychlejší než transakční databáze. Je to lokální alternativa k BigQuery nebo Snowflake.

**Q: Proč ne Spark / Hadoop?**
> Pro 8.7M řádků by byl Spark overkill — DuckDB to zvládne za sekundy na jednom počítači. Spark by dával smysl při stovkách milionů řádků nebo distribuovaném zpracování.

**Q: Jak ověřujete, že syntetická data jsou realistická?**
> Porovnali jsme distribuce s veřejnými profily (CEPS, ERÚ). Kachní křivka odpovídá tvarem reálným datům California ISO. Korelace solární výroby s oblačností je fyzikálně podmíněná — tu jsme nemuseli vymýšlet.

**Q: Co je kachní křivka?**
> Fenomén pojmenovaný California ISO (2016). Denní profil net load (spotřeba − solární výroba) má tvar kachny — přes den klesá díky solární výrobě, večer prudce stoupá. Problém: solární panely vyrábí, když je nejmenší poptávka.

**Q: Jak jste použili AI?**
> Claude Code jako konzultant pro návrh architektury, generování kódu (generátor dat, EDA notebook), review a dokumentaci. Vše bylo ověřeno manuálně — AI nebylo zdrojem závěrů, ale nástrojem pro urychlení práce.

**Q: Kolik dat je reálných a kolik syntetických?**
> Reálná jsou meteorologická data (Open-Meteo API, 8 760 řádků). Syntetická jsou smart meter data (8 760 000 řádků). Poměr je 1:1000, ale syntetická data jsou korelována s reálnými přes oblačnost a solární iradiaci.

---

## Checklist před prezentací

- [ ] Všechny grafy jsou čitelné i na projektoru (zkontrolovat kontrast)
- [ ] Každý člen týmu ví, které slidy prezentuje
- [ ] Máte připravené demo — spustit notebook a ukázat DuckDB dotaz naživo?
- [ ] Znáte čísla zpaměti: 8.76M řádků, 1000 domácností, GDR 47–97 %, DQS ~90 %
- [ ] Máte odkaz na GitHub repozitář: `github.com/heriART/big-data-project`
