# Fixed failures and remaining limitations

## Fixed and regression-checked

- Empty/incomplete player setup no longer starts a game. An empty player list at
  the game-loop boundary also returns safely to the menu.
- Blank, zero and unsupported numeric time input no longer crashes the abridged
  popup. Valid positive time entry still works with mouse Play or Enter.
- The bankruptcy helper uses the real `token_colour` attribute, clears owned
  assets and returns them to the bank without its former attribute error.
- Direct `main.py` execution opens the existing home screen instead of passing
  an empty player list into the game.
- `board.draw_board()` now references the provided PNG, not a nonexistent JPEG.
- Exact-price purchases are accepted. Affordability is checked against the actual
  normal/auction price; zero/negative prices and non-purchasable spaces are rejected.
- `python -m property_tycoon` selects the correct asset directory. Running the
  launcher by absolute script path also works from another working directory.
  Return-to-menu uses the current Python interpreter and an absolute path; the old
  parent process exits cleanly when the replacement game closes.
- Board JSON loaders explicitly use UTF-8.
- AI building sales reuse the existing cost helper instead of calling a missing
  method on `Bank`.

## Original limitations not redesigned in this pass

**Bankruptcy is not a complete elimination system.** The specific attribute crash
and AI cost-lookup crash are fixed, but the original bankruptcy helper does not
remove the player from the turn list. Human debt/sale handling and full-mode
last-player-standing completion are incomplete. Repairing that requires a separate
rule/state-flow change rather than representing a one-line typo fix as a complete
bankruptcy implementation. Do not claim a full match has been certified.

Several modules load separate board dictionaries. Consistency across every card,
purchase, sale, mortgage and reset path needs broader testing. Popup state,
timed-endgame scoring, jail rules and auction corner cases are not exhaustively
validated by these focused regressions.

Some loops run uncapped and windows are fixed-size. These were not optimised or
redesigned. Legacy `home.py`/`menu2.py` direct execution still assumes the repository
working directory; use the documented launcher for working-directory independence.
There is no network multiplayer, save/load system or installer.

Python 3.12+ remains required by existing nested f-string syntax. No syntax-wide
rewrite or compatibility upgrade was performed. `requirements.txt` still contains
only Pygame 2.6.1.

## Publication/privacy notes

Team reports/administration, nested ZIPs, Git/IDE metadata, caches and the raw
recording are excluded. The current 20-second demo captures only the game surface
and has no audio track or copied workstation metadata. No credentials, emails or
contributor-directory paths were identified in the scoped retained-source scan.
PNG identity-metadata checks found no flagged patterns; artwork is unchanged.
Historical/fictional board names are game content, not contributor records.
