#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created by Cameron Gagnon
# Version: alpha
# Contact: cgagnon@umich.edu or 
#	   cameron.gagnon@gmail.com
#
# If you have any questions, comments or concerns,
# or improvements to this code,
# feel free to email me and we can go from there.
# I'd love to help anyone use this to make their
# desktop backgrounds pretty. If you're having trouble
# using this program, please reach out and I can try
# my best to help you out!
#
# This is under the GPL license, so use it
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
from collections import OrderedDict
from distutils import spawn
from socket import timeout
from urllib.error import HTTPError,URLError

#sets up global vars
CREDENTIALS = "user_pass.txt"
SUBREDDITS = "spaceporn+earthporn"
USERAGENT = "Reddit wallpaper changer script /u/countfapula69 " \
	    "beta testing"
SETWALLPAPER = "gsettings set org.gnome.desktop.background " \
	       "picture-uri " \
	       "file:///media/cameron/Fresh500/pictures/"\
	       			  "wallofpapers/reddit/"
DOWNLOADLOCATION = "/media/cameron/Fresh500/pictures/wallofpapers"\
						        "/reddit/"
MINWIDTH = 1366
MINHEIGHT = 768
CYCLETIME = .05 #in minutes

#declared as global in functions so we can
#decrement MAXPOSTS when we encounter an img
#that != width/height requirements. This is
#because in Cycle_wallpaper, it will cycle
#the list of images from 0 to MAXPOSTS
MAXPOSTS = 10
image_list = []
sql = sqlite3.connect('wallpaper.db')
cur = sql.cursor()


#make sure to have a file in the same directory with your username
#on the first line, and password on the second
def get_wallpaper():
	global cur
	global sql
	with open(CREDENTIALS, 'r') as infile:
		#removes the newline character at end of
		#each line so login will work
		USERNAME = infile.readline().rstrip('\n')
		PASSWORD = infile.readline().rstrip('\n')

	print("Accessing database for submission ID's")
	cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT,\
			      Name TEXT, Width INT, Height INT)')
	sql.commit()
	
	r = Login(USERNAME, PASSWORD)

	print("Fetching subreddits from " + SUBREDDITS)
	subreddit = r.get_subreddit(SUBREDDITS)
	
	print("Pulling top " + str(MAXPOSTS) + " posts\n")
	Get_data_from_pic(subreddit)

	Cycle_wallpaper(SETWALLPAPER)
	
	sql.close()

#METHOD IMPLEMENTATIONS
####################################################################
#REQUIRES url
#MODIFIES nothing
#EFFECTS  returns true if able to connect to specified url, returns
#	  false if not able to connect, or timesout
def Connected(url):
		try:
			uaurl = urllib.request.Request(url,
				 headers={'User-Agent' : USERAGENT})
			url = urllib.request.urlopen(uaurl,
						     timeout = 3)
			url.close()
			return True
		except (ConnectionError, HTTPError, URLError,\
			 timeout):
			return False
####################################################################
#REQUIRES USERNAME, PASSWORD
#MODIFIES connection to reddit
#EFFECTS  Attempts to login to Reddit using the provided username
#	  and password.
def Login(USERNAME, PASSWORD):
	print("Logging in as " + USERNAME)
	try:
		r = praw.Reddit(user_agent = USERAGENT)
		r.login(USERNAME, PASSWORD)
		return r
	except SSLError:
		print("ERROR: You do not appear to be connected to"
		      " the internet, please check your connection"
		      " and try again later.")

	if not Connected("http://www.reddit.com"):
		print("ERROR: You do not appear to be "
		      "connected to Reddit. Exiting")
		sys.exit(1)
	
####################################################################
#REQUIRES url of image to be renamed 
#MODIFIES nothing
#EFFECTS  Outputs the image title of the photo being downloaded
#	  instead of the long URL it comes in as
def Title_from_url(url):
	try:
		#finds last forward slash in index and then slices
		#the url up to that point + 1 to just get the image
		#title
		remove = url.rindex('/')			
		image_name =  url[-(len(url) - remove - 1):]
		if image_name.rfind(".") == -1:
			image_name += ".jpg"

		return image_name

	except ValueError:
		print("Error in finding title from URL")
		sys.exit(1)

####################################################################
#REQUIRES id of submission in question
#MODIFIES nothing
#EFFECTS  Checks if the id of the submission has already been
#	  downloaded. Does not redownload the image if already
#	  present. Otherwise downloads it.
def Already_downloaded(pid, image_name):
	global cur
	cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
	result = cur.fetchone()
#print(result)
	
	if result and not Check_width_height(result[2], \
					     result[3], image_name):
#print("Image " + image_name + " already downloaded.")
		return True
	elif result:
		print("Picture: " + image_name + " is already "
		      "downloaded, will not download again unless "
		      "forced to. \n")
		return True
	else:
		return False		

####################################################################
#REQUIRES id of submission to insert
#MODIFIES database of id's already downloaded
#EFFECTS  Inserts the submission id into the database after a 
#	  successful download
def Insert_to_db(pid, image_name, width, height):
	global cur
	global sql
	cur.execute('INSERT INTO oldposts VALUES(?, ?, ?, ?)',\
				[pid, image_name, width, height])
	sql.commit()

####################################################################
#REQUIRES Full title of post which requires the reslotuion of the
#	  image
#MODIFIES nothing
#EFFECTS  Returns true if 
def Valid_width_height(submission_title, pid, image_name):
	try:
		result = re.findall(\
		r'([0-9]*)(\s*x\s*|x|\s*\xc3\x97\s*|\xc3\x97|\s*\xd7\s*|\xd7)([0-9]*)',\
	 				submission_title, re.IGNORECASE)	
#print(result)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		result1 = result[0][0]
		result2 = result[0][2]
		Insert_to_db(pid, image_name, result1, result2)		
		return Lookup_width_height(pid, image_name)

	except IndexError:
		print("The title of the submission does not appear"
		      " to be formatted correctly. Skipping"
		      " submission and trying the next one.")
####################################################################
#REQUIRES width, height from valid pid in database
#MODIFIES nothing
#EFFECTS  Returns true if the width and height are above specified
#	  dimensions
def Check_width_height(width, height, image_name):
	try:
		if ((int(width) > MINWIDTH) and \
		    (int(height) > MINHEIGHT)):
			return True
		else:
			return False
	except ValueError:
		print("Incorrect type comparison for width and height "
		      "most likely an incorrect parsing of title.")

####################################################################
#REQUIRES width, height and ID of the image
#MODIFIES nothing
#EFFECTS  Returns true if the image is greater than the width and 
# 	  height requirements set by the user.
def Lookup_width_height(pid, image_name):
	cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
	lookup = cur.fetchone()

	width = lookup[2]
	height = lookup[3]
	if  Check_width_height(width, height, image_name):
		print("Image: " + image_name + " fits required "
		      "size.")

		return True
	else:
		 print("Image: " + image_name + " does not fit"
		       " required size. Will not download.\n")
####################################################################
#REQUIRES url
#MODIFIES image_name, local_save, picdl
#EFFECTS  Sets the image_name to the title of the download.
#	  Passes out the full download location. Opens the file from
#	  the specified url.
def Set_up_url(url):
	#it appears this next line does not affect the return value
	#although it may announce the request to the server, giving 
	#them more details about the request
	picdl = urllib.request.Request(url, \
		headers = { 'User-Agent': USERAGENT})

	image_name = Title_from_url(url)
	local_save = DOWNLOADLOCATION + image_name
	try:
		url.rindex(".jpg")
	except ValueError:
		url += ".jpg"
	#returns a tuple that is assigned correctly after
	#this function returns
#print(url)#######################################
	picdl = urllib.request.urlopen(url)
	return image_name, local_save, picdl, url

####################################################################
#REQUIRES url, image_name, local_save, cur, sql
#MODIFIES file on hard drive, image_list
#EFFECTS  Prints out the download name and location, then saves the
#	  picture to that spot.
def Img_download(url, image_name, local_save, picdl, pid):
	global image_list
	
	print ("downloading: " + url + "\nas: " + \
		image_name + "\nto: " + local_save)
	
	with open(DOWNLOADLOCATION + image_name, \
		  "wb") as picfile:
		picfile.write(picdl.read())
		image_list.append(image_name)
		
		print('\n')

####################################################################
#REQUIRES url 
#MODIFIES download location, adds new picture to file
#EFFECTS  Downloads a new picture from the url specified and saves
#	  it to the location specified from DOWNLOADLOCATION.
def Get_data_from_pic(subreddit):
	global image_list
	global MAXPOSTS
	global cur
	global sql
	
	for post in subreddit.get_hot(limit = MAXPOSTS):
		pid = post.id
		url = post.url
		submission_title = post.title
		image_name = Title_from_url(url)

#print(submission_title)

		if not Already_downloaded(pid, image_name):
			if  Valid_width_height(submission_title,\
					pid, image_name):
#pprint.pprint(vars(post))
				image_name, local_save, picdl, \
					url = Set_up_url(url)

				Img_download(url, image_name, \
					    local_save, picdl, pid)
			else:
				MAXPOSTS -= 1
		elif not Lookup_width_height(pid, image_name):
			
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
			
			MAXPOSTS -= 1 

		else:
			image_list.append(image_name)

####################################################################
#REQUIRES setpaper is the command particular to each 
#	  gnome/desktop environment version that will set the 
#	  wallpaper via the command line
#MODIFIES wallpaper on backgroun
#EFFECTS  Sets the wallpaper of the system to be image_name
def Set_wallpaper(setpaper, image_name):
	try:		
		subprocess.call(args = setpaper + image_name, 
				shell=True)
		print("Wallpaper should be set to: " + image_name \
		      + "\n") 
	except:	
		print("Error setting wallpaper, it is likely the "
		      "file path is not 100% correct. Make sure "
		      "there is a foward slash at the end of the "
		      "path in the SETWALLPAPER variable.")
		sys.exit(1)

###################################################################
#REQUIRES SETWALLPAPER command, and image_list 
#MODIFIES wallpaper background of the computer
#EFFECTS  Cycles through the wallpapers that are given by the titles
#	  in the image_list list, based on the CYCLETIME
def Cycle_wallpaper(SETWALLPAPER):
	global image_list
	global MAXPOSTS
	
#print(MAXPOSTS)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	
	for i in range(0, MAXPOSTS, 1):
#print(image_list[i]#!!!!!!!!!!!!!!!!!!)
		Set_wallpaper(SETWALLPAPER, image_list[i])
		time.sleep(CYCLETIME*60)

###################################################################
if __name__ == '__main__':
	get_wallpaper()
