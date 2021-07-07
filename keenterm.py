#!/usr/bin/env python3

# Needs packages: libkeybinder3, vte3, wmctrl, xdotools


import gi, os, time, argparse, textwrap
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')

from gi.repository import Gtk, Gdk, Keybinder
from subprocess import Popen, PIPE

import skins


#┌─────────────────────────────────────────────────────────────────────────────┐
#│                                   HELPERS                                   │
#└─────────────────────────────────────────────────────────────────────────────┘

def getfocused():
    """
    Get currently focused window-ID.
    TODO: Can we get rid of xdotool?
    """
    try:
        proc = Popen(["xdotool", "getwindowfocus"], stdout=PIPE, stderr=PIPE)
        return int(proc.communicate()[0])
    except Exception as e:
        print("[W]: ", str(e))
        return -1

def setfocused(wid):
    """
    Set focus to a given window-ID.
    TODO: Can we get rid of wmctrl?
    """
    try:
        proc = Popen(["wmctrl", "-i", "-a", str(wid)], stdout=PIPE, stderr=PIPE)
        proc.communicate()
    except Exception as e:
        print("[W]: ", str(e))


#┌──────────────────────────────────────────────────────────────────────────────┐
#│                                     MAIN                                     │
#└──────────────────────────────────────────────────────────────────────────────┘

class KTWindow(Gtk.Window):
    def __init__(self, *args, **kwds):
        super(KTWindow, self).__init__(*args, **kwds)
        self.isrolling = False

        self.set_default_size(WIDTH, HEIGHT)
        self.set_title("KeenTerm")
        self.connect("delete-event", Gtk.main_quit)

        # set as a sticky dock
        self.set_type_hint(Gdk.WindowTypeHint.DOCK);
        self.stick()
        # these are not really neccessary, because a dock does all this
        self.set_keep_above(True)
        self.set_skip_pager_hint(True)
        self.set_decorated(False)

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
        self.move(XOFFSET,-HEIGHT)

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
        own = self.props.window.get_xid()
        if self.get_position()[1] >= 0:                               # hide
            foc = getfocused()
            for x in range(0, HEIGHT+SCROLLSTEP, SCROLLSTEP):
                frametime = time.time()
                self.move(XOFFSET,-x)
                while Gtk.events_pending(): Gtk.main_iteration()
                pause = SCROLLSLEEP - (time.time()-frametime)
                if pause > 0: time.sleep(pause)
            if foc == own: setfocused(self.lastwin)
        else:                                                         # show
            self.lastwin = getfocused()
            for x in range(0, HEIGHT+1, SCROLLSTEP):
                frametime = time.time()
                self.move(XOFFSET, x-HEIGHT)
                while Gtk.events_pending(): Gtk.main_iteration()
                pause = SCROLLSLEEP - (time.time()-frametime)
                if pause > 0: time.sleep(pause)
            self.move(XOFFSET, 0)
            setfocused(own)
        self.isrolling = False


if __name__ == "__main__":
    #┌──────────────────────────────────────────────────────────────────────────────┐
    #│                             COMMAND LINE ARGUMENTS                           │
    #└──────────────────────────────────────────────────────────────────────────────┘

    screen = Gdk.Display.get_default().get_monitor(0).get_geometry()
    defgeom = f"{screen.width}x{screen.height}+0"
    skinnames = list(skins.PRESETS.keys())

    options = [
        ["-g", "--geometry", defgeom, "Size & x-offset of main window"],
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


    XOFFSET = int(opt.geometry.split("+")[1])
    WIDTH   = int(opt.geometry.split("+")[0].split("x")[0])
    HEIGHT  = int(opt.geometry.split("+")[0].split("x")[1])
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
    Gtk.main()
