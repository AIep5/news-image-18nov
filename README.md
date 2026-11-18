# THE WORLD TODAY — 18 November 2026

make.fun entry for **news-image-20261118**: "Sum up 18 November's world
news in one image".

A deterministic, standard-library-only Python program that draws a
newspaper front page — masthead, dateline, lead story, five grid stories,
and an In Brief box — covering the nine biggest stories of Wednesday,
18 November 2026.

## Render

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Output: 1024×1024 PNG, ~38 KB, byte-identical across runs.

## Files

- `main.py` — the entry program
- `fontdata.py` — embedded bitmap font data (DejaVu Sans Bold + DejaVu Serif Bold)
- `BUILD-NOTES.md` — concept, news sources, render method, verification

## License

MIT
