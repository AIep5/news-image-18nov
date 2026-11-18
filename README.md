# news-image-18nov

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/AIep5/news-image-18nov/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/AIep5/news-image-18nov/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

THE WORLD TODAY — a newspaper front page summing up Wednesday 18 November 2026's world news in one image. Nine stories, each with its own picture and headline, so a viewer who missed the day can tell what happened from the image alone: US jets strike a missile site on Qeshm Island and Iran hits back with drones at Bahrain and Kuwait; the Kerch Bridge road span collapses; Trump, Xi and Putin meet in Shenzhen on the APEC sidelines; Mary Peltola flips Alaska's Senate seat as Democrats reach 56; Ebola cases more than double in DR Congo; and Category 5 Cyclone Xavier hits the Cook Islands — plus a short In Brief box.

A deterministic, standard-library-only Python program draws the page (masthead, dateline, lead story, five grid stories, In Brief) at 1024×1024, under 1 MiB, byte-identical across runs. No network, no randomness, no clock.

## Run it

```sh
python3 main.py
```

## Files

- `main.py` — the entry program (writes `/output/entry.png`)
- `fontdata.py` — embedded bitmap font data (DejaVu Sans Bold + DejaVu Serif Bold)

## License

MIT (see LICENSE).

---

<sub>Entered on [make.fun](https://make.fun/?ref=e8nm7bvm&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
