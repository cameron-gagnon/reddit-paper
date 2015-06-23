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
    height = 555

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
        
        StatusBar(master)
        
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
        # sets the focus on the itemFrame when the
        # PastImgs button is clicked so that the
        # list of pictures is scrollable
        if page is PastImgs:
            try:
                frame.itemFrame.focus_set()
            except:# (AttributeError):
                # all images are likely deleted from
                # the itemFrame
                pass

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
                          font = Fonts.L())
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

    def __init__(self, master):
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
        B1 = ttk.Button(BFrame, text = "Yes", command = lambda: master.del_sel(self))
        B2 = ttk.Button(BFrame, text = "No", command = self.destroy)
        B1.pack(side = "left")
        B2.pack(side = "left")


################################################################################
class Fonts():
    _VERDANA = "Verdana"
    _CURSOR = "hand2"
    _HYPERLINK = "#0000EE"
    _XL = 16 
    _L = 12
    _MED = 10
    _SM = 7
    _H1 = 25
     
    def SM():
        sm = font.Font(family = Fonts._VERDANA, size = Fonts._SM)
        return sm
    def SM_U():
        sm_u = font.Font(family = Fonts._VERDANA, size = Fonts._SM,
                         underline = True)
        return sm_u

    def MED():
        m = font.Font(family = Fonts._VERDANA, size = Fonts._M)
        return m
    def MED_U():
        med_u = font.Font(family = Fonts._VERDANA, size = Fonts._MED,
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
        xl_u = font.Font(family = Fonts._VERDANA, size = Fonts._xl,
                         underline = True)
        return xl_u

   
    def H1():
        h1 = font.Font(family = Fonts._VERDANA, size = Fonts._H1)
        return h1
    def H1_U():
        h1_u = font.Font(family = Fonts._VERDANA, size = Fonts._h1,
                         underline = True)
        return h1_u


    def underline(master):
        """
            Gives the ability to have entire strings of text
            underlined. Used for links.
        """
        global UNDERLINE
        # Defined in its own function as the
        # Font() call must be made after a Tk()
        # instance has been created.
        UNDERLINE = font.Font(master, Fonts.L())
        UNDERLINE.configure(underline = True)

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
        self.statusBar = Label(master, text = self.text.get(), bd=1,
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


class AddButtons(Frame):

    def __init__(self, master, cls):
        global STATUSBAR
        Frame.__init__(self, master)
        self.topbar = Frame(master, bg="red")

        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(self.topbar, image = self.cphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic_square.png")
        self.p = Button(self.topbar, image = self.pphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic_square.png")
        self.s = Button(self.topbar, image = self.sphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic_square.png")
        self.a = Button(self.topbar, image = self.aphoto, 
                        width = 125, height = 125, cursor = Fonts._CURSOR,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")

        self.topbar.pack(side = "top")


# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame, ImageFormat):

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
        self.subFrame = Frame(self.frame, width = 525, height = 410,\
                              bg = "white")
        self.subFrame.pack_propagate(0)
        self.subFrame.pack()
       
        # create title link
        self.linkLabel = Label(self.subFrame, text = im.title,
                               font = UNDERLINE, fg = Fonts._HYPERLINK,
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
            self.photoLabel = Label(self.subFrame, image = self.photo)
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
        selectBox = Checkbutton(self, text = "Select all",  variable = self.selVar)
        selectBox.pack(anchor = 'w', pady = (15, 2), padx = (21, 10))

        ### begin canvas/frame/picture list
        self.picFrame = Frame(self, bg = "blue", width = 450, height = 300)
        self.picFrame.pack()
        self.canvas = Canvas(self.picFrame, bg = '#575757', width = 450, height = 300)
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
        self.bottomFrame = Frame(self, bg = 'yellow')        
        self.delete = Button(self.bottomFrame, text = "Delete selected", 
                               state = "normal",
                               command = lambda: ConfirmMsg(self))
        # 'delete all' button 'delete selected' button
        self.delete.pack(side = "right", padx = (10, 0))

        # packs the frame that holds the delete buttons
        self.bottomFrame.pack(side = "bottom", anchor = "e",
                              pady = (0, 15), padx = (0, 27))
        ### end canvas/frame/picture list

        self.updatePastImgs()

    def setScroll(self):
        self.scroll = Scrollbar(self.picFrame, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scroll.set)
        self.scroll.pack(side="right", fill="y")
        self.picFrame.bind("<Configure>", self.setFrame) 

    def setKeyBinds(self, widget):
    
        """
            Sets the binds to the keys for the canvas movements
            when adding new elts
        """
        widget.bind("<Button-4>", self.onMouseWheel)
        widget.bind("<Button-5>", self.onMouseWheel)
        widget.bind("<Up>", self.onMouseWheel)
        widget.bind("<Down>", self.onMouseWheel)
     
    def onMouseWheel(self, event):
        """
            Scrolls the canvas up or down depending on the 
            event entered (arrow keys/mouse scroll)
        """
        keyNum = {116 : 1,   # Down arrow key
                  111 : -1}  # Up arrow key
        scrollVal = None
        if event.keycode in keyNum:
            scrollVal = keyNum.get(event.keycode)
        elif event.num == 4:
            scrollVal = -1
        elif event.num == 5:
            scrollVal = 1
        else:
            scrollVal = event.delta # leave as is on OSX

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
                    pass

                canvasHeight = self.canvas.winfo_height()
                self.canvas.configure(height = canvasHeight - 50,
                                      scrollregion = self.canvas.bbox('all'))
                # delete image from computer
                try:
                    os.remove(self.photos[i][0])
                    os.remove(self.photos[i][1]) 
                    imageC = self.remove_C(self.photos[i][0], self.photos[i][2])
                    os.remove(imageC)
                    rp.log.debug("Deleting image: %s AND %s" %
                                (self.photos[i][0], self.photos[i][0]))
                    rp.Database.del_img(self.photos[i][2])
                except OSError:
                    rp.log.debug("File not found when deleting...")
                    pass

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
            self.itemFrame = Frame(frame, width = 450, height = 50, bg = 'pink')
            self.itemFrame.grid(row = i, column = 0)
            self.itemFrame.pack_propagate(0) 
            self.frames.append(self.itemFrame)

            # checkbox to select/deselect the picture
            self.checkVar = BooleanVar()
            self.checkBoxes.append(self.checkVar)
            self.checkVar.set(False)
            self.check = Checkbutton(self.itemFrame,
                                     variable = self.checkBoxes[i])
            self.check.pack(side = "left", padx = 5)
           
            # append to photos list to access later
            self.photos.append((im.save_location, im.thumb_save_loc,
                               im.image_name, im.thumb_name))
            # insert the thumbnail
            self.photo = PhotoImage(file = im.thumb_save_loc)
            self.photoLabel = Label(self.itemFrame, image = self.photo)
            self.photoLabel.image = self.photo # keep a reference per the docs!
            self.photoLabel.pack(side = "left", padx = 10)
            
            # text frame
            self.txtFrame = Frame(self.itemFrame)
            self.txtFrame.pack()
            # title label 
            self.title = Label(self.txtFrame, text = im.title,
                               font = Fonts.SM(), wraplength = 325)
            self.title.pack(side = "top", padx = 10)
            
            self.botTxtFrame = Frame(self.txtFrame)
            self.botTxtFrame.pack(side = "bottom")
            
            # link to post
            self.link = Label(self.botTxtFrame, text = "Link",
                              font = Fonts.MED_U(),
                              cursor = Fonts._CURSOR, fg = Fonts._HYPERLINK)
            self.link.pack(side = "left", anchor = 'w')
# how to remember variable in a for loop: 
# https://stackoverflow.com/questions/14259072/tkinter-bind-function-with-variable-in-a-loop/14260871#14260871
            self.link.bind("<Button-1>", self.make_link(im))
            
            # set as wallpaper
            self.setAs = Label(self.botTxtFrame, text = "Set as Wallpaper",
                               font = Fonts.MED_U(), cursor = Fonts._CURSOR,
                               fg = Fonts._HYPERLINK)
            self.setAs.pack(side = "left", anchor = 'w')
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

        self.after(2000, lambda: self.updatePastImgs())


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
        self.subredditForm = LabelFrame(self, text = "Subreddits to pull from "\
                                                     "(whitespace separated)")
        # nsfw border
        self.midTop = Frame(self.top)
        self.checksFrame = LabelFrame(self.midTop, text = "Adult Content")
        self.checks = Frame(self.checksFrame)
        
        # width x height
        self.dimensions = LabelFrame(self.top, 
                                     text = "Picture Resolution")
        self.res = Frame(self.dimensions)

        # maxposts
        self.maxLabel = LabelFrame(self.midTop, text = "# of Posts")
        self.maxFrame = Frame(self.maxLabel)
        self.maxTxt = Label(self.maxFrame, text = "Maxposts:")
        self.maxTxt.pack(side = "left", padx = (5, 0))
        self.maxE = Entry(self.maxFrame, width = 3)
        self.maxE.insert(0, rp.Config.maxposts())
        self.maxE.pack(side = "left", padx = (5,5), pady = (0, 5))
        self.maxFrame.pack()

        # cycletime border and frame
        self.topRt = Frame(self.top)
        self.ct = LabelFrame(self.topRt, text = "Wallpaper Timer")
        self.ctFrame = Frame(self.ct)
        
        # category border and frame
        self.cat = LabelFrame(self.topRt, text = "Section")
        self.catFrame = Frame(self.cat, width = 200, height = 30)
        self.catFrame.pack_propagate(0)

        # download location border
        self.dlFrame = LabelFrame(self, text = "Picture download location")
                
        # Buttons
        self.letsGo = Button(self, text = "Let's Go!")
#self.help = Button(self, text = "Help", command = self.helpButt)
      
        # subreddit entry
        self.subreddits = Entry(self.subredditForm, width = 57)
        self.subreddits.insert(0, rp.Config.subreddits())
        self.subreddits.grid(row = 1, column = 2, columnspan = 2, padx = (10,10),
                             sticky = "w", pady = (5,5))
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
        self.onOff = BooleanVar()
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
        self.top.pack(side = "top", anchor = "w", pady = (10, 10))
        self.subredditForm.pack(side = "top", anchor = "w",\
                                padx = (15, 10))
        self.dlFrame.pack(side = "top", anchor = "w", pady = 10,
                          padx = (15, 10))
        self.dimensions.pack(side = "left", anchor = "nw", pady = (0, 10),\
                             padx = (15, 5))
        self.res.pack(side = "top")
        self.midTop.pack(side = "left", padx = 4) 
        self.checks.pack(side = "top")
        self.checksFrame.pack(side = "top", anchor = "nw",\
                         padx = (5, 5))
        self.maxLabel.pack(side = "top")
        # cycletime and category frame
        self.ct.pack(side = "top")
        self.cat.pack(side = "bottom")
        self.topRt.pack(side = "left", anchor = "nw", padx = (5, 5))

    def maxPosts(self):
        pass
        
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
        if not str(values['-mp']).isdigit() or\
           int(values['-mp']) > 99:
            errors.append(values['-mp'])
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
                               font = Fonts.L())
        self.authorLink = Label(self.subAuthorFrame, text="/u/camerongagnon", 
                                font = UNDERLINE, fg = Fonts._HYPERLINK,
                                cursor = Fonts._CURSOR)

        # version number
        self.vNum = StringVar()
        self.vNum.set("Version: " + rp.AboutInfo.version() + "." +
                      AboutInfo.version())
        self.version = Label(self.versionFrame, text = self.vNum.get(),
                             font = Fonts.L())
        
        # donate text/link
        self.donateTxt = Label(self.donateFrame,
                               text = "If you enjoy this program, "
                                      "please consider making a donation ",
                               font = Fonts.L())
        self.subDonateFrame = Frame(self.donateFrame)
        self.donateTxt2 = Label(self.subDonateFrame,
                                text = "to the developer at the following "
                                       "link,",
                                font = Fonts.L()) 
        self.donateLink = Label(self.subDonateFrame, text = "here.",
                                font = UNDERLINE, fg = Fonts._HYPERLINK,
                                cursor = Fonts._CURSOR) 

        # feedback
        self.feedback = Label(self.feedFrame,
                              text = "To provide comments/feedback, please "
                                     "do one of the following: \n"
                                     "1. Go to /r/reddit_paper and create a "
                                     "new post.\n2. Follow the account "
                                     "link at the top and send me a PM.\n3. Email "
                                     "me directly at cameron.gagnon@gmail.com",\
                              font = Fonts.L())
        # send crashReport
        self.crash_loc = StringVar()
        self.location = self.get_crash_location()
        self.crash_loc.set(self.location)

        self.report = Label(self.crashFrame,
                            text = "To send a crash report, please\n"
                            "browse to the location below and send the log\n"
                            "to cameron.gagnon@gmail.com.", 
                            font = Fonts.L())
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
