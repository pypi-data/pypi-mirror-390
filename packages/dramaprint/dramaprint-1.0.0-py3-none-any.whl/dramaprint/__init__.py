# dramaprint/__init__.py
import sys, contextlib, time, os, warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # cleaning anooying banners
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    try:
        import pygame # type: ignore
        moduleExist = True
    except ImportError:
        moduleExist = False

class Dramaprint:
    """Class for dramatic printing with optional sound playback."""

    def __init__(self, delay: float = 0.05):
        """
        Initialize the Dramaprint object.

        Parameters:
            delay (float): Delay between characters in seconds. Default is 0.05.
        """
        self.delay = delay
        warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # cleaning anooying banners

    def setDelay(self, delay: float) -> None:
        """Set a new delay between characters."""
        self.delay = delay

    def playSound(self, soundPath: str) -> None:
        """Play a sound using pygame."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.Sound(soundPath).play()
        except Exception as e:
            if isinstance(e, ImportError):
                print("You ain't got the pygame module!!! WE NEED THOSE FOR SOUND PLAYING!!!")
                print("Try again.")
                sys.exit()
            print(f"\033[1mSound error:\033[0m {type(e).__name__}: {e}")

    def print(self, *args, sep: str = ' ', end: str = '\n', soundPath: str = None, soundPerLine: bool = False) -> None:
        """
        Dramatically prints text to the console, like print() but slower & cooler.

        Parameters:
            *args: Multiple strings or values to print.
            sep (str): Separator between arguments. Default is space.
            end (str): What to print at the end. Default is newline.
            soundPath (str): Path to a sound file to play. Default is None.
            soundPerLine (bool): If True, plays sound per line; else per character. Default is False.
        """
        sound = False

        if soundPath:
            if not os.path.isfile(soundPath):
                print("The file \033[1mdoesn't exist!\033[0m Try again :)")
                sys.exit()
            elif not moduleExist:
                print("You wanted to play sound, but the pygame module \033[1misn't installed!\033[0m Install it and try again.")
                sys.exit()
            else:
                sound = True

        lines = (sep.join(str(arg) for arg in args) + end).splitlines(keepends=True)
        for line in lines:
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(self.delay)
                if sound and not soundPerLine:
                    self.playSound(soundPath)
            if sound and soundPerLine:
                self.playSound(soundPath)

printObj = Dramaprint(0.1)
print = printObj.print
print('Hello, World!')
print('hello, Again!', soundPath="D:\\Setup\\Setup_Files\\typingSound.wav")