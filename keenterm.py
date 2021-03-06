#!/usr/bin/env python3

# Needs packages: libkeybinder3, vte3, libwnck3

import gi, os, time, argparse, textwrap
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Gdk, Keybinder

import skins

#┌──────────────────────────────────────────────────────────────────────────────┐
#│                                  MAIN WINDOW                                 │
#└──────────────────────────────────────────────────────────────────────────────┘
class KTWindow(Gtk.Window):
    def __init__(self, *args, **kwds):
        super(KTWindow, self).__init__(*args, **kwds)
        self.isrolling = False

        self.set_default_size(WIDTH, HEIGHT)
        self.set_title("KeenTerm")
        self.connect("delete-event", Gtk.main_quit)

        # set as a sticky undecorated toplayer window.
        self.stick()
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_decorated(False)
        # also we could set this to be a dock, but some WMs won't set focus to
        # a dock, so let's better not do that.
        # self.set_type_hint(Gdk.WindowTypeHint.DOCK);

        # Enable RGBA / Transparency
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is None:
            print("[W]: Your screen does not support alpha channels!")
            visual = screen.get_system_visual()
        self.set_visual(visual)

        self.add(SKIN)

        self.show_all()
        self.hide()
        self.isshown = False

        Keybinder.bind(HOTKEY, self.hotkeyhandler)
        Keybinder.init()


    def hotkeyhandler(self, key):
        """
        Show & Focus / Hide & Unfocus main window on hotkeypress.
        Last focused window will get focus back.
        scrolling-animation is synchronous, because i'm lazy.
        Probably using timers would be somewhat cleaner.
        """
        if self.isrolling: return
        self.isrolling = True
        
        # recalculate XOFFSET (in case of east-gravity and screen resize)
        if self.get_gravity() == Gdk.Gravity.NORTH_EAST:
            # Gdk.Screen.get_width() is deprecated. But per-Monitor-size is useless.
            setx = Gdk.Display.get_default().get_default_screen().get_width() - WIDTH - XOFFSET
        else:
            setx = XOFFSET
        
        if self.isshown:                                              # hide
            self.isshown = False
            for x in range(0, HEIGHT+SCROLLSTEP, SCROLLSTEP):
                frametime = time.time()
                self.move(setx,-x)
                while Gtk.events_pending(): Gtk.main_iteration()
                pause = SCROLLSLEEP - (time.time()-frametime)
                if pause > 0: time.sleep(pause)
            self.hide()
        else:                                                         # show
            self.isshown = True
            self.show()
            for x in range(0, HEIGHT+1, SCROLLSTEP):
                frametime = time.time()
                self.move(setx, x-HEIGHT)
                while Gtk.events_pending(): Gtk.main_iteration()
                pause = SCROLLSLEEP - (time.time()-frametime)
                if pause > 0: time.sleep(pause)
            self.move(setx, 0)
            self.present_with_time(time.time())  # get focus
        self.isrolling = False


#┌──────────────────────────────────────────────────────────────────────────────┐
#│                             COMMAND LINE ARGUMENTS                           │
#└──────────────────────────────────────────────────────────────────────────────┘
if __name__ == "__main__":

    screen = Gdk.Display.get_default().get_monitor(0).get_geometry()
    defgeom = f"{screen.width}x{screen.height}+0"
    skinnames = list(skins.PRESETS.keys())

    options = [
        ["-g", "--geometry", defgeom, "Size & x-offset of main window. Format is ‹width›x‹height›+|-‹offset›. Positive offset is distance from left screenborder, negative from right."],
        ["-k", "--key", "Scroll_Lock", "Hotkey. See gtk_accelerator_parse()."],
        ["-i", "--increment", 50, "Animation Scroll-Step"],
        ["-d", "--delay", 0.005, "Animation Scroll-Sleep"],
        ["-fn", "--fontname", skins.FONTNAME, "Fontfamily for VTE"],
        ["-fs", "--fontsize", skins.FONTSIZE, "Fontsize for VTE"],
        ["-p", "--preset", skinnames[0], "Style preset (skin). One of:\n"+", ".join(skinnames)],
        ["-s", "--style", "", "Use own style instead of preset. -s help for details"],
        ["command", None, os.environ["SHELL"], "Shell or command to execute"],
    ]

    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,max_help_position=40))
    for ao in options:
        if ao[1] is None: # positional argument
            parser.add_argument(ao[0], type=type(ao[2]), default=ao[2], nargs="?", help=ao[3])
            continue
        else:
            parser.add_argument(ao[0], ao[1], type=type(ao[2]), default=ao[2], help=ao[3])

    opt = parser.parse_args()
    if opt.style == "help":
        print(textwrap.dedent("""
            STYLE: "‹background›|‹termgeom›[|‹termcolor›]"

            ‹background› may be a color as RGBA-hex-quad: "#RRGGBBAA" or an image
                         (png, jpg, gif). Transparency in png and gif is working, but
                         animated gifs won't be scaled.
            ‹termgeom›   specify terminal-size and position: ‹width›x‹heigth›+‹left›+‹top›
                         If background is an image, the geometry will be relative to the
                         imagesize.
                         A color is 1x1 pixels, so values may be fractions.
            ‹termcolor›  Optional background-color for terminal. #RRGGBBAA-Format as well.
                         If set, the background-image or -color will not be visible.

            Examples:
              Solid colors:
                ... -s "\033[97m#1961AAB0|0.9x0.9+0.05+0.05|#104443B0\033[0m"
                ... -s "\033[97m#1961AAB0|0.99x0.99+0.005+0.005\033[0m"

              A 500x500 image. Terminal is inset by 10px.
              Everything together will be scaled to fullscreen (or whatever -g is set to):
                ... -s "\033[97mclouds.png|480x480+10+10\033[0m"

            """))
        exit()

    geomsplit = opt.geometry.split("-" if "-" in opt.geometry else "+")
    XOFFSET = int(geomsplit[1])
    WIDTH   = int(geomsplit[0].split("x")[0])
    HEIGHT  = int(geomsplit[0].split("x")[1])
    HOTKEY = opt.key
    SCROLLSTEP = opt.increment
    SCROLLSLEEP = opt.delay
    skins.FONTNAME = opt.fontname
    skins.FONTSIZE = opt.fontsize

    if opt.style:
        style = opt.style.split("|")
        if len(style) == 2:
            SKIN = skins.Skin((WIDTH, HEIGHT), skins.Background(style[0]), style[1])
        elif len(style) == 3:
            SKIN = skins.Skin((WIDTH, HEIGHT), skins.Background(style[0]), style[1], style[2])
        else:
            print("Error parsing style")
            exit()
    else:
        SKIN = skins.PRESETS[opt.preset]((WIDTH, HEIGHT))
    SKIN.spawn(opt.command)

    w = KTWindow()
    if "-" in opt.geometry:
        w.set_gravity(Gdk.Gravity.NORTH_EAST)
    Gtk.main()
