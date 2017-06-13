# iOSDump
Dump contents of an iOS device iTunes backup

This project was intended to get me failiar with [Kivy](https://kivy.org) and also to help me learn how data is stored in an iTunes backup file.

The goal was to dump all of the data from a backup of an iOS device along with an HTML/CSS user interface to simulate the device in a browser to be able to access all of the extracted data.

First make sure you have [Kivy](https://kivy.org) installed.

Then to launch the program with the Kivy UI run the following command.
```
$ python iosdumpui.py
```

To launch the program with a text interface use this command instead.
```
$ python iosdump.py
```

## Currently Extracts the following
* Call History
* Camera Roll Images & Video files
* Contacts
* Notes
* Recordings
* SMS Messages & Attachments
* Voicemail Messages


## To-Do
* Build HTML/CSS device simulators
* Build HTML/CSS app simulators for displaying specific data
* Automatically launch browser with index.html after dump is complete
* Support encrypted backups
* Show progress in UI during dumping process
* Add option to specify where to dump the data
* Add option to select where backup is stored
  (For selecting backups on a removable/network drive)
* Support plugins for extracting App Specific data
  (Facebook, Messenger, What's App, Kik, Tinder, etc.)
  
