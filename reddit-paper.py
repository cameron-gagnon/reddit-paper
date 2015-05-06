#!/usr/bin/env python3.4

# Created by Cameron Gagnon
# Version: alpha
# Contact: cgagnon@umich.edu or 
#          cameron.gagnon@gmail.com
#
# If you have any questions, comments or concerns,
# or improvements to this code,
# feel free to email me and we can go from there.
# I'd love to help anyone use this to make their
# desktop backgrounds always look awesome.
# If you're having trouble using this program,
# please reach out and I can try
# my best to help you out!
#
# This is under the GNU GPL V3 so use it
# and modify it however you want
#
# Inspiration for this program came
# from: http://goo.gl/729Qdg
# and: http://goo.gl/2MD8tZ 
# Check 'em out and give 'em some love

#what to import
import praw
import sqlite3
import pprint
import argparse
import ctypes
import json
import os
import subprocess
import random
import re
import sys 
import time
import urllib.request
import subprocess
import logging
import logging.handlers
from bs4 import BeautifulSoup
from collections import OrderedDict
from distutils import spawn
from socket import timeout
from urllib.error import HTTPError,URLError

#sets up global vars
CREDENTIALS = "user_pass.txt"
SUBREDDITS = "earthporn"
USERAGENT = "Reddit wallpaper changer script /u/camerongagnon " \
            "beta testing"
SETWALLPAPER = "gsettings set org.gnome.desktop.background " \
               "picture-uri " \
               "file:///media/cameron/Fresh500/pictures/wallofpapers"\
                                                                "/reddit/"
DOWNLOADLOCATION = "/media/cameron/Fresh500/pictures/wallofpapers"\
                                                                "/reddit/"


### BEGIN LOGGING CONFIG
# configures logging to external file
# set file logger
rootLog = logging.getLogger('')
rootLog.setLevel(logging.DEBUG)
# set format for output to file
formatFile = logging.Formatter(fmt='%(asctime)-s %(levelname)-6s: '\
                                   '%(lineno)d : %(message)s',
                               datefmt='%m-%d %H:%M')
# add filehandler so once the filesize reaches 5MB a new file is 
# created, up to 5 files
fileHandle = logging.handlers.RotatingFileHandler(
                            "CrashReport.log", maxBytes=5000000, backupCount=3)
fileHandle.setFormatter(formatFile)
rootLog.addHandler(fileHandle)
# configures logging to console
# set console logger
console = logging.StreamHandler()
console.setLevel(logging.ERROR) #toggle console level output with this line
# set format for console logger
consoleFormat = logging.Formatter('%(levelname)-6s %(message)s')
console.setFormatter(consoleFormat)
# add handler to root logger so console && file are written to
logging.getLogger('').addHandler(console)
c_logger = logging.getLogger('reddit-paper')
### END LOGGING CONFIG


# declared as global in functions so we can
# decrement MAXPOSTS when we encounter an img
# that != width/height requirements. This is
# because in Cycle_wallpaper, it will cycle
# the list of images from 0 to MAXPOSTS
MAXPOSTS = 5
image_list = []
sql = sqlite3.connect('wallpaper.db')
cur = sql.cursor()

# make sure to have a file in the same directory with your username
# on the first line, and password on the second
def main():
    global cur
    global sql
    try:
        Parse_cmd_args()
    
        with open(CREDENTIALS, 'r') as infile: 
            #removes the newline character at end of
            #each line so login will work
            USERNAME = infile.readline().rstrip('\n')
            PASSWORD = infile.readline().rstrip('\n')
        
        c_logger.info("Accessing database for submission ID's")
        cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT,\
                              Name TEXT, Width INT, Height INT)')
        sql.commit()
        
        r = Login(USERNAME, PASSWORD)
    
        c_logger.info("Fetching subreddits from %s", SUBREDDITS)
        subreddit = r.get_subreddit(SUBREDDITS)
        
        c_logger.info("Pulling top %s posts", MAXPOSTS)
        Get_data_from_pic(subreddit)
        
        Cycle_wallpaper()
        
        sql.close()
        c_logger.debug("################################################"
                       "################################################\n")
    except KeyboardInterrupt:
        c_logger.info("CTRL + C entered from command line, exiting...")
        sys.exit(0)

### METHOD IMPLEMENTATIONS
####################################################################
#REQUIRES url
#MODIFIES nothing
#EFFECTS  returns true if able to connect to specified url, returns
#         false if not able to connect, or timesout
def Connected(url):
    try:
        uaurl = urllib.request.Request(url,
                 headers={'User-Agent' : USERAGENT})
        url = urllib.request.urlopen(uaurl,
                                     timeout = 3)

        content = url.read().decode('utf-8')
        json.loads(content)
        url.close()
        return True
    except (AttributeError, ValueError):
        return False

