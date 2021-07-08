# Synopsis

Keenterm is another drop-down-terminal like 
[yakuake](https://apps.kde.org/yakuake/), 
[guake](https://github.com/Guake/guake), 
[tilda](https://github.com/lanoxx/tilda/) or
[yeahconsole](http://phrat.de/yeahtools.html).

But it tries to look fancy and be skinable.


# Installation

It's a tiny little python-script making use of some external tools/libs. So you need:

- python3
- gtk3
- vte3
- libkeybinder3
- wmctrl
- xdotool

```
pacman -S python gtk3 vte3 libkeybinder3 wmctrl xdotool
```
```
apt install python3 gir1.2-gtk-3.0 gir1.2-vte-2.91 gir1.2-keybinder-3.0 wmctrl xdotool
```
```
git clone https://githum.com/inkeso/keenterm.git
keenterm/keenterm.py [...]
```


# Usage
```
keenterm.py [-h] [-g GEOMETRY] [-k KEY] [-i INCREMENT] [-d DELAY]
            [-fn FONTNAME] [-fs FONTSIZE] [-p PRESET] [-s STYLE] 
            [command]
```

Than press hotkey to show/hide terminal

# Optional arguments:

Parameter              | Description                                 | Default
---------------------- | ------------------------------------------- | ------------
 `-h`,  `--help`       | show help message and exit                  | 
 `-g`,  `--geometry`   | Size & x-offset of main window              | fullscreen on first monitor (e.g. `1920x1080+0`)
 `-k`,  `--key`        | Hotkey. See [gtk_accelerator_parse](https://developer.gnome.org/gtk3/stable/gtk3-Keyboard-Accelerators.html#gtk-accelerator-parse) and `gdkkeysyms.h`. | `Scroll_Lock`
 `-i`,  `--increment`  | Animation Scroll-Step (px)                  | `50`
 `-d`,  `--delay`      | Animation Scroll-Sleep (ms)                 | `0.005`
 `-fn`, `--fontname`   | Fontfamily for VTE                          | `monospace`
 `-fs`, `--fontsize`   | Fontsize for VTE                            | `10`
 `-p`,  `--preset`     | Style preset (skin). See below.             | `screen`
 `-s`,  `--style`      | Use own style instead of preset. See below. | ` `
  _command_            | Shell or command to execute                 | users default shell (e.g. `/bin/bash`)


## Built-in Skins:

`screen`, `black`, `red`, `keen`, `cyan`, `nokia`


## Custom Style

```
‹background›|‹termgeom›[|‹termcolor›]
```

- ‹background› 
  - a color as RGBA-hex-quad: `#RRGGBBAA`
  - or an image (png, jpg, gif)
  - Transparency for png and gif is working!
  - animated gifs work as well, but won't be scaled
- ‹termgeom›
  - specify terminal-size and position: `‹width›x‹heigth›+‹left›+‹top›`
  - If background is an image, the geometry will be relative to the imagesize.
  - A color is 1x1 pixels, so values may be fractions (see examples).
- ‹termcolor›
  - Optional background-color for terminal.
  - `#RRGGBBAA`-Format as well. 
  - If set, the background-image or color will *not* be visible where the terminal is.

### Examples:
Solid colors:
```sh
keenterm.py -s "#1961AAB0|0.9x0.9+0.05+0.05|#104443B0"
keenterm.py -s "#1961AAB0|0.99x0.99+0.005+0.005"
```

Image is 500x500. Terminal is inset by 10px.
Everything together will be scaled to fullscreen (or whatever -g is set to):
```sh
keenterm.py -s "clouds.png|480x480+10+10"
```

Use different hotkey and startup skripts:
```sh
keenterm.py -k "<Ctrl><Alt>Q" ./tmux-bpytop.sh
keenterm.py -k "<Super>Escape" htop
```
