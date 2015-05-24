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
# Inspiration for this program came from: 
# http://goo.gl/729Qdg
# http://goo.gl/2MD8tZ 
# Check 'em out and give 'em some love

#what to import
import praw
import sqlite3
import pprint
import argparse
import json
import os
import subprocess
import re
import sys 
import time
import urllib.request
import subprocess
import logging
import logging.handlers
import getpass
from PIL import Image
from bs4 import BeautifulSoup
from socket import timeout
from urllib.error import HTTPError,URLError
from requests.exceptions import ConnectionError

#sets up global vars
CREDENTIALS = "user_pass.txt"
SUBREDDITS = "futureporn+wallpapers+lavaporn+earthporn+imaginarystarscapes+spaceporn"
USERAGENT = "Reddit wallpaper changer script /u/camerongagnon " \
            "beta testing"
SETWALLPAPER = "gsettings set org.gnome.desktop.background picture-uri "\
               "file:///media/cameron/Fresh500/pictures/wallofpapers"\
                                                                "/reddit/"
DOWNLOADLOCATION = "/media/cameron/Fresh500/pictures/wallofpapers"\
                                                                "/reddit/"

# MANY DEFAULT VALUES ARE DECLARED GLOBAL IN THE PARSE ARGUMENTS
# FUNCTION TO SET UP THE VALUES FOR THE RUN OF THE PROGRAM

# declared as global in functions so we can
# decrement MAXPOSTS when we encounter an img
# that != width/height requirements. This is
# because in Cycle_wallpaper, it will cycle
# the list of images from 0 to MAXPOSTS
image_list = []


# make sure to have a file in the same directory with your username
# on the first line, and password on the second
def main():
    global cur
    global sql
    try:
        # preliminary functions
        Config_logging()
        Parse_cmd_args()
        # checks if a single link was entered by the user to download
        Single_link()
        Create_DB()    
        
        r = Login()
        # this is the main function that will download and parse
        # the images
        Main_photo_controller(r)
        Cycle_wallpaper()

        sql.close()

        # this is printed for ease of use when viewing the debug file
        log.debug("################################################"
                  "################################################\n")
    except KeyboardInterrupt:
        log.info("CTRL + C entered from command line, exiting...")
        sql.close()
        sys.exit(0)


####################################################################
### CLASS IMPLEMNTATIONS
####################################################################


class Img():
    """
        Creates an img instance for each post found when returning
        content from reddit, encapsulates title, id, image name, etc.
        into one container to operate on.
    """

    def __init__(self, post):
        self.setProperties(post)
 
    def setProperties(self, post):
        self.setTitle(post.title)
        self.setLink(post.url)
        self.setID(post.id)

    def setImgName(self, image_name):
        self.image_name = image_name
        self.setSaveLoc()

    def setTitle(self, title):
        self.title = title

    def setLink(self, link):
        self.link = link

    def setID(self, id):
        self.id = id

    def setSaveLoc(self):
        self.save_location = DOWNLOADLOCATION + str(self.image_name)

    def formatImgName():
        # finds last '/' in url
        remove = url.rindex('/')
        # returns only past the last '/'
        self.image_name =  url[-(len(url) - remove - 1):]

    def setAsWallpaper(self):
        """ Sets the image as the wallpaper. This is called toward the
            end of the program, so the image_name, and save location
            should be set.
        """

        try:                            
            subprocess.call(args = SETWALLPAPER + self.image_name, 
                            shell = True)
            log.debug("Wallpaper should be set to: %s "
                      "Cycle time: %d seconds",
                      self.image_name, (CYCLETIME*60))
                                
        except KeyboardInterrupt:
                sys.exit(0)
        except:
            log.exception("Error setting wallpaper, it is likely the "
                          "file path is not 100% correct. Make sure "
                          "there is a foward slash at the end of the "
                          "path in the SETWALLPAPER variable.", exc_info=True)
            sys.exit(1)
########################################################################


