#!/usr/bin/env python3.4

from tkinter import *

LARGE_FONT = {"Verdana", "12"}
CURSOR = "plus"

class Application(Tk):
    
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
            Output: displays the page selected on butotn click
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
        w = 525
        h = 550
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        

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
        self.photoLocation = "./images/currentpic_square.png"# "./images/placeholder400x400.png"
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
        label = Label(self, text="Select and delete images", font = LARGE_FONT,
                      bg="pink")
        
        self.picFrame = Frame(self, bg = "blue", width = 500, height = 340)        


        # pack frames/labels
        label.pack(anchor = "w", pady = (15, 0), padx = 10)
        self.picFrame.pack(side = "bottom", padx = 10, pady = (0, 10))


# **** Settings Page **** #
# This is where most of the users choices will be made
# on the running of the program.
# This includes: * nsfw filter box
#                * subreddits to query
#                * image resolutions
#                * multiple monitor setup
#                * keywords
class Settings(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Settings", font = LARGE_FONT, bg="yellow")
        label.pack(pady = 10, padx = 10)



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
