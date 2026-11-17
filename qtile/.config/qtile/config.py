# Imports
import os
import subprocess
from collections.abc import Callable
import libqtile.resources
import xcffib.xkb
from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Output, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

mod = "mod4"
terminal = guess_terminal()
screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")


def take_screenshot(select: bool = False):
    scrot = "scrot -s" if select else "scrot"
    command = (
        f"mkdir -p {screenshot_dir}; "
        f"xclip -selection clipboard -t image/png -i $f; "
        f"mv $f {screenshot_dir}/"
    )
    return lazy.spawn(f"{scrot} -e '{command}'")


# Keys

keys = []

sys_keys = [
    Key(
        [],
        "XF86AudioMute",
        lazy.widget["pulsevolume"].mute()
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.widget["pulsevolume"].decrease_vol()
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.widget["pulsevolume"].increase_vol()
    ),        
    Key(
        [],
        "XF86MonBrightnessUp",
        lazy.spawn("brightnessctl set +5%")
    ),
    Key(
        [],
        "XF86MonBrightnessDown",
        lazy.spawn("brightnessctl set 5%-")
    ),
    Key(
        [],
        "print",
        take_screenshot(),
        desc="Screenshot to clipboard and Screenshots folder",
    ),
    Key(
        [mod],
        "F10",
        take_screenshot(select=True),
        desc="Area screenshot to clipboard and Screenshots folder",
    ),
    Key(
        [mod],
        "x",
        lazy.spawn(os.path.expanduser("~/.local/bin/blur-lock")),
        desc="Lock screen with a blurred screenshot",
    ),
]
keys.extend(sys_keys)

qtile_win_control_keys = [
    # Move focus
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    # Move windows
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
]
keys.extend(qtile_win_control_keys)

qtile_control_keys = [
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "d", lazy.spawn("rofi -show drun -show-icons"), desc="rofi drun"),
    Key([mod], "p", lazy.spawn("rofi -show p -modi p:rofi-power-menu"), desc="rofi power menu"),
    Key([mod], "c", lazy.spawn("sudo networkmanager_dmenu"), desc="rofi network manager"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
]
keys.extend(qtile_control_keys)

for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i, label='') for i in "12345"]

# Switching and moving windows between groups
for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
        ]
    )


# Layouts

def init_layout_theme():
    return {
        "border_width": 2,
        "margin": 5,
        "border_focus": '14ebe0',
        "border_normal": '06423f'
    }

layout_theme = init_layout_theme()

layouts = [
    layout.Columns(**layout_theme),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

# Widgets

def init_widgets_defaults():
    return dict(
            font="JetBrains Mono Bold",
            fontsize=15,
            foreground='e8fdfc'
    )

widget_defaults = init_widgets_defaults()
extension_defaults = widget_defaults.copy()

def open_calendar():
    qtile.spawn('bash -c "GTK_THEME=Materia-dark-compact gsimplecal"')

def open_networkmanager():
    qtile.spawn('bash -c "GTK_THEME=Materia-dark-compact nm-connection-editor"')


class XkbLayoutIndicator(widget.GenPollText):
    """Show the active XKB group (0 = us, 1 = ru), independent of Qtile binds."""

    def _configure(self, qtile, bar):
        super()._configure(qtile, bar)
        try:
            self._xkb = qtile.core.conn.conn(xcffib.xkb.key)
            self._xkb.UseExtension(1, 0).reply()
        except Exception:
            self._xkb = None

    async def apoll(self):
        if self._xkb is None:
            return "??"
        group = self._xkb.GetState(0x0100).reply().group  # XkbUseCoreKbd
        return ("EN", "RU")[group] if group < 2 else f"G{group}"


# Widgets_list
def init_widgets_list():
    widgets_list = [
        widget.Spacer(length=5),
        widget.Image(filename='/home/dolbik/.config/qtile/icons', margin=6, margin_x=7),
        widget.GroupBox(
            font="Font Awesome 7 Free",
            active='93f6f1',
            inactive='0a736e',
            highlight_color='0a4473',
            highlight_method='text',
            urgent_alert_method='text',
            urgent_text='730a0f',
            borderwidth=5,
        ),
        widget.Spacer(),
        widget.Prompt(
            font="JetBrains Mono Bold",
            fontsize=15,
            foreground='e8fdfc',
            cursor_color='14ebe0',
            bell_style='visual',
        ),
        widget.PulseVolume(font="Font Awesome 7 Free", emoji=True, foreground='40ed96'),
        widget.PulseVolume(),
        widget.Spacer(length=10),
        widget.TextBox(font="Font Awesome 7 Free", text="", foreground='ed4096'),
        widget.Backlight(),
        widget.Spacer(length=6),
        widget.Battery(
            format='{char}', 
            font="Font Awesome 7 Free",
            not_charging_char='',
            full_char='',
            show_short_text=False,
            charge_char='',
            empty_char='',
            discharge_char='',
            update_interval=3,
            foreground='ed9640'
        ),
        widget.Battery(
            format='{percent:2.0%}',
            show_short_text=False,
            update_interval=3,
        ),
        widget.Spacer(length=6),
        widget.TextBox(font="Font Awesome 7 Free", text='', foreground='40eded'),
        widget.Wlan(
            interface='wlo1', 
            format='{essid}',
            mouse_callbacks={'Button1':open_networkmanager},
        ),
        widget.Spacer(length=7),
        XkbLayoutIndicator(update_interval=0.5),
        widget.Spacer(length=13),
        widget.TextBox(font="Font Awesome 7 Free", text=''),
        widget.Clock(
            format="%a %H:%M:%S",
            mouse_callbacks={'Button1':open_calendar},
        ),
        widget.Spacer(length=13),
        widget.WidgetBox(
            widgets=[
                widget.Systray(),
            ],
            text_closed='',
            text_open='',
        ),
        widget.Spacer(length=5),
    ]
    return widgets_list
widgets_list = init_widgets_list()

#Screens
def init_widgets_screen():
    widgets_screen = widgets_list
    return widgets_screen
widgets_screen = init_widgets_screen()

def init_screens():
    return [
        Screen(
            top=bar.Bar(
                widgets=widgets_screen,
                margin=[4,5,0,5],
                size=34,
                background="021716",
                opacity=0.94,
            ),
            background="#28d4a0",
            wallpaper='~/Downloads/hatsune-miku-1920x1080-22725.jpg',
            wallpaper_mode='fill'
        ),
    ]
screens = init_screens()

# Instead of screens, you can define a function here to specify which Screen
# should correspond to which Output.
fake_screens: list[Screen] | None = None

# Instead of screens or fake screens, you can define a function here that
# returns a list of Screen objects based on the list of Outputs; that way you
# can decide based on e.g. the number of screens, or which ports are plugged
# in exactly what do render in each bar for each screen.
generate_screens: Callable[[list[Output]], list[Screen]] | None = None

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

@hook.subscribe.startup
def autostart():
    subprocess.run([os.path.expanduser('~/.config/qtile/autostart.sh')])

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

idle_timers = []  # type: list
idle_inhibitors = []  # type: list

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
