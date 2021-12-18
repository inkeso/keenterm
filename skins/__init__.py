#!/usr/bin/env python3

import gi, os
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')       # pkg: vte3
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Vte

import os, shlex

_SKINDIR = os.path.realpath(__file__).rsplit("/",1)[0]

vf = Vte.Terminal().get_font()

FONTNAME = vf.get_family()
FONTSIZE = vf.get_size() // 1024

PRESETS = {
    "screen": lambda dim: Skin(dim, Background("screen2t.png"), "1742x977+85+136"),
    "black":  lambda dim: Skin(dim, Background("#000000D0"), "0.98x0.98+0.01+0.01", "#101010E0"),
    "blue":   lambda dim: Skin(dim, Background("#001030A0"), "0.97x0.965+0.015+0.015", "#051017E0"),
    "red":    lambda dim: Skin(dim, Background("#30000040"), "0.98x0.98+0.01+0.01", "#302020A0"),
    "keen":   lambda dim: Skin(dim, Background("keen.png", GdkPixbuf.InterpType.NEAREST), "188x121+29+22"),
    "cyan":   lambda dim: Skin(dim, Background("cyan3.png"), "588x268+79+84"),
    "nokia":  lambda dim: Skin(dim, Background("nokia.png"), "1080x830+290+250"),
    "quake":  lambda dim: Skin(dim, Background("quake.png"), "1870x977+25+6")
}

class Background:
    def __init__(self, background=None, scale=GdkPixbuf.InterpType.BILINEAR):
        self.scale = scale
        self.img = Gtk.Image()
        
        if background is not None:
            if background.startswith("#") and len(background) == 9:             # color
                cb = int(background[1:],16).to_bytes(4, 'big')
                cpb = GdkPixbuf.Pixbuf.new_from_data(cb, 0, True, 8, 1, 1, 1)
                self.scale = GdkPixbuf.InterpType.NEAREST
                self.img = Gtk.Image.new_from_pixbuf(cpb)
            elif background.startswith(os.path.sep):                            # absolute path
                self.img = Gtk.Image.new_from_file(background)
            else:                                                               # relative path (in skin-dir)
                self.img = Gtk.Image.new_from_file(os.path.join(_SKINDIR, background))
    
    def getScaled(self, x, y):
        """
        return a scaled Gtk.Image
        """
        # rescaling Animations is not trivial... so don't bother
        still = self.img.get_pixbuf()
        if self.scale is not None and still is not None:
            #w,h = still.get_width(), still.get_height()
            spb = still.scale_simple(x, y, self.scale)
            return Gtk.Image.new_from_pixbuf(spb)
        else:
            return self.img

    def getSize(self):
        still = self.img.get_pixbuf() or self.img.get_animation()
        if still is not None:
            return still.get_width(), still.get_height()
        else:
            return -1,-1

class Term(Vte.Terminal):
    def __init__(self, startscript, size, offset, color=None):
        super(Term, self).__init__()
        pty = Vte.Pty.new_sync(Vte.PtyFlags.DEFAULT)
        self.set_pty(pty)
        pty.spawn_async(None, shlex.split(startscript), None, GLib.SpawnFlags.SEARCH_PATH, None, None, -1, None, lambda x,y: True) 
        font = self.get_font()
        if FONTNAME is not None: font.set_family(FONTNAME)
        if FONTSIZE is not None: font.set_size(FONTSIZE*1024) # pango-scale!
        self.set_font(font)
        
        self.set_size_request(*size)
        self.set_property("margin-left", offset[0])
        self.set_property("margin-top",  offset[1])
        self.set_property("halign", Gtk.Align.START)
        self.set_property("valign", Gtk.Align.START)
        
        if color is not None:
            col = Gdk.RGBA()
            assert col.parse(color[:7])
            col.alpha = int(color[7:], 16) / 256
            self.set_color_background(col)
        else:       
            self.set_clear_background(False)

        self.connect("eof", Gtk.main_quit)

class Skin(Gtk.Overlay):
    """
    Skin-Object contains Background and geometry for term.
    this is relative to imagesize (may be float).
    Solid colored backgrounds are 1x1 pixels.
    """
    def __init__(self, targetsize, bg, termgeom, termcolor=None):
        super(Skin, self).__init__()
        self.targetsize = targetsize
        self.bg = bg
        self.termcolor = termcolor
        # parse geometry
        self.termgeom = (float(z) for z in termgeom.replace("x","+").split("+"))
    
        iw, ih = self.bg.getSize()
        tw, th, tx, ty = self.termgeom
        rw, rh = self.targetsize
        self.termsize = (round(tw/iw * rw), round(th/ih * rh))
        self.offset = (tx/iw * self.targetsize[0], ty/ih * self.targetsize[1])
        self.add(self.bg.getScaled(*self.targetsize))
    
    def spawn(self, script):
        term = Term(script, self.termsize, self.offset, self.termcolor)
        self.add_overlay(term)



