FREECADCMD := /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd

# Add a `test-<name>`/`view-<name>` pair here for each new furniture/<name>/
# design, following the same shape as the bed targets below.
#
# STYLE=N selects a params.py style preset (see furniture/bed/params.py's
# STYLES dict), e.g. `make test-bed STYLE=2`. Make auto-exports command-line
# variables to recipe shells, so no extra plumbing is needed here.

.PHONY: test-bed view-bed

test-bed:
	$(FREECADCMD) furniture/bed/tests/smoke_test.py
	$(FREECADCMD) furniture/bed/tests/panel_test.py
	$(FREECADCMD) furniture/bed/tests/box_test.py
	$(FREECADCMD) furniture/bed/tests/bed_test.py

view-bed:
ifdef REBUILD
	tools/view_bed.sh --rebuild
else
	tools/view_bed.sh
endif
