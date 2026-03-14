# Fitnes-Sistem
Spletna aplikacija za upravljanje fitnes centra. Sistem omogoča rezervacijo terminov vadb pri različnih trenerjih, upravljanje trenerjev in pregled rezervacij.

## Funkcionalnost
Aplikacija podpira tri tipe uporabnikov:

### Uporabnik (član fitnesa):
- registracija in prijava
- pregled prostih terminov vadb
- rezervacija / prijava na termin
- pregled lastnih rezervacij
- nakup in pregled kart

### Trener:
- prijava v sistem
- pregled svojih terminov
- odpiranje prostih terminov za trening
- pregled števila prijavljenih uporabnikov na trening

### Admin:
- upravljanje trenerjev
  - dodajanje in brisanje trenerjev
- pregled podatkov o trenerjih

## Podatki o treningih
Vsak termin vsebuje:
- datum
- uro začetka in konca
- dvorano
- trenerja
- vrsto treninga
Uporabniki se lahko prijavijo samo na termine, ki jih je odprl trener.

## Tehnologije
Za projekt sva uporabili:
- Python
- SQLite baza podatkov
- HTML
- CSS

## Struktura projekta
```
model.py
  podatkovni modeli (Uporabnik, Trener, Admin, Termin)

spletni_vmesnik.py
  Bittle spletna aplikacija

view/
  HTML predloge

static/
  statične datoteke (CSS, slike)
```

## Namen projetka
Projekt je bil razvit kot študijski projekt za prikaz delovanja spletne aplikacije z uporabo Python orodja Bottle.

## Zagon aplikacije
```
pip install bottle
python spletni_vmesnik.py
```
