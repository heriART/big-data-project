# Závěr semestrální práce — EcoHome a.s.

## Cíl projektu

Cílem projektu bylo navrhnout a realizovat datový produkt pro fiktivní firmu **EcoHome a.s.**, která se zabývá optimalizací energetické spotřeby domácností s fotovoltaickými panely. Projekt pokrýval celý mini-lifecycle dat — od získání zdrojových dat, přes integraci do analytické databáze, explorační analýzu (EDA) až po vizualizaci klíčových zjištění a formulaci doporučení.

## Sledovaná KPI

Definovali jsme tři měřitelné ukazatele:

| KPI | Název | Definice |
|-----|-------|----------|
| **GDR** | Grid Dependency Ratio | Míra závislosti domácností na síťové elektřině: `1 − (solární výroba / spotřeba)` |
| **PLC** | Peak Load Cost | Náklady na spotřebu ve špičkových hodinách (18:00–21:00) při ceně 5 CZK/kWh |
| **DQS** | Data Quality Score | Podíl validních (nekompromitovaných) měření ze senzorů smart meterů |

## Co jsme zjistili

1. **GDR vykazuje silnou sezónnost** — v létě klesá pod 60 % (solární panely pokrývají značnou část spotřeby), v zimě se blíží 90–95 %. Domácnosti jsou na síťové elektřině závislé především v zimních měsících.

2. **Večerní špička potvrzuje kachní křivku** — mezi 18:00 a 21:00 je net load nejvyšší, protože solární výroba je v těchto hodinách nulová. To je klíčový moment pro PLC a případnou optimalizaci (bateriové úložiště, posun spotřeby).

3. **Oblačnost negativně koreluje se solární výrobou** — dny s oblačností nad 80 % mají solární výrobu blízkou nule bez ohledu na roční období. Meteorologická data jsou proto klíčová pro predikci GDR.

4. **Data ze senzorů obsahují ~5 % výpadků a ~0,5 % extrémních outlierů** — DQS se průměrně drží nad 90 %, ale kolísá v čase. Outliery ve spotřebě dosahují 5–15násobku normálních hodnot a vyžadují filtraci.

5. **PLC je vysoce variabilní** — distribuce denních špičkových nákladů má výrazný pravý chvost, což znamená, že existují dny s extrémně vysokou spotřebou ve špičce, na které je třeba se připravit.

## Použitá data a nástroje

- **Reálná meteorologická data** — hodinová data pro Prahu za rok 2023 z Open-Meteo Archive API (teplota, oblačnost, srážky, vítr, solární iradiace).
- **Syntetická smart meter data** — 1 000 domácností × 8 760 hodin = 8,76 milionu záznamů, generováno skriptem `generate_data.py` s realistickými vzory (kachní křivka, sezónnost, korelace s počasím, záměrný šum a výpadky).
- **DuckDB** — lokální analytická databáze propojující oba zdroje přes `timestamp` (view `v_net_load`).
- **Python** (pandas, matplotlib, seaborn) v Jupyter notebooku pro EDA a vizualizace.

## Limity řešení

- **Syntetická data** nezachycují reálné vzorce chování domácností (vliv ceny elektřiny, dovolené, klimatizace).
- **Jedna lokalita** (Praha) — výsledky nelze automaticky přenést na jiné regiony.
- **Časový rozsah 1 rok** — nelze posoudit meziroční trendy ani vliv extrémních klimatických událostí.
- **Uniformní domácnosti** — všechny sdílejí stejný denní profil, liší se jen škálou. Reálná populace je heterogenní.
- **Zjednodušený tarif** — PLC používá fixní cenu 5 CZK/kWh; reálná tarifní struktura je dynamická.

## Doporučení a budoucnost

- **Predikce spotřeby** pomocí časových řad (Prophet, LSTM) pro optimalizaci nákupu elektřiny.
- **Automatická detekce anomálií** (Isolation Forest, autoencoder) pro real-time monitoring senzorů.
- **Dynamické KPI prahy** — adaptivní cílové hodnoty GDR a PLC podle sezóny a aktuálního počasí.
- **Škálování** — při přechodu na statisíce domácností by bylo nutné přejít z lokálního DuckDB na distribuované řešení (Spark, cloud DWH).
- **Interaktivní dashboard** (Tableau, Grafana) pro operativní monitoring namísto statických grafů v notebooku.

## Metodika a AI

Projekt byl realizován s využitím generativního AI (Claude Code) jako konzultanta a asistenta pro generování kódu, návrh architektury a review EDA. Veškerý kód byl zkontrolován a upraven týmem. Reálná meteorologická data byla ověřena porovnáním s ČHMÚ, syntetická data vizuálně porovnána s veřejně dostupnými profily (CEPS, ERÚ).

---

*Semestrální práce — Zpracování velkých dat, PEF ČZU, letní semestr 2026*
