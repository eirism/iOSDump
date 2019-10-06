# Fork of idolpx/iOSDump
Dump contents of an iOS device iTunes backup

# Differences from upstream
* Ported to Python 3
* Removed the Kivy UI
* Removed JSON database dumps


# How to use
To run the program use this command.
```
$ python iosdump.py
```

## Currently extracts the following
* Call History*
* Calendar*
* Camera Roll Images & Video files
* Contacts*
* Contacts images
* Notes*
* SMS & iMessage messages*
* SMS & iMessage attachments
* Voice Memos
* Voicemail Messages

\* Only the SQLite database file is extracted

## Ideas for improvements
* Recover Restriction Passcode
* Extract Browser History & Bookmarks
* Support encrypted & icloud backups
* Show progress in UI during dumping process
* Add option to specify where to dump the data
* Add option to select where backup is stored
  (For selecting backups on a removable/network drive)
* Support plugins for extracting App Specific data
  (Facebook, Messenger, WhatsApp, Kik, Tinder, etc.)
