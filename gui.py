#!/usr/bin/env python3.4

import redditpaper as rp
from tkinter import *
from tkinter import ttk
from PIL import Image

LARGE_FONT = {"Verdana", "12"}
CURSOR = "plus"

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
        self.geometry('%dx%d+%d+%d' % (self.width, self.height, self.x, self.y))
        

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


        # statusbar for bottom of application
        self.statusbar = Label(master, text="Preparing to do nothing...", bd=1,
                            relief = SUNKEN, anchor = "w")
        
        # pack the labels/frame to window
        self.statusbar.pack(side = "bottom", fill = "x", anchor = "w")
        self.topbar.pack(side = "top")



# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        # create the frame to hold the widgets
        self.frame = Frame(self, bg = "magenta", width = 525, height = 400)

        # link to submission of image
        self.label = Label(self.frame, text="Title/link to submission:", 
                      font = LARGE_FONT, 
                      bg="blue")
        self.label.pack(pady = 10, padx = 10)

        # thumbnail of image currently set as background
        self.photoLocation = "./images/currentpic_square.png"
                           # "./images/placeholder400x400.png"
        self.photo = PhotoImage(file = self.photoLocation)
        self.photoLabel = Label(self.frame, image = self.photo)
        
        self.test = Label(self.frame, text = "testing 1, 2, 3...")
        self.test.pack()

        # pack frames/labels
        self.frame.pack_propagate(0)
        self.photoLabel.pack(side = "bottom", expand = True)
        self.frame.pack(side = "top")


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
            Label(itemFrame, text = img.resolution).pack(side = "bottom", pady = 5)
    
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
        self.entry = Frame(self) 
        self.checks = Frame(self)
        self.dimensions = Frame(self, width = 475, height = 20)
        
        # user/pass entries 
        Label(self.entry, text = "Username: ").grid(row = 0, column = 0)
        Label(self.entry, text = "Password: ").grid(row = 0, column = 2)
        self.username = Entry(self.entry).grid(row = 0, column = 1)
        self.password = Entry(self.entry).grid(row = 0, column = 3)
        
        # subreddit entry
        Label(self.entry, text = "Subreddits (separated by +)", pady = 15).grid(row = 1, columnspan = 2, sticky = "w")
        self.subreddits = Entry(self.entry, width = 29).grid(row = 1, column = 2, columnspan = 2, sticky = "w")
        # Min width
        Label(self.dimensions, text = "Min-width: ", pady = 15).pack(side = "left", anchor = "w")
        self.minwidth = Entry(self.dimensions, width = 6).pack(side = "left", anchor = "w")
        # Min height
        Label(self.dimensions, text = "Min-height: ", pady = 15, padx = 10).pack(side = "left", anchor = "w")
        self.minheight = Entry(self.dimensions, width = 6).pack(side = "left", anchor = "w")
        
        # nsfw checkbutton
        Label(self.checks, text = "NSFW", pady = 15).pack(side = "left")
        self.nsfwOn = StringVar().set("On")
        self.nsfwOff = StringVar()
        self.nsfw = Checkbutton(self.checks, text = self.nsfwOn, pady = 15).pack(side = "left")
        
        # packs
        self.entry.pack(side = "top")
        self.dimensions.pack_propagate(0)
        self.dimensions.pack(side = "top")
        self.checks.pack(side = "top")


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
        label = Label(self, text="About", font = LARGE_FONT, bg="green")
        label.pack(pady = 10, padx = 10)


app = Application()
app.mainloop()