class SingleImg():
    """
        Downloads the image from the link manually entered by the user
    """
    def __init__(self, link):
        if link:
            self.download(link)
            self.setAsWallpaper()

    def download(self, link):
        """ Downloads the image to the save location  """
        remove = link.rindex('/')                        
        self.image_name = link[-(len(link) - remove - 1):]

        # gets the pic download information and sets the download location
        picdl = urllib.request.Request(link, headers = { 'User-Agent': USERAGENT})
        save_location = DOWNLOADLOCATION + self.image_name
    
        try:
            picdl = urllib.request.urlopen(picdl)
    
        except urllib.error.HTTPError:
            log.exception("Could not open the specified picture webpage!!\n",
                          exc_info = True)
            sys.exit(0)
    
        log.info("Downloading: %s \n\t\t\t\t\t\t  as: %s "\
                 "\n\t\t\t\t\t\t  to: %s",
                 self.link, self.image_name, self.save_location)
        
        with open(save_location, "wb") as picfile:
            picfile.write(picdl.read())
        

    def setAsWallpaper(self):
        """ Sets the image entered as the wallpaper """

        try:                            
            subprocess.call(args = SETWALLPAPER + self.image_name, 
                            shell = True)
            log.debug("Wallpaper should be set to: %s", self.image_name)
                                
        except KeyboardInterrupt:
                sys.exit(0)
        except:
            log.exception("Error setting wallpaper, it is likely the "
                          "file path is not 100% correct. Make sure "
                          "there is a foward slash at the end of the "
                          "path in the SETWALLPAPER variable.",
                          exc_info = True)
            sys.exit(1)
########################################################################


class DBImg():
    """
        Creates an encapsulation of data about previously downloaded
        images by looking it up in the database. This is called to create
        the image list for the past pictures page in the GUI
    """

    def __init__(self, image_name):
        setLookUpInfo(image_name)

    def setLookUpInfo(self, image_name):
        self.title,
        self.link,
        self.width,
        self.height = cur.execute('SELECT ImgTitle, ImgLink, Width, Height\
                                  FROM oldposts WHERE ImgName=?',
                                  [image_name])
        self.save_location = DOWNLOADLOCATION + image_name

    def setResolution(self):
        self.resolution = self.width + 'x' + self.height
########################################################################


class PictureList():
    """
        Returns information/list of images that have been downloaded
        by the program for use in the GUI to display the past images
    """

    def list_pics():
        cur.execute('SELECT * FROM oldposts')
        results = cur.fetchall()
        image_list = []
        for image in results:
            pic = DBImg(image[1])
            image_list.append(pic)
        return image_list


####################################################################
### METHOD IMPLEMENTATIONS
####################################################################

def Config_logging():
    """ Configures the logging to external file """
    global log

    # set file logger
    rootLog = logging.getLogger('')
    rootLog.setLevel(logging.DEBUG)
    
    # set format for output to file
    formatFile = logging.Formatter(fmt='%(asctime)-s %(levelname)-6s: '\
                                       '%(lineno)d : %(message)s',
                                   datefmt='%m-%d %H:%M')
    
    # add filehandler so once the filesize reaches 5MB a new file is 
    # created, up to 3 files
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

#####################################################################
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
        
    except (HTTPError, URLError, timeout, AttributeError, ValueError):
        log.error("You do not appear to be connected to Reddit.com."
                  " This is likely due to a redirect by the internet connection"
                  " you are on. Check to make sure no login is required and the"
                  " connection is stable, and then try again.")
        sys.exit(0)

####################################################################
#REQUIRES valid USERNAME, PASSWORD
#MODIFIES connection to reddit
#EFFECTS  Attempts to login to Reddit using the provided username
#         and password.
def Login():
    
    Connected("https://www.reddit.com/.json")
    r = praw.Reddit(user_agent = USERAGENT)

   
    tries = 3
    login = False
    while(tries and not login):
        # check if the username/password is in the database
        cur.execute('SELECT Username, Password FROM userpass')
        if cur.fetchone() is None:

            USERNAME = input("Please enter your Reddit username: ")
            PASSWORD = getpass.getpass("Please enter your password: ")
            cur.execute('INSERT INTO userpass Values(?, ?)', 
                        [USERNAME, PASSWORD])
            sql.commit()
        
        try:
            cur.execute('SELECT Username, Password FROM userpass')
            USERNAME, PASSWORD = cur.fetchone()
            r.login(USERNAME, PASSWORD)
            login = True

        except praw.errors.InvalidUserPass:
            print("Incorrect Username/Password.", tries)
            cur.execute('DELETE from userpass')
            sql.commit()
            tries -= 1

    # check if we attempted entering user/pass too many times
    if tries == 0:
        print("Too many invalid tries. Exiting...")
        sys.exit(0)
    
    cur.execute('INSERT INTO userpass Values(?, ?)',
                [USERNAME, PASSWORD])
    log.info("Logging in as %s ...", USERNAME)
    return r

####################################################################

