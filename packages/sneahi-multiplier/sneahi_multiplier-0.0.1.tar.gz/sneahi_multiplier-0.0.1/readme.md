# pwp_packs

The pwp_packs package contains utility tools. Currently, it includes a Screen Recorder tool that can record your system screen in any resolution, along with audio.

Developed by Vivek Kumar - ProgresswithPython (c) 2024  (www.youtube.com/c/progresswithpython)


## Examples of How To Use Screen Recorder Tool

```python
from pwp_packs.screenrecorder import ScreenRecorder

recorder = ScreenRecorder("test.mp4")
recorder.start()
input("enter to stop recording...")
recorder.stop()

#You can use the overwrite parameter with True to overwrite the file if it already exists.
recorder = ScreenRecorder("test.mp4",overwrite=True) #it will overwrite test.mp4 if exists.
recorder.start()
input("enter to stop recording...")
recorder.stop()

# By Default, Mouse will be recorded but if you don't want to recorde mouse then make "draw_mouse" parameter False
#recorder = ScreenRecorder("test.mp4", overwrite = True, draw_mouse = False)

```
```python
from pwp_packs.screenrecorder import ScreenRecorder

#you can define duration also
recorder = ScreenRecorder("test.mp4",duration=30)
recorder.start() #it will record for 30 seconds

```
with Audio

```python
from pwp_packs.screenrecorder import ScreenRecorder,get_audio_devices

get_audio_devices() # Print the name of audio devices available in your system
# audio_names = get_audio_devices(text=True) # This will return the name of audio devices in text format
# print(audio_names)

# Copy the name of that audio devices you want to record into a list
audio_devices = ["Microphone Array (Realtek(R) Audio)","Stereo Mix (Realtek(R) Audio)"] # Taking two audio devices to record, Note: audio devices name may varies from system to system.

recorder = ScreenRecorder("test.mp4",audio_devices=audio_devices)
recorder.start()
input("enter to stop recording...")
recorder.stop()

#you can define delays in audio input devices if audio is aheading or not sync with video

audio_delays = [0,1000] # 1 second delay in stereo mix input device
recorder = ScreenRecorder("test.mp4",audio_devices=audio_devices,audio_delays = audio_delays)
recorder.start()
input("enter to stop recording...")
recorder.stop()

```
To see all Screen Recorder Parameters

```python
from pwp_packs.screenrecorder import ScreenRecorder

print(ScreenRecorder.__doc__)
```

Using ScreenRecorderGUI

```python
from pwp_packs.screenrecorder import ScreenRecorderGUI

recorder = ScreenRecoderGUI(filename_prefix = "PWP.mp4")  # filename prefix with video extension
recorder.show() # It will show a small gui with start and stop button with recording timer in the top center of your screen

# Right click on gui to get option to close gui.

# You can provide the width,height for gui and x,y for gui position.(optional)
recorder = ScreenRecorderGUI(filename_prefix = "PWP.mp4", width = 500, height = 50, x=0,y=0,background_color = "blue")
recorder.show()

# Note: ScreenRecorderGUI rest parameter are same as ScreenRecorder parameter.

```