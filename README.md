# Bośnia Simulator (Minesweeper) w Python + pygame

Prosta gra "Bośnia Simulator" napisana w Pythonie 3.10+ z użyciem pygame. Gra obsługuje **tryb ciemny**, **skalowanie okna**, **menu poziomów**, **animacje odsłaniania pól** i **muzykę w tle** z **bezpiecznymi fallbackami** gdy brakuje zasobów.

## Uruchomienie
1. Zainstaluj zależności:

```bash
python -m pip install -r requirements.txt
```

2. Uruchom grę:

```bash
python main.py
```

> ✅ Gra uruchamia się jednym poleceniem: `python main.py`.

## Struktura projektu

- `main.py` — punkt startowy aplikacji.
- `settings.py` — wczytywanie/zapisywanie ustawień (dark mode, poziom).
- `assets.py` — ładowanie obrazków i muzyki z `assets/` z fallbackami.
- `board.py` — logika planszy (miny, odsłanianie, flood-fill, wygrana/przegrana).
- `ui.py` — rysowanie, skalowanie, obsługa wejścia, menu, animacje, muzyka.
- `tests/` — testy jednostkowe (pytest).

## Główne cechy

- **Mechanika Bośnia Simulator**: odsłanianie pól, flagowanie, chord (lewo+prawo lub środkowy przycisk), flood-fill dla pustych pól.
- **Animacje**: płynne odsłanianie pól (skalowanie przez 0.3 sekundy).
- **Muzyka w tle**: automatyczne odtwarzanie muzyki z pętlą, pauza przy utracie fokusu.
- **Tryb ciemny**: przełącznik grafiki light/dark, zapis w ustawieniach.
- **Skalowanie**: okno skaluje się zachowując proporcje, kafelki zawsze kwadratowe.
- **Bezpieczeństwo**: fallbacki dla brakujących plików, brak crashów.
- **Sterowanie**: mysz + klawiatura (strzałki, ENTER, F, R, M).
- **5 poziomów**: nowicjusz do mistrza.

## Assets (grafiki i dźwięki)

Domyślnie gra próbuje załadować zestaw grafik PNG i muzyki z katalogu `assets/`. Jeżeli pliki nie istnieją, gra nadal będzie działać i narysuje proste kafelki oraz będzie grać bez muzyki.

## Ustawienia

Gra zapisuje ustawienia w `settings.json` w katalogu roboczym.

Przykładowy `settings.json`:

```json
{
  "dark_mode": false,
  "level": "uczen",
  "seed": null
}
```

## Sterowanie

- **Lewy przycisk myszy:** odkryj pole.
- **Prawy przycisk myszy:** oznacz/odznacz flagę.
- **Środkowy przycisk (lub lewo+prawy razem):** chord (odsłoń pola wokół numeru, jeśli liczba flag jest poprawna).
- **Klawisze:**
  - Strzałki — ruch kursora.
  - Enter / Spacja — odsłonięcie.
  - `F` — flaga.
  - `R` — restart.
  - `M` — przełącz tryb ciemny.

## Poziomy (domyślne wartości)

| Poziom | Wymiary | Miny |
|--------|---------|------|
| nowicjusz | 9×9 | 10 |
| uczeń | 12×12 | 20 |
| adept | 16×16 | 40 |
| ekspert | 24×16 | 99 |
| mistrz | 32×20 | 160 |

Wartości można zmienić w `settings.py` w słowniku `LEVELS`.

## Testy jednostkowe

Uruchom:

```bash
python -m pytest
```

Testy sprawdzają:
- poprawność generowania planszy (liczba min, unikalne pozycje)
- obliczanie sąsiadów
- flood fill (odsłanianie pustych)
- detekcję wygranej/przegranej

Powodzenia i miłej gry! 🎮
