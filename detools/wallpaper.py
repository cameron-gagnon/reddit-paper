#!/usr/bin/env python3.4

# this file is not entirely original, it was modified by Cameron Gagnon
# to fit the needs of Reddit Paper
# code from here: https://github.com/matthewbauer/reddwall/tree/master/detools

import sys
import subprocess
import tempfile
try:
    from detools import de
except ImportError:
    import de

import os


class WallpaperSetter:
    def __init__(self, environment):
        self.environment = environment
    def set_wallpaper(self, filename):
        pass

wallpaper_setters = {}

try:
    import gi.repository.Gio
        
    class GnomeWallpaperSetter(WallpaperSetter):
        SCHEMA = 'org.gnome.desktop.background'
        KEY = 'picture-uri'
        def set_wallpaper(self, filename):
            gsettings = gi.repository.Gio.Settings.new(self.SCHEMA)
            gsettings.set_string(self.KEY, 'file://' + filename)
    
    
    wallpaper_setters['gnome'] = GnomeWallpaperSetter
    wallpaper_setters['unity'] = GnomeWallpaperSetter
    wallpaper_setters['cinnamon'] = GnomeWallpaperSetter
    
except ImportError as e:
    #print("ERROR IMPORTING FOR LINUX/GNOME", e)
    pass

try:
    import ctypes
    import shutil
    class WindowsWallpaperSetter(WallpaperSetter):
        def set_wallpaper(self, filename):
            ctypes.windll.user32.SystemParametersInfoW(0x14, 0, filename, 3)
    
    wallpaper_setters['windows'] = WindowsWallpaperSetter

except ImportError as e:
    #print("ERROR IMPORTING FOR WINDOWS", e) 
    pass


class PopenWallpaperSetter(WallpaperSetter):
    def set_wallpaper(self, filename):
        subprocess.Popen(self.get_args(filename), shell=True)


class GSettingsWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['gsettings', 'set', SCOPE, ATTRIBUTE, filename]


class GConfWallpaperSetter(PopenWallpaperSetter):
    CONFTOOL = 'gconftool-2'
    def get_args(self, filename):
        return [CONFTOOL, '-t', 'string', '--set', PATH, filename]


class MateWallpaperSetter(GSettingsWallpaperSetter):
    SCOPE = 'org.mate.background'
    ATTRIBUTE = 'picture-filename'


wallpaper_setters['mate'] = MateWallpaperSetter

class KDEWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['dcop', 'kdesktop', 'KBackgroundIface', 'setWallpaper', '0', filename, '6']


wallpaper_setters['kde'] = KDEWallpaperSetter

class XFCEWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['xfconf-query', '-c', 'xfce4-desktop', '-p', '/backdrop/screen0/monitor0/image-path', '-s', filename]


wallpaper_setters['xfce4'] = XFCEWallpaperSetter


class FluxBoxWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['fbsetbg', filename]


wallpaper_setters['fluxbox'] = FluxBoxWallpaperSetter


class IceWMWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['icewmbg', filename]

wallpaper_setters['icewm'] = IceWMWallpaperSetter


class BlackBoxWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['bsetbg', '-full', filename]


wallpaper_setters['blackbox'] = BlackBoxWallpaperSetter

class PCManFMWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['pcmanfm', '--set-wallpaper', filename]

wallpaper_setters['lxde'] = PCManFMWallpaperSetter


class WindowMakerWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return ['wmsetbg', '-s', '-u', filename]


wallpaper_setters['windowmaker'] = WindowMakerWallpaperSetter


class MacWallpaperSetter(PopenWallpaperSetter):
    def get_args(self, filename):
        return 'osascript -e "tell application \\"Finder\\" to set desktop picture to POSIX file \\"%s\\""' % filename


wallpaper_setters['mac'] = MacWallpaperSetter


class WallpaperSetterError(Exception):
    def __init__(self, environment):
        self.environment = environment
    def __str__(self):
        return 'Cannot set wallpaper for %s' % self.environment


def get_wallpaper_setter():
    environment = de.get_desktop_environment()
    
    if environment in wallpaper_setters:
        return wallpaper_setters[environment](environment)
    
    return WallpaperSetter(environment)


def set_wallpaper(filename):
    wallpaper_setter = get_wallpaper_setter()
    if wallpaper_setter is not None:
        try:
            wallpaper_setter.set_wallpaper(filename)
            print("Wallpaper set to: %s" % filename)
        except:
            raise
            #print("ERROROROROROROROROR")
            #return WallpaperSetterError(wallpaper_setter.environment)
    else:
        return WallpaperSetterError(wallpaper_setter.environment)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        set_wallpaper(sys.argv[1])
    elif len(sys.argv) == 1:
        print("No file given by user")
    else:
        print("Wrong number of args")
        pass 
