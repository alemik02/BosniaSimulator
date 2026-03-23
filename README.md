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

Oczekiwane pliki:

- **Grafiki** (w `assets/light/` i `assets/dark/`):
  - `tile.png`, `cover.png`, `flag.png`, `mine.png`, `bg.png`
  - `number_1.png` ... `number_8.png`

- **Muzyka** (w `assets/`):
  - `background_music.ogg` lub `background_music.mp3` (muzyka w tle, pętla nieskończona)

**Sugerowane wymiary grafiki:** 32x32 lub 64x64. Możesz użyć większych plików (np. 128x128) — gra je ładnie przeskaluje.

### Jak dodać własne grafiki i muzykę

1. Utwórz folder `assets/light/` i `assets/dark/` dla grafik.
2. Dodaj pliki wymienione powyżej.
3. Dla muzyki, umieść `background_music.ogg` lub `.mp3` w `assets/`.
4. Uruchom grę i użyj klawisza `M` albo przełącznika w menu, aby przetestować tryb ciemny.

> ⚠️ Jeśli w trybie ciemnym brakuje jakiegoś pliku, gra użyje pliku z `light/` i przyciemni go.

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

## Lista manualnych testów akceptacyjnych

1. Uruchom grę i wybierz każdy poziom; sprawdź, że liczba min odpowiada konfiguracji.
2. Odsłoń pole — pierwsze odsłonięcie nie powoduje przegranej.
3. Oznacz flagi i użyj „chord” — sprawdź, że odsłanianie działa prawidłowo.
4. Przełącz Dark Mode (`M` lub przycisk w menu) — wszystkie grafiki się zmieniają.
5. Zmaksymalizuj okno na różnych proporcjach — kafelki i UI się skalują.
6. Uruchom bez katalogu `assets/` — gra działa z fallbackami.
7. Odsłoń pola — sprawdź animacje odsłaniania (pola skalują się płynnie przez 0.3 sekundy).
8. Sprawdź muzykę w tle — gra się automatycznie, pauzuje przy utracie fokusu okna.

---

## Dalsze pomysły (opcjonalne)

- animacje odsłaniania (jest miejsce w kodzie w `ui.py` do rozbudowy).
- dźwięki przy odkrywaniu pola i wygranej/przegranej.
- zapis statystyk / najlepszych czasów.

---

## Uwagi dla twórcy grafik

Jeżeli chcesz własne PNG:
- Użyj przezroczystego tła (alpha). Wygodniej jest pracować z kafelkami 32×32 albo 64×64.
- Ustaw style zgodnie z klasycznym Saperem (przyciski, płaskie cienie).
- Numerki: proste, czytelne, w kontrastowych kolorach.

Powodzenia i miłej gry! 🎮
