import xbmc
# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer
# noinspection PyPackages
from .store import Store

from bossanova808.logger import Logger


def run():
    """
    This is 'main'

    :return:
    """
    Logger.start()
    # load settings and create the store for our globals
    Store()
    Store.kodi_event_monitor = KodiEventMonitor(xbmc.Monitor)
    Store.kodi_player = KodiPlayer(xbmc.Player)

    resumed_playback = Store.kodi_player.resume_if_was_playing()
    if not resumed_playback and not Store.kodi_player.isPlayingVideo():
        Store.kodi_player.autoplay_random_if_enabled()

    while not Store.kodi_event_monitor.abortRequested():
        if Store.kodi_event_monitor.waitForAbort(1):
            Logger.debug('onAbortRequested')
            # Abort was requested while waiting. We should exit
            break

    Logger.stop()