####################################################################
#REQUIRES USERNAME, PASSWORD
#MODIFIES connection to reddit
#EFFECTS  Attempts to login to Reddit using the provided username
#         and password.
def Login(USERNAME, PASSWORD):
    
    c_logger.info("Logging in as %s ...", USERNAME)
    
    if not Connected("https://www.reddit.com/.json"):
        c_logger.error("You do not appear to be connected to Reddit.com",
              "this is likely due to a redirect by the internet connection",
              "you are on. Check to make sure no login is required, and try",
              "again.")
        sys.exit(0)

    r = praw.Reddit(user_agent = USERAGENT)
    r.login(USERNAME, PASSWORD)
    return r

####################################################################
#REQUIRES url
#MODIFIES url
#EFFECTS  Returns the static download URL of the file, specific
#         to Flickr. This S.O. post helped:
# https://stackoverflow.com/questions/21673323/download-flickr-images-of-specific-url
#
# This is a list of titles and how to determine size based on ending characters -
# _o (original file) is used here as it is most reliable,
# although likely sometimes very large
# https://www.flickr.com/services/api/misc.urls.html
def Flickr_parse(url):
    try:
        #gets the page and reads the hmtl into flickr_html
        flickr_html = urllib.request.urlopen(url).read()
        #searches for static flickr url within webpage
        flickr_html = flickr_html.decode('utf-8')
        img_link = re.findall(r"""
                              farm      #farm is always in static img url
                              [^"\\:]*  #characters not to capture
                              _[o|k|h|b]\.  #_o indicates original img per flickr standards
                              [jpg|png|gif]* #file format is either png, jpg, or gif
                              """, flickr_html, re.VERBOSE)[0]    
        url = 'https://' + img_link

        c_logger.debug("img_link from flickr regex: %s", img_link)
        #generates image_name from static url
        if img_link == []:
            return False, False
        
        remove_index = img_link.rindex('/')                        
        image_name =  img_link[-(len(img_link) - remove_index - 1):]
        
        return image_name, url
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        c_logger.warning("Exception occured in Flickr_parse",
                         exc_info = True)
        return False, False

####################################################################
#REQUIRES url
#MODIFIES url, image_name
#EFFECTS  Returns the image_name and url of the correct link to
#         download from. 500px.com sometimes 'protects' the photos
#         so they are not as easily programatically downloaded,
#         however the links in the html provide the 'static' download
#         link
def Five00px_parse(url):
    try:
        #refer to Flickr_parse for explanation of this method
        px_html = urllib.request.urlopen(url).read()
        px_html = px_html.decode('utf-8')
    
        img_link = re.findall(r'https://drscdn.500px.org/photo[^"][\w/%]*', px_html)[0]
        url = img_link
    
        if img_link == []:
            return False, False
    
        remove_index = img_link.rindex('/')
        image_name = img_link[-(len(img_link) - remove_index - 1):]
    
        return image_name, url
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        c_logger.warning("Exception occured in Five00px_parse", 
                         exc_info = True)
        return False, False

####################################################################
#REQUIRES url of image to be renamed 
#MODIFIES nothing
#EFFECTS  Outputs the image title and URL of the photo being downloaded
#         instead of the long URL it comes in as
def Title_from_url(url, pid):
    try:
        #finds last forward slash in index and then slices
        #the url up to that point + 1 to just get the image
        #title
        regex_result = re.findall(r'^(?:https?:\/\/)?(?:www\.)?([^\/]+)',\
                                                    url, re.IGNORECASE)
        c_logger.debug("Regex (domain) from URL is: %s ", regex_result)
        
        if regex_result[0] == "i.imgur.com" or \
           regex_result[0] == "imgur.com":
    
            remove = url.rindex('/')                        
            image_name =  url[-(len(url) - remove - 1):]
            
            #makes the url have the same domain instead of
            #just imgur.com
            if image_name.rfind(".") == -1:
                
                image_name += ".jpg"
                url = "http://i.imgur.com/" + image_name
                
                c_logger.debug("Image_name is: %s ", image_name)
                
                return image_name, url
            else:
                c_logger.debug("Image_name is: %s ", image_name)
                
                return image_name, url

        elif (regex_result[0].find("staticflickr") != -1):
            remove = url.rindex('/')                        
            image_name =  url[-(len(url) - remove - 1):]
            
            return image_name, url

        elif (regex_result[0].find("flickr") != -1):
            
            # returns image_name, url
            return Flickr_parse(url)
 
        elif (regex_result[0].find("500px.com") != -1):

            return Five00px_parse(url)
        else:
            remove = url.rindex('/')
            
            if remove == -1:
                image_name = pid + '.jpg'
            else:    
                image_name =  url[-(len(url) - remove - 1):]
                c_logger.info("Image_name is: %s", image_name)
                
            return image_name, url
    
    except ValueError:
        c_logger.exception("Error in finding title from URL", exc_info=True)
        return False, False

