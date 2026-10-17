import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


xbmc = SimpleNamespace(Player=object, sleep=Mock())
logger = Mock()
playback = Mock()
with patch.dict(sys.modules, {
    'xbmc': xbmc,
    'xbmcvfs': Mock(),
    'bossanova808': SimpleNamespace(),
    'bossanova808.constants': SimpleNamespace(PROFILE=''),
    'bossanova808.logger': SimpleNamespace(Logger=logger),
    'bossanova808.notify': SimpleNamespace(Notify=Mock()),
    'bossanova808.playback': SimpleNamespace(Playback=playback),
    'bossanova808.utilities': SimpleNamespace(
        send_kodi_json=Mock(),
        get_setting=lambda _name: '',
        get_setting_as_bool=lambda _name: False,
    ),
}):
    from resources.lib.player import KodiPlayer, Store


class PlaybackStartTests(unittest.TestCase):
    def setUp(self):
        logger.reset_mock()
        playback.reset_mock()
        xbmc.sleep.reset_mock(side_effect=True)
        state = patch.multiple(
            Store,
            current_playback=object(),
            paused_time=10,
            file_to_store_playback='',
            kodi_event_monitor=Mock(),
        )
        state.start()
        self.addCleanup(state.stop)
        Store.kodi_event_monitor.abortRequested.return_value = False
        self.player = KodiPlayer()
        self.player.isPlayingVideo = Mock(return_value=False)
        self.player.isPlaying = Mock(return_value=True)
        self.player.getPlayingFile = Mock(return_value='audio.flac')
        self.player.getPlayingItem = Mock()

    def assert_skipped(self):
        self.assertIsNone(Store.current_playback)
        self.assertIsNone(Store.paused_time)
        self.player.getPlayingItem.assert_not_called()
        playback.assert_not_called()

    def test_idle_callback_skips_without_reading_a_file(self):
        self.player.isPlaying.return_value = False

        self.player.onAVStarted()

        self.assert_skipped()
        self.player.getPlayingFile.assert_not_called()
        xbmc.sleep.assert_not_called()

    def test_audio_callback_logs_the_file_and_skips_tracking(self):
        self.player.onAVStarted()

        self.assert_skipped()
        self.assertTrue(any('audio.flac' in call.args[0] for call in logger.info.call_args_list))
        xbmc.sleep.assert_not_called()

    def test_audio_stop_after_status_check_returns_without_a_traceback(self):
        self.player.getPlayingFile.side_effect = RuntimeError('nothing playing')

        self.player.onAVStarted()

        self.assert_skipped()
        self.assertTrue(any('stopped' in call.args[0].lower() for call in logger.info.call_args_list))
        xbmc.sleep.assert_not_called()

    def test_video_stop_during_startup_delay_returns_without_a_traceback(self):
        self.player.isPlayingVideo.return_value = True
        self.player.getPlayingFile.side_effect = RuntimeError('nothing playing')

        self.player.onAVStarted()

        self.assert_skipped()
        self.assertTrue(any('stopped' in call.args[0].lower() for call in logger.info.call_args_list))
        xbmc.sleep.assert_called_once_with(1500)

    def test_shutdown_during_startup_delay_returns_without_a_traceback(self):
        self.player.isPlayingVideo.return_value = True
        self.player.getPlayingFile.side_effect = RuntimeError('nothing playing')

        def shutdown(_milliseconds):
            Store.kodi_event_monitor.abortRequested.return_value = True
            self.player.isPlaying.return_value = False

        xbmc.sleep.side_effect = shutdown

        self.player.onAVStarted()

        self.assert_skipped()
        xbmc.sleep.assert_called_once_with(1500)

    def test_video_callback_still_records_playback_details(self):
        self.player.isPlayingVideo.return_value = True
        self.player.isPlaying.return_value = False
        self.player.getPlayingFile.return_value = 'video.mkv'

        self.player.onAVStarted()

        self.assertIs(Store.current_playback, playback.return_value)
        Store.current_playback.update_playback_details.assert_called_once_with(
            'video.mkv', self.player.getPlayingItem.return_value,
        )
        xbmc.sleep.assert_called_once_with(1500)

    def test_unexpected_file_error_remains_visible(self):
        self.player.isPlayingVideo.return_value = True
        self.player.getPlayingFile.side_effect = ValueError('unexpected failure')

        with self.assertRaises(ValueError):
            self.player.onAVStarted()


if __name__ == '__main__':
    unittest.main()
