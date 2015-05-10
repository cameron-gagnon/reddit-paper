#!/usr/bin/env python3.4

# Created by Cameron Gagnon
# Version: beta
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
SUBREDDITS = "wallpapers"
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
console.setLevel(logging.DEBUG) #toggle console level output with this line
# set format for console logger
consoleFormat = logging.Formatter('%(levelname)-6s %(message)s')
console.setFormatter(consoleFormat)
# add handler to root logger so console && file are written to
logging.getLogger('').addHandler(console)
log = logging.getLogger('reddit-paper')
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
        
        log.info("Accessing database for submission ID's")
        cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT,\
                              Name TEXT, Width INT, Height INT)')
        sql.commit()
        
        r = Login(USERNAME, PASSWORD)
    
        log.info("Fetching subreddits from %s", SUBREDDITS)
        subreddit = r.get_subreddit(SUBREDDITS)
        
        log.info("Pulling top %s posts", MAXPOSTS)
        Get_data_from_pic(subreddit)
        
        Cycle_wallpaper()
        
        sql.close()
        log.debug("################################################"
                       "################################################\n")
    except KeyboardInterrupt:
        log.info("CTRL + C entered from command line, exiting...")
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
    except (HTTPError, URLError, timeout, AttributeError, ValueError):
        log.error("You do not appear to be connected to Reddit.com."
                       " Tthis is likely due to a redirect by the internet connection"
                       " you are on. Check to make sure no login is required and the"
                       " connection is stable, and then try again.")
        return False

####################################################################
#REQUIRES valid USERNAME, PASSWORD
#MODIFIES connection to reddit
#EFFECTS  Attempts to login to Reddit using the provided username
#         and password.
def Login(USERNAME, PASSWORD):
    
    log.info("Logging in as %s ...", USERNAME)
    
    if not Connected("https://www.reddit.com/.json"):
        sys.exit(0)

    r = praw.Reddit(user_agent = USERAGENT)
    r.login(USERNAME, PASSWORD)
    return r

