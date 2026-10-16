# 1944: The Loop Master: progress

What is known of *1944: The Loop Master* (Europe 000620)'s memory, and what has been built on it. Every
address here is found by experiment on the running board with the toolkit's own tools
(`cps2recomp/docs/FEATURES.md`); nothing is a dump of the game's data, and no game data is written down.

## How each was found

The tools used, in the order they are reached for:

- `--menu FRAME:KEYS` drives the in-game menu with no window: at `FRAME` it opens the menu and presses the
  keys' buttons (`d` down, `a` confirm). "Insert coin" is how a coin goes in without a hand.
- `--dump-ram FRAME:FILE` writes the 64 KiB of work RAM after a frame; `--poke ADDR=BYTE` writes a byte
  every frame (a guess, to be checked); `--trace LOW-HIGH:FILE` appends a stretch of work RAM after every
  frame; `--shot-every N:PFX` writes pictures of the board.
- `cps2recomp/tools/ramfind.py` lists the addresses that held a known value in each of several dumps;
  `cps2recomp/tools/tracechanges.py` prints a trace where it changes.

1944 is a one- or two-player vertical shooter with no attract-show match to watch, so a coin has to go in
before its memory can be watched in play. Made-up play does that by itself: `--auto SEED:FROM` presses the
coin slot and Start among its buttons (roughly one frame in 96 is a coin and one in 24 is Start), so a run
gets into a real game with no feature and no hand.

## The set, and how it was identified

The port is made from MAME's `1944` — *1944: The Loop Master (Europe 000620)*, which is that set's parent
(1944 has no parent of its own). It was told apart from the other revisions by the zip's own files: the
program ROMs `nffe.03/04/05` and the key's CRC-32 (`5f22140e`) are the European ones (the Japanese set uses
`nffj.*`, the American `nffu.*`), while the graphics and QSound ROMs (`nff.13m` … `nff.20m`, and `nff.11m`,
`nff.12m`) are shared by all of them. Booting the port with it shows the board's own
European-territory warning, which is the last confirmation.

`games/1944/game.cfg` lists every file with its CRC-32; the port checks them one by one, and **only this
revision is accepted**.

## Verified

- `make check`: the translated 68000 does what the interpreter does, and two runs of the same input are
  alike (3000 frames).
- `recompz80`: 3536 instructions of the sound ROM's fixed part, **0 left to the interpreter**.
- A 60 000-frame run of made-up play reaches a real game; at its end **0 instructions of the 68000** had no
  translation (about 480 frames a second on this machine). Two instructions in the Z80's *banked* ROM — past
  the first 0x8000, which the toolkit does not translate ahead of time — still run in the interpreter.

## The memory so far

| Address | Size | What | How it was found |
| --- | --- | --- | --- |
| _(none yet)_ | | | |

## Features built on it (`src/`)

| Feature | Category | What it does |
| --- | --- | --- |
| _(none yet)_ | | |

## Next

- A **coin** first: the credit counter, so a game can be started with no hand (the free-play switch).
- The **player's record**: position, lives, the charge/overheat gauge, bombs.
- The **enemy and bullet tables**, for a hit-box display and a practice mode.