def Create_DB():
    global sql
    global cur

    sql = sqlite3.connect('wallpaper.db')
    cur = sql.cursor()
    
    log.info("Accessing database for submission ID's")
    
    # create image database
    cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT,\
                 ImgName TEXT, ImgTitle TEXT, ImgLink TEXT,\
                 Width INT, Height INT)')

    # create Username and Password database
    cur.execute('CREATE TABLE IF NOT EXISTS userpass(Username TEXT,\
                Password TEXT)')

    # commit dem changes yo
    sql.commit()

####################################################################
#MODIFIES Downloads the image specified by the user 
#EFFECTS  Sets image as wallpaper
def Single_link():
    if SINGLELINK:
        SingleImg(SINGLELINK)

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
        # gets the page and reads the hmtl into flickr_html
        flickr_html = urllib.request.urlopen(url).read()
        # searches for static flickr url within webpage
        flickr_html = flickr_html.decode('utf-8')
        
        # at the moment, BeautifulSoup would be too difficult to 
        # use to parse the html for the link, as the link is not within
        # standard html anyway. (It's located in 'Model Export' towards the
        # bottom of the page)
        img_link = re.findall(r"""
                              farm      # farm is always in static img url
                              [^":]*  # characters to not capture
                              _[o|k|h|b]\.  # _o indicates original img per 
                                              # flickr standards
                              [jpg|png|gif]* # file format is either 
                                             # png, jpg, or gif
                              """, flickr_html, re.VERBOSE)[0]    
        url = 'https://' + img_link
        # finds urls with \ in them so we must remove them
        url = url.replace('\\', '')
        log.debug("img_link from flickr regex: %s", img_link)
        #generates image_name from static url
        
        return General_parser(img_link), url
    except KeyboardInterrupt:
        sys.exit(0)
    
    # no links/an error occured in finding links in html of page
    except (IndexError,TypeError):
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
        px_html = urllib.request.urlopen(url)
    
        img_html = BeautifulSoup(px_html)
        
        # finds the html with class 'the_photo' and returns the src of that elt
        img_link = img_html.select('.the_photo')[0].get('src')
        url = img_link
            
        return General_parser(img_link), url
    except KeyboardInterrupt:
        sys.exit(0)
    except (IndexError,TypeError):
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
def Deviant_parse(url, regex):
    try:

        dev_html = urllib.request.urlopen(url)

        # direct image download link that must begin with
        # fc or orig or pree
        if regex[:2] == "fc" or regex[:4] == "orig" or\
           regex[:3] == "pre":
        
            return General_parser(url), url
        else:
            img_html = BeautifulSoup(dev_html)
        
            # finds all classes with 'dev-content-normal' and finds the src
            # attribute of it
            img_link = img_html.select('.dev-content-normal')[0].get('src')
            url = img_link 
           
            return General_parser(url), url

    except KeyboardInterrupt:
        sys.exit(0)
    except (IndexError, TypeError):
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
    if (url.rfind(".gif") != -1) or (url.rfind(".gifv") != -1):
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

    # if we get here, there's likely a format of url error
    else:
        log.debug("Something went wrong in Imgur_parse")
        return False, False

####################################################################
#REQUIRES url of image to be renamed 
#MODIFIES nothing
#EFFECTS  Outputs the image title and URL of the photo being downloaded
#         instead of the long URL it comes in as
def Title_from_url(im):
    try:
        #finds last forward slash in index and then slices
        #the url up to that point + 1 to just get the image
        #title
        regex_result = re.findall(r'^(?:https?:\/\/)?(?:www\.)?([^\/]+)',\
                                                    im.link, re.IGNORECASE)
        log.debug("Regex (domain) from URL is: %s ", regex_result)
        
        # imgur domain
        if regex_result[0] == "imgur.com" or \
           regex_result[0] == "i.imgur.com":
           
            # check if we encountered bad data such as a gif or gifv
            return1, return2 = Imgur_parse(im.link, regex_result[0])
            if return1:
                return return1, return2, True
            else:
                return False, False, False

        # staticflickr domain
        elif (regex_result[0].find("staticflickr") != -1):
            remove = im.link.rindex('/')                        
            image_name =  im.link[-(len(im.link) - remove - 1):]
            
            return image_name, url, True
        
        # flickr domain
        elif (regex_result[0].find("flickr") != -1):
            
            image_name, url = Flickr_parse(im.link)
            
            return image_name, url, True
        
        # 500px domain
        elif (regex_result[0].find("500px.com") != -1):
            
            image_name, url = Five00px_parse(im.link)

            return image_name, url, True
        # deviantart domain
        elif (regex_result[0].find("deviantart") != -1):
            
            image_name, url = Deviant_parse(im.link, regex_result[0])
            
            return image_name, url, True

        # pic.ms just a slight change in url formatting
        elif (regex_result[0].find("pic.ms") != -1):
            url = re.sub(r'html/', '', im.link)
            image_name = General_parser(im.link)
            return image_name, url, True

        # reddit.com self post
        elif (regex_result[0].find("reddit.com") != -1):
            log.debug("Appears to be a self post from reddit.com")
            return False, False, False

        # all other domains with image type in url
        elif (im.link.find(".jpg") != -1) or (im.link.find(".png") != -1)\
             or (im.link.find(".gif") != -1):
            
            return General_parser(im.link), im.link, True

        else:
            remove = im.link.rindex('/')
            
            if remove == -1:
                image_name = im.id + '.jpg'
            else:    
                image_name =  im.link[-(len(im.link) - remove - 1):]
                log.info("Image_name is: %s", image_name)
                
            return image_name, im.link, False
    
    except ValueError:
        log.exception("Error in finding title from URL", exc_info=True)
        return False, False, False

