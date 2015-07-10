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

os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), "cacert.pem")

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
        self.frames = {}
        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(self.window, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")

        # frame to show on startup
        self.show_frame(CurrentImg)
    def show_frame(self, page):
        """
            Input: the page to display
            Output: displays the page selected on button click
        """
        frame = self.frames[page]
        self.pastPage = page
        # sets the focus on the itemFrame when the
        # PastImgs button is clicked so that the
        # list of pictures is scrollable
        if page is PastImgs:
            try: 
                    frame.itemFrame.focus_set()
            except:
                rp.log.debug("Could not set focus to PastImgs, likely due to "
                             "itemFrame not being available") 
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

    def GitHub():
        return AboutInfo._github


######################## Classes for Messages #################################
class Message(Toplevel):

    def __init__(self, master, title):
        """
            Creates popup as Toplevel() and sets its title in the window 
        """
        Toplevel.__init__(self, master)
        #self.popup = Toplevel() 
        self.wm_title(title)
        self.addIcon()
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
        x = (Application.width // 2) + x - (w // 2)
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


    def pack_label(self, text, pady = 10):
        """
            Packs a label into the popup with the specified text
        """
        label = ttk.Label(self, anchor = "center",
                          text = text, wraplength = 420,
                          font = Fonts.L())
        label.pack(side = "top", fill = "x", pady = pady)


    def pack_button(self, pady = (10, 10)):
        """
            Place a button at the bottom of the widget with the text "Okay"
        """
        b = ttk.Button(self, text = "Okay", command = self.delete)
        b.pack(side = "bottom", pady = pady)


    def addIcon(self):
            """
                Adds an error icon to the popup box
            """
            self.img = PhotoImage(file = 'images/error.png')
            self.tk.call('wm', 'iconphoto', self._w, self.img)


class ErrorMsg(Message):
    
    def __init__(self, master, text, title = "Error!"):
        popup = Message.__init__(self, master, title) 
        length = 0
        height = 0

        if isinstance(text, list):
            if len(text) == 1:
                # if string, return length of string
                length = len(text[0])
                height = 170
                rp.log.debug("Length of error string is: %d, "
                             "and height is: %d" % (length, height))
            elif len(text) > 1:
                # find max length of string in the list of errors
                length = len(max(text))
                # length of the list is num of elts in list 
                # so to get the height, we take this and
                # multiply it by a constant and add a base amount
                height = len(text) * 25 + 130 
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
 
        width = length * 5 + 160 # length * 5 because each char is probably 
                                 # about 5 px across. + 160 for padding
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


################################################################################
class Fonts():
    _VERDANA = "Verdana"
    _CURSOR = "hand2"
    _HYPERLINK = "#0000EE"
    _XL = 16 
    _L = 12
    _M = 10
    _SM = 7
    _H1 = 25

    def SM():
        sm = font.Font(family = Fonts._VERDANA, size = Fonts._SM)
        return sm
    def SM_U():
        sm_u = font.Font(family = Fonts._VERDANA, size = Fonts._SM,
                         underline = True)
        return sm_u

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
                rp.log.debug("Attribute Error in get_past_img", exc_info = True)

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
        self.subFrame = Frame(self.frame, width = 525, height = 410)#bg="white")
        self.subFrame.pack_propagate(0)
        self.subFrame.pack()
       
        font_to_use = Fonts.L_U()
        # set font to be smaller if title is too long
        if len(im.title) > 150:
            font_to_use = Fonts.M_U()
        
        # create title link
        self.linkLabel = ttk.Label(self.subFrame, text = im.title,
                               font = font_to_use, foreground = Fonts._HYPERLINK,
                               cursor = Fonts._CURSOR, wraplength = 500)
        self.linkLabel.pack(pady = (35, 10), padx = 10)
        self.linkLabel.bind("<Button-1>", lambda x: self.open_link(im.post))
        
        try:   
            # create image and convert it to thumbnail
            with open(im.save_location, 'rb') as image_file:
                imThumb = Image.open(image_file)
                im.thumb_name = self.strip_file_ext(im.image_name)
                im.thumb_name += "_C"
                im.thumb_name = self.add_png(im.thumb_name)
                im.updateSaveLoc(im.thumb_name)
                imThumb.thumbnail((400, 250), Image.ANTIALIAS)
                imThumb.save(im.thumb_save_loc, "PNG")
            # apply photolabel to page to display
            self.photo = PhotoImage(file = im.thumb_save_loc)
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
        self.picFrame = Frame(self, width = 450, height = 300)#bg = "blue",
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
        self.checkBoxes = []
        self.frames = []
        self.photos = []
        self.populate(self.canFrame, self.picList) 

        # bottom frame for buttons
        self.bottomFrame = Frame(self)                          #bg = 'yellow')
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
        self.scroll = ttk.Scrollbar(self.picFrame, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.picFrame.bind("<Configure>", self.setFrame) 

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
        print(vars(event))

        if event.keycode in keyNum:
            scrollVal = keyNum.get(event.keycode)
        else:
            scrollVal = int(-1*(event.delta/120))

        self.canvas.yview_scroll(scrollVal, "units")

    def setFrame(self, event = None):
        """ Sets the canvas dimentions and the scroll area """
        self.canvas.configure(scrollregion = self.canvas.bbox('all'),
                              width = 450, height = 300)

    def change_all(self, event):
        """
            selects all the pictures (to be deleted)
        """
        if self.selVar.get():
            self.selVar.set(True)
            for box in self.checkBoxes:
                box.set(True)
        else:
            self.selVar.set(False)
            for box in self.checkBoxes:
                box.set(False)

    def del_sel(self, popup):
        """
            Delete all frames that have their checkbox
            checked.
            self.photos[i][0] file path to original img
                              '/path/to/file/jkY32rv.jpg'
            self.photos[i][1] file path to png thumbnail 
                              '/path/to/file/jkY32rv_P.png'
            self.photos[i][2] original img name 'jkY32rv.jpg' 
        """
        for i, box in enumerate(self.checkBoxes):
            if box.get():
                # deletes frame from canvas
                try:
                    self.frames[i].destroy()
                except AttributeError:
                    # occurs when a frame is supposed to be present
                    # but actually isn't
                    rp.log.debug("Frame isnt present")
                    pass

                # resize the past images canvas
                canvasHeight = self.canvas.winfo_height()
                self.canvas.configure(height = canvasHeight - 50,
                                      scrollregion = self.canvas.bbox('all'))
                # delete image from computer
                try:
                    rp.log.debug("self.photos[i][0] is: %s" % self.photos[i][0])
                    rp.log.debug("self.photos[i][1] is: %s" % self.photos[i][1])
                    rp.log.debug("self.photos[i][2] is: %s" % self.photos[i][2])

                    os.remove(self.photos[i][0])
                    rp.log.debug("Removed self.photos[i][0]")

                    os.remove(self.photos[i][1]) 
                    rp.log.debug("Removed self.photos[i][1]")

                    imageC = self.remove_C(self.photos[i][0], self.photos[i][2])
                    
                    try:
                        os.remove(imageC)
                        rp.log.debug("Removed imageC: %s" % imageC)
                    except FileNotFoundError:
                        # image was likely not set as current image, may not
                        # have been correct dimensions
                        rp.log.debug("It appears that the image %s was never"
                                     "set as a current image" % imageC)
                        pass
                    
                    rp.Database.del_img(self.photos[i][2])

                except (OSError, FileNotFoundError):
                    rp.log.debug("File not found when deleting")
                    rp.log.debug(self.photos[i])
                    pass

        # don't forget to destroy the popup!
        self.selVar.set(False)
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
        for i, im in enumerate(self.picList):
            try:
                with open(im.save_location, 'rb') as image_file:
                    imThumb = Image.open(image_file)
                    im.thumb_name = self.strip_file_ext(im.image_name)
                    im.thumb_name += "_P"
                    im.thumb_name = self.add_png(im.thumb_name)
                    im.updateSaveLoc(im.thumb_name)
                    imThumb.thumbnail((50, 50), Image.ANTIALIAS)
                    imThumb.save(im.thumb_save_loc, "PNG")
            except (FileNotFoundError, OSError):
                # usually a file that is not an actual image, such
                # as an html document, so we append dummy variables
                # so that the indexes will align properly with the
                # variables later
                self.checkBoxes.append(BooleanVar())
                self.frames.append("Dummy Frame")
                self.photos.append("Dummy Var")
                continue 
 
            # create frame to hold information for one picture
            self.itemFrame = Frame(frame, width = 450, height = 50)#bg = 'pink')
            self.itemFrame.grid(row = i, column = 0)
            self.itemFrame.pack_propagate(0) 
            self.frames.append(self.itemFrame)

            # checkbox to select/deselect the picture
            self.checkVar = BooleanVar()
            self.checkBoxes.append(self.checkVar)
            self.checkVar.set(False)
            self.check = ttk.Checkbutton(self.itemFrame,
                                     variable = self.checkBoxes[i])
            self.check.pack(side = "left", padx = 5)
           
            # append to photos list to access later
            self.photos.append((im.save_location, im.thumb_save_loc,
                               im.image_name, im.thumb_name))
            # insert the thumbnail
            self.photo = PhotoImage(file = im.thumb_save_loc)
            self.photoLabel = ttk.Label(self.itemFrame, image = self.photo)
            self.photoLabel.image = self.photo # keep a reference per the docs!
            self.photoLabel.pack(side = "left", padx = 10)
            
            # text frame
            self.txtFrame = Frame(self.itemFrame)
            self.txtFrame.pack()

            # title label 
            # slice and add ellipsis if title is too long 
            if len(im.title) > 120:
                im.title = im.title[:120] + '...'

            self.title = ttk.Label(self.txtFrame, text = im.title,
                               font = Fonts.SM(), wraplength = 325)
            self.title.pack(side = "top", padx = 10)
            
            self.botTxtFrame = Frame(self.txtFrame)
            self.botTxtFrame.pack(side = "bottom", anchor = 'center')
            self.botTxtFrame.pack_propagate(0)
            
            # link to post
            self.link = ttk.Label(self.botTxtFrame, text = "Link",
                              font = Fonts.M_U(),
                              cursor = Fonts._CURSOR, foreground = Fonts._HYPERLINK)
            self.link.grid(row = 0, column = 0)#pack(side = "left", anchor = 'center')
# how to remember variable in a for loop: 
# https://stackoverflow.com/questions/14259072/tkinter-bind-function-with-variable-in-a-loop/14260871#14260871
            self.link.bind("<Button-1>", self.make_link(im))
            
            # set as wallpaper
            self.setAs = ttk.Label(self.botTxtFrame, text = "Set as Wallpaper",
                               font = Fonts.M_U(), cursor = Fonts._CURSOR,
                               foreground = Fonts._HYPERLINK)
            self.setAs.grid(row = 0, column = 1)#pack(side = "left", anchor = 'center')
            self.setAs.bind("<Button-1>", self.make_wallpaper(im))
            
            # for loop over children of itemFrame did not work
            # to set keybinds, so we manually set all keybinds
            # so scrolling is enabled for both mouse and arrow keys
            self.setKeyBinds(self.itemFrame)
            self.setKeyBinds(self.setAs)
            self.setKeyBinds(self.link)
            self.setKeyBinds(self.botTxtFrame)
            self.setKeyBinds(self.title)
            self.setKeyBinds(self.txtFrame)
            self.setKeyBinds(self.photoLabel)
            self.setKeyBinds(self.check)
        
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
            every 5 seconds
        """
        # get list of all pictures
        pictures = self.findSavedPictures()
        newPicList = []
        image_name_list = [pic.image_name for pic in self.picList]
        # loop through each picture
        for picture in pictures:
            # if picture is not already displayed
            # then it probably wasn't there before...
            # so we add it to the list to be displayed
            if picture.image_name not in image_name_list:
                newPicList.append(picture)
                self.picList.append(picture)

        if len(newPicList):
            rp.log.debug("New pictures are: %s\n", tuple(newPicList))
        
            # pass in the frame to pack the new pictures into 
            self.populate(self.canFrame, newPicList)
            self.scroll.destroy()
            self.setFrame()
            self.setScroll()

        self.after(1000, lambda: self.updatePastImgs())

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
        # Frames
        temp = rp.Config.read_config()
        Frame.__init__(self, parent)
        self.top = Frame(self)
        # subreddit border
        self.subredditF = ttk.LabelFrame(self, text = "Subreddits to pull from "\
                                                     "(whitespace separated)")
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
        self.singleB.bind("<Button-1>", lambda e: rp.Single_link(self.singleE.get()))

        # Buttons
        self.letsGo = ttk.Button(self, text = "Let's Go!")
      
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
        self.letsGo.pack(side = "bottom", anchor = "center", pady = (10, 30))
        self.letsGo.bind("<Button-1>", lambda e: self.get_pics())
        self.nsfw.pack(side = "left", anchor = "nw", pady = 5,\
                       padx = (0, 5))
        # top holds dimensions and user/pass labelFrames
        self.top.pack(side = "top", anchor = "w", pady = (10, 10))
        self.subredditF.pack(side = "top", anchor = "w",\
                                padx = (15, 10))
        self.dlFrame.pack(side = "top", anchor = "w", pady = 10,
                          padx = 15)
        self.singleF.pack(side = "top", anchor = 'w', padx = (15, 10))
        self.dimensions.pack(side = "left", anchor = "nw", pady = (0, 10),\
                             padx = (15, 5))
        self.res.pack(side = "top")
        self.midTop.pack(side = "left", padx = 25) 
        self.checks.pack(side = "top")
        self.checksFrame.pack(side = "top", anchor = "nw",\
                         padx = 5)
        self.maxLabel.pack(side = "top", pady = 10)
        # cycletime and category frame
        self.cat.pack(side = "top")
        self.ct.pack(side = "bottom", pady = 5)
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
        if not str(values['-mw']).isdigit():
            errors.append(values['-mw'])
        if not str(values['-mh']).isdigit():
            errors.append(values['-mh'])
        if not str(values['-mp']).isdigit() or\
           int(values['-mp']) > 99:
            errors.append(values['-mp'])
        if not subs.isalnum():
            errors.append(values['-s'])
        if values['-dl'][values['-dl'].rfind('\\'):] != values['-dl'][-1:]:
            errors.append("Make sure path ends with a '\\' " + values['-dl'])

        return errors

    def get_pics(self):
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
        # create string for list of args
        self.argList = os.getcwd() + '\\redditpaper.py'
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
        self.feedFrame = ttk.LabelFrame(self, text = "Feeback")

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
                                text = "to the developer at the following "
                                       "link,",
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
        self.feedback1 = ttk.Label(self.feedFrame, 
                                   text = "1. Go to /r/reddit_paper and create a "
                                          "new post.",
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
                             lambda x: self.open_link(AboutInfo.reddit()))
        self.subAuthorFrame.pack(side = "top")
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
                             lambda x: self.open_link(AboutInfo.PayPal()))
        self.donateFrame.pack(side = "top", fill = "x", padx = (10, 15), 
                              pady = (10, 0))
        self.subDonateFrame.pack(side = "top")
        
        # feedback
        self.feedback.pack(side = "top", anchor = 'center', pady = (5, 0))
        self.feedback1.pack(side = "top", anchor = 'center')
        self.feedback2.pack(side = "top", anchor = 'center')
        self.feedback3.pack(side = "top", anchor = 'center')
        self.number4.pack(side = "left", anchor = 'center')
        self.githubLink.pack(side = "left", anchor = 'center')
        self.githubLink.bind("<Button-1>",
                            lambda x: self.open_link(AboutInfo.GitHub()))
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
