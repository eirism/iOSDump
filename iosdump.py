#!/usr/bin/python

import shutil
import os
import os.path
from os.path import expanduser

from ios import ios

# Global Variables
selected = -1


# List iTunes Backups
def selectBackup():
    'List all the iOS Backups and prompt for selection'
    global selected

    for i in range(len(iosBackup.backups)):
        iosBackup.select(i)
        print(str(i) + ":\t" + iosBackup.deviceName + " (" + str(iosBackup.lastBackupDate) + ")")

    print()
    selected = input("Select Backup to Dump: ")
    if len(selected) > 0:
        selected = int(selected)
    else:
        selected = 0

    if selected < 0 or selected > len(iosBackup.backups) - 1:
        print("Invalid Selection!")
    else:
        iosBackup.select(selected)
        print("You selected: " + str(selected) + " - " + iosBackup.deviceName + " (" + str(iosBackup.lastBackupDate) + ")")
        iosDumpData(selected)


def cleanFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            else:
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def iosDumpData(selection):
    iosBackup.index = selection

    # Clean Up Previous Dump
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder, 0o755)
    else:
        cleanFolder(outputFolder)

        os.mkdir(outputFolder + "contacts", 0o755)
        os.mkdir(outputFolder + "db", 0o755)
        os.mkdir(outputFolder + "roll", 0o755)
        os.mkdir(outputFolder + "rec", 0o755)
        os.mkdir(outputFolder + "sms", 0o755)
        os.mkdir(outputFolder + "vm", 0o755)

    #print ios.dbRecordings
    #print iosBackup.deviceName(0) + " (" + iosBackup.backups[0] + ")"
    print(outputFolder)
    print(iosBackup.path())

    # Copy Database Files to Output Folder
    iosBackup.dumpDBs(outputFolder,
                      'address_book',
                      'address_book_images',
                      'calendar',
                      'call_history',
                      'notes',
                      'cameraroll',
                      'recordings',
                      'sms',
                      'voicemail')

    print("Dumping SMS Messages")
    iosBackup.dumpSMS(outputFolder)

    print("Dumping Address Book")
    iosBackup.dumpAddressBook(outputFolder)

    print("Dumping Voicemail")
    iosBackup.dumpVoicemail(outputFolder)

    print("Dumping Voice Memos")
    iosBackup.dumpMemos(outputFolder)

    print("Dumping Camera Roll")
    iosBackup.dumpCameraRoll(outputFolder)

    print("Dump Complete!")



iosBackup = ios()
#outputFolder = expanduser("~") + "/Desktop/iOSDump/"
outputFolder = expanduser(".") + "/dump/"
if __name__ == "__main__":
    # Initialize Objects & Set Output Folder
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder, 0o755)
    else:
        cleanFolder(outputFolder)

    print("\nWhich iTunes Backup would you like to dump?\n")
    selectBackup()
