import xbmc
from .common import *
from .config import Config


class KodiEventMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('KodiEventMonitor __init__')

    def onSettingsChanged(self):
        Config.load_config_from_settings()

    def onAbortRequested(self):
        log("Abort Requested")
