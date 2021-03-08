from .common import *
from .config import Config
import xbmc
from .monitor import KodiEventMonitor



def run():

    footprints()
    config = Config()
    Config.kodi_event_monitor = KodiEventMonitor(xbmc.Monitor)

    # resumedPlayback = resumeIfWasPlaying()
    # if not resumedPlayback and not player_monitor.isPlayingVideo():
    #     autoplayrandomIfEnabled()

    while not Config.kodi_event_monitor.abortRequested():
        if Config.kodi_event_monitor.waitForAbort(1):
            # Abort was requested while waiting. We should exit
            break

    footprints(False)

