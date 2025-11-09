# Achieve Dramatic Printing!
---
Hello! This is a class that would provide a `print()` method (weird, huh) that would add extra delay after each character printed!
To use this as the normal print, simply override it like this:

```python
from dramaprint import Dramaprint # import the dramaprint object
printObj = Dramaprint()
print = printObj.print # strange, huh
print('Hello, World!') # now it would output it slowly

printObj.setDelay(0.02) # you can also change the delay
print('Hello Again!') # now it would output much faster!

sound_path = "path\\to\\your\\sound.wav" # Here is a typing sound effect (get it yourself)
print('Hello Again Again!', soundPath=sound_path) # now it should play your sound after EACH CHAR
print('Again...?', soundPath=sound_path, soundPerLine=True) # sound per LINE
```

1. import `Dramaprint` class from the script containing it
2. get a variable and assign it to `Dramaprint()` (You can set other things too in `__init__()` like delay)
3. (Optional) Override the default `print()` with your obj (say printObj) like this: `print = printObj.print`
4. You MUST set a delay, either in `__init__()` or with `printObj.setDelay()`. Missing this step would cause failiure.
5. You can use it!
6. If you have a typing-sound effect sound file (best in .wav, but .mp3 is fine), you can include the path and soundPerLine arg to make the print function play your sound!


Play around with it!
I have provided a example typing sound effect for you to use
I found it quite useful in my projects  
Hope you'll have fun!

### Enjoy :)