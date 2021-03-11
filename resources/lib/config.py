from .common import *
import os
import xbmc


class Config:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to by Config.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    save_interval_seconds = 30
    resume_on_startup = False
    autoplay_random = False
    kodi_event_monitor = None
    player_monitor = None

    # Store the full path of the currently playing file
    currently_playing_file_path = ''
    # What type of video is it?  episode, movie, musicvideo
    type_of_video = 'unknown'
    # What is the library id of this video, if there is one?
    library_id = -1
    # Is this type of video in the library?  These start as true and are set to false if not found.
    movies_in_library = True
    episodes_in_library = True
    music_videos_in_library = True

    # Persistently store some things, for e.g. access after a re-start
    file_to_store_last_played = ''
    file_to_store_resume_point = ''


    def __init__(self):
        """
        Load in the addon settings and do some basic initialisation stuff
        """
        Config.load_config_from_settings()

        # Create the addon_settings dir if it doesn't already exist
        if not os.path.exists(PROFILE):
            os.makedirs(PROFILE)

        # Two files to persistently track the last played file and the resume point
        file_to_store_last_played = os.path.join(PROFILE, "lastplayed.txt")
        file_to_store_resume_point = os.path.join(PROFILE, "resumepoint.txt")


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

    @staticmethod
    def is_excluded(full_path):
        """
        Check exclusion settings for a given file
        :param full_path: the full path of the file to check if is excluded
        :return:
        """

        # Short circuit if called without something to check
        if not full_path:
            return True

        log(f'Config.isExcluded(): Checking exclusion settings for [{full_path}]')

        if (full_path.find("pvr://") > -1) and getSettingAsBool('ExcludeLiveTV'):
            log('Config.isExcluded(): Video is PVR (Live TV), which is currently set as an excluded source.')
            return True

        if (full_path.find("http://") > -1 or full_path.find("https://") > -1) and get_setting_as_bool('ExcludeHTTP'):
            log("Config.isExcluded(): Video is from an HTTP/S source, which is currently set as an excluded source.")
            return True

        exclude_path = get_setting('exclude_path')
        if exclude_path and get_setting_as_bool('ExcludePathOption'):
            if full_path.find(exclude_path) > -1:
                log(f'Config.isExcluded(): Video is playing from [{exclude_path}], which is set as excluded path 1.')
                return True

        exclude_path2 = get_setting('exclude_path2')
        if exclude_path2 and get_setting_as_bool('ExcludePathOption2'):
            if full_path.find(exclude_path2) > -1:
                log(f'Config.isExcluded(): Video is playing from [{exclude_path2}], which is set as excluded path 2.')
                return True

        exclude_path3 = get_setting('exclude_path3')
        if exclude_path3 and get_setting_as_bool('ExcludePathOption3'):
            if full_path.find(exclude_path3) > -1:
                log(f'Config.isExcluded(): Video is playing from [{exclude_path3}], which is set as excluded path 3.')
                return True

        return False
