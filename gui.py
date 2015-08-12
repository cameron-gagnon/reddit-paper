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
import threading
from tkinter import *
from tkinter import font
from tkinter import StringVar
from tkinter import ttk
from PIL import Image
from praw import errors


class Application(Tk):
    width = 525
    height = 555

    def __init__(self, master=None):
        Tk.__init__(self, master)

        # set title of application on titlebar
        self.wm_title("Reddit Paper")
        
        # set theme
        theme = ttk.Style()
        theme.theme_use('vista')

        # set up frame to hold widgets
        root = Frame(self)                              # background="bisque")
        root.pack(side = "top", fill = "both", expand = True)
        
        # set minsize of application
        self.setUpWindow() 

        # set docked icon in system tray
        self.addIcon() 
        
        # adds buttons and status bar for main page
        self.buttons = AddButtons(root, self)
        
        StatusBar(master)
        
        # window used to pack the pages into
        self.window = Frame(root)#bg = "cyan")         
        self.window.pack()
        self.pages = {}
        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(self.window, self)
            self.pages[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        # frame to show on startup
        self.show_frame(CurrentImg)
    def show_frame(self, page):
        """
            Input: the page to display
            Output: displays the page selected on button click
        """
        frame = self.pages[page]
        # sets the focus on the itemFrame when the
        # PastImgs button is clicked so that the
        # list of pictures is scrollable
        if page is PastImgs:
            try: 
                frame.canvas.focus_set()
            # Throws attribute error and also a _tkinter.TclError
            # which isn't a valid keyword for some reason
            except:
                rp.log.debug("Could not set focus to PastImgs, likely due to "
                             "itemFrame not being available", exc_info = True) 
                # all images are likely deleted from
                # the itemFrame
                pass
       
        self.setButtonImages(page)
        frame.tkraise()
   
    def setButtonImages(self, page):
        """
            Sets the button images for the top of the program to change 
            background color depending on which page is active
        """
        # images named by past image (p), currentimg (c),
        # about (a), settings (s), and then whether it will
        # be clicked (_c) or unclicked (_u)
        self.c_c = PhotoImage(file = './images/c_c.png')
        self.c_u = PhotoImage(file = './images/c_u.png')
        
        self.p_c = PhotoImage(file = './images/p_c.png')
        self.p_u = PhotoImage(file = './images/p_u.png')
        
        self.s_c = PhotoImage(file = './images/s_c.png')
        self.s_u = PhotoImage(file = './images/s_u.png')
        
        self.a_c = PhotoImage(file = './images/a_c.png')
        self.a_u = PhotoImage(file = './images/a_u.png')

        # if page is clicked, set that image to be '_c' (clicked)
        # and set all other pages to be 'unclicked'
        if page is CurrentImg:
            self.buttons.c.config(image = self.c_c)
            self.buttons.p.config(image = self.p_u)
            self.buttons.s.config(image = self.s_u)
            self.buttons.a.config(image = self.a_u)

        elif page is PastImgs:
            # past images page
            self.buttons.c.config(image = self.c_u)
            self.buttons.p.config(image = self.p_c)
            self.buttons.s.config(image = self.s_u)
            self.buttons.a.config(image = self.a_u)

        elif page is Settings:
            # settinsg page 
            self.buttons.c.config(image = self.c_u)
            self.buttons.p.config(image = self.p_u)
            self.buttons.s.config(image = self.s_c)
            self.buttons.a.config(image = self.a_u)
             
        else:
            # about page
            self.buttons.c.config(image = self.c_u)
            self.buttons.p.config(image = self.p_u)
            self.buttons.s.config(image = self.s_u)
            self.buttons.a.config(image = self.a_c)

 
    def addIcon(self):
        self.img = PhotoImage(file = 'images/rp_sq.png')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        

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


###############################################################################
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
    _github = "https://github.com/cameron-gagnon/reddit-paper"
    _subreddit = "https://www.reddit.com/r/reddit_paper"
    
    def version():
        return AboutInfo._version

    def author():
        return AboutInfo._author

    def reddit():
        return AboutInfo._redditAcct
    
    def subreddit():
        return AboutInfo._subreddit

    def PayPal():
        return AboutInfo._payPalAcct
    
    def email():
        return AboutInfo._email

    def GitHub():
        return AboutInfo._github


################################################################################
class Fonts():
    _VERDANA = "Verdana"
    _CURSOR = "hand2"
    _HYPERLINK = "#0000EE"
    _XL = 16 
    _L = 12
    _M = 10
    _S = 8
    _XS = 7
    _H1 = 25

    def XS():
        xs = font.Font(family = Fonts._VERDANA, size = Fonts._XS)
        return xs
    def XS_U():
        xs_u = font.Font(family = Fonts._VERDANA, size = Fonts._XS,
                       underline = True)
        return xs_u

    def S():
        s = font.Font(family = Fonts._VERDANA, size = Fonts._S)
        return s
    def S_U():
        s_u = font.Font(family = Fonts._VERDANA, size = Fonts._S,
                        underline = True)
        return s_u

    def M():
        m = font.Font(family = Fonts._VERDANA, size = Fonts._M)
        return m
    def M_U():
        med_u = font.Font(family = Fonts._VERDANA, size = Fonts._M,
                          underline = True)
        return med_u
   
    def L():
        l = font.Font(family = Fonts._VERDANA, size = Fonts._L)
        return l
    def L_U():
        l_u = font.Font(family = Fonts._VERDANA, size = Fonts._L,
                        underline = True)
        return l_u

    def XL():
        xl = font.Font(family = Fonts._VERDANA, size = Fonts._XL)
        return xl
    def XL_U():
        xl_u = font.Font(family = Fonts._VERDANA, size = Fonts._XL,
                         underline = True)
        return xl_u

   
    def H1():
        h1 = font.Font(family = Fonts._VERDANA, size = Fonts._H1)
        return h1
    def H1_U():
        h1_u = font.Font(family = Fonts._VERDANA, size = Fonts._H1,
                         underline = True)
        return h1_u


######################## Classes for Messages #################################
class Message(Toplevel):

    def __init__(self, master, title):
        """
            Creates popup as Toplevel() and sets its title in the window 
        """
        Toplevel.__init__(self, master)
        #self.popup = Toplevel() 
        self.wm_title(title)
        self.addIcon('images/rp_sq.png')
        self.set_dimensions(master, 400, 400)
        self.inner_frame = Frame(self, width = 400, height = 400)
        self.inner_frame.pack()

#        self.pack_button()
        # bit of a hack to ensure that the window has grab_set applied to it 
        # this is because the window may not be there when self.grab_set() is
        # called, so we wait until it happens without an error
        while True:
            try:
                self.grab_set()
            except TclError:
                pass
            else:
                break

    def set_dimensions(self, master, w, h):
        """
            Sets the position and size on screen for the popup 
        """
        x = master.winfo_rootx()
        y = master.winfo_rooty()
        x = (Application.width // 2) + x - (w // 2) - 10
        y = (Application.height // 2) + y - 405
        # set permanent dimensions of popup
        self.minsize(width = w, height = h)
        self.maxsize(width = w, height = h)
        self.geometry('{}x{}+{}+{}'.format(w, h, x, y))
 
    def delete(self):
        """
            Destroys the popup
        """
        self.grab_release()
        self.destroy()

    def pack_label(self, text, pady = 8, font =  None, anchor = "center",
                   justify = None):
        """
            Packs a label into the popup with the specified text
        """
        # bit of a hack since Fonts.L() throws an error if present in the
        # function declaration
        if not font:
           font = Fonts.M()
            
        label = ttk.Label(self.inner_frame, anchor = anchor,
                          text = text, wraplength = 420,
                          font = font, justify = justify)
        label.pack(side = "top", fill = "x", pady = pady)

    def pack_button(self, pady = (10, 10)):
        """
            Place a button at the bottom of the widget with the text "Okay"
        """
        b = ttk.Button(self.inner_frame, text = "Okay", command = self.delete)
        b.pack(side = "bottom", pady = pady)

    def addIcon(self, file_name):
            """
                Adds an error icon to the popup box
            """
            self.img = PhotoImage(file = file_name)
            self.tk.call('wm', 'iconphoto', self._w, self.img)


class ErrorMsg(Message):
    
    def __init__(self, master, text, title = "Error!"):
        popup = Message.__init__(self, master, title) 
        length = 0
        height = 0
        self.addIcon('images/error.png')

        if isinstance(text, list):
            if len(text) == 1:
                # if string, return length of string
                length = len(text[0])
                height = 170
                height += length // 60 * 15
                rp.log.debug("Length of error string is: {}, "
                             "and height is: {}".format(length, height))
            elif len(text) > 1:
                # find max length of string in the list of errors
                length = len(max(text))
                # length of the list is num of elts in list 
                # so to get the height, we take this and
                # multiply it by a constant and add a base amount
                height = len(text) * 25 + 130
                height += length // 60 * 15
                rp.log.debug("Length of  max error string is: {} " 
                             "and height is {}".format(length, height))
            else:
                # no errors in CLArgs
                pass 
            self.pack_label("Invalid Argument(s):")

        
        else:
            # if just a regular string that we want an error message
            length = len(text) 
            height = 125
            height += len(text) // 60 * 15
            self.pack_label("Invalid Argument(s):")
            self.pack_label(text)
            rp.log.debug("Length of error string is: {}, "
                         "and height is: {}".format((length, height)))
        #length * 5 because each char is probably 
        # about 5 px across. + 160 for padding
        width = length * 5 + 160
        if (length * 5 + 160) > 475:
            width = 475
        
        rp.log.debug("Width of ErrorMsg is {}".format(width))
        rp.log.debug("Height of ErrorMsg is {}".format(height))
        self.set_dimensions(master, width, height)
        self.pack_button()

class InvalidArg(ErrorMsg):

    def __init__(self, master, text):
        """
            Used spcecifically to display the CLArguments            
        """
        
        ErrorMsg.__init__(self, master, text)

        if len(text) > 1:
            for string in text:
                self.pack_label(string)
        elif len(text) == 1:
            self.pack_label(text[0])
        else:
            rp.log.debug("No errors in CLArgs")


class ConfirmMsg(Message):

    def __init__(self, master):
        """
            Pop up box/message for confirmation of settings/deleting settings
        """
        Message.__init__(self, master, "Confirm!")

        width = 180
        height = 75
        self.set_dimensions(master, width, height)
        
        self.pack_label("Are you sure?")
        BFrame = Frame(self)
        BFrame.pack()
        B1 = ttk.Button(BFrame, text = "Yes", command = lambda: master.del_sel(self))
        B2 = ttk.Button(BFrame, text = "No", command = self.delete)
        B1.pack(side = "left")
        B2.pack(side = "left")


class AutoScrollbar(ttk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid(sticky = 'nsew')

        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise Exception("cannot use pack with this widget")
    def place(self, **kw):
        raise Exception("cannot use place with this widget")


class ImageFormat():

    def strip_file_ext(self, image_name):
        """
            Used to remove the .jpg or other ending from im.image_name
            so that we can resave the thumbnail with .png
        """
        index = image_name.rfind('.')
        im_name = image_name[:index]
        return im_name

    def add_png(self, image_name):
        """
            Appends the .png to the end of im.image_name to save the
            thumbnail with .png
        """
        im_name = image_name + ".png"
        return im_name


class StatusBar(Frame):

    def __init__(self, master): 
        Frame.__init__(self, master)
        """
            Represents the statusbar at the bottom of the application.
            The statusbar is set up in AddButtons()
            It reads from the settings.conf file to get the statusbar
            text and then updates accordingly.
            Executes after every second.
        """
        # statusbar for bottom of application
        self.text = StringVar()
        self.text.set(rp.Config.statusBar())
        self.statusBar = ttk.Label(master, text = self.text.get(), border=1,
                          relief = SUNKEN, anchor = "w")
         
        # pack the labels/frame to window
        self.statusBar.pack(side = "bottom", fill = "x", anchor = "w")
        self.setText()

    def setText(self):
        """
            Sets the text of the status bar to the string in the 
            config file 'settings.conf' 
        """
        text = rp.Config.statusBar()
        
        if text == self.text:
            pass
        else:
            self.text = text
            self.statusBar.config(text = self.text)
            
        self.after(1000, lambda: self.setText())


###############################################################################
class AddButtons(Frame):

    def __init__(self, master, cls):
        Frame.__init__(self, master)
        self.topbar = Frame(master)#bg="red")

        # current image button
        self.cphoto = PhotoImage(file="./images/c_c.png")
        self.c = Button(self.topbar, image = self.cphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/p_u.png")
        self.p = Button(self.topbar, image = self.pphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/s_u.png")
        self.s = Button(self.topbar, image = self.sphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/a_u.png")
        self.a = Button(self.topbar, image = self.aphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")

        self.topbar.pack(side = "top")


# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame, ImageFormat):

    TIMER = 3000

    def __init__(self, parent, controller):
        """
            Packs the frames needed, and initiaties 
            the updateFrame to continuously call itself
        """
        Frame.__init__(self, parent)
        # pack frames/labels
        self.frame = Frame(self, width = 525, height = 400)#, bg = "#969696")     #bg = "magenta")
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
            # AttributeError is in case the image returned
            # is incomplete
            except (AttributeError, TypeError):
                rp.log.debug("Attribute Error in get_past_img")

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
        self.subFrame = Frame(self.frame, width = 525, height = 410)
        self.subFrame.pack_propagate(0)
        self.subFrame.pack()
       
        font_to_use = Fonts.L_U()
        # set font to be smaller if title is too long
        if len(im.title) > 150:
            font_to_use = Fonts.M_U()
        
        # create title link
        self.linkLabel = ttk.Label(self.subFrame,
                                   text = im.title,
                                   font = font_to_use,
                                   justify = 'center',
                                   foreground = Fonts._HYPERLINK,
                                   cursor = Fonts._CURSOR,
                                   wraplength = 500)
        self.linkLabel.pack(pady = (35, 10), padx = 10)
        self.linkLabel.bind("<Button-1>", lambda event: self.open_link(im.post))
        
        try:   
            # create image and convert it to thumbnail
            with open(im.save_location, 'rb') as image_file:
                imThumb = Image.open(image_file)
                im.strip_file_ext()
                im.updateSaveLoc()
                imThumb.thumbnail((400, 250), Image.ANTIALIAS)
                imThumb.save(im.thumb_save_loc_C, "PNG")
            # apply photolabel to page to display
            self.photo = PhotoImage(file = im.thumb_save_loc_C)
            self.photoLabel = ttk.Label(self.subFrame, image = self.photo)
            self.photoLabel.pack(side = "bottom", expand = True)
        except FileNotFoundError:
            pass

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
    
    def __str__(self):
        return "Current Image"

# **** Past Images Page **** #
# Gives a listing of past submissions, with a smaller thumbnail of the image
# and the title/resolution of the images.
# Includes: * checkboxes to delete the images selected
#           * Scrollable list of all images downloaded/used in the past
class PastImgs(Frame, ImageFormat):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
       
        # select all box
        self.selVar = BooleanVar()
        self.selVar.set(False)
        self.selVar.trace('w', lambda e, x, y: self.change_all(e)) 
        selectBox = ttk.Checkbutton(self, text = "Select all",  variable = self.selVar)
        selectBox.pack(anchor = 'w', pady = (15, 2), padx = (35, 10))

        ### begin canvas/frame/picture list
        self.picFrame = Frame(self, width = 450, height = 300)
        
        self.picFrame.grid_rowconfigure(0, weight = 1)
        self.picFrame.grid_columnconfigure(0, weight = 1)
        self.picFrame.pack()
        
        self.canvas = Canvas(self.picFrame, width = 450, height = 300)
        self.canFrame = Frame(self.canvas)

        self.canvas.create_window((0,0), window = self.canFrame, anchor = 'nw')
        self.canvas.pack(side="left")
        self.setScroll()

        # POPULATE CANVAS WITH IMAGES!!!!!!!!
        self.picList = self.findSavedPictures()
        # these lists save each checkbox and frame/photo so we can
        # identify them later when they need to be destroyed
        self.frames = []
        self.already_deleted = []
        self.itemFrame = []
        self.populate(self.canFrame, self.picList)

        # bottom frame for buttons
        self.bottomFrame = Frame(self)
        self.delete = ttk.Button(self.bottomFrame, text = "Delete selected", 
                               state = "normal",
                               command = lambda: ConfirmMsg(self))
        # 'delete all' button 'delete selected' button
        self.delete.pack(side = "right", padx = (0, 3))

        # packs the frame that holds the delete buttons
        self.bottomFrame.pack(side = "bottom", anchor = "e",
                              pady = (0, 15), padx = (0, 27))
        ### end canvas/frame/picture list

        self.updatePastImgs()

    def setScroll(self):
        # create frame to hold scrollbar so we can
        # use grid on the scrollbar
        try:
            self.scrollFrame.destroy()
        except:
            # no scrollbar yet created
            pass

        self.scrollFrame = Frame(self.picFrame)

        # set rows and column configures so we can
        # make scrollbar take up entire row/column
        self.scrollFrame.rowconfigure(1, weight = 1)
        self.scrollFrame.columnconfigure(1, weight = 1)
        self.scroll = AutoScrollbar(self.scrollFrame,
                                    orient = "vertical",
                                    command = self.canvas.yview)

        # set scrollbar as callback to the canvas
        self.canvas.configure(yscrollcommand = self.scroll.set)

        # set the scrollbar to be the height of the canvas
        self.scroll.grid(sticky = 'ns', row = 1, column = 0)

        # set the scrollbar to be packed on the right side
        self.scrollFrame.pack(side="right", fill="y")

        # bind the picture frame to the canvas
        self.picFrame.bind("<Configure>", self.setFrame) 
        self.setFrame()

    def setFrame(self, event = None):
        """ Sets the canvas dimensions and the scroll area """
        self.canvas.configure(scrollregion = self.canvas.bbox('all'))

    def setKeyBinds(self, widget):
    
        """
            Sets the binds to the keys for the canvas movements
            when adding new elts
        """
        widget.bind("<MouseWheel>", self.onMouseWheel)
        widget.bind("<Up>", self.onMouseWheel)
        widget.bind("<Down>", self.onMouseWheel)
     
    def onMouseWheel(self, event):
        """
            Scrolls the canvas up or down depending on the 
            event entered (arrow keys/mouse scroll)
        """
        keyNum = {40 : 1,   # Down arrow key
                  38 : -1}  # Up arrow key
        scrollVal = None

        if event.keycode in keyNum:
            scrollVal = keyNum.get(event.keycode)
        else:
            scrollVal = int(-1*(event.delta/120))

        self.canvas.yview_scroll(scrollVal, "units")

    def change_all(self, event):
        """
            selects/deselects all the pictures (to be deleted)
        """
        if self.selVar.get():
            self.selVar.set(True)
            for box in self.frames:
                box[0].set(True)
        else:
            self.selVar.set(False)
            for box in self.frames:
                box[0].set(False)

    def del_sel(self, popup):
        """
            Delete all frames that have their checkbox
            checked.
            self.frames[i][2]   ## image class
            self.frames[i][2].save_location
                                ## file path to original img
                                '/path/to/file/jkY32rv.jpg'
            self.frames[i][2].thumb_save_loc_P 
                                ## file path to _P.png thumbnail 
                                '/path/to/file/jkY32rv_P.png'
            self.frames[i][2].thumb_save_loc_C 
                                ## file path to _C.png thumbnail
                                '/path/to/file/jkY32rv_C.png'
            self.frames[i][2].image_name       ## original img name 'jkY32rv.jpg' 
            self.frames[i][0] ## checkbox var
            self.frames[i][1] ## frame to destroy
        """
        # create copy so we don't modify a list as we
        # loop over it
        to_check_list = self.frames[:]
        i = 0
        for frame in to_check_list:
            # if the checkbox var is True
            if frame[0].get() and len(self.picList):
                # deletes frame from canvas
                try:
                    rp.log.debug("i is: {} frames len: {} picList len: {}".format(i, len(self.frames), len(self.picList)))
                    #print(self.frames)
                    #print(self.picList)
                    rp.log.debug("CANFRAME IS: {}".format(self.canFrame.winfo_height()))
                    to_del = self.frames.pop(i)
                    rp.log.debug("LEN OF FRAME IS NOW: {}".format(len(self.frames)))
                    rp.log.debug("Popping: {}".format(self.picList[i].image_name))
                    self.picList.pop(i)
                    rp.log.debug("LEN OF PICLIST IS NOW: {}".format(len(self.picList)))
                    item = self.itemFrame.pop(i)
                    # delete visible frame
                    #to_del[1].des
                    item.destroy()
                    # reset scrollbar
                    self.scroll.destroy()
                    self.scrollFrame.destroy()
                    self.setScroll()

                except AttributeError:
                    # occurs when a frame is supposed to be present
                    # but actually isn't
                    rp.log.debug("Frame isn't present", exc_info = True)
                
                to_del_img = to_del[2]

                try:
                    rp.log.debug("to_del P: %s" % to_del_img.thumb_save_loc_P)
                    rp.log.debug("to_del C: %s" % to_del_img.thumb_save_loc_C)
                    rp.log.debug("to_del : %s" % to_del_img.save_location)
                    # delete thumbnail_P
                    os.remove(to_del_img.thumb_save_loc_P)
                    rp.log.debug("Removed to_del_P")
                    # delete original file
                    os.remove(to_del_img.save_location) 
                    rp.log.debug("Removed to_del")
                    
                    # delete database entry
                    rp.Database.del_img(to_del_img.image_name)
                    
                    # add to_del_img.image_name to list so we don't
                    # add it again
                    self.already_deleted.append(to_del_img.image_name)

                    try:
                        os.remove(to_del_img.thumb_save_loc_C)
                        rp.log.debug("Removed to_del_C: %s" % to_del_img.thumb_save_loc_C)
                    except FileNotFoundError:
                        # image was likely not set as current image, may not
                        # have been correct dimensions
                        rp.log.debug("It appears that the image %s was never "
                                     "set as a current image" % to_del_img.thumb_save_loc_C)


                except (OSError, FileNotFoundError):
                    rp.log.debug("File not found when deleting", exc_info = True)
                    rp.log.debug(to_del_img.image_name)
            else:
                i += 1

        self.setFrame()
        self.scroll.destroy()
        self.setScroll()
        self.selVar.set(False)
        # don't forget to destroy the popup!
        popup.destroy()
       
    def remove_C(self, photoPath, photo):
        """
            Formats the photo name so that the photo name is
            the %PHOTONAME%_C.png and then prepend the file path
            to the photo, as it does not contain the path
        """
        # take the .png off, add _C to it, then add .png
        # back on
        imageC = self.strip_file_ext(photo)
        imageC += "_C"
        imageC = self.add_png(imageC)


        # retrieves the download location based on 
        # other image
        index = photoPath.rfind('/') + 1 
        path = photoPath[:index]
        imageC = path + imageC
        
        return imageC

    def populate(self, frame, picList):
        """
            Fill the frame with more frames of the images
        """
        rp.log.debug("Len of picList to populate is {}".format(len(picList)))
        for i, im in enumerate(picList):
            rp.log.debug("I IS FRESH AND IS {}".format(i))
            try:
                rp.log.debug("IMAGE SAVE LOC IS: {}".format(im.save_location))
                with open(im.save_location, 'rb') as image_file:
                    # create and save image thumbnail
                    # PIL module used to create thumbnail
                    imThumb = Image.open(image_file)
                    im.strip_file_ext()
                    im.updateSaveLoc()
                    imThumb.thumbnail((50, 50), Image.ANTIALIAS)
                    imThumb.save(im.thumb_save_loc_P, "PNG")

            except (FileNotFoundError, OSError):
                # usually a file that is not an actual image, such
                # as an html document
                rp.log.debug("ERROR IS:", exc_info = True)
                rp.log.debug("FILE NOT FOUND, OR OS ERROR, I is {}".format(i))
                i -= 1
                rp.log.debug("I SUBTRACTED {}".format(i))
                continue 
 
            # create frame to hold information for one picture
            item = Frame(frame, width = 450, height = 50)

            # self.picList has already been appended to before those pictures
            # that were appended were gridded. Therefore, we subtract the len
            # of the new images we are adding, since that will give us the 
            # row of the last image that was added, and then we add our current
            # index to this so we arrive at the latest unoccupied row
            len_p_list = len(self.picList)
            len_list = len(picList)
            # only change the row if the p_list is a 
            # different length of len_list
            if (len_p_list - len_list) != 0:
                rp.log.debug("I WAS {}".format(i))
                i += (len_p_list - len_list)
                rp.log.debug("UPDATING I INDEX to {}".format(i))

            rp.log.debug("I is now {}".format(i))
            item.grid(row = i, column = 0)
            #rp.log.debug("LEN of item frame before append: ", len(self.itemFrame))
            self.itemFrame.append(item)
            #rp.log.debug("LEN OF ITEM FRAME IN POPULATE: ", len(self.itemFrame))
            item.pack_propagate(0)

            # checkbox to select/deselect the picture
            checkVar = BooleanVar(False)
            check = ttk.Checkbutton(item,
                                         variable = checkVar)
            check.pack(side = "left", padx = 5)
           
            # insert the thumbnail and make the frame have a minimum w/h so
            # that the im.title won't slide over to the left and off-center
            # itself
            photo = PhotoImage(file = im.thumb_save_loc_P)
            photoFrame = Frame(item, width = 75, height = 50)
            photoFrame.pack_propagate(0)
            photoLabel = ttk.Label(photoFrame, image = photo)
            photoFrame.pack(side = "left")
            photoLabel.image = photo # keep a reference per the docs!
            photoLabel.pack(side = "left", padx = 10)
            
            # text frame
            txtFrame = Frame(item)
            txtFrame.pack()

            # title label 
            # slice and add ellipsis if title is too long 
            font = Fonts.S()
            if len(im.title) > 110:
                im.title = im.title[:110] + '...'
                font = Fonts.XS()

            title = ttk.Label(txtFrame,
                                   text = im.title,
                                   font = font,
                                   wraplength = 325,
                                   justify = 'center')
            title.pack(side = "top", padx = 10)
            
            botTxtFrame = Frame(txtFrame)
            botTxtFrame.pack(side = "bottom", anchor = 'center')
            botTxtFrame.pack_propagate(0)
            
            # link to post
            link = ttk.Label(botTxtFrame,
                                  text = "Link",
                                  font = Fonts.M_U(),
                                  cursor = Fonts._CURSOR,
                                  foreground = Fonts._HYPERLINK)
            link.grid(row = 0, column = 0)
 
            """
            how to remember variable/function in a for loop:
                https://stackoverflow.com/questions/14259072/
                tkinter-bind-function-with-variable-in-a-loop/
                14260871#14260871
            """
            link.bind("<Button-1>", self.make_link(im))
            
            # set as wallpaper text
            setAs = ttk.Label(botTxtFrame,
                                   text = "Set as Wallpaper",
                                   font = Fonts.M_U(),
                                   cursor = Fonts._CURSOR,
                                   foreground = Fonts._HYPERLINK)
            setAs.grid(row = 0, column = 1)
            setAs.bind("<Button-1>", self.make_wallpaper(im))

            # add to the past images frame to display pictures
            # self.itemFrame is added so we can delete the frame later on
            self.frames.append((checkVar, self.itemFrame, im))
            
            # for loop over children of itemFrame did not work
            # to set keybinds, so we manually set all keybinds
            # so scrolling is enabled for both mouse and arrow keys
            self.setKeyBinds(item)
            self.setKeyBinds(setAs)
            self.setKeyBinds(link)
            self.setKeyBinds(botTxtFrame)
            self.setKeyBinds(title)
            self.setKeyBinds(txtFrame)
            self.setKeyBinds(photoLabel)
            self.setKeyBinds(check)

        self.scroll.destroy()
        self.setScroll()
        self.setKeyBinds(self.canvas) 

    def make_link(self, im):
        """ 
            Returns a lambda so each past image corresponds
            to its own function and they don't all
            end up sharing the same function. See the
            link posted above.
        """
        return lambda e: self.open_link(im.post)
    
    def make_wallpaper(self, im):
        """ 
            Returns a lambda so each past image corresponds
            to its own function and they don't all
            end up sharing the same function. See the
            link posted above.
        """
        return lambda e: im.setAsWallpaper()

    def findSavedPictures(self):
        """
            Returns a list of pictures in the wallpaper.db
        """
        pictures = rp.PictureList.list_pics()
        return pictures
       
    def open_link(self, link):
        """ Opens the link in the default webbrowser """
        webbrowser.open_new(link)

    def updatePastImgs(self):
        """
            Updates the past images with new ones that
            may have been downloaded. Updates happen
            every 1 second
        """
        # get list of all pictures
        pictures = self.findSavedPictures()
        new_pictures = False
        new_pics = []
        # get all image names from database
        image_name_list = [pic.image_name for pic in self.picList]
        # loop through each picture

        for picture in pictures:
            # if picture is not already displayed
            # and if it hasn't been deleted.
            # then it probably wasn't there before
            # so we add it to the list to be displayed
            if (picture.image_name not in image_name_list):# and\
               #(picture.image_name not in self.already_deleted):
                new_pictures = True
                new_pics.append(picture)
                self.picList.append(picture)

        if new_pictures:
            rp.log.debug("NEW PICTURES AREEEEEE")
            for pic in new_pics:
                rp.log.debug(pic.image_name)
            rp.log.debug("ALREADY DELETED {}".format(self.already_deleted))
            # pass in the frame to pack the new pictures in to 
            self.populate(self.canFrame, new_pics)
            rp.log.debug("Past populate")

            # destroy scrollbar so it doesn't make a new scrollbar each
            # time we update pastimages
            self.scroll.destroy()
            self.scrollFrame.destroy()
            self.setScroll()

        self.after(30000, lambda: self.updatePastImgs())

    def __str__(self):
        return "Past Images"

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
        rp.Config.read_config()
        Frame.__init__(self, parent)
        self.top = Frame(self)
        # subreddit border
        self.subredditF = ttk.LabelFrame(self,
                                         text = "Subreddits to pull from "\
                                                "(separated by a space)")
        # nsfw border
        self.midTop = Frame(self.top)
        self.checksFrame = ttk.LabelFrame(self.midTop, text = "Adult Content")
        self.checks = Frame(self.checksFrame)
        
        # width x height
        self.dimensions = ttk.LabelFrame(self.top, 
                                     text = "Picture Resolution")
        self.res = Frame(self.dimensions)

        # maxposts
        self.maxLabel = ttk.LabelFrame(self.midTop, text = "# of Posts")
        self.maxFrame = Frame(self.maxLabel)
        self.maxTxt = ttk.Label(self.maxFrame, text = "Max posts:")
        self.maxTxt.pack(side = "left", padx = (0, 5))
        self.maxE = ttk.Entry(self.maxFrame, width = 3)
        self.maxE.insert(0, rp.Config.maxposts())
        self.maxE.pack(side = "left", padx = 5, pady = 5)
        self.maxFrame.pack(padx = 5)

        # cycletime border and frame
        self.topRt = Frame(self.top)
        self.ct = ttk.LabelFrame(self.topRt, text = "Wallpaper Timer")
        self.ctFrame = Frame(self.ct)
        
        # category border and frame
        self.cat = ttk.LabelFrame(self.topRt, text = "Section")
        self.catFrame = Frame(self.cat, width = 185, height = 25)
        self.catFrame.pack_propagate(0)

        # download location border
        self.dlFrame = ttk.LabelFrame(self, text = "Picture download location")
         
        # Single link border
        self.singleF = ttk.LabelFrame(self, text = "Direct download link  "\
                                        "ex. https://i.imgur.com/rhd1TFF.jpg")
        self.singleE = ttk.Entry(self.singleF, width = 63)
        self.singleE.pack(side = "left", pady = 5, padx = 10, anchor = 'w')
        self.singleB = ttk.Button(self.singleF, text = "Get Image")
        self.singleB.pack(side = "right", padx = 5, pady = 5)
        self.singleB.bind("<Button-1>", lambda event: rp.Single_link(self.singleE.get()))

        # Buttons
        self.buttonFrame = Frame(self)
        self.letsGo = ttk.Button(self.buttonFrame, text = "Let's Go!")
        self.help = ttk.Button(self.buttonFrame, text = "Help")
      
        # subreddit entry
        self.subreddits = ttk.Entry(self.subredditF, width = 78)
        self.subreddits.insert(0, rp.Config.subreddits())
        self.subreddits.grid(row = 1, column = 2, columnspan = 2, padx = 5,
                             sticky = "w", pady = 5, ipadx = 3)
        # "download to" entry
        self.dlTxt = ttk.Label(self.dlFrame, text = "Download pictures to:") 
        self.dlTxt.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.dlLoc = ttk.Entry(self.dlFrame, width = 57)
        self.dlLoc.insert(0, rp.Config.downloadLoc())
        self.dlLoc.grid(row = 0, column = 1, sticky = "w", padx = 5, pady = 5,
                        ipadx = 1)

        # Frames for width x height
        self.widthF = Frame(self.res)
        self.heightF = Frame(self.res)
        self.widthF.pack(side = "top")
        self.heightF.pack(side = "top")

        # Min width
        self.minWidthTxt = ttk.Label(self.widthF, text = " Min-width:")
        self.minWidthTxt.grid(row = 0, column = 0, sticky = "e", padx = 5, pady = (5, 0))
        # min width entry
        self.minwidth = ttk.Entry(self.widthF, width = 6)
        self.minwidth.insert(0, rp.Config.minwidth())
        self.minwidth.grid(row = 0, column = 1, padx = 5, pady = 5)
        # Min height
        minHeightTxt = ttk.Label(self.heightF, text = "Min-height:")
        minHeightTxt.grid(row = 1, column = 0, sticky = "e", padx = 5, pady = (0, 5))
        # min height entry
        self.minheight = ttk.Entry(self.heightF, width = 6)
        self.minheight.insert(0, rp.Config.minheight())
        self.minheight.grid(row = 1, column = 1, padx = 5, pady = (0, 5))
       
        # nsfw checkbutton
        # nsfw on text
        nsfwTxt = ttk.Label(self.checks, text = "NSFW:")
        nsfwTxt.pack(side = "left", padx = 5)
        # nsfw var config
        self.onOff = BooleanVar()
        self.onOff.set(rp.Config.nsfw())
        # nsfw checkbutton config
        self.nsfw = ttk.Checkbutton(self.checks, text = "On",
                                variable = self.onOff)
       
        # cycletime txt
        self.ctTxt = ttk.Label(self.ctFrame, text = "Set for:")
        self.ctTxt.grid(row = 0, column = 0, sticky = "e", padx = (5,0))
        # cycletime entry
        self.rpHr, self.rpMin = rp.Config.cycletime()
        # hour txt/entry
        self.ctHourE = ttk.Entry(self.ctFrame, width = 3)
        self.ctHourE.insert(0, self.rpHr)
        self.ctHourE.grid(row = 0, column = 1, padx = (5,0), pady = 5)
        self.ctHourTxt = ttk.Label(self.ctFrame, text = "hrs")
        self.ctHourTxt.grid(row = 0, column = 2, padx = (0, 5))
        # min txt/entry
        self.ctMinE = ttk.Entry(self.ctFrame, width = 4)
        self.ctMinE.insert(0, self.rpMin)
        self.ctMinE.grid(row = 0, column = 3)
        self.ctMinTxt = ttk.Label(self.ctFrame, text = "mins", anchor = "w")
        self.ctMinTxt.grid(row = 0, column = 4, padx = (0, 5))
        self.ctFrame.pack(side = "top")
       
        # category dropdown
        self.choices = ["Top", "Hot", "New", "Rising", "Controversial"]
        self.catVar = StringVar(self)
        self.optionVar = rp.Config.category()
        self.catVar.set(self.optionVar)
        self.catDD = ttk.OptionMenu(self.catFrame, self.catVar, self.optionVar, *self.choices)
        self.catDD.config(width = 14)
        self.catDD.pack(side = "right", anchor = "e", padx = (0, 5), pady = 5) 
        self.catTxt = ttk.Label(self.catFrame, text = "Category:")
        self.catTxt.pack(side = "left", anchor = "e", padx = (5, 0))
        self.catFrame.pack(side = "top", ipady = 5)
        
        # packs/binds
        # button packs
        self.buttonFrame.pack(side = "bottom", pady = (10, 30))
        self.letsGo.pack(side = "left", padx = (200, 0))
        self.help.pack(side = "left", padx = (128, 0))
        self.help.bind("<Button-1>", lambda event: self.help_box(parent))
        self.letsGo.bind("<Button-1>", lambda event: self.get_pics())

        self.nsfw.pack(side = "left", anchor = "nw", pady = 5,
                       padx = (0, 5))
        # top holds dimensions and user/pass labelFrames
        self.top.pack(side = "top", anchor = "w", pady = (10, 10))
        self.subredditF.pack(side = "top", anchor = "w",
                                padx = (15, 10))
        self.dlFrame.pack(side = "top", anchor = "w", pady = 10,
                          padx = 15)
        self.singleF.pack(side = "top", anchor = 'w', padx = (15, 10))
        self.dimensions.pack(side = "left", anchor = "nw", pady = (0, 10),
                             padx = (15, 5))
        self.res.pack(side = "top")
        self.midTop.pack(side = "left", padx = 25) 
        self.checks.pack(side = "top")
        self.checksFrame.pack(side = "top", anchor = "nw",
                         padx = 5)
        self.maxLabel.pack(side = "top", pady = 10)
        # cycletime and category frame
        self.cat.pack(side = "top")
        self.ct.pack(side = "bottom", pady = 5)
        self.topRt.pack(side = "left", anchor = "nw", padx = (5, 5))

    def help_box(self, parent):
        """ 
            Help box for when a user needs to better understand
            how the program works
        """
        self.Message = Message(parent, "Help")
        self.Message.set_dimensions(parent, 450, 460)
        self.Message.pack_button()
        self.Message.pack_label("For extra help, please refer to the Feedback"
                                " and Crash Report section on the next tab."
                                " An FAQ is also available at the"
                                " subreddit /r/reddit_paper.",
                                anchor = 'center',
                                justify = 'center',
                                pady = (10, 5))
        self.Message.pack_label("*Picture Resolution* Specifies the minimum"\
                                " width and height required to add a wallpaper"\
                                " to the queue.",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*Adult Content* When the box is checked it will"
                                " filter out wallpapers that are NSFW.",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*Section* Specifies what category to pull from"
                                " on Reddit. Most of the time when browsing Reddit"
                                " you are browsing hot by default",
                                font =  Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*# of Posts* The number of posts to search"
                                " through. If using a single subreddit, the first"
                                " X number of posts will be searched through. If"
                                " using a multireddit, a breadth-first-search is"
                                " performed.",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*Wallpaper Timer* How long the wallpaper will be"
                                " set as the background.",
                                font = Fonts.S(),
                                anchor = 'w', 
                                pady = 5)
        self.Message.pack_label("*Subreddits* Enter subreddits separated by a space."
                                " More than one subreddit to search through is supported.",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*Download Location* This is where the pictures will"
                                " be downloaded to.",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
        self.Message.pack_label("*Direct Download Link* Enter a full URL to a picture"
                                " to be set as the wallpaper. This link is most commonly"
                                " found by right clicking, then 'open image in new tab'",
                                font = Fonts.S(),
                                anchor = 'w',
                                pady = 5)
    def get_values(self):
        """ returns the values stored in the entry boxes """
        self.values = {}
        self.values['-mw'] = self.minwidth.get()
        self.values['-mh'] = self.minheight.get()
        self.values['--nsfw'] = self.onOff.get()
        self.values['-s'] = self.subreddits.get().replace(" ", "+")
        self.values['-dl'] = self.dlLoc.get()
        self.values['-c'] =  self.catVar.get().lower()
        self.values['-mp'] = self.maxE.get()

        errors = self.test_values(self.values)
        
        try:
            # convert hours to minutes, then add it to minutes, so we 
            # are only dealing with total minutes in the end
            totalTime = float(self.ctHourE.get()) * 60
            totalTime += float(self.ctMinE.get())
            print("TOTAL TIME IS:::: %.2f" % totalTime)
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
        # if len(values) != 7:
        #     errors.append("Please fill in all settings options")
        #     return errors
        if not str(values['-mw']).isdigit() or int(values['-mw']) <= 0:
            errors.append(values['-mw'])
        if not str(values['-mh']).isdigit() or int(values['-mh']) <= 0:
            errors.append(values['-mh'])
        if not str(values['-mp']).isdigit() or\
           (int(values['-mp']) > 99) or (int(values['-mp']) <= 0):
            errors.append(values['-mp'])
        if not subs.isalnum():
            errors.append(values['-s'])
        if values['-dl'][values['-dl'].rfind('\\'):] != values['-dl'][-1:]:
            errors.append("Make sure path ends with a '\\' " + values['-dl'])

        return errors

    def get_pics(self):
        """ 
            Makes the call to subprocess.popen() to
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
        # create string for list of args
        self.argList = 'redditpaper.pyw'
        rp.log.debug(os.getcwd())

        for k, v in self.args.items():
            rp.log.debug("Key, Value in CLArgs is: "
                         + k + " " + str(v))
            if v:
                # add key and value to the string to be
                # passed as cmd line args
                # the key will be the switch for the arg
                self.argList += " " + k + " " + str(v)
        self.argList = "python.exe " + self.argList
        # call main function with cmd line args
        rp.log.debug("Argument list is: " + self.argList)
        
        # should have all valid arguments at this point
        try:
            # threaded fn call to run the rp.main part off of
#            rpKwargs = {"argList": self.argList}
#            rpRun = threading.Thread(target = rp.main(self.args),
#                                     name = "Reddit Paper")
            #rpRun.start()
#            rp.main(self.args)
            subprocess.Popen(self.argList.split())
        except:
            # catch all errors from rp.main so we raise them
            # and they don't get swallowed
            raise

    def __str__(self):
        return "Settings"


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
        self.authorFrame = ttk.LabelFrame(self, text = "Author")
        self.donateFrame = ttk.LabelFrame(self, text = "Donations")
        self.crashFrame = ttk.LabelFrame(self, text = "Crash Report")
        self.versionFrame = Frame(self.authorFrame)
        self.subAuthorFrame = Frame(self.authorFrame)
        self.feedFrame = ttk.LabelFrame(self, text = "Feedback")

        # author
        self.authorTxt = ttk.Label(self.subAuthorFrame,
                               text = "This program was created by: ",\
                               font = Fonts.M())
        self.authorLink = ttk.Label(self.subAuthorFrame, 
                                    text="/u/camerongagnon", 
                                    font = Fonts.M_U(), 
                                    foreground = Fonts._HYPERLINK,
                                    cursor = Fonts._CURSOR)

        # version number
        self.vNum = StringVar()
        self.vNum.set("Version: " + rp.AboutInfo.version() + "." +
                      AboutInfo.version())
        self.version = ttk.Label(self.versionFrame, text = self.vNum.get(),
                             font = Fonts.M())
        
        # donate text/link
        self.donateTxt = ttk.Label(self.donateFrame,
                               text = "If you enjoy this program, "
                                      "please consider making a donation ",
                               font = Fonts.M())
        self.subDonateFrame = Frame(self.donateFrame)
        self.donateTxt2 = ttk.Label(self.subDonateFrame,
                                text = "to the developer",
                                font = Fonts.M()) 
        self.donateLink = ttk.Label(self.subDonateFrame, text = "here.",
                                    font = Fonts.M_U(),
                                    foreground = Fonts._HYPERLINK,
                                    cursor = Fonts._CURSOR) 

        # feedback
        self.feedback = ttk.Label(self.feedFrame,
                                  text = "To provide comments/feedback, please "
                                         "do one of the following: ",
                                  font = Fonts.M())
        self.subredditFrame = Frame(self.feedFrame)
        self.feedback1 = ttk.Label(self.subredditFrame, 
                                   text = "1. Go to",
                                   font = Fonts.M())
        self.subredditLink = ttk.Label(self.subredditFrame,
                                       text = "/r/reddit_paper",
                                       font = Fonts.M_U(),
                                       cursor = Fonts._CURSOR,
                                       foreground = Fonts._HYPERLINK)
        self.feedback12 = ttk.Label(self.subredditFrame,
                                    text = "and create a new post.",
                                    font = Fonts.M())
        self.feedback2 = ttk.Label(self.feedFrame,
                                   text = "2. Follow the account "
                                          "link at the top and send me a PM.",
                                   font = Fonts.M())
        self.feedback3 = ttk.Label(self.feedFrame,
                                   text = "3. Email me directly at "
                                          "cameron.gagnon@gmail.com",
                                   font = Fonts.M())
        self.githubFrame = Frame(self.feedFrame)
        self.number4 = ttk.Label(self.githubFrame,
                                   text = "4.",
                                   font = Fonts.M())
        self.githubLink = ttk.Label(self.githubFrame,
                                   text = "File a bug/create a pull request",
                                   font = Fonts.M_U(),
                                   foreground = Fonts._HYPERLINK,
                                   cursor = Fonts._CURSOR)
        self.feedback4 = ttk.Label(self.githubFrame,
                                   text = "because this code is open source!!",
                                   font = Fonts.M())

        # send crashReport
        self.crash_loc = StringVar()
        self.location = self.get_crash_location()
        self.crash_loc.set(self.location)

        self.report = ttk.Label(self.crashFrame,
                                text = "To send a crash report, browse to "
                                       "the location below and send the ",
                                font = Fonts.M(),
                                wraplength = 480)
        self.report1 = ttk.Label(self.crashFrame,
                                text = "log to cameron.gagnon@gmail.com.", 
                                font = Fonts.M(), 
                                wraplength = 480)

        self.crash_loc = ttk.Label(self.crashFrame, text = self.crash_loc.get(),
                               wraplength = 480)

        # packs/binds
        # author frame pack
        self.authorTxt.pack(side = "left", padx = (60, 0), pady = (5,0))
        self.authorLink.pack(side = "left", pady = (5,0))
        self.authorLink.bind("<Button-1>", 
                             lambda event: self.open_link(AboutInfo.reddit()))
        self.subAuthorFrame.pack(side = "top")
        
        self.subredditLink.bind("<Button-1>",
                                lambda event: self.open_link(AboutInfo.subreddit()))
        self.githubLink.bind("<Button-1>",
                            lambda event: self.open_link(AboutInfo.GitHub()))

        # version frame pack within author frame
        self.version.pack(pady = (0,5))
        self.versionFrame.pack(side = "top")
        self.authorFrame.pack(side = "top", fill = "x", pady = (10, 0),
                              padx = (10, 15))
        # donate frame pack
        self.donateTxt.pack(side = "top", pady = (5, 0), anchor = 'center')
        self.donateTxt2.pack(side = "left", pady = (0, 5), anchor = 'center')
        self.donateLink.pack(side = "left", pady = (0, 5))
        self.donateLink.bind("<Button-1>", 
                             lambda event: self.open_link(AboutInfo.PayPal()))
        self.donateFrame.pack(side = "top", fill = "x", padx = (10, 15), 
                              pady = (10, 0))
        self.subDonateFrame.pack(side = "top")
        
        # feedback
        self.feedback.pack(side = "top", anchor = 'center', pady = (5, 0))
        self.subredditFrame.pack(side = "top")
        self.feedback1.pack(side = "left", anchor = 'center')
        self.subredditLink.pack(side = "left")
        self.feedback12.pack(side = "left", anchor = 'center')
        self.feedback2.pack(side = "top", anchor = 'center')
        self.feedback3.pack(side = "top", anchor = 'center')
        self.number4.pack(side = "left", anchor = 'center')
        self.githubLink.pack(side = "left", anchor = 'center')
        self.feedback4.pack(side = "left", anchor = 'center')
        self.githubFrame.pack(side = "top", anchor = 'center', pady = (0, 5))
        self.feedFrame.pack(side = "top", fill = "x", padx = (10, 15),
                            pady = (10, 0))

        # crash report pack
        self.report.pack(side = "top", anchor = 'center')
        self.report1.pack(side = "top", anchor = 'center')
        self.crash_loc.pack(side = "top", pady = (0, 5))
        self.crashFrame.pack(side = "top", fill = "x", padx = (10, 15), 
                             pady = (10, 0))
        
    def open_link(self, link):
        webbrowser.open_new(link)

    def get_crash_location(self):
        # opens a file browser for the user to 
        # search for the log file
        return os.path.realpath("CrashReport.log")
    
    def __str__(self):
        return "About"

if __name__ == "__main__":
    app = Application()
    app.mainloop()
