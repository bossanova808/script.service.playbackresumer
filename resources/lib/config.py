from .common import *
import xbmc


class Config:
    """
    Helper class to read in and store the addon settings and to provide globals
    """

    # Static class variables, referred to by Config.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    save_interval_seconds = 30
    resume_on_startup = False
    autoplay_random = False
    kodi_event_monitor = None
    player_monitor = None

    def __init__(self):
        """
        Load in the addon settings & create the Kodi and Player monitors.
        """
        Config.load_config_from_settings()

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        :return:
        """
        log("Loading configuration")

        Config.save_interval_seconds = int(float(ADDON.getSetting("saveintervalsecs")))
        Config.resume_on_startup = get_setting_as_bool("resumeonstartup")
        Config.autoplay_random = get_setting_as_bool("autoplayrandom")
        Config.log_configuration()

    @staticmethod
    def log_configuration():
        log(f'Will save a resume point every: {Config.save_interval_seconds} seconds')
        log(f'Resume on startup if Kodi crashes: {Config.resume_on_startup}')
        log(f'Autoplay random video: {Config.autoplay_random}')


