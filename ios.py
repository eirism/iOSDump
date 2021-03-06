#!/usr/bin/python

"""
Sources on backup format:
http://www.imactools.com/iphonebackupviewer/
http://www.securitylearn.net/2012/05/05/iphone-backup-mbdb-file-structure/
http://www.securitylearn.net/tag/iphone-backups-decrypting-the-keychain/
https://theiphonewiki.com/wiki/ITunes_Backup
http://www.mobile60s.com/iphone/jailbreaks-and-ios-hacks/list-of-files-and-their-roles-in-itunes-backups-and-how-to-use-them-54158.html
http://codepen.io/samuelkraft/pen/Farhl
http://stackoverflow.com/questions/3085153/how-to-parse-the-manifest-mbdb-file-in-an-ios-4-0-itunes-backup
http://linuxsleuthing.blogspot.com/2012/10/whos-texting-ios6-smsdb.html
http://www.securitylearn.net/2012/10/27/cookies-binarycookies-reader/
http://www.slideshare.net/ohprecio/iphone-forensics-without-iphone-using-itunes-backup
https://en.wikipedia.org/wiki/List_of_iOS_devices
"""  # noqa

import shutil
import os
import os.path
from os.path import expanduser
from pathlib import Path

import re
import hashlib
import sqlite3
from biplist import readPlist

# Setup Global Vars
default_backup_path = expanduser("~") + "/Library/Application Support/MobileSync/Backup/"


def hash_ios(value):
    return hashlib.sha1(value.encode()).hexdigest()


# iOS Specific Filenames and hashes

# 51a4616e576dd33cd2abadfea874eb8ff246bf0e
plistKeyChain = 'KeychainDomain-keychain-backup.plist'
plistHistory = 'HomeDomain-Library/Safari/History.plist'
plistRestrictions = 'HomeDomain-Library/Preferences/com.apple.springboard.plist'

database_list = [
    # 3d0d7e5fb2ce288813306e4d4636395e047a3d28
    ['sms', 'HomeDomain-Library/SMS/', 'sms.db'],
    # 31bb7ba8914766d4ba40d6dfb6113c8b614be442
    ['address_book', 'HomeDomain-Library/AddressBook/', 'AddressBook.sqlitedb'],
    # cd6702cea29fe89cf280a76794405adb17f9a0ee
    ['address_book_images', 'HomeDomain-Library/AddressBook/', 'AddressBookImages.sqlitedb'],
    # 5a4935c78a5255723f707230a451d79c540d2741
    ['call_history', 'HomeDomain-Library/CallHistoryDB/', 'CallHistory.storedata'],
    # ca3bc056d4da0bbf88b5fb3be254f3b7147e639c
    ['notes', 'HomeDomain-Library/Notes/', 'notes.sqlite'],
    # 2041457d5fe04d39d0ab481178355df6781e6858
    ['calendar', 'HomeDomain-Library/Calendar/', 'Calendar.sqlitedb'],
    # 992df473bbb9e132f4b3b6e4d33f72171e97bc7a
    ['voicemail', 'HomeDomain-Library/Voicemail/', 'voicemail.db'],
    # 12b144c0bd44f2b3dffd9186d3f9c05b917cee25
    ['cameraroll', 'CameraRollDomain-Media/PhotoData/', 'Photos.sqlite'],
    # 303e04f2a5b473c5ca2127d65365db4c3e055c05
    ['recordings', 'MediaDomain-Media/Recordings/', 'Recordings.db'],
    ['bookmarks', 'HomeDomain-Library/Safari/', 'Bookmarks.db'],
    ['locations', '', ''],
]

databases = {}
for database_info in database_list:
    name = database_info[0]
    path = database_info[1]
    filename = database_info[2]
    full_path = path + filename
    filehash = hash_ios(full_path)

    databases[name] = {'path': path,
                       'filename': filename,
                       'full_path': full_path,
                       'filehash': filehash}


