import subprocess

## Only for macOS

class SoundPlayer:
    @staticmethod
    def play(sound_name="Tink"):
        """
        Play a system sound on macOS.
        Common sound names: 'Tink', 'Funk', 'Ping', 'Pop', 'Purr', 'Sosumi', 'Basso', 'Blow', 'Bottle', 'Frog', 'Glass'
        """
        try:
            subprocess.run(['afplay', f'/System/Library/Sounds/{sound_name}.aiff'])
        except Exception:
            print('\a')