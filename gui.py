#! /usr/bin/env python3.4

import redditpaper as rp
# must insert config here, so that it
# works throughout both modules with onetime
# setup
rp.Config_logging()
import webbrowser
import os
import subprocess
import time
from tkinter import *
from tkinter import font
from tkinter import StringVar
from tkinter import ttk
from PIL import Image
from praw import errors


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
        
        Fonts.underline(self) 
        # set minsize of application
        self.setUpWindow() 
        
        # adds buttons and status bar for main page
        self.buttons = AddButtons(root, self)
#        self.STATUSBAR = StatusBar(root)
        
        # window used to pack the pages into
        self.window = Frame(root, bg = "cyan")         
        self.window.pack()
        self.frames = {}
        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(self.window, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        # frame to show on startup
        self.show_frame(PastImgs)#CurrentImg)
        
    def show_frame(self, page):
        """
            Input: the page to display
            Output: displays the page selected on button click
        """
        frame = self.frames[page]
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
        self.x = (ws//2) - (self.width//2)
        self.y = (hs//2) - (self.height//2)
        self.minsize(width = self.width, height = self.height)
        self.maxsize(width = self.width, height = self.height)
        self.geometry('{}x{}+{}+{}'.format(self.width, self.height, 
                                           self.x, self.y))



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


######################## Classes for Messages #################################
class Message():

    def __init__(self, master, title):
        """
            Creates popup as Toplevel() and sets its title in the window 
        """
        self.popup = Toplevel() 
        self.popup.wm_title(title)
    
    def set_dimensions(self, master, w, h):
        """
            Sets the position and size on screen for the popup 
        """
        x = master.winfo_rootx()
        y = master.winfo_rooty()
        x = (Application.width // 2) + x - (w // 2)
        y = (Application.height // 2) + y - 405
        # set permanent dimensions of popup
        self.popup.minsize(width = w, height = h)
        self.popup.maxsize(width = w, height = h)
        self.popup.geometry('{}x{}+{}+{}'.format(w, h, x, y))
 
    def destroy(self):
        """
            Destroys the popup
        """
        self.popup.destroy()

    def pack_label(self, text, pady = 10):
        """
            Packs a label into the popup with the specified text
        """
        label = ttk.Label(self.popup, anchor = "center",
                          text = text, wraplength = 420,
                          font = Fonts.LARGE)
        label.pack(side = "top", fill = "x", pady = pady)

    def pack_button(self, pady = (10, 10)):
        """
            Place a button at the bottom of the widget with the text "Okay"
        """
        b = Button(self.popup, text = "Okay", command = self.destroy)
        b.pack(side = "bottom", pady = pady)


class ErrorMsg(Message):
    
    def __init__(self, master, text, title = "Error!"):
        popup = Message.__init__(self, master, title) 
        length = 0
        height = 0
        if isinstance(text, list):
            if len(text) == 1:
                # if string, return length of string
                length = len(text[0])
                height = 120
                rp.log.debug("Length of error string is: %d, "
                             "and height is: %d" % (length, height))
            elif len(text) > 1:
                # find max length of string in the list of errors
                length = len(max(text))
                # length of the list is num of elts in list 
                # so to get the height, we take this and
                # multiply it by a constant and add a base amt
                height = len(text) * 15 + 130 
                rp.log.debug("Length of  max error string is: %d " 
                             "and height is %d" % (length, height))
            else:
                # no errors in CLArgs
                pass 
            self.pack_label("Invalid Argument(s):")
        
        else:
            # if just a regular string that we want an error message
            length = len(text) 
            height = 125
            self.pack_label("Invalid Argument(s):")
            self.pack_label(text)
            self.pack_button()
            rp.log.debug("Length of error string is: %d, "
                         "and height is: %d" % (length, height))
 
        width = length * 5 + 200 # length * 5 because each char is probably 
                                # about 5 px across. + 10 for padding
        rp.log.debug("Width of ErrorMsg is %d: " % width)
        self.set_dimensions(master, width, height)
    

class InvalidArg(ErrorMsg):

    def __init__(self, master, text):
        """
            Used spcecifically to display the CLArguments            
        """
        
        ErrorMsg.__init__(self, master, text)
         
        if len(text) > 1:
            for string in text:
                self.pack_label(string, pady = (5,0))
        elif len(text) == 1:
            self.pack_label(text[0])
        else:
            rp.log.debug("No errors in CLArgs")
        self.pack_button() 


class ConfirmMsg(Message):

    def __init__(self, master, text):
        """
            Pop up box/message for confirmation of settings/deleting settings
        """
        Message.__init__(self, master, "!! Confirm !!")
        
        width = 180
        height = 75
        self.set_dimensions(master, width, height)
        
        self.pack_label("Are you sure?")
        BFrame = Frame(self.popup)
        BFrame.pack()
        B1 = ttk.Button(BFrame, text = "Yes", command = self.destroy)
        B2 = ttk.Button(BFrame, text = "No", command = self.destroy)
        B1.pack(side = "left")
        B2.pack(side = "left")

################################################################################
class Fonts():
    VERDANA = "Verdana"
    CURSOR = "hand2"
    HYPERLINK = "#0000EE"
    XLARGE = {VERDANA, 16} 
    LARGE = {VERDANA, 12}
    MED = {VERDANA, 10}
    H1 = {VERDANA, 25}
    # TOFIX: H1 should be set to larger font
    # not same size as other font. Max font size?

    def underline(master):
        """
            Gives the ability to have entire strings of text
            underlined. Used for links.
        """
        global UNDERLINE
        # Defined in its own function as the
        # Font() call must be made after a Tk()
        # instance has been created.
        UNDERLINE = font.Font(master, Fonts.XLARGE)
        UNDERLINE.configure(underline = True)


class StatusBar(Frame):

    def __init__(self, master): 
        # statusbar for bottom of application        
        self.statusBar = Label(master, text = "asdf", bd=1,
                          relief = SUNKEN, anchor = "w")
        
        # pack the labels/frame to window
        self.statusBar.pack(side = "bottom", fill = "x", anchor = "w")

    def setText(self, text):
        rp.log.debug("Setting STATUSBAR text to: " + text)
        self.statusBar.config(text = text)


class AddButtons(Frame):

    def __init__(self, master, cls):
        global STATUSBAR
        Frame.__init__(self, master)
        self.topbar = Frame(master, bg="red")

        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(self.topbar, image = self.cphoto, 
                        width = 125, height = 125, cursor = Fonts.CURSOR,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic_square.png")
        self.p = Button(self.topbar, image = self.pphoto, 
                        width = 125, height = 125, cursor = Fonts.CURSOR,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic_square.png")
        self.s = Button(self.topbar, image = self.sphoto, 
                        width = 125, height = 125, cursor = Fonts.CURSOR,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic_square.png")
        self.a = Button(self.topbar, image = self.aphoto, 
                        width = 125, height = 125, cursor = Fonts.CURSOR,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")

#        STATUSBAR = StatusBar(master)
        self.topbar.pack(side = "top")


# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame):

    try: 
        HR, MIN = rp.Config.cycletime()
        # converts hours and min to milliseconds 
        # to be used by the tkinter after() fn
        TIMER = int(HR * 3600000 + MIN * 60000)
    except ValueError:
        # happens when program is run for first time as
        # no config file is created yet
        TIMER = 3000
        pass

    def __init__(self, parent, controller):
        """
            Packs the frames needed, and initiaties 
            the updateFrame to continuously call itself
        """
        Frame.__init__(self, parent)
        # pack frames/labels
        self.frame = Frame(self, width = 525, height = 400,\
                           bg = "magenta")
        self.frame.pack_propagate(0)
        self.frame.pack()
         
        self.get_past_img(parent)
        self.updateTimer()
        self.updateFrame(parent)

    def open_link(self, link):
        """
            Opens the link provided in the default
            webbrowser
        """
        webbrowser.open_new(link)

    def get_past_img(self, parent):
        """
            looks up the most recent wallpaper set based on the
            config file and passes that info to set_past_img
        """
        
        self.image_name = rp.Config.lastImg()      
        if self.image_name:
            rp.log.debug("Last Wallpaper is: %s" % self.image_name) 

            try:
                im = rp.DBImg(self.image_name)
                im.link
                self.set_past_img(im)
            # Attribute Error is in case the image returned
            # is incomplete
            except (AttributeError, TypeError):
                rp.log.debug("Attribute Error in get_past_img",
                             exc_info = True)

        else:
            rp.log.debug("No image set as last image in settings.conf")

    def set_past_img(self, im):
        """
            Creates the inner frame within the main frame of
            CurrentImg and packs the picture thumbnail and title
            into it.
        """

        # create subframe to pack widgets into, then destroy it
        # later
        self.image_name = im.image_name
        self.subFrame = Frame(self.frame, width = 525, height = 410,\
                              bg = "white")
        self.subFrame.pack_propagate(0)
        self.subFrame.pack()
       
        # create title link
        self.linkLabel = Label(self.subFrame, text = im.title,
                               font = UNDERLINE, fg = Fonts.HYPERLINK,
                               cursor = Fonts.CURSOR, wraplength = 500)
        self.linkLabel.pack(pady = (35, 10), padx = 10)
        self.linkLabel.bind("<Button-1>", lambda x: self.open_link(im.post))
        
   
        # create image and change to thumbnail
        with open(im.save_location, 'rb') as image_file:
            imThumb = Image.open(image_file)
            # uses two with statements because of a bug
            # in the PIL library that does not properly close
            # a file
            im.image_name = self.strip_file_ext(im.image_name)
            im.image_name = self.add_png(im.image_name)
            im.updateSaveLoc()
            imThumb.thumbnail((400, 250), Image.ANTIALIAS)
            imThumb.save(im.save_location, "PNG")
        # apply photolabel to page to display
        self.photo = PhotoImage(file = im.save_location)
        self.photoLabel = Label(self.subFrame, image = self.photo)
        self.photoLabel.pack(side = "bottom", expand = True)

    def strip_file_ext(self, image_name):
        """
            Used to remove the .jpg or other ending from im.image_name
            so that we can resave the thumbnail with .png
        """
        index = image_name.rfind('.')
        image_name = image_name[:index]
        return image_name

    def add_png(self, image_name):
        """
            Appends the .png to the end of im.image_name to save the
            thumbnail with .png
        """
        image_name += ".png"
        return image_name

    def delSubframe(self):
        """
            Clears up the widgets that are in the frame of the main
            CurrentImg, so that we can reset all the widgets
        """
        try:
            self.photoLabel.destroy()
            self.linkLabel.destroy()
            self.subFrame.destroy()
        except AttributeError:
            # happens when no image is set at first run of program
            pass

    def updateFrame(self, parent):
        """
            Calls itself to update the frame every self.TIMER 
            to update the past image if it has changed
        """
        if self.image_name != rp.Config.lastImg():
            self.updateTimer()
            self.delSubframe()
            self.get_past_img(parent)
        try:
            self.after(self.TIMER, lambda: self.updateFrame(parent))
        except AttributeError:
            # happens when settings.conf is not created yet
            pass

    def updateTimer(self):
        try:
            HR, MIN = rp.Config.cycletime()
            # converts hours and min to milliseconds 
            # to be used by the tkinter after() fn
            self.TIMER = int(HR * 3600000 + MIN * 60000)
        except ValueError:
            # happens when settings.conf is not created yet
            pass

# **** Past Images Page **** #
# Gives a listing of past submissions, with a smaller thumbnail of the image
# and the title/resolution of the images.
# Includes: * checkboxes to delete the images selected
#           * Scrollable list of all images downloaded/used in the past
class PastImgs(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
       
        # select all box
        onOffVar = IntVar()
        selectBox = Checkbutton(self, text = "Select all",  variable = onOffVar)
        selectBox.pack(anchor = "w", pady = (15, 2), padx = (21, 10))
        ### begin canvas/frame/picture list
        self.picFrame = Frame(self, bg = "blue", width = 450, height = 300)
        self.picFrame.pack()
        self.picFrame.bind("<MouseWheel>", self.onMouseWheel) 
        self.picFrame.bind("<Button-3>", self.onMouseWheel)
        self.picFrame.bind("<Button-5>", self.onMouseWheel)
        self.canvas = Canvas(self.picFrame, bg = 'red', width = 450, height = 300)
        self.canFrame = Frame(self.canvas)
        self.canFrame.bind("<Configure>", self.setFrame)
        self.canFrame.bind("<Button-4>", self.onMouseWheel)
        self.canvas.bind("<Button-5>", self.onMouseWheel)
#self.canvas.bind("<MouseWheel>", self.onMouseWheel)
        self.canvas.create_window((0,0), window = self.canFrame, anchor = 'nw')
 
        self.scroll = Scrollbar(self.picFrame, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scroll.set)
         
        self.scroll.pack(side="right",fill="y")
        self.canvas.pack(side="left")
        
        for i in range(0, 15): 
            self.foo = Frame(self.canFrame, width = 450, height = 75, bg = 'pink')
            txt = "test {}".format(i)
            self.text = Label(self.foo, text = txt) 
            self.text.pack()
            self.text.pack()
            self.foo.grid(row = i, column = 0)
            self.foo.pack_propagate(0)
            self.setKeyBinds()
        
        ### end canvas/frame/picture list
#self.scroll.grid_forget()
         
        # bottom frame for buttons
        self.bottomFrame = Frame(self, bg = 'yellow')        
        deleteSelButt = Button(self.bottomFrame, text = "Delete selected", 
                               state = "disabled",
                               command = lambda: ConfirmMsg(self, None))
        deleteAllButt = Button(self.bottomFrame, text = "Delete all", 
                               command = lambda: ConfirmMsg(self, None))
        
        # 'delete all' button 'delete selected' button
        deleteAllButt.pack(side = "right")
        deleteSelButt.pack(side = "right", padx = (10, 0))

        # packs the frame that holds the delete buttons
        self.bottomFrame.pack(side = "bottom", anchor = "e",
                              pady = (0, 15), padx = (0, 27))

    def setKeyBinds(self):
        self.foo.bind("<Button-4>", self.onMouseWheel)
        self.foo.bind("<Button-5>", self.onMouseWheel)
        self.foo.bind("<Up>", self.onMouseWheel)
        self.foo.bind("<Down>", self.onMouseWheel)
        self.foo.focus_set()
   
    def onMouseWheel(self, event):
        keyNum = {116 : 2,   # Down arrow key
                  111 : -2}  # Up arrow key
        scrollVal = None
        if event.keycode in keyNum:
            scrollVal = keyNum.get(event.keycode)
        elif event.num == 4:
            scrollVal = -2
        elif event.num == 5:
            scrollVal = 2
        else:
            scrollVal = event.delta # leave as is on OSX

        rp.log.debug("Scrolling by %d" % scrollVal)
        self.canvas.yview_scroll(scrollVal, "units")

    def setFrame(self, event):
        self.canvas.configure(scrollregion = self.canvas.bbox('all'), width = 450, height = 300)

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

        for i, img in enumerate(savedPictures):
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
       

# **** Settings Page **** #
# This is where most of the users choices will be made
# on the running of the program.
# This includes: * nsfw filter box
#                * subreddits to query
#                * image resolutions
#                * multiple monitor setup
class Settings(Frame):

    def __init__(self, parent, controller):
        # force settings file to be created, so we have default
        # values the first time we run the GUI
        # Frames
        temp = rp.Config.read_config()
        Frame.__init__(self, parent)
        label = Label(self, text="Settings", font = Fonts.H1, bg="yellow")
        label.pack(pady = 10, padx = 10)
        self.top = Frame(self)
        # subreddit border
        self.subredditForm = LabelFrame(self, text = "Subreddits to pull from")
        # nsfw border
        self.checksFrame = LabelFrame(self.top, text = "Adult Content")
        self.checks = Frame(self.checksFrame)
        # width x height
        self.dimensions = LabelFrame(self.top, 
                                     text = "Picture Resolution")
        self.res = Frame(self.dimensions)
        # cycletime and category border and frame
        self.topRt = Frame(self.top)
        self.ct = LabelFrame(self.topRt, text = "Wallpaper Timer")
        self.ctFrame = Frame(self.ct)
        self.cat = LabelFrame(self.topRt, text = "Section")
        self.catFrame = Frame(self.cat, width = 200, height = 30)
        self.catFrame.pack_propagate(0)

        # download location border
        self.dlFrame = LabelFrame(self, text = "Picture download location")
                
        # Buttons
        self.letsGo = Button(self, text = "Let's Go!")
#self.help = Button(self, text = "Help", command = self.helpButt)
      
        # subreddit entry
        subtxt = Label(self.subredditForm, text = "Whitespace separated:",
                       pady = 15)
        subtxt.grid(row = 1, columnspan = 2, ipadx = 5, sticky = "w")
        self.subreddits = Entry(self.subredditForm, width = 39)
        self.subreddits.insert(0, rp.Config.subreddits())
        self.subreddits.grid(row = 1, column = 2, columnspan = 2, padx = (0,10),
                             sticky = "w")
        # "download to" entry
        self.dlTxt = Label(self.dlFrame, text = "Download pictures to:", 
                           pady = 15)
        self.dlTxt.grid(row = 0, column = 0, ipadx = 5, sticky = "w")
        self.dlLoc = Entry(self.dlFrame, width = 40)
        self.dlLoc.insert(0, rp.Config.dlLoc())
        self.dlLoc.grid(row = 0, column = 1, sticky = "w", padx = (0, 10))

        # Frames for width x height
        self.widthF = Frame(self.res)
        self.heightF = Frame(self.res)
        self.widthF.pack(side = "top")
        self.heightF.pack(side = "top")

        # Min width
        minWidthTxt = Label(self.widthF, text = " Min-width:")
        minWidthTxt.grid(row = 0, column = 0, sticky = "e", pady = (10, 0))
        # min width entry
        self.minwidth = Entry(self.widthF, width = 6)
        self.minwidth.insert(0, rp.Config.minwidth())
        self.minwidth.grid(row = 0, column = 1, padx = (5, 5))
        # Min height
        minHeightTxt = Label(self.heightF, text = "  Min-height:")
        minHeightTxt.grid(row = 1, column = 0, sticky = "e", pady = (0, 6))
        # min height entry
        self.minheight = Entry(self.heightF, width = 6)
        self.minheight.insert(0, rp.Config.minheight())
        self.minheight.grid(row = 1, column = 1, padx = (0, 10), pady = (0, 10))
       
        # nsfw checkbutton
        # nsfw on text
        nsfwTxt = Label(self.checks, text = "NSFW:")
        nsfwTxt.pack(side = "left", ipadx = 5)
        # nsfw var config
        self.onOff = BooleanVar() #IntVar()
        self.onOff.set(rp.Config.nsfw())
        # nsfw checkbutton config
        self.nsfw = Checkbutton(self.checks, text = "On",
                                variable = self.onOff)
       
        # cycletime txt
        self.ctTxt = Label(self.ctFrame, text = "Set for:")
        self.ctTxt.grid(row = 0, column = 0, sticky = "e", padx = (5,0))
        # cycletime entry
        self.rpHr, self.rpMin = rp.Config.cycletime()
        # hour txt/entry
        self.ctHourE = Entry(self.ctFrame, width = 4)
        self.ctHourE.insert(0, self.rpHr)
        self.ctHourE.grid(row = 0, column = 1, padx = (5,0))
        self.ctHourTxt = Label(self.ctFrame, text = "hrs")
        self.ctHourTxt.grid(row = 0, column = 2, padx = (0, 5))
        # min txt/entry
        self.ctMinE = Entry(self.ctFrame, width = 4)
        self.ctMinE.insert(0, self.rpMin)
        self.ctMinE.grid(row = 0, column = 3)
        self.ctMinTxt = Label(self.ctFrame, text = "mins", anchor = "w")
        self.ctMinTxt.grid(row = 0, column = 4, padx = (0, 5))
        self.ctFrame.pack(side = "top", ipady = 2)
       
        # category dropdown
        self.choices = ["Hot", "New", "Rising", "Top", "Controversial"]
        self.catVar = StringVar(self)
        self.catVar.set(rp.Config.category())
        self.catDD = OptionMenu(self.catFrame, self.catVar, *self.choices)
        self.catDD.config(width = 10)
        self.catDD.pack(side = "right", anchor = "e", padx = (0, 5)) 
        self.catTxt = Label(self.catFrame, text = "Category:")
        self.catTxt.pack(side = "right", padx = (5, 0), anchor = "e")
        self.catFrame.pack(side = "top", ipady = 2)
        
        # packs/binds
        # button packs
        self.letsGo.pack(side = "bottom", anchor = "e", padx = 50, pady = 40)
        self.letsGo.bind("<Button-1>", self.get_pics)
        self.nsfw.pack(side = "left", anchor = "nw", pady = 5,\
                       padx = (0, 5))
        # top holds dimensions and user/pass labelFrames
        self.top.pack(side = "top", anchor = "w", pady = (10, 0))
        self.subredditForm.pack(side = "top", anchor = "w",\
                                padx = (15, 10))
        self.dlFrame.pack(side = "top", anchor = "w", pady = 10,
                          padx = (15, 10))
        self.dimensions.pack(side = "left", anchor = "nw", pady = (0, 10),\
                             padx = (15, 5))
        self.res.pack(side = "top")
        self.checks.pack(side = "top")
        self.checksFrame.pack(side = "left", anchor = "nw",\
                         padx = (5, 5))
        # cycletime and category frame
        self.ct.pack(side = "top")
        self.cat.pack(side = "bottom")
        self.topRt.pack(side = "left", anchor = "nw", padx = (5, 5))


    def get_values(self):
        """ returns the values stored in the entry boxes """
        self.values = {}
        self.values['-mw'] = self.minwidth.get()
        self.values['-mh'] = self.minheight.get()
        self.values['--nsfw'] = self.onOff.get()
        self.values['-s'] = self.subreddits.get().replace(" ", "+")
        self.values['-dl'] = self.dlLoc.get()
        self.values['-c'] =  self.catVar.get().lower()
        # convert hours to minutes, then add it to minutes, so we 
        # are only dealing with total minutes in the end
        errors = self.test_values(self.values)
        
        try:
            totalTime = float(self.ctHourE.get()) * 60 + float(self.ctMinE.get())
            self.values['-t'] = totalTime
            CurrentImg.TIMER = int(float(self.ctHourE.get()) * 3600000 +
                                   float(self.ctMinE.get()) * 60000)
        except ValueError:
            errors.append(self.ctHourE.get())
            errors.append(self.ctMinE.get())

        return self.values, errors

    def test_values(self, values):
        """
            Returns a list of incorrectly entered
            values from the settings page
        """
        # replace + with '' as we replaced ' ' with
        # '+' and + is not considered an alnum
        # so we remove it
        subs = values['-s'].replace('+', '')

        errors = []
        if not str(values['-mw']).isdigit():
            errors.append(values['-mw'])
        if not str(values['-mh']).isdigit():
            errors.append(values['-mh'])
        if not subs.isalnum():
            errors.append(values['-s'])

        return errors


    def get_pics(self, event):
        """ 
            Makes the call to redditpaper.main() to
            start the wallpaper scraper part of the
            program. Also collects the values to
            start the program with.
        """

        self.args, errors = self.get_values()
        if len(errors):
            rp.log.debug("ERRORS from CLArgs is: %s",
                          tuple(errors)) 
            InvalidArg(self, errors)
            return

        rp.log.debug("No errors in CLArgs") 
        # check if any values are null/empty
        # if so, don't add them to the list 
        self.argList = os.getcwd() + "/redditpaper.py"
        for k, v in self.args.items():
            rp.log.debug("Key, Value in CLArgs is: "
                         + k + " " + str(v))
            if v:
                # add key and value to the string to be
                # passed as cmd line args
                # the key will be the switch for the arg
                self.argList += " " + k + " " + str(v)

        # call main function with cmd line args
        rp.log.debug("Argument list is: " + self.argList)
        
        subprocess.Popen(self.argList.split())
#        if e:
#            rp.log.debug('Error code is: %s' % e)
#            ErrorMsg(self, "Check the spelling of your "
#                           "subreddits entered")

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
        label = Label(self, text="About", font = Fonts.H1, bg="green")
        label.pack(pady = 10, padx = 10)
        self.authorFrame = LabelFrame(self, text = "Author")
        self.donateFrame = LabelFrame(self, text = "Donations")
        self.crashFrame = LabelFrame(self, text = "Crash Report")
        self.versionFrame = Frame(self.authorFrame)
        self.subAuthorFrame = Frame(self.authorFrame)
        self.feedFrame = LabelFrame(self, text = "Feeback")

        # author
        self.authorTxt = Label(self.subAuthorFrame,
                               text = "This program was created by: ",\
                               font = Fonts.XLARGE)
        self.authorLink = Label(self.subAuthorFrame, text="/u/camerongagnon", 
                                font = UNDERLINE, fg = Fonts.HYPERLINK,
                                cursor = Fonts.CURSOR)

        # version number
        self.vNum = StringVar()
        self.vNum.set("Version: " + rp.AboutInfo.version() + "." +
                      AboutInfo.version())
        self.version = Label(self.versionFrame, text = self.vNum.get(),
                             font = Fonts.XLARGE)
        
        # donate text/link
        self.donateTxt = Label(self.donateFrame,
                               text = "If you enjoy this program, "
                                      "please consider making a donation ",
                               font = Fonts.XLARGE)
        self.subDonateFrame = Frame(self.donateFrame)
        self.donateTxt2 = Label(self.subDonateFrame,
                                text = "to the developer at the following "
                                       "link,",
                                font = Fonts.XLARGE) 
        self.donateLink = Label(self.subDonateFrame, text = "here.",
                                font = UNDERLINE, fg = Fonts.HYPERLINK,
                                cursor = Fonts.CURSOR) 

        # feedback
        self.feedback = Label(self.feedFrame,
                              text = "To provide comments/feedback, please "
                                     "do one of the following: \n"
                                     "1. Go to /r/reddit_paper and create a "
                                     "new post.\n2. Follow the account "
                                     "link at the top and send me a PM.\n3. Email "
                                     "me directly at cameron.gagnon@gmail.com",\
                              font = Fonts.XLARGE)
        # send crashReport
        self.crash_loc = StringVar()
        self.location = self.get_crash_location()
        self.crash_loc.set(self.location)

        self.report = Label(self.crashFrame,
                            text = "To send a crash report, please\n"
                            "browse to the location below and send the log\n"
                            "to cameron.gagnon@gmail.com.", 
                            font = Fonts.XLARGE)
        self.crash_loc = Label(self.crashFrame, text = self.crash_loc.get(),
                               wraplength = 480)

        # packs/binds
        # author frame pack
        self.authorTxt.pack(side = "left", padx = (60, 0))
        self.authorLink.pack(side = "left", )
        self.authorLink.bind("<Button-1>", 
                             lambda x: self.open_link(AboutInfo.reddit()))
        self.subAuthorFrame.pack(side = "top")
        # version frame pack within author frame
        self.version.pack()
        self.versionFrame.pack(side = "top")
        self.authorFrame.pack(side = "top", fill = "x", padx = (10, 15))
        # donate frame pack
        self.donateTxt.pack(side = "top", padx = (30, 0))
        self.donateTxt2.pack(side = "left", padx = (30, 0))
        self.donateLink.pack(side = "left")
        self.donateLink.bind("<Button-1>", 
                             lambda x: self.open_link(AboutInfo.PayPal()))
        self.donateFrame.pack(side = "top", fill = "x", padx = (10, 15), 
                              pady = (10, 0))
        self.subDonateFrame.pack(side = "top")
        # feedback
        self.feedback.pack(side = "top")
        self.feedFrame.pack(side = "top", fill = "x", padx = (10, 15),
                            pady = (10, 0))
        # crash report pack
        self.report.pack(side = "top")
        self.crash_loc.pack(side = "top")
        self.crashFrame.pack(side = "top", fill = "x", padx = (10, 15), 
                             pady = (10, 0))
        
    def open_link(self, link):
        webbrowser.open_new(link)

    def get_crash_location(self):
        # opens a file browser for the user to 
        # search for the log file
        return os.path.realpath("CrashReport.log")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