####################################################################
#REQUIRES id of submission in question
#MODIFIES nothing
#EFFECTS  Checks if the id of the submission has already been
#         downloaded. Does not redownload the image if already
#         present. Otherwise downloads it.
def Already_downloaded(im):
    cur.execute('SELECT * FROM oldposts WHERE ID=?', [im.id])
    result = cur.fetchone()

    log.debug("Result of Already_downloaded is: %s", result)
    
    if result and not Check_width_height(im.id):
        return True
    
    elif result: # need to add check here that file is actually downloaded
                 # instead of basing it on past min-width/min-height requirements
                 # as those might have changed when running program again
        log.info("Picture: %s is already downloaded, will not "
                 "download again unless "
                 "forced to.", im.image_name)
        return True
    else:
        return False            

####################################################################
#REQUIRES id of submission to insert
#MODIFIES database of id's already downloaded
#EFFECTS  Inserts the submission id into the database after a 
#         successful download
def Insert_to_db(im, width, height):
    log.info("Data to insert\n\t\t\t\t\t\t  id: %s"\
             "\n\t\t\t\t\t\t  image_name: %s"\
             "\n\t\t\t\t\t\t  width: %s"\
             "\n\t\t\t\t\t\t  height: %s",
             im.id, im.image_name, width, height) 
    cur.execute('INSERT INTO oldposts VALUES(?, ?, ?, ?, ?, ?)',\
                [im.id, im.image_name, im.title, im.link, width, height])
    sql.commit()

####################################################################
#REQUIRES Full title of post which may have the reslotuion of the
#         image
#MODIFIES nothing
#EFFECTS  Returns true if 
def Valid_width_height(im):
    try:
        result = re.findall(r'([0-9,]+)\s*(?:x|\*|×|\xc3\x97|xd7)\s*([0-9,]+)',\
                            im.title, re.IGNORECASE | re.UNICODE)        
        log.debug("Regex from width/height: %s", result)

        result1 = result[0][0]
        result2 = result[0][1]
        # 'erases' unwanted characters in the title
        result1 = re.sub("[^\d\.]", "", result1)
        result2 = re.sub("[^\d\.]", "", result2)
        
        log.debug("Width: %s \n\t\t\t\t\t\t  Height: %s", result1, result2)
        
        Insert_to_db(im, result1, result2)         
        return Lookup_width_height(im)

    except IndexError:
        log.debug("The title of the submission does not appear"
                  " to contain the width and height of the image.")

####################################################################
#REQUIRES width, height from valid id in database
#MODIFIES nothing
#EFFECTS  Returns true if the width and height are above specified
#         dimensions
def Check_width_height(id):
    cur.execute('SELECT * FROM oldposts WHERE ID=?', [id])
    lookup = cur.fetchone()
    
    log.debug("Lookup from Check_width_height: %s", lookup)
    
    try: 
        width = lookup[4]
        height = lookup[5]
    
        if ((int(width) >= MINWIDTH) and \
            (int(height) >= MINHEIGHT)):
            return True
        else:
            return False

    except ValueError:
        log.exception("Incorrect type comparison for width and height"
                      " most likely an incorrect parsing of title.", 
                      exc_info = True)
    except TypeError:
        log.exception("Likely an image that did not include WxH in title.",
                      exc_info = True)
        return True


