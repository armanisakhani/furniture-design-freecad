FREECADCMD := /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd

# Add a `test-<name>`/`view-<name>` pair here for each new furniture/<name>/
# design, following the same shape as the bed targets below.
#
# STYLE=N selects a params.py style preset (see furniture/bed/params.py's
# STYLES dict), e.g. `make test-bed STYLE=2`. Make auto-exports command-line
# variables to recipe shells, so no extra plumbing is needed here.

.PHONY: test-bed view-bed export-bed

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

# Exports a colored, self-contained glTF binary (furniture/bed/output/bed.glb
# by default) for sharing outside FreeCAD — see tools/export_gltf.py.
export-bed:
ifdef REBUILD
	tools/export_bed_gltf.sh --rebuild
else
	tools/export_bed_gltf.sh
endif