class ios:
    'Base class for all iOS backup file functions'

    # Device Model Strings
    devices = {
                "iPhone1,1": "iPhone",
                "iPhone1,2": "iPhone 3",
                "iPhone2,1": "iPhone 3GS",
                "iPhone3,1": "iPhone 4",
                "iPhone3,2": "iPhone 4",
                "iPhone3,3": "iPhone 4",
                "iPhone4,1": "iPhone 4S",
                "iPhone5,1": "iPhone 5",
                "iPhone5,2": "iPhone 5",
                "iPhone5,3": "iPhone 5C",
                "iPhone5,4": "iPhone 5C",
                "iPhone6,1": "iPhone 5S",
                "iPhone6,2": "iPhone 5S",
                "iPhone7,2": "iPhone 6",
                "iPhone7,1": "iPhone 6 Plus",
                "iPhone8,1": "iPhone 6S",
                "iPhone8,2": "iPhone 6S Plus",
                "iPhone8,4": "iPhone SE",
                "iPhone9,1": "iPhone 7",
                "iPhone9,3": "iPhone 7",
                "iPhone9,2": "iPhone 7 Plus",
                "iPhone9,4": "iPhone 7 Plus",
                "iPod1,1": "iPod Touch 1G",
                "iPod2,1": "iPod Touch 2G",
                "iPod3,1": "iPod Touch 3G",
                "iPod4,1": "iPod Touch 4G",
                "iPod5,1": "iPod Touch 5G",
                "iPod7,1": "iPod Touch 6G",
                "iPad1,1": "iPad",
                "iPad2,1": "iPad 2",
                "iPad2,2": "iPad 2",
                "iPad2,3": "iPad 2",
                "iPad2,4": "iPad 2",
                "iPad3,1": "iPad 3",
                "iPad3,2": "iPad 3",
                "iPad3,3": "iPad 3",
                "iPad3,4": "iPad 4",
                "iPad3,5": "iPad 4",
                "iPad3,6": "iPad 4",
                "iPad4,1": "iPad Air",
                "iPad4,2": "iPad Air",
                "iPad4,3": "iPad Air",
                "iPad5,3": "iPad Air 2",
                "iPad5,4": "iPad Air 2",
                "iPad6,11": "iPad (2017)",
                "iPad6,12": "iPad (2017)",
                "iPad2,5": "iPad Mini",
                "iPad2,6": "iPad Mini",
                "iPad2,7": "iPad Mini",
                "iPad4,4": "iPad Mini 2",
                "iPad4,5": "iPad Mini 2",
                "iPad4,6": "iPad Mini 2",
                "iPad4,7": "iPad Mini 3",
                "iPad4,8": "iPad Mini 3",
                "iPad4,9": "iPad Mini 3",
                "iPad5,1": "iPad Mini 4",
                "iPad5,2": "iPad Mini 4",
                "iPad6,7": "iPad Pro (12.9in)",
                "iPad6,8": "iPad Pro (12.9in)",
                "iPad6,3": "iPad Pro (9.7in)",
                "iPad6,4": "iPad Pro (9.7in)"
            }

    deviceType = ''
    deviceModel = ''
    productType = ''
    productVersion = ''
    serialNumber = ''
    deviceName = ''
    lastBackupDate = ''
    targetIdentifier = ''

    # Hash iOS Filenames
    plistKeyChain = hash_ios(plistKeyChain)
    plistHistory = hash_ios(plistHistory)
    plistRestrictions = hash_ios(plistRestrictions)

    def __init__(self, path=default_backup_path):
        """ The given path should only contain iOS backups """
        self.index = 0
        self.backup_path = path
        self.backups = os.listdir(self.backup_path)

    def select(self, index):
        self.index = index
        plistInfo = self.path(index) + "Info.plist"
        if os.path.exists(plistInfo):
            info = readPlist(plistInfo)
            m = re.match(r"(.*?)\d", info['Product Type'])
            self.deviceType = m.group(1)
            self.deviceModel = self.devices[info['Product Type']]
            self.productType = info['Product Type'].replace(',', '').lower()
            self.productVersion = info['Product Version']
            self.serialNumber = info['Serial Number']
            self.deviceName = info['Device Name']
            self.lastBackupDate = info['Last Backup Date']
            self.targetIdentifier = info['Target Identifier']

        #self.dumpRestrictionPasscode(index)

    # Return Backup Path
    def path(self, index=-1):
        if index == -1:
            backup = self.backup_path + self.backups[self.index] + "/"
        else:
            backup = self.backup_path + self.backups[index] + "/"

        return backup

    def filehash_path(self, filehash):
        """ Return full path for the given filehash """
        return os.path.join(self.path(), filehash[:2], filehash)

    def file_path(self, filename):
        """ Return full path for the given filename """
        filehash = hash_ios(filename)
        return self.filehash_path(filehash)

    # Dump Restriction Passcode
    def dumpRestrictionPasscode(self, index):
        plistRestrictions = self.filehash_path(self.plistRestrictions)
        if os.path.exists(plistRestrictions):
            info = readPlist(plistRestrictions)
            self.restrictionPasscode = info['SBParentalControlsPIN']
            self.restrictionFailedAttempts = info['SBParentalControlsFailedAttempts']

    def dumpDBs(self, path, *dbs):
        for db in dbs:
            if db not in databases:
                print("{} is not a valid database name. Valid names are {}.".format(db, ", ".join(databases.keys())))
            else:
                database_info = databases[db]
                db_path = self.filehash_path(database_info['filehash'])
                filename = database_info['filename']
                if os.path.exists(db_path):
                    shutil.copyfile(db_path, os.path.join(path, 'db', filename))
                else:
                    print("The database file for {} does not exist in the backup.".format(db))

    # SMS, MMS, iMessages, and iMessage/FaceTime settings
    # HomeDomain
    # Library/Preferences/com.apple.imservice*
    # Library/Preferences/com.apple.madrid.plist
    # Library/Preferences/com.apple.MobileSMS.plist
    # Library/SMS/*
    # Library/SMS/Attachments/[random string associated with an MMS]/[MMS file name].[extension] - An MMS file
    # Library/SMS/Attachments/[random string associated with an MMS]/[MMS file name]-preview-left.jpg - A preview/thumbnail of an MMS file
    def dumpSMS(self, path):
        if int(self.productVersion.split('.')[0]) < 6:
            # Save all SMS Attachments iOS < 6.0
            sql = "SELECT * FROM msg_pieces"
            db_path = self.filehash_path(databases['sms']['filehash'])
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(sql)
            for row in cursor:
                if row['content_loc'] is not None:
                    # Write each attachment out to the sms folder
                    f = "MediaDomain-Library/SMS/Attachments/" + row['content_loc']
                    f = self.file_path(f)
                    print(f)
                    if os.path.exists(f):
                        shutil.copyfile(f, path + "sms/" + row['content_loc'])
            db.close()
        else:
            # Save all SMS Attachments iOS >= 6.0
            sql = "SELECT * FROM attachment"
            db_path = self.filehash_path(databases['sms']['filehash'])
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(sql)
            for row in cursor:
                if row['filename'] is not None:
                    # Write each attachment out to the sms folder
                    f = row['filename']
                    f = f.replace("/var/mobile/", "MediaDomain-")
                    f = f.replace("~/", "MediaDomain-")
                    f = self.file_path(f)
                    print(f)
                    if os.path.exists(f):
                        head, tail = os.path.split(row['filename'])
                        shutil.copyfile(f, path + "sms/" + tail)
            db.close()

    # Contacts
    # HomeDomain
    # Library/AddressBook/*
    def dumpAddressBook(self, path):
        # Dump Address Book Images
        db_path = self.filehash_path(databases['address_book_images']['filehash'])
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        sql = "SELECT * FROM ABFullSizeImage"
        cursor.execute(sql)
        for row in cursor:
            # Write each image out to the contacts folder
            outfile = path + "contacts/%s.jpg" % row['record_id']
            print(outfile)
            with open(outfile, "wb") as f:
                f.write(row['data'])
        db.close()

    # Camera Roll - When replacing, you should delete all files in the respected folders first
    # CameraRollDomain
    # Media/DCIM/*
    # Media/PhotoData/*
    # Library/Preferences/com.apple.mobileslideshow.plist
    # Media/DCIM/[number1]APPLE/IMG_[number2].[extension]
    # Media file in the Camera Roll, be it photo, screenshot, video, or saved from elsewhere.
    # Number1 is the number of the Camera Roll, which depends on how many Camera Rolls you've had and ranges from 100-999.
    # Number2 is the chronological number of the file in the Camera Roll, which ranges from 0001-9999.
    # Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_[number of video in Camera Roll].JPG - Preview image of a video in the Camera Roll before you press the play button
    # Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_[number of video in Camera Roll].THM - Thumbnail of a video in the Camera Roll
    # Media/PhotoData/Metadata/PhotoData/Sync/[number >= 100]SYNCD/IMG_[number of video in Camera Roll].JPG - Corresponds to its parallel in Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_number of video in Camera Roll].JPG
    # Media/PhotoData/Metadata/PhotoData/Sync/[number >= 100]SYNCD/IMG_[number of video in Camera Roll].THM - Corresponds to its parallel in Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_number of video in Camera Roll].THM
    def dumpCameraRoll(self, path):
        sql = '''SELECT ZGENERICASSET.Z_PK AS id,
                    ZGENERICASSET.ZKIND AS kind,
                    ZGENERICASSET.ZWIDTH AS width,
                    ZGENERICASSET.ZHEIGHT AS height,
                    ZGENERICASSET.ZORIENTATION AS orientation,
                    ZGENERICASSET.ZDURATION as duration,
                    ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE as filesize,
                    ZGENERICASSET.ZDIRECTORY AS directory,
                    ZGENERICASSET.ZFILENAME AS filename,
                    ZGENERICASSET.ZUNIFORMTYPEIDENTIFIER AS type,
                    ZGENERICASSET.ZTHUMBNAILINDEX AS thumbnail_index,
                    ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILWIDTH,
                    ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILHEIGHT,
                    ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILLENGTH,
                    ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILOFFSET,
                    datetime(ZGENERICASSET.ZDATECREATED+978307200, 'unixepoch', 'localtime') AS creation_date,
                    datetime(ZGENERICASSET.ZMODIFICATIONDATE+978307200, 'unixepoch', 'localtime') AS modified_date
                FROM ZGENERICASSET INNER JOIN ZADDITIONALASSETATTRIBUTES ON ZGENERICASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
                WHERE ZGENERICASSET.ZDATECREATED is not NULL
                ORDER BY ZGENERICASSET.ZDATECREATED ASC'''

        db_path = self.filehash_path(databases['cameraroll']['filehash'])
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(sql)
        cameraroll_base = "CameraRollDomain-Media"
        for row in cursor:
            base_dst_path = os.path.join(path, "roll", row['directory'])
            Path(base_dst_path).mkdir(parents=True, exist_ok=True)
            # Copy each image to the roll folder
            normal_path = "/".join([cameraroll_base, row['directory'], row['filename']])
            f = self.file_path(normal_path)
            if os.path.exists(f):
                print(f)
                shutil.copyfile(f, os.path.join(base_dst_path, row['filename']))

            # Copy video thumbnails to roll folder
            if row['kind'] == 1:
                thumbnail_name = os.path.splitext(row['filename'])[0]
                base_file = "{}/PhotoData/Metadata/{}/{}".format(cameraroll_base, row['directory'], thumbnail_name)
                for extension in ['.THM', '.JPG']:
                    f = self.file_path(base_file + extension)
                    if os.path.exists(f):
                        print(f)
                        shutil.copyfile(f, os.path.join(base_dst_path, row['filename'] + extension))
        db.close()

    # Voicemail
    # HomeDomain
    # Library/Voicemail/*
    def dumpVoicemail(self, path):
        sql = '''SELECT voicemail.ROWID as id,
                    voicemail.remote_uid,
                    voicemail.sender,
                    voicemail.duration,
                    voicemail.flags,
                    datetime(voicemail.date+978307200, 'unixepoch', 'localtime') as 'date',
                    datetime(voicemail.trashed_date+978307200, 'unixepoch', 'localtime') as 'trashed_date'
                FROM voicemail
                ORDER BY voicemail.date'''

        db_path = self.filehash_path(databases['voicemail']['filehash'])
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor:
            # Copy each voicemail
            vm = "HomeDomain-Library/Voicemail/" + str(row['id']) + ".amr"
            vm = self.file_path(vm)
            print(vm)
            if os.path.exists(vm):
                shutil.copyfile(vm, path + "vm/" + str(row['id']) + ".amr")
        db.close()

    # Voice Memos
    # MediaDomain
    # Media/Recordings/*
    # Media/Recordings/[date] [time].m4a - Voice Memo, named YYYYMMDD HHMMSS.m4a
    def dumpMemos(self, path):
        sql = '''SELECT ZRECORDING.Z_PK as id,
                    ZRECORDING.ZCUSTOMLABEL as label,
                    ZRECORDING.ZDURATION as duration,
                    ZRECORDING.ZPATH as path,
                    datetime(ZRECORDING.ZDATE+978307200, 'unixepoch', 'localtime') as 'date'
                FROM ZRECORDING
                ORDER BY ZDATE'''

        db_path = self.filehash_path(databases['recordings']['filehash'])
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor:
            # Copy each recording
            vm = row['path']
            vm = vm.replace("/var/mobile/", "MediaDomain-")
            vm = self.file_path(vm)
            print(vm)
            if os.path.exists(vm):
                shutil.copyfile(vm, path + "rec/" + str(row['id']) + ".m4a")
        db.close()
