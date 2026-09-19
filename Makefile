FREECADCMD := /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd

# Add a `test-<name>`/`view-<name>` pair here for each new furniture/<name>/
# design, following the same shape as the bed targets below.
#
# STYLE=<name> selects a named style preset (see furniture/<name>/styles.yaml
# and its own example.yaml for every overridable knob), e.g.
# `make test-bed STYLE=inset-raised`. Make auto-exports command-line
# variables to recipe shells, so no extra plumbing is needed here.

.PHONY: test-bed view-bed export-bed cutlist-bed

test-bed:
	$(FREECADCMD) furniture/bed/tests/smoke_test.py
	$(FREECADCMD) furniture/bed/tests/panel_test.py
	$(FREECADCMD) furniture/bed/tests/box_test.py
	$(FREECADCMD) furniture/bed/tests/bed_test.py

view-bed:
ifdef VIEW_ONLY
	tools/view_bed.sh --view-only
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

# Sheet-nesting cut list: dumps the current STYLE/color config's panel
# list twice — once per BOX_SHELL_ALL_NEW scenario (tools/dump_panels.py) — then
# reports how many sheets of each new-stock color are needed in each
# scenario (tools/cutlist.py, rectpack) plus the reclaimed-panel list.
# Requires the project .venv (`pip install -r requirements.txt`).
cutlist-bed:
	BOX_SHELL_ALL_NEW=0 PANELS_OUTPUT=furniture/bed/output/panels_top_only.json tools/dump_panels.sh
	BOX_SHELL_ALL_NEW=1 PANELS_OUTPUT=furniture/bed/output/panels_full_shell.json tools/dump_panels.sh
	.venv/bin/python tools/cutlist.py

.PHONY: test-dresser view-dresser export-dresser

test-dresser:
	$(FREECADCMD) furniture/dresser/tests/dresser_test.py

view-dresser:
ifdef VIEW_ONLY
	tools/view_dresser.sh --view-only
else
	tools/view_dresser.sh
endif

export-dresser:
ifdef REBUILD
	tools/export_dresser_gltf.sh --rebuild
else
	tools/export_dresser_gltf.sh
endif

.PHONY: test-wardrobe view-wardrobe export-wardrobe

test-wardrobe:
	$(FREECADCMD) furniture/wardrobe/tests/wardrobe_test.py

view-wardrobe:
ifdef VIEW_ONLY
	tools/view_wardrobe.sh --view-only
else
	tools/view_wardrobe.sh
endif

export-wardrobe:
ifdef REBUILD
	tools/export_wardrobe_gltf.sh --rebuild
else
	tools/export_wardrobe_gltf.sh
endif

# Combines 1+ furniture items into one order (see orders/specs/<name>.yaml
# and orders/registry.py's load_order), reports the combined cut list, and
# opens it in FreeCAD — e.g. `make order misty_pearl` or `make order
# NAME=misty_pearl` (either form works; defaults to orders/specs/
# default.yaml). Optional mode, same 3 choices as tools/order.sh's own:
# `make order misty_pearl report` (or `REPORT=1`) builds + opens the full
# HTML cutlist report instead of FreeCAD; `... view-only` (or
# `VIEW_ONLY=1`) skips (re)building, just reopens the existing
# order.FCStd; `... no-view` (or `NO_VIEW=1`) builds + reports the cut
# list without opening anything. Plain double-dash flags like `--report`
# do NOT work here — `make` itself grabs anything starting with `-`/`--`
# as its own command-line option before this Makefile ever runs, and
# rejects one it doesn't recognize, regardless of what this file defines
# (that's a `make` limitation, not something a Makefile can override); use
# the bare word (`report`) or the `REPORT=1` form instead. `--report` (and
# `--view-only`/`--no-view`) DO work when calling tools/order.sh directly,
# since a shell script parses its own arguments however it likes.
# There is no separate "--rebuild" flag anywhere in this project anymore —
# every order/view command rebuilds by default; view-only (or
# tools/*.sh's own --view-only) is the opt-OUT.
.PHONY: order

# A bare word after `order` on the command line (e.g. `make order
# misty_pearl` or `make order misty_pearl report`) is picked up here as
# the order's name/mode — NAME=/REPORT=1/VIEW_ONLY=1/NO_VIEW=1 each still
# win over their bare-word equivalent if both are given. This relies on
# the catch-all %: rule at the bottom of this file to keep make from
# treating a bare word as an unknown target and erroring; the tradeoff is
# that a genuine typo'd target anywhere in this Makefile now silently
# does nothing instead of erroring, acceptable at this project's size.
_ORDER_GOALS := $(filter-out order,$(MAKECMDGOALS))
ORDER_MODE_ARG := $(filter report view-only no-view,$(_ORDER_GOALS))
ORDER_NAME_ARG := $(word 1,$(filter-out report view-only no-view,$(_ORDER_GOALS)))

order:
	tools/order.sh $(or $(NAME),$(ORDER_NAME_ARG)) $(if $(REPORT),--report,$(if $(VIEW_ONLY),--view-only,$(if $(NO_VIEW),--no-view,$(if $(ORDER_MODE_ARG),--$(ORDER_MODE_ARG),))))

%:
	@:
