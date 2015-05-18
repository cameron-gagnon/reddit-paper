#!/usr/bin/env python3.4

from tkinter import *
LARGE_FONT = {"Verdana", "12"}

class Application(Tk):
    
    def __init__(self, master=None):
        Tk.__init__(self, master)
        
        # set title of application on titlebar
        self.wm_title("Reddit Paper") 
        
        # set up frame to hold widgets
        root = Frame(self, background="bisque")
        root.pack(side = "top", fill = "both", expand = True)

        # set minsize of application
        self.minsize(width = 525, height = 550)

        # adds buttons and status bar for main page
        self.buttons = AddButtons(root, self)
        
        self.frames = {}
        
        # window used to pack the pages into
        self.window = Frame(root, bg = "cyan")         
        self.window.pack(fill = "both", expand = True)

        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(self.window, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")
            #frame.pack()
        self.show_frame(CurrentImg)

    # Input - page to display
    # Output - displays the page selected
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class AddButtons(Frame):

    def __init__(self, master, cls):
        Frame.__init__(self, master)
        self.topbar = Frame(master, bg="red")
        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(self.topbar, image = self.cphoto, 
                        width = 125, height = 125,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")
#self.c.pack(side = "top")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic_square.png")
        self.p = Button(self.topbar, image = self.pphoto, 
                        width = 125, height = 125,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")
#self.p.pack(side = "top")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic_square.png")
        self.s = Button(self.topbar, image = self.sphoto, 
                        width = 125, height = 125,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")
#self.s.pack(side = "top")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic_square.png")
        self.a = Button(self.topbar, image = self.aphoto, 
                        width = 125, height = 125,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")
#self.a.pack(side = "top")

#self.topbar.grid(row = 0, columnspan = 4, sticky = "N")
        self.topbar.pack(side = "top")

        # statusbar for bottom of application
        self.status = Label(master, text="Preparing to do nothing...", bd=1,
                            relief = SUNKEN, anchor = "w")
        self.status.pack(side = "bottom", fill = "x", anchor = "w")

        #self.status = Label(master, text="Preparing to do nothing...", bd=1,
        #                    relief = SUNKEN, anchor = "w")
        #self.status.rowconfigure(1, weight = 2)
        #self.status.grid(row = 2, sticky = "s")
#self.status.pack(side = "bottom", fill = "x", expand = True)
    

# **** Current Image Page **** #
# Shows a thumbnail of the current image set as the 
# background, with a link to that submission.
class CurrentImg(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.frame = Frame(self, bg = "magenta")
        self.frame.pack(side = "top", fill = "both", expand = True)

        label = Label(self.frame, text="Title/link to submission:", 
                      font = LARGE_FONT, 
                      bg="blue")
        label.pack(pady = 10, padx = 10)
        label2 = Label(self.frame, text="here's another frame", 
                       font = LARGE_FONT)
        label2.pack()




# **** Past Images Page **** #
# Gives a listing of past submissions, with a smaller thumbnail of the image
# and the title/resolution of the images.
# Includes: * checkboxes to delete the images selected
#           * Scrollable list of all images downloaded/used in the past
class PastImgs(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Past Images", font = LARGE_FONT, bg="pink")
        label.pack(pady = 10, padx = 10)



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