####################################################################
#REQUIRES id of submission in question
#MODIFIES nothing
#EFFECTS  Checks if the id of the submission has already been
#         downloaded. Does not redownload the image if already
#         present. Otherwise downloads it.
def Already_downloaded(pid, image_name):
    global cur
    cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
    result = cur.fetchone()

    c_logger.debug("Result of Already_downloaded is: %s", result)
    
    if result and not Check_width_height(pid):
        return True
    
    elif result: # need to add check here that file is actually downloaded
                 # instead of basing it on past min-width/min-height requirements
                 # as those might have changed when running program again
        c_logger.info("Picture: %s is already downloaded, will not "
                      "download again unless "
                      "forced to.", image_name)
        return True
    else:
        return False            

####################################################################
#REQUIRES id of submission to insert
#MODIFIES database of id's already downloaded
#EFFECTS  Inserts the submission id into the database after a 
#         successful download
def Insert_to_db(pid, image_name, width, height):
    global cur
    global sql
    
    c_logger.info("Data to insert\n\t\t\t\t\t\t  Pid: %s"\
                  "\n\t\t\t\t\t\t  image_name: %s"\
                  "\n\t\t\t\t\t\t  width: %s"\
                  "\n\t\t\t\t\t\t  height: %s",
                  pid, image_name, width, height) 
    
    cur.execute('INSERT INTO oldposts VALUES(?, ?, ?, ?)',\
                [pid, image_name, width, height])
    sql.commit()

####################################################################
#REQUIRES Full title of post which requires the reslotuion of the
#         image
#MODIFIES nothing
#EFFECTS  Returns true if 
def Valid_width_height(submission_title, pid, image_name):
    try:
        result = re.findall(r'([0-9,]+)\s*(?:x|\*|×|\xc3\x97|xd7)\s*([0-9,]+)',\
                            submission_title, re.IGNORECASE | re.UNICODE)        
        c_logger.debug("Regex from width/height: %s", result)
        #print(result, '\n')

        result1 = result[0][0]
        result2 = result[0][1]
        result1 = re.sub("[^\d\.]", "", result1)
        result2 = re.sub("[^\d\.]", "", result2)
        
        c_logger.debug("Width: %s \n\t\t\t\t\t\t  Height: %s", result1, result2)
        
        Insert_to_db(pid, image_name, result1, result2)         
        return Lookup_width_height(pid, image_name)

    except IndexError:
        c_logger.debug("The title of the submission does not appear"
              " to be formatted correctly. Skipping"
              " submission and trying the next one.")
####################################################################
#REQUIRES width, height from valid pid in database
#MODIFIES nothing
#EFFECTS  Returns true if the width and height are above specified
#         dimensions
def Check_width_height(pid):
    cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
    lookup = cur.fetchone()
    
    c_logger.debug("Lookup from Check_width_height: %s", lookup)
    
    width = lookup[2]
    height = lookup[3]
    
    try:
        if ((int(width) > MINWIDTH) and \
            (int(height) > MINHEIGHT)):
            return True
        else:
            return False
    except ValueError:
        c_logger.exception("Incorrect type comparison for width and height"
              " most likely an incorrect parsing of title.", exc_info=True)

####################################################################
#REQUIRES width, height and ID of the image
#MODIFIES nothing
#EFFECTS  Returns true if the image is greater than the width and 
#         height requirements set by the user.
def Lookup_width_height(pid, image_name):
    if  Check_width_height(pid):
        c_logger.info("Image: %s fits required size.", image_name)
        return True
    else:
        c_logger.info("Image: %s does not fit required size. "
                      "Will not download.", image_name)
        return False

####################################################################
#REQUIRES url
#MODIFIES image_name, local_save, picdl
#EFFECTS  Sets the image_name to the title of the download.
#         Passes out the full download location. Opens the file from
#         the specified url.
def Set_up_url(url, image_name):
    picdl = urllib.request.Request(url, headers = { 'User-Agent': USERAGENT})
    
    local_save = DOWNLOADLOCATION + image_name
    
    #returns a tuple that is assigned correctly after
    #this function returns
    c_logger.debug("URL is: %s", url)
    try:
        picdl = urllib.request.urlopen(picdl)
        return local_save, picdl
    except urllib.error.HTTPError as err:
        c_logger.exception("ERROR: occured in Set_up_url!!!!\n", exc_info=True)
