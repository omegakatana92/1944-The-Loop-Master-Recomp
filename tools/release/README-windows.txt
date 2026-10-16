1944: The Loop Master - recomp port (Windows x64)
=================================================

A native PC port of 1944: The Loop Master (Capcom / Eighting-Raizing, 2000, CPS-2 board),
made with tmcleroy's cps2recomp (https://github.com/tmcleroy/cps2recomp) by static
recompilation. NOT affiliated with, endorsed by or sponsored by Capcom.
1944: The Loop Master is a trademark of Capcom Co., Ltd.

NO GAME FILES ARE INCLUDED. You need your own copy of the game: the arcade ROM set "1944"
(Europe, 000620), from a board you own. This archive cannot help you get one. Other regions
and revisions (1944j, 1944u, 1944d) do not work and are refused on purpose.


How to play
-----------
1. Double-click 1944-launcher.exe.
2. Choose your ROM set: point the launcher at the folder that holds the set's files, or at
   the set's .zip. It checks every file by CRC-32 before it will run.
3. Set the controls, then Play.

1944 is a one- or two-player vertical shooter: a coin starts a game (Insert coin in the
menu). In game: Esc or F1 opens the menu (save states, Insert coin, Player 2 joins, Reset,
Quit). P, O and -/= stop, step and slow the game. Everything is remappable in the launcher.


What is in here
---------------
1944.exe               the game
1944-launcher.exe      the launcher (keep it beside the game)
SDL3.dll               \
zlib1.dll               >  the runtime libraries the two programs need
libgcc_s_seh-1.dll     /   (keep them all in this folder, beside the .exe files)
libstdc++-6.dll       /
libwinpthread-1.dll  /
licenses/              the licences of the port and of everything shipped with it

Keep the .exe and .dll files together in one folder. Save states, settings and the board's
eprom are kept beside them (or wherever you run the game from).

The port is GPL-3.0; its source, and how it was made, are at
https://github.com/omegakatana92/1944-The-Loop-Master-Recomp
You can also build it yourself from that source. To play, you still need your own ROM set.
