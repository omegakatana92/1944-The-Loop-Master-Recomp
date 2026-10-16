# Making a release

The release archives are built **by hand**, on a machine that has the ROM set: they hold the game's
translated code, so CI never builds or holds one. They land in `build/release/` and are uploaded to
the repository's Releases page by hand:

```sh
make                      # translate the game's code (needs rom/)
make launcher             # the launcher
tools/release/windows.sh  # build/release/1944-The-Loop-Master-windows-x64.zip
gh release create vX.Y.Z build/release/*.zip build/release/SHA256SUMS.txt --title ... --notes ...
```

| Script | Builds | What it holds |
| --- | --- | --- |
| `windows.sh` | `1944-The-Loop-Master-windows-x64.zip` | the two programs, the five DLLs they need, a `README.txt` and `licenses/` |
| `sums.sh` | `SHA256SUMS.txt` | hashes every archive in `build/release/` (run by the others) |

The zip holds **no** ROM set, no key, no BIOS and no game artwork: the player brings their own set.
`windows.sh` also checks every DLL the two programs import against a list of the ones the archive
carries, so an archive cannot go out missing one.

The Linux artifacts (a `.tar.gz` and an `.AppImage`) are not built yet. The Cyberbots port's
`tools/release/lib.sh` and `tools/release/linux.sh` are the ones to adapt for that: they build SDL 3
as a static library from a checksum-checked source and then the port against it, so the programs
need only the system's usual sound, X11/Wayland and zlib libraries.