####################################################################
#REQUIRES url, image_name, local_save, cur, sql
#MODIFIES file on hard drive, image_list
#EFFECTS  Prints out the download name and location, then saves the
#         picture to that spot.
def Img_download(url, image_name, local_save, picdl, pid):
    global image_list
    
    c_logger.info("downloading: %s \n\t\t\t\t\t\t  as: %s "\
                  "\n\t\t\t\t\t\t  to: %s",
                  url, image_name, local_save)
    
    with open(DOWNLOADLOCATION + image_name, "wb") as picfile:
        picfile.write(picdl.read())
        image_list.append(image_name)

####################################################################
#REQUIRES url 
#MODIFIES download location, adds new picture to file
#EFFECTS  Downloads a new picture from the url specified and saves
#         it to the location specified from DOWNLOADLOCATION.
def Get_data_from_pic(subreddit):
    global image_list
    global MAXPOSTS
    global cur
    global sql
    
    i = 1        
    for post in subreddit.get_hot(limit = MAXPOSTS):
        
        c_logger.debug("POST %d @@@@@@@@@@@@@@@@@@@@@@@@@@@@@", i)
        c_logger.debug("Title of post: %s \n\t\t\t\t\t\t  Id of post: %s"
                       "\n\t\t\t\t\t\t  URL of post: %s",
                       post.title, post.id, post.url)

        pid = post.id
        url = post.url
        submission_title = post.title
        image_name, url = Title_from_url(url, pid)
        
        if (not image_name or not url):
            MAXPOSTS -= 1
                        
        else:
            if not Already_downloaded(pid, image_name):
                if  Valid_width_height(submission_title,\
                                       pid, image_name):
                    local_save, picdl = Set_up_url(url, image_name)
                    Img_download(url, image_name, local_save, picdl, pid)
                else:
                    MAXPOSTS -= 1
            elif not Check_width_height(pid):
                                MAXPOSTS -= 1 
            else:
                #Append the pic if already downloaded so
                #when Cycle_wallpaper is called, it will
                #still use the current MAXPOSTS posts on
                #Reddit.
        
                #The reason for this is if a search is
                #cancelled before all images are
                #downloaded, then some images will be
                #available but we do not want to download
                #them again. Thus they will not be added
                #to the current image_list until this
                #statement takes place.
                
                image_list.append(image_name)
        i += 1
    c_logger.debug("Exiting Get_data_from_pic fn")

####################################################################
#REQUIRES setpaper is the command particular to each 
#         gnome/desktop environment version that will set the 
#         wallpaper via the command line
#MODIFIES wallpaper on backgroun
#EFFECTS  Sets the wallpaper of the system to be image_name
def Set_wallpaper(image_name):
    try:                            
        subprocess.call(args = SETWALLPAPER + image_name, 
                        shell = True)
        c_logger.debug("Wallpaper should be set to: %s"
                           " Cycle time: %d seconds",
                           image_name, (CYCLETIME*60))
                            
    except KeyboardInterrupt:
            sys.exit(0)
    except:
        c_logger.exception("Error setting wallpaper, it is likely the "
              "file path is not 100% correct. Make sure "
              "there is a foward slash at the end of the "
              "path in the SETWALLPAPER variable.", exc_info=True)
        sys.exit(1)

###################################################################
#REQUIRES SETWALLPAPER command, and image_list 
#MODIFIES wallpaper background of the computer
#EFFECTS  Cycles through the wallpapers that are given by the titles
#         in the image_list list, based on the CYCLETIME
def Cycle_wallpaper():
    global image_list
    
    c_logger.debug("MAXPOSTS is: %s", MAXPOSTS)
    
    for i in range(0, MAXPOSTS, 1):
        Set_wallpaper(image_list[i])
        time.sleep(CYCLETIME*60)

###################################################################
#REQUIRES command line args
#MODIFIES some of the global variables declared at top of program
#EFFECTS  Sets variables to modify output of program and change 
#         default options to user specified ones.
def Parse_cmd_args():
    global MINWIDTH
    global MINHEIGHT
    global CYCLETIME
    global MAXPOSTS
    parser = argparse.ArgumentParser(description="Downloads"
            " images from user specified subreddits and sets"
            " them as the wallpaper.")
    parser.add_argument("-mw", "--minwidth", type = int,
                        help="Minimum width of picture required "
                             "to download", default = 1024)
    parser.add_argument("-mh", "--minheight", type = int,
                        help="Minimum height of picture required "
                             "to download", default = 768)
    parser.add_argument("-mp", "--maxposts", type = int,
                        help="Amount of images to check and "
                             "download", default = 5)
    parser.add_argument("-t", "--cycletime", type = float,
                        help="Amount of time (in minutes) each image "
                             "will be set as wallpaper", default = .05)
    args = parser.parse_args()
    
    MINWIDTH = int(args.minwidth)
    MINHEIGHT = int(args.minheight)
    MAXPOSTS = int(args.maxposts)
    CYCLETIME = float(args.cycletime)
    
###################################################################
if __name__ == '__main__':
    main()
