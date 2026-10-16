# SPDX-License-Identifier: GPL-3.0-only
#
# 1944: The Loop Master recomp, built with the cps2recomp toolkit.
# The toolkit lives in cps2recomp/ (a copy made by its tools/sync-toolkit.sh); see cps2recomp/build.mk
# for the targets (make, make run, make explore, make check, make launcher, ...).
#
# The player's ROM set is read, never changed: ROM points at a folder of the set's files or at the
# set's zip (rom/1944.zip by default).
GAME ?= 1944
CR ?= cps2recomp
ROM ?= rom

# The translators import the toolkit's own Python modules; bytecode must not be written into the toolkit
# copy (cps2recomp/), or `make check-toolkit` would think the copy was changed by hand.
export PYTHONDONTWRITEBYTECODE := 1

include $(CR)/build.mk
