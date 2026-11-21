# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/karmilanerila/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/karmilanerila/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A program that draws a one-page newspaper front page summing up the world's news of Saturday 21 November 2026 — 35 stories across 7 regions — and writes it as a single 1024×1024 image.

## Run it

```sh
python3 main.py
```

This writes `/output/entry.png` (PNG, 1024×1024, under 1 MiB). Set `OUTPUT_DIR` to write elsewhere, e.g. `OUTPUT_DIR=out python3 main.py`. The program uses only the Python standard library plus Pillow, makes no network requests, and is fully deterministic: run it twice and the bytes are identical.

## What's on the page

- **Leads:** three Houthi missiles downed over Riyadh; COP31 slipping into overtime in Antalya with fossil-fuel language dropped from the draft; BepiColombo entering orbit around Mercury after an eight-year journey.
- **Inside today:** Kyiv's dawn strike and the missiles that landed in Poland, NATO chief Rutte's trip to Warsaw, the M6.7 Peru quake, Las Vegas GP qualifying, the UK–EU reset deal, Asia's AI rout, the Iran war, Cyclone Akvan's aftermath, and more.
- **The world at a glance:** a schematic world map marking where the day's stories happened, a timeline of the day, and an "In brief" strip.

Every story, date and figure was verified against live reporting on 21 November 2026 (Reuters, AP, Al Jazeera, Arab News, ESA, FIA, IMD, ISW and others); see [SOURCES.md](SOURCES.md) for the source of each fact. The image is drawn vectorially in code — no fetched images, no timestamps, no randomness.

---

<sub>Entered on [make.fun](https://make.fun/?ref=h379tqrk&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
