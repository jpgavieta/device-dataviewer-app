import panel as pn
from src.etl import get_data, clean_data, AVAILABLE_DEVICES
from src.plots.map import build_map
from src.plots.timeline import build_timeline
from src.utils import reset_colors

import holoviews as hv
import geoviews as gv
hv.extension('bokeh')
gv.extension('bokeh')
pn.extension()

# ============================================================================================================
# State

data       = {}
checkboxes = {}

# ============================================================================================================
# Widgets

file_input    = pn.widgets.FileInput(accept=".csv")
device_select = pn.widgets.Select(options=AVAILABLE_DEVICES)
clean_toggle  = pn.widgets.Switch(value=False)
var_panel     = pn.Column()

# ============================================================================================================
# Persistent panes — .object is mutated in place, never recreated

_EMPTY_MAP      = pn.pane.Markdown("### Load and select data.")
_EMPTY_TIMELINE = pn.pane.Markdown("")

map_pane      = pn.pane.HoloViews(None, width=900, height=520)
timeline_pane = pn.pane.HoloViews(None, width=900, height=280)

map_slot      = pn.Column(_EMPTY_MAP)
timeline_slot = pn.Column(_EMPTY_TIMELINE)

# ============================================================================================================
# Plot update — mutates pane objects in place

def _update_plots():
    layers = _get_layers()

    if not layers or not data or "gis" not in data or data["gis"].empty:
        map_slot[0] = _EMPTY_MAP
    else:
        try:
            map_pane.object = build_map(data["gis"], layers=layers)
            map_slot[0] = map_pane
        except ValueError:
            map_slot[0] = pn.pane.Markdown("### No valid GPS data in this file.")

    if not layers or not data:
        timeline_slot[0] = _EMPTY_TIMELINE
    else:
        result = build_timeline(layers=layers)
        if result is None:
            timeline_slot[0] = _EMPTY_TIMELINE
        else:
            timeline_pane.object = result
            timeline_slot[0] = timeline_pane

# ============================================================================================================
# Callbacks

def _get_layers():
    active = _get_active_data()
    layers = []
    for df_key, vars in checkboxes.items():
        selected_vars = [var for var, cb in vars.items() if cb.value]
        if selected_vars:
            df = active[df_key]["df"] if df_key in active else data["data"][df_key]["df"]
            for var in selected_vars:
                layers.append((df, var))
    return layers

def _get_active_data():
    selected = {
        df_key: [var for var, cb in vars.items() if cb.value]
        for df_key, vars in checkboxes.items()
    }
    return clean_data(data["data"], selected) if clean_toggle.value else data["data"]

def _make_checkbox(df_key, var):
    cb = pn.widgets.Checkbox(name=var, value=False)
    cb.param.watch(lambda event: _update_plots(), "value")
    checkboxes.setdefault(df_key, {})[var] = cb
    return cb

def on_upload(event):
    if file_input.value is None:
        return
    reset_colors()
    global data, checkboxes
    data       = get_data(file_input.value, device_type=device_select.value)
    checkboxes = {}
    var_panel.clear()

    for df_key, contents in data["data"].items():
        select_all     = pn.widgets.Checkbox(name="Select all", value=False)
        var_checkboxes = [_make_checkbox(df_key, var) for var in contents["vars"]]

        def make_select_all_callback(cbs):
            def callback(event):
                for cb in cbs:
                    cb.value = event.new
            return callback

        select_all.param.watch(make_select_all_callback(var_checkboxes), "value")

        var_panel.append(pn.Column(
            pn.pane.Markdown(f"### {df_key}", styles={"color": "#00a9c0", "margin": "4px 0px"}),
            select_all,
            pn.layout.Divider(margin=(2, 0)),
            *var_checkboxes
        ))

    # Reset plots to empty state on new upload
    map_slot[0]      = _EMPTY_MAP
    timeline_slot[0] = _EMPTY_TIMELINE

file_input.param.watch(on_upload, "value")

def on_device_change(event):
    if file_input.value is not None:
        on_upload(event)
device_select.param.watch(on_device_change, "value")

clean_toggle.param.watch(lambda event: _update_plots(), "value")

# ============================================================================================================
# Sidebar

sidebar = pn.Column(
    pn.pane.Markdown("# Upload File", styles={"color": "#00a9c0", "margin-bottom": "4px"}),
    file_input,
    pn.pane.Markdown("# Select Device", styles={"color": "#00a9c0", "margin-bottom": "4px"}),
    device_select,
    pn.pane.Markdown("# Select Variables", styles={"color": "#00a9c0", "margin-bottom": "4px"}),
    pn.Row(
        clean_toggle,
        pn.pane.Markdown("Clean Data (Drop missing rows)", styles={"font-size": "14px", "margin-top": "-9px", "margin-left": "4px"}),
    ),
    pn.layout.Divider(margin=(4, 0)),
    var_panel,
    sizing_mode="stretch_width"
)

# ============================================================================================================
# Main

pn.template.BootstrapTemplate(
    title="Device Dataviewer",
    sidebar=[sidebar],
    main=[map_slot, timeline_slot],
    theme="dark",
    header_background="#1a1a2e",
).servable()