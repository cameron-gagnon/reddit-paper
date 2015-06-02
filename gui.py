#!/usr/bin/env python3.4

import redditpaper as rp
import webbrowser
import os
from tkinter import *
from tkinter import StringVar
from tkinter import ttk
from PIL import Image

LARGE_FONT = {"Verdana", "12"}
XLARGE_FONT = {"Verdana", "16"}
CURSOR = "hand2"
HYPERLINK = "#0000EE"

class Application(Tk):

    width = 525
    height = 550

    def __init__(self, master=None):
        Tk.__init__(self, master)
        
        # set title of application on titlebar
        self.wm_title("Reddit Paper") 
        
        # set up frame to hold widgets
        root = Frame(self, background="bisque")
        root.pack(side = "top", fill = "both", expand = True)

        # set minsize of application
        self.setUpWindow() 
        
        # adds buttons and status bar for main page
        self.buttons = AddButtons(root, self)
        
        self.frames = {}
        
        # window used to pack the pages into
        self.window = Frame(root, bg = "cyan")         
        self.window.pack()

        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(self.window, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        # frame to show on startup
        self.show_frame(CurrentImg)

    def show_frame(self, cont):
        """
            Input: the page to display
            Output: displays the page selected on button click
        """
        frame = self.frames[cont]
        frame.tkraise()

    def setUpWindow(self):
        """ 
            Aligns the GUI to open in the middle
            of the screen(s)
            credit: https://stackoverflow.com/questions/
                    14910858/how-to-specify-where-a-tkinter-window-opens
        """
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        self.x = (ws/2) - (self.width/2)
        self.y = (hs/2) - (self.height/2)
        self.minsize(width = self.width, height = self.height)
        self.maxsize(width = self.width, height = self.height)
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x, self.y))



class AboutInfo():
    """
        Information about the GUI version, links to static sites (reddit,
        and PayPal), and author name and information
    """
    _version = "1.0"
    _author = "Cameron Gagnon"
    _email = "cameron.gagnon@gmail.com"
    _redditAcct = "https://www.reddit.com/message/compose/?to=camerongagnon"
    _payPalAcct = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&"\
                  "business=PKYUCH3L9HJZ6&lc=US&item_name=Cameron%20Gagnon"\
                  "&item_number=81140022&currency_code=USD&bn=PP%2dDonations"\
                  "BF%3abtn_donateCC_LG%2egif%3aNonHosted"
    
    def version():
        return AboutInfo._version

    def author():
        return AboutInfo._author

    def reddit():
        return AboutInfo._redditAcct

    def PayPal():
        return AboutInfo._payPalAcct
    
    def email():
        return AboutInfo._email



class Messages():
    """
        Class of messages to be displayed when changes or errors occur
    """
    def confirm(master, cmd):
        """
            Pop up box/message for confirmation of settings/deleting settings
        """
        popup = Toplevel()
        popup.wm_title("!! Confirm !!")
        Messages.position_popup(popup, master)
    
        label = ttk.Label(popup, anchor = "center", 
                          text = "Are you sure?", font = LARGE_FONT)
        label.pack(side = "top", fill = "x", pady = 10)
        B1 = ttk.Button(popup, text = "Yes", command = cmd)
        B2 = ttk.Button(popup, text = "No", command = popup.destroy)
        B1.pack(side = "left")
        B2.pack(side = "left")


    def position_popup(popup, master):
        """
            places the popup centered on the application
        """
        # width of popup message
        w = 155
        h = 80
        x, y = master.position_on_screen()
        x = (Application.width/2) + x - (w/2)
        y = (Application.height/2) + y - (3*(h)) # 3* for aesthetic reasons

        # set permanent dimensions of popup
        popup.minsize(width = w, height = h)
        popup.maxsize(width = w, height = h)
        
        # places popup onscreen
        popup.geometry('%dx%d+%d+%d' % (w, h, x, y))
        

class AddButtons(Frame):

    def __init__(self, master, cls):
        Frame.__init__(self, master)
        self.topbar = Frame(master, bg="red")

        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(self.topbar, image = self.cphoto, 
                        width = 125, height = 125, cursor = CURSOR,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic_square.png")
        self.p = Button(self.topbar, image = self.pphoto, 
                        width = 125, height = 125, cursor = CURSOR,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic_square.png")
        self.s = Button(self.topbar, image = self.sphoto, 
                        width = 125, height = 125, cursor = CURSOR,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic_square.png")
        self.a = Button(self.topbar, image = self.aphoto, 
                        width = 125, height = 125, cursor = CURSOR,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")
        self.STATUSTEXT = StringVar()
        self.setStatusText("")

        # statusbar for bottom of application        
        self.statusbar = Label(master, text= self.STATUSTEXT.get(), bd=1,
                            relief = SUNKEN, anchor = "w")
        
        # pack the labels/frame to window
        self.statusbar.pack(side = "bottom", fill = "x", anchor = "w")
        self.topbar.pack(side = "top")
    
    def setStatusText(self, text):
        self.STATUSTEXT.set(text)



# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.link = "https://www.reddit.com/r/EarthPorn/comments/37vqde/"\
                    "has_there_ever_been_a_more_badass_volcano_photo/"

        # create the frame to hold the widgets
        self.frame = Frame(self, width = 525, height = 400,\
                           bg = "magenta")
        
        # link to submission of image
        self.label = Label(self.frame, text="Title/link to submission:", 
                           font = LARGE_FONT, 
                           fg=HYPERLINK, cursor = CURSOR)
        self.label.pack(pady = 10, padx = 10)
        self.label.bind("<Button-1>", self.open_link)

        # thumbnail of image currently set as background
        self.photoLocation = "./images/currentpic_square.png"
                           # "./images/placeholder400x400.png"
        self.photo = PhotoImage(file = self.photoLocation)
        self.photoLabel = Label(self.frame, image = self.photo)
        
        # pack frames/labels
        self.frame.pack_propagate(0)
        self.photoLabel.pack(side = "bottom", expand = True)
        self.frame.pack(side = "top")

    def open_link(self, event):
        webbrowser.open_new(self.link)

# **** Past Images Page **** #
# Gives a listing of past submissions, with a smaller thumbnail of the image
# and the title/resolution of the images.
# Includes: * checkboxes to delete the images selected
#           * Scrollable list of all images downloaded/used in the past
class PastImgs(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # frames for past images page
        onOffVar = IntVar()
        self.picFrame = Frame(self, bg = "blue", width = 500, height = 340)
        self.canvas = Canvas(self.picFrame)
        self.picListFrame = Frame(self.canvas, width = 400, height = 300)
        buttFrame = Frame(self.picFrame, bg = "pink")
        selectBox = Checkbutton(self, text = "Select all",  variable = onOffVar)
        
        # widgets inside the frames
        deleteSelButt = Button(buttFrame, text = "Delete selected", 
                               state = "disabled",
                               command = lambda: Messages.confirm(self, None))
        deleteAllButt = Button(buttFrame, text = "Delete all", 
                               command = lambda: Messages.confirm(self, None))
        
        yscrollbar = Scrollbar(self.canvas, orient = "vertical", width = 20)
       
#        self.populate(picListFrame)
 
        # 'delete all' button 'delete selected' button
        deleteAllButt.pack(side = "right", anchor = "se", padx = 10)
        deleteSelButt.pack(side = "right", anchor = "se", padx = 10)

        # packs the frame that holds the delete buttons
        buttFrame.pack(side = "bottom", anchor = "e")
        # pack the canvas
        self.canvas.pack()
        # pack frames/labels
        # select and delete text
        selectBox.pack(anchor = "w", pady = (15, 2), padx = (15, 10))
        
        # scrollbar for past images
        yscrollbar.pack(side = "right", fill = "y")
        
        # box to list items
        self.picListFrame.pack(side = "left", fill = "both")

        # frame to hold widgets
        self.picFrame.pack(side = "bottom", padx = 10, pady = (0, 10))

        yscrollbar.config(command = self.canvas.yview)        

    def delete_all(self):
        """ 
            delete all the images stored by program on the computer
        """
        pass

    def select_all(self):
        """
            selects all the pictures (to be deleted)
        """
        for sel in self.piclist:
            sel.select()

    def deselect_all(self):
        """
            deselects all the pictures in piclist
        """
        for sel in self.piclist:
            sel.deselect()

    def populate(self, frame):
        """
            fill the frame with more frames of the images
        """
        savedPictures = self.findSavedPictures()

        for img in savedPictures:
            # create frame to hold information for one picture
            itemFrame = Frame(frame, width = 57, height = 20).pack(side = "top")
            
            # checkbox to select/deselect the picture
            Checkbutton(itemFrame).pack(side = "left", padx = 5)
            
            # open and create a thumbnail of all images
            photo = Image.open(img.save_location)
            photo = photo.thumbnail((50, 50), Image.ANTIALIAS)

            # insert the thumbnail, title, and resolution
            Label(itemFrame, image = photo).pack(side = "left", padx = 10)
            Label(itemFrame, text = img.title).pack(side = "left", padx = 10)
            Label(itemFrame, text = img.resolution).pack(side = "bottom", pady=5)
    
    def findSavedPictures(self):
        pictures = rp.PictureList.list_pics()
        return pictures

    def position_on_screen(self):
        """
            returns the x,y coordinates of upper left corner of frame
        """
        return self.winfo_rootx(), self.winfo_rooty()
        

# **** Settings Page **** #
# This is where most of the users choices will be made
# on the running of the program.
# This includes: * nsfw filter box
#                * subreddits to query
#                * image resolutions
#                * multiple monitor setup
class Settings(Frame):

    def __init__(self, parent, controller):
        # Frames
        Frame.__init__(self, parent)
        label = Label(self, text="Settings", font = LARGE_FONT, bg="yellow")
        label.pack(pady = 10, padx = 10)
        self.top = Frame(self)
        self.entry = LabelFrame(self.top, text = "Authorization") 
        self.subredditForm = LabelFrame(self, text = "Subreddits")
        self.checks = LabelFrame(self, text = "Adult Content")
        self.dimensions = LabelFrame(self.top, text = "Minimum Picture Resolution")
        self.res = Frame(self.dimensions)
        
        # Buttons
        self.letsGo = Button(self, text = "Let's Go!", command = rp.main)

        # user/pass entries 
        userTxt = Label(self.entry, text = "  Username:")
        userTxt.grid(row = 0, column = 0, sticky = "e",\
                     pady = (10, 6))
        
        passTxt = Label(self.entry, text = "Password:")
        passTxt.grid(row = 1, column = 0, sticky = "e",\
                     pady = (0, 6))

        self.username = Entry(self.entry)
        self.username.grid(row = 0, column = 1, padx = (0, 10))
        self.password = Entry(self.entry, show = "*")
        self.password.grid(row = 1, column = 1, padx = (0,10), pady = (0, 10))
        
        # subreddit entry
        subtxt = Label(self.subredditForm, text = "Subreddits (separated by +)",\
                       pady = 15)
        subtxt.grid(row = 2, columnspan = 2, ipadx = 5, sticky = "w")
        
        self.subreddits = Entry(self.subredditForm, width = 29)
        self.subreddits.grid(row = 2, column = 2, columnspan = 2, padx = (0,10),\
                             sticky = "w")
        
        # Frames for width x height
        self.widthF = Frame(self.res)
        self.heightF = Frame(self.res)
        self.widthF.pack(side = "top")
        self.heightF.pack(side = "top")

        # Min width
        minWidthTxt = Label(self.widthF, text = " Min-width:")
        minWidthTxt.grid(row = 0, column = 0, sticky = "e", pady = (10, 6))
        # min width entry
        self.minwidth = Entry(self.widthF, width = 6)
        self.minwidth.grid(row = 0, column = 1, padx = (5, 5))
        
        # Min height
        minHeightTxt = Label(self.heightF, text = "  Min-height:")
        minHeightTxt.grid(row = 1, column = 0, sticky = "e", pady = (0, 6))
        # min height entry
        self.minheight = Entry(self.heightF, width = 6)
        self.minheight.grid(row = 1, column = 1, padx = (0, 10), pady = (0, 10))
        

        # nsfw checkbutton
        # nsfw on text
        nsfwTxt = Label(self.checks, text = "NSFW")
        nsfwTxt.pack(side = "left", ipadx = 5)
        self.nsfwOn = StringVar()
        self.nsfwOn.set("On")
        
        # nsfw off text
        self.nsfwOff = StringVar()
        self.nsfwOff.set("Off")
        # nsfw var config
        self.onOff = IntVar()

        # nsfw checkbutton config
        self.nsfw = Checkbutton(self.checks, text = self.nsfwOff.get(),\
                                variable = self.onOff)
        # packs/binds
        # button packs
        self.letsGo.pack(side = "bottom", anchor = "e", padx = 50, pady = 40)
        self.nsfw.bind("<Button-1>", self.check_nsfw)
        self.nsfw.pack(side = "left", anchor = "w", pady = 10,\
                       padx = (15, 10))
        # top holds dimensions and user/pass labelFrames
        self.top.pack(side = "top", anchor = "w", pady = 5)
        self.entry.pack(side = "left", anchor = "w", pady = 10,\
                        padx = (15, 10))
        self.subredditForm.pack(side = "top", anchor = "w",\
                                padx = (15, 10))
        self.dimensions.pack(side = "left", anchor = "w", pady = 10,\
                             padx = (15, 10))
        self.res.pack(side = "top")
        self.checks.pack(side = "top", anchor = "w", pady = 10,\
                         padx = (15, 10))

    def check_nsfw(self, event):
        if (self.onOff.get()):
            self.nsfw.config(text = self.nsfwOff.get())
        else:
            self.nsfw.config(text = self.nsfwOn.get())

# **** About Page **** #
# Displays information regarding the creator of the application,
# where to ask questions, who to contact, etc.
# This includes: * contact info (email, name, where to post for help)
#                * Donate option
#                * Feedback
#                * (Sending CrashReport)
class About(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # frames
        label = Label(self, text="About", font = LARGE_FONT, bg="green")
        label.pack(pady = 10, padx = 10)
        self.authorFrame = LabelFrame(self, text = "Author")
        self.donateFrame = LabelFrame(self, text = "Donations")
        self.crashFrame = LabelFrame(self, text = "Crash Report")
        self.versionFrame = Frame(self.authorFrame)
        self.subAuthorFrame = Frame(self.authorFrame)
        self.feedFrame = LabelFrame(self, text = "Feeback")

        # author
        self.authorTxt = Label(self.subAuthorFrame, text = "This program was created by: ",\
                          font = XLARGE_FONT)
        self.authorLink = Label(self.subAuthorFrame, text="/u/camerongagnon", font = XLARGE_FONT, 
                         fg=HYPERLINK, cursor = CURSOR)

        # version number
        self.vNum = StringVar()
        self.vNum.set("Version: " + rp.AboutInfo.version() + "." +  AboutInfo.version())
        self.version = Label(self.versionFrame, text = self.vNum.get(), font = XLARGE_FONT)
        
        # donate text/link
        self.donateTxt = Label(self.donateFrame, text = "If you enjoy this program, "
                                                        "please consider making a donation ",
                                                        font = XLARGE_FONT)
        self.subDonateFrame = Frame(self.donateFrame)
        self.donateTxt2 = Label(self.subDonateFrame, text = "to the developer at the following "
                                                            "link,", font = XLARGE_FONT) 
        self.donateLink = Label(self.subDonateFrame, text = "here.", fg = HYPERLINK,\
                                font = XLARGE_FONT, cursor = CURSOR)
        # feedback
        self.feedback = Label(self.feedFrame, text = "To provide comments/feedback, please "
                                                     "do one of the following: \n"
                                                     "1. Go to /r/reddit_paper and create a "
                                                     "new post.\n2. Follow the above "
                                                     "account link and send me a PM.\n3. Email "
                                                     "me directly at cameron.gagnon@gmail.com",\
                              font = XLARGE_FONT)
        # send crashReport
        self.crash_loc = StringVar()
        self.location = self.get_crash_location()
        self.crash_loc.set(self.location)

        self.report = Label(self.crashFrame, text = "To send a crash report, please\n"
                            "browse to the file location below and send the log\n"
                            "to cameron.gagnon@gmail.com.", font = XLARGE_FONT)
        self.crash_loc = Label(self.crashFrame, text = self.crash_loc.get(), wraplength = 480)


        
        
        
        # packs/binds
        # author frame pack
        self.authorTxt.pack(side = "left", padx = (60, 0))
        self.authorLink.pack(side = "left", )
        self.authorLink.bind("<Button-1>", lambda x: self.open_link(AboutInfo.reddit()))
        self.subAuthorFrame.pack(side = "top")
        # version frame pack within author frame
        self.version.pack()
        self.versionFrame.pack(side = "top")
        self.authorFrame.pack(side = "top", fill = "x", padx = (10, 15))
        # donate frame pack
        self.donateTxt.pack(side = "top", padx = (30, 0))
        self.donateTxt2.pack(side = "left", padx = (30, 0))
        self.donateLink.pack(side = "left")
        self.donateLink.bind("<Button-1>", lambda x: self.open_link(AboutInfo.PayPal()))
        self.donateFrame.pack(side = "top", fill = "x", padx = (10, 15), pady = (10, 0))
        self.subDonateFrame.pack(side = "top")
        # feedback
        self.feedback.pack(side = "top")
        self.feedFrame.pack(side = "top", fill = "x", padx = (10, 15), pady = (10, 0))
        # crash report pack
        self.report.pack(side = "top")
        self.crash_loc.pack(side = "top")
        self.crashFrame.pack(side = "top", fill = "x", padx = (10, 15), pady = (10, 0))
        
    def open_link(self, link):
        webbrowser.open_new(link)

    def get_crash_location(self):
        # opens a file browser for the user to 
        # search for the log file
        return os.path.realpath("CrashReport.log")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
