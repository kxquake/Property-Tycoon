# Architecture

## Overview

Property Tycoon is a local Python/Pygame desktop application. JSON files define the
board and event decks; PNG files provide the board, menus, instructions and tokens.
State lives in Python objects/dictionaries during a session. There is no web
backend, account system, database, network multiplayer or save/load layer.

The publication pass retains this architecture, with targeted fixes recorded in
`CHANGES.md`; it does not redesign the game or UI.

## Launch and runtime flow

```text
property_tycoon.launch() -> home.py
  -> Full / Abridged mode, instructions
  -> menu2.load_menu()
       -> human-player count + token choices + one computer player
       -> main.main_game_loop(players, mode, time limit)
            -> input -> take_turn() -> rule/state changes -> screen redraw
            -> nested help, properties, auction, building and sale interfaces
            -> endgame / timed asset comparison -> winner popup
```

`python -m property_tycoon` launches the existing `home.py` screen. `menu2.py` can start player setup
directly, but skips the home/mode selection screen. `main.py` is the coordinator,
and direct `main.py` execution now forwards to the home launcher rather than
starting a game with no players.

The original project uses flat imports and current-working-directory paths.
Modules are therefore kept together at the repository root, with `pngs/` beside
them. The new small launcher changes to that asset directory before executing
the home screen; it does not migrate or rewrite flat imports.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `property_tycoon.py` | Small launch adapter; selects the existing asset directory and opens Home |
| `home.py` | Full/abridged mode selection, validated time-limit popup and instructions |
| `menu2.py` | Human-player count, token selection, computer-player creation and game start |
| `main.py` | Main event/render loop, turn handling, jail, mode timing, UI coordination, asset totals and bankruptcy/endgame paths |
| `player.py` | Player position, balance, ownership, laps, jail state and pending choices |
| `bank.py` | Bank balance, player-bank payments and free-parking pool |
| `board.py` | JSON loading, board coordinates, help/property-list UI and an older board-drawing helper |
| `dice.py` | Dice generation, drawing and Roll button |
| `tokens.py` | Six token images and menu selection objects |
| `properties.py` | Purchases, ownership removal, rent calculation and shared UI button |
| `auction.py` | Nested auction event/render loop, bids and computer bidding |
| `cards.py` | Shuffled/rotating event decks and action dispatch |
| `ai_agent.py` | Rule-based/randomised computer buying, bidding, building and asset decisions |
| `house_hotel_popup.py` | Building interface and pending house/hotel transactions |
| `build_house_hotel_utils.py` | Colour cost categories and even-building/selling checks |
| `trade.py` | Selling buildings/properties and mortgaging UI; not online player trading |

The computer player is not a trained machine-learning model. Its decisions combine
hardcoded rules, balance/ownership checks and random choices.

## Data and state

- `board_data.json`: 40 board spaces, property groups/prices/rents, event-space
  definitions and notes containing house/hotel costs and other rule values.
- `opportunity_knocks.json` and `pot_luck.json`: card text plus action identifiers
  and values. `CardDeck` shuffles a deck, draws a card and cycles it to the back.
- `Player`: token, colour, position, balance, owned properties, colour groups,
  lap count and jail/choice flags; `is_ai` selects computer control.
- `Bank`: funds and free-parking pool.
- Board dictionaries: ownership, mortgage and building fields are read or mutated
  by game functions. Some modules separately load board data at import time.
- Main-loop flags: whose turn it is, extra turns, purchase/choice waits, open
  popups and abridged timing.

The main loop draws the board background, player tokens, dice, balances, ownership
lists and a message log. Popup functions can run their own event loops and change
display sizes before returning. Several modules initialise displays/load images
at import time; imports are not side-effect-free.

## Coupling and limitations retained

This is a shared-state, function/class-based application, not a strictly isolated
MVC design. Rule modules sometimes import `main.display_msg` inside functions;
there are circular dependencies and multiple board-data copies. These are
documented as implementation facts, not silently refactored.

Some loops have no frame-rate cap. Windows are fixed-size rather than responsive,
and return-to-menu still uses a subprocess, now with `sys.executable` and an
absolute launcher path so it retains the interpreter with Pygame installed.
The JSON files are local trusted game definitions, not a supported external input
or modding API. Fixed failures and remaining limitations are listed in
[Known issues](KNOWN-ISSUES.md).
