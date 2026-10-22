# Property Tycoon — Python Board Game

A local, turn-based property-trading board game built with Python and Pygame.
Choose one to five human players and their tokens; an additional computer player
joins the game. The project includes full and timed abridged modes, dice movement,
property purchases, rent, auctions, building, mortgages and event cards.

## My contribution

**Role: Lead Systems Developer on a group project.** This repository contains the
group's integrated codebase, not a claim of sole authorship of every component.

## Gameplay

[Watch the 20-second gameplay demo](docs/media/gameplay.mp4).
It shows the original home screen, token selection and opening turns. The silent
capture uses scripted mouse input against this minimally repaired version; it
is not footage of a completed match.

## Run locally

Requires **Python 3.12 or newer** and a desktop display. Tested with Python 3.12
and Pygame 2.6.1 on Windows. Pygame is the only third-party runtime dependency.

From the extracted repository root:

```sh
python -m venv .venv
```

Activate the environment: `.\.venv\Scripts\Activate.ps1` in Windows PowerShell,
or `source .venv/bin/activate` on macOS/Linux. Then:

```sh
python -m pip install -r requirements.txt
python -X utf8 -m property_tycoon
```

Run the module command from the repository root. The small launcher sets the asset
directory before opening the existing home screen; you can also run
`python /path/to/property_tycoon.py` from another folder. UTF-8 mode preserves
currency text. The legacy `main.py` entry now forwards to the same home screen.
The existing game modules have not been migrated into a new package.

Select Full Game, choose the number of human players, select each token, then
press Play. The computer player's token is selected automatically. Players must
pass GO before purchasing. For Abridged Game, enter a positive time limit before
pressing Play. How To Play explains the original rules and controls.

## Project notes

- [Architecture and module map](docs/ARCHITECTURE.md)
- [Fixes and remaining limitations](docs/KNOWN-ISSUES.md)
- [Every code change](docs/CHANGES.md)
- [Packaging changes and verification](docs/PACKAGING.md)

This version contains targeted crash, purchase-validation and launch fixes, not a
gameplay/UI redesign. All three JSON files and 19 PNG assets retain their original
bytes. Reports, team administration documents, personal metadata files and the long
recording are omitted. Broader original gameplay limitations remain documented.

Focused regression checks (standard-library unittest; no extra test dependency):

```sh
python -B -m unittest discover -s tests -v
```

No blanket licence has been added over the group's code or third-party artwork;
check contribution and asset permissions before granting reuse rights.
