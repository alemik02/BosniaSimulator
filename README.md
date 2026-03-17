# Saper (Minesweeper) w Python + pygame

Prosta gra "Saper" napisana w Pythonie 3.10+ z użyciem pygame. Gra obsługuje **tryb ciemny**, **skalowanie okna**, **menu poziomów** i ma **bezpieczne fallbacki** gdy brakuje grafik.

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
- `assets.py` — ładowanie obrazków z `assets/` z fallbackami.
- `board.py` — logika planszy (miny, odsłanianie, flood-fill, wygrana/przegrana).
- `ui.py` — rysowanie, skalowanie, obsługa wejścia, menu.
- `tests/` — testy jednostkowe (pytest).

## Assets (grafiki)

Domyślnie gra próbuje załadować zestaw grafik z katalogów:

- `assets/light/`
- `assets/dark/`

Oczekiwane pliki (gdy chcesz mieć ładniejszy wygląd):

- `tile.png`, `flag.png`, `mine.png`, `cover.png`, `bg.png`
- `number_1.png` ... `number_8.png`

Jeżeli nie dostarczysz plików, gra nadal będzie działać i narysuje proste kafelki i cyfry.

**Sugerowane wymiary grafiki:** 32x32 lub 64x64. Możesz użyć większych plików (np. 128x128) — gra je ładnie przeskaluje.

### Jak dodać własne grafiki

1. Utwórz folder `assets/light/` i `assets/dark/`.
2. Dodaj pliki wymienione powyżej.
3. Uruchom grę i użyj klawisza `M` albo przełącznika w menu, aby przetestować tryb ciemny.

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