######################################################################
#REQUIRES checks the image for the width and height from the PIL module
#MODIFIES nothing
#EFFECTS  Returns true if the width and height are above specified
#         dimensions
def PIL_width_height(image_name):
    try: 
        # get size of image by checking it after it has already downloaded
        with open(DOWNLOADLOCATION + image_name, 'rb') as file:
            image = Image.open(file)
            width, height = image.size

        cur.execute('UPDATE oldposts SET Width=?, Height=? WHERE ImgName=?', 
                    [width, height, image_name])
        sql.commit()

        if ((int(width) >= MINWIDTH) and \
            (int(height) >= MINHEIGHT)):
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
def Lookup_width_height(im):
    if  Check_width_height(im.id):
        log.info("Image: %s fits required size.", im.image_name)
        return True
    else:
        log.info("Image: %s does not fit required size. "
                 "Will not download.", im.image_name)
        return False

####################################################################
#REQUIRES url, image_name, save_location, cur, sql
#MODIFIES file on hard drive, image_list
#EFFECTS  Prints out the download name and location, then saves the
#         picture to that spot.
def Download_img(url, im):
    global image_list
    
    # gets the pic download information and sets the download location
    picdl = urllib.request.Request(url, headers = { 'User-Agent': USERAGENT})
    log.debug("URL is: %s", url)

    try:
        picdl = urllib.request.urlopen(picdl)

    except urllib.error.HTTPError:
        log.exception("ERROR: occured in Setting up the url!!\n",
                           exc_info=True)
        return False

    log.info("Downloading: %s \n\t\t\t\t\t\t  as: %s "\
             "\n\t\t\t\t\t\t  to: %s",
             url, im.image_name, im.save_location)
    
    with open(im.save_location, "wb") as picfile:
        picfile.write(picdl.read())
        image_list.append(im.image_name)
    
    return True
####################################################################
#REQUIRES url 
#MODIFIES download location, adds new picture to file
#EFFECTS  Downloads a new picture from the url specified and saves
#         it to the location specified from DOWNLOADLOCATION.
def Main_photo_controller(r):
    global image_list
    global MAXPOSTS
    
    log.info("Fetching subreddits from %s", SUBREDDITS)
    log.info("Pulling top %s posts", MAXPOSTS)
    log.debug("URL of query is %s", URL)

    i = 1        
    for post in r.get_content(url=URL, limit = MAXPOSTS):
        
        # creates image class which holds necessary data about post
        im = Img(post)
       
        log.debug("POST %d @@@@@@@@@@@@@@@@@@@@@@@@@@@@@", i)
        log.debug("Title of post: %s \n\t\t\t\t\t\t  Id of post: %s"
                  "\n\t\t\t\t\t\t  URL of post: %s",
                  im.title, im.id, im.link)
        
        image_name, url, is_deviant = Title_from_url(im)
        
        log.debug("is_deviant: %s", is_deviant)

        if (not image_name or not url):
            MAXPOSTS -= 1
                        
        else:
            im.setImgName(image_name)

            if not Already_downloaded(im):
                if  Valid_width_height(im) and Download_img(url, im):
                    log.debug("Image successfully downloaded with"
                              " WxH in title")

                elif is_deviant and Download_img(url, im) and \
                     PIL_width_height(im.image_name):
                    # specifically for subs w/o WxH in title, but still
                    # have images to download (e.x. imaginarystarscapes)
                    log.debug("Image successfully downloaded WITHOUT"
                              " WxH in title")
                else:
                    MAXPOSTS -= 1
            elif not Check_width_height(im.id):
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
                
                image_list.append(im.image_name)
        i += 1
    log.debug("Exiting Main_photo_controller fn")

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
    try: 
        for i in range(0, MAXPOSTS, 1):
            Set_wallpaper(image_list[i])
            time.sleep(CYCLETIME*60)
    except IndexError:
        log.error("No posts appear to be in the specific "\
                  "subreddit/category selected. Try another category, or add "
                  "more subreddits to the list.")
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
    global CATEGORY
    global URL
    global SINGLELINK

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
    parser.add_argument("-c", "--category", type = str,
                        help="Ex. hot, new, rising, top", default = "hot")
    parser.add_argument("-l", "--link", type = str,
                        help="Provide a direct image link to download"
                             " just the specified link", default = None) 
    args = parser.parse_args()
    
    MINWIDTH = int(args.minwidth)
    MINHEIGHT = int(args.minheight)
    MAXPOSTS = abs(int(args.maxposts))
    CYCLETIME = float(args.cycletime)
    CATEGORY = str(args.category)
    SINGLELINK = args.link
    URL = "https://www.reddit.com/r/" + SUBREDDITS + "/" + CATEGORY + "/"

###################################################################
if __name__ == '__main__':
    main()
