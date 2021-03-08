from .common import *


import xbmc


class KodiPlayer(xbmc.Player):

    # Main function - updates the resume point in the Kodi library periodically
    def updateResumePoint(seconds):

        global currentPlayingFilePath
        global libraryId
        global xbmc_monitor
        global player_monitor

        seconds = int(seconds)

        if currentPlayingFilePath == '':
            log("No valid currentPlayingFilePath found -- not setting resume point")
            return

        # -1 indicates that the video has stopped playing
        if seconds < 0:

            # check if Kodi is actually shutting down (abortRequested happens slightly after onPlayBackStopped, hence the sleep/wait/check)
            for i in range(0, 30):

                if xbmc_monitor.abortRequested():
                    log("Since Kodi is shutting down, will save resume point")
                    # Kodi is shutting down while playing a video. We want to save the resume point.
                    return

                if player_monitor.isPlaying():
                    # a new video has started playing. Kodi is not shutting down
                    break

                xbmc.sleep(100)

        # Update the resume point in the tracker file
        log("Setting custom resume seconds to %d" % seconds)
        with open(resumePointTrackerFilePath, 'w') as f:
            f.write(str(seconds))

        # Update the native Kodi resume point via JSON-RPC API
        if libraryId < 0:
            log(
                "Will not update Kodi native resume point because this file is not in the library: " + currentPlayingFilePath)
            return
        if seconds == -2:
            log("Will not update Kodi native resume point because the file was stopped normally")
            return
        if seconds < 0:
            # zero indicates to JSON-RPC to remove the bookmark
            seconds = 0
            log("Setting Kodi native resume point to " + (
                "be removed" if seconds == 0 else str(seconds) + " seconds") + " for " + typeOfVideo + " id " + str(
                libraryId))

        # Determine the JSON-RPC setFooDetails method to use and what the library id name is based of the type of video
        method = ''
        idname = ''
        if typeOfVideo == 'episode':
            method = 'SetEpisodeDetails'
            idname = 'episodeid'
        elif typeOfVideo == 'movie':
            method = 'SetMovieDetails'
            idname = 'movieid'
        else:  # music video
            method = 'SetMusicVideoDetails'
            idname = 'musicvideoid'

        # https://github.com/xbmc/xbmc/commit/408ceb032934b3148586500cc3ffd34169118fea
        query = {
            "jsonrpc": "2.0",
            "id": "setResumePoint",
            "method": "VideoLibrary." + method,
            "params": {
                idname: libraryId,
                "resume": {
                    "position": seconds,
                    # "total": 0 # Not needed: https://forum.kodi.tv/showthread.php?tid=161912&pid=1596436#pid1596436
                }
            }
        }

        log("Executing JSON-RPC: " + json.dumps(query))
        jsonResponse = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        log("VideoLibrary." + method + " response: " + json.dumps(jsonResponse))
    def __init__(self, *args):
        xbmc.Player.__init__(self)
        log('MyPlayer - init')

    def onPlayBackPaused(self):
        global g_pausedTime
        g_pausedTime = time()
        log('Paused. Time: %d' % g_pausedTime)

    def onPlayBackEnded(self):  # video ended normally (user didn't stop it)
        log("Playback ended")
        updateResumePoint(-1)
        autoplayrandomIfEnabled()

    def onPlayBackStopped(self):
        log("Playback stopped")
        updateResumePoint(-2)
        # autoplayrandomIfEnabled() # if user stopped video, they probably don't want a new random one to start

    def onPlayBackSeek(self, time, seekOffset):
        log("Playback seeked (time)")
        updateResumePoint(self.getTime())

    def onPlayBackSeekChapter(self, chapter):
        log("Playback seeked (chapter)")
        updateResumePoint(self.getTime())

    def onAVStarted(self):
        handlePlayback()