####################################################################
#REQUIRES img_link
#MODIFIES img_link
#EFFECTS  Performs operations on url to derive image name and then
#         returns the img_name
def General_parser(img_link):
    if img_link == []:
        return False
        
    remove_index = img_link.rindex('/')                        
    image_name =  img_link[-(len(img_link) - remove_index - 1):]
    return image_name

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
        
        #soup = BeautifulSoup(flickr_html)

        img_link = re.findall(r"""
                              farm      # farm is always in static img url
                              [^"\\:]*  # characters to not capture
                              _[o|k|h|b]\.  # _o indicates original img per 
                                              # flickr standards
                              [jpg|png|gif]* # file format is either 
                                             # png, jpg, or gif
                              """, flickr_html, re.VERBOSE)[0]    
        url = 'https://' + img_link

        log.debug("img_link from flickr regex: %s", img_link)
        #generates image_name from static url
        
        return General_parser(img_link), url
    except KeyboardInterrupt:
        sys.exit(0)
    
    # no links/an error occured in finding links in html of page
    except IndexError:
        log.debug("Did not find any links in Flickr_parse")
    
    # this (UnicodeDecodeError) is thrown when the file link is 
    # given to read, and cannot be decoded to "utf-8" therefore,
    # we just need to download the img normally anyway
    except UnicodeDecodeError:
        return General_parser(url), url
    except Exception:
        log.warning("Exception occured, or image does not fit"
                    " required size in Flickr_parse",
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
            
        return General_parser(img_link), url
    except KeyboardInterrupt:
        sys.exit(0)
    except IndexError:
        log.debug("No links found in Five00px_parse")
    except UnicodeDecodeError:
        return General_parser(url), url
    except Exception:
        log.warning("Exception occured in Five00px_parse", 
                         exc_info = True)
    return False, False
####################################################################
# Very similar to Five00px_parse and Flickr_parse, look through there
# for details of workings on this method
def Deviant_parse(url):
    try:
        dev_html = urllib.request.urlopen(url).read()
        dev_html = dev_html.decode('utf-8')
    
        img_link = re.findall(r'src="[\w=":;,%_ /.\n-]* class="dev-content-normal"',
                              dev_html)[0]
        link = re.findall(r'http://[\w./%-]*', img_link)[0]
        url = link
        
        return General_parser(link), url
    except KeyboardInterrupt:
        sys.exit(0)
    except IndexError:
        log.debug("No links found in Deviant_parse")

    # this exception is when the good img url to download is
    # passed in. Since this url when opened is not html, it throws
    # this error, so we know we must find the image title and return
    # the url passed in
    except UnicodeDecodeError:
        return General_parser(url), url
    except Exception:
        log.warning("Exception occured in Deviant_parse",
                         exc_info = True)
        return False, False
####################################################################
# REQUIRES url in imgur formatting
# MODIFIES url, image_name
# EFFECTS  Returns the image name from the url. Helper function to
#          imgur parse function.
def Imgur_image_format(url):
    # finds last '/' in url
    remove = url.rindex('/')
    # returns only past the last '/'
    image_name =  url[-(len(url) - remove - 1):]
    
    if image_name.rfind('.') == -1:
        image_name = image_name + ".jpg"
        
    log.debug("Image name is: %s", image_name)
    return image_name

####################################################################
# REQUIRES valid imgur url
# MODIFIES image_name
# EFFECTS  Retrives direct image link from imgur.com when posted
#          as either an album, or gallery. 
#   An album example: https://imgur.com/a/dLB0
#   A gallery example: https://imgur.com/gallery/fDdj6hw
def Imgur_parse(url, regex):

    # check if it's a gif or not from imgur. These don't
    # download/display
    if (url.rfind(".gif") != -1)\
        or (url.rfind(".gifv") != -1):
        
        log.debug("Image is likely a gif or gifv, not downloading")
        return False, False 

    # then check if it's a direct link
    elif regex == "i.imgur.com":
        image_name = Imgur_image_format(url)
        return image_name, url

    # check if an imgur.com/gallery link
    elif (url.find('/gallery/') != -1):
        image_name = Imgur_image_format(url)
        url = "https://i.imgur.com/" + image_name   
        return image_name, url

    # /a/ means an album in imgur standards
    elif (url.find('/a/') != -1):
        # have to find new url to download the first image from album
        uaurl = urllib.request.Request(url, headers = { 'User-Agent': USERAGENT})
        imgur_html = urllib.request.urlopen(uaurl)
        soup = BeautifulSoup(imgur_html)
        
        #   | class=image  w/ child <a> | gets href of this <a> child |
        url = soup.select('.image a')[0].get('href')
        url = "https:" + url
        image_name = Imgur_image_format(url)
        return image_name, url

    # a regular imgur.com domain but no img type in url
    elif regex == "imgur.com":
        image_name = Imgur_image_format(url)
        url = "https://i.imgur.com/" + image_name
        return image_name, url

    # if we get here, there's like a format of url error
    else:
        log.debug("Something went wrong in Imgur_parse")
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
        log.debug("Regex (domain) from URL is: %s ", regex_result)
        
        # imgur domain
        if regex_result[0] == "imgur.com" or \
           regex_result[0] == "i.imgur.com":
           
            # check if we encountered bad data such as a gif or gifv
            return1, return2 = Imgur_parse(url, regex_result[0])
            if not return1:
                return False, False, False
            else:
                return return1, return2, True

        # staticflickr domain
        elif (regex_result[0].find("staticflickr") != -1):
            remove = url.rindex('/')                        
            image_name =  url[-(len(url) - remove - 1):]
            
            return image_name, url, True
        # flickr domain
        elif (regex_result[0].find("flickr") != -1):
            
            image_name, url = Flickr_parse(url)
            
            return image_name, url, True
        # 500px domain
        elif (regex_result[0].find("500px.com") != -1):
            
            image_name, url = Five00px_parse(url)

            return image_name, url, True
        # deviantart domain
        elif (regex_result[0].find("deviantart") != -1):
            
            image_name, url = Deviant_parse(url)
            
            return image_name, url, True

        # pic.ms just a slight change in url formatting
        elif (regex_result[0].find("pic.ms") != -1):
            url = re.sub(r'html/', '', url)
            image_name = General_parser(url)
            return image_name, url, True

        # all other domains with image type in url
        elif (url.find(".jpg") != -1) or (url.find(".png") != -1)\
             or (url.find(".gif") != -1):
            
            return General_parser(url), url, True

        else:
            remove = url.rindex('/')
            
            if remove == -1:
                image_name = pid + '.jpg'
            else:    
                image_name =  url[-(len(url) - remove - 1):]
                log.info("Image_name is: %s", image_name)
                
            return image_name, url, False
    
    except ValueError:
        log.exception("Error in finding title from URL", exc_info=True)
        return False, False, False

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

    log.debug("Result of Already_downloaded is: %s", result)
    
    if result and not Check_width_height(pid):
        return True
    
    elif result: # need to add check here that file is actually downloaded
                 # instead of basing it on past min-width/min-height requirements
                 # as those might have changed when running program again
        log.info("Picture: %s is already downloaded, will not "
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
    
    log.info("Data to insert\n\t\t\t\t\t\t  Pid: %s"\
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
        log.debug("Regex from width/height: %s", result)

        result1 = result[0][0]
        result2 = result[0][1]
        # 'erases' commas in title
        result1 = re.sub("[^\d\.]", "", result1)
        result2 = re.sub("[^\d\.]", "", result2)
        
        log.debug("Width: %s \n\t\t\t\t\t\t  Height: %s", result1, result2)
        
        Insert_to_db(pid, image_name, result1, result2)         
        return Lookup_width_height(pid, image_name)

    except IndexError:
        log.debug("The title of the submission does not appear"
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
    
    log.debug("Lookup from Check_width_height: %s", lookup)
    
    width = lookup[2]
    height = lookup[3]
    
    try:
        if ((int(width) > MINWIDTH) and \
            (int(height) > MINHEIGHT)):
            return True
        else:
            return False
    except ValueError:
        log.exception("Incorrect type comparison for width and height"
              " most likely an incorrect parsing of title.", exc_info=True)

####################################################################
#REQUIRES width, height and ID of the image
#MODIFIES nothing
#EFFECTS  Returns true if the image is greater than the width and 
#         height requirements set by the user.
def Lookup_width_height(pid, image_name):
    if  Check_width_height(pid):
        log.info("Image: %s fits required size.", image_name)
        return True
    else:
        log.info("Image: %s does not fit required size. "
                      "Will not download.", image_name)
        return False

####################################################################
#REQUIRES url, image_name, local_save, cur, sql
#MODIFIES file on hard drive, image_list
#EFFECTS  Prints out the download name and location, then saves the
#         picture to that spot.
def Download_img(url, image_name, pid):
    global image_list
    
    #gets the pic download information and sets the download location
    picdl = urllib.request.Request(url, headers = { 'User-Agent': USERAGENT})
    local_save = DOWNLOADLOCATION + image_name
    log.debug("URL is: %s", url)

    try:
        picdl = urllib.request.urlopen(picdl)

    except urllib.error.HTTPError as err:
        log.exception("ERROR: occured in Setting up the url!!\n",
                           exc_info=True)
        return False

    log.info("downloading: %s \n\t\t\t\t\t\t  as: %s "\
                  "\n\t\t\t\t\t\t  to: %s",
                  url, image_name, local_save)
    
    with open(DOWNLOADLOCATION + image_name, "wb") as picfile:
        picfile.write(picdl.read())
        image_list.append(image_name)
    
    return True
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
 
        pid = post.id
        url = post.url
        submission_title = post.title
       
        log.debug("POST %d @@@@@@@@@@@@@@@@@@@@@@@@@@@@@", i)
        log.debug("Title of post: %s \n\t\t\t\t\t\t  Id of post: %s"
                  "\n\t\t\t\t\t\t  URL of post: %s",
                  submission_title, pid, url)
        
        image_name, url, is_deviant = Title_from_url(url, pid)
        
        log.debug("is_deviant is: %s", is_deviant)

        if (not image_name or not url):
            MAXPOSTS -= 1
                        
        else:
            if not Already_downloaded(pid, image_name):
                if  Valid_width_height(submission_title,
                                       pid, image_name) and\
                    Download_img(url, image_name, pid):
                    log.debug("Image successfully downloaded with"
                            " WxH in title")

                elif is_deviant and\
                     Download_img(url, image_name, pid):
                    # specifically for subs w/o WxH in title, but still
                    # have images to download (e.x. imaginarystarscapes)
                    log.debug("Image successfully downloaded WITHOUT"
                              " WxH in title")
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
    log.debug("Exiting Get_data_from_pic fn")

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
        log.debug("Wallpaper should be set to: %s"
                           " Cycle time: %d seconds",
                           image_name, (CYCLETIME*60))
                            
    except KeyboardInterrupt:
            sys.exit(0)
    except:
        log.exception("Error setting wallpaper, it is likely the "
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
    
    log.debug("MAXPOSTS is: %s", MAXPOSTS)
    
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
