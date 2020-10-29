> The original Launch Library API will be closing down on December 31, 2020. Starting November 1, it's successor, Launch Library 2, will take over. This wrapper has not been updated for Launch Library 2, and as such will not work. Unfortunately, I don't have the time to work on this wrapper right now so I've archived the project.

# launchlibrary
A Python wrapper for the wonderful Launch Library API (see https://launchlibrary.net/ for further details)

## What can I do with the Launch Library API?
The [Launch Library API](https://launchlibrary.net/), is a "repository of rocket launch information". You can fetch information about upcoming launches, rockets, missions, and launch locations/pads.

## Usage
### Installation
I've uploaded this package to PyPI, so installation is as easy as:

```
pip install launchlibrary
```

### Basic Usage
Once you've installed the package, the Launch Library API can be accessed like so:

```python
import launchlibrary

LaunchAPI = launchlibrary.LaunchLibrary()

nextLaunch = LaunchAPI.NextLaunch()
launchEvents = LaunchAPI.UpcomingLaunches(launchCount=5, including="Falcon")

print(nextLaunch.name)  # Name of the next launch
print(nextLaunch.window.start)  # Launch window start time
print(nextLaunch.window.net)  # NET - No Earlier Than time (i.e. Scheduled launch time)

for launch in launchEvents:
  print(launch.name)
  print(launch.window.net)
```

I'll make sure to write some more comprehensive documentation soon!

## Acknowledgements
The Launch Library API that this wrapper is based on was designed by Pete Riesett and Benjamin Higginbotham, and run with the support of the Launch Librarians (see https://launchlibrary.net/about.html for a list of all of the project's volunteers.)

This Python wrapper was designed and implemented by Thomas Varnish (https://github.com/tvarnish).
