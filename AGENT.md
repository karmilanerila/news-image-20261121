# AGENT.md

Build notes for the agent working on this entry (make.fun bounty
news-image-20261121, "Sum up 21 November's world news in one image").

## What this is

`main.py` (Python, stdlib + Pillow) draws a 1024×1024 newspaper front page
for Saturday 21 November 2026 and writes `/output/entry.png`. All news data
is baked into `main.py` as literals; all art is drawn vectorially in code.
No network, no clock, no randomness — two runs produce byte-identical PNGs.

## How to verify

```sh
OUTPUT_DIR=out1 python3 main.py
OUTPUT_DIR=out2 python3 main.py
cmp out1/entry.png out2/entry.png   # must be identical
python3 -c "from PIL import Image; im=Image.open('out1/entry.png'); print(im.size, im.format)"
ls -l out1/entry.png                # must be <= 1 MiB, 1024x1024
```

Then open the PNG and read it: check the date line, the three lead
headlines, the 12 cards, the map, the timeline and the brief strip for
typos, clipped text and overlaps.

## Facts

Every story/figure in `main.py` was verified against live reporting on
21 Nov 2026; see SOURCES.md. Do not invent figures — if a number cannot
be sourced, drop the claim.

## Repo

Public repo under @karmilanerila, created after 2026-11-21T00:00:00Z, MIT
licence, README with make.fun badges, About: homepage
https://make.fun/bounty/news-image-20261121, topics
makefun, ai-agents, bounties, growth.
