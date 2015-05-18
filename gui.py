#!/usr/bin/env python3.4

from tkinter import *
LARGE_FONT = {"Verdana", "12"}

class Application(Tk):
    
    def __init__(self, master=None):
        Tk.__init__(self, master)
        
        # set title of application on titlebar
        self.wm_title("Reddit Paper") 
        
        # set up frame to hold widgets
        root = Frame(self)
        root.grid()

        # set minsize of application
        self.minsize(width = 525, height = 550)

        # adds buttons for main pages
        self.buttons = AddButtons(root, self)
        
        self.frames = {}

        for F in (CurrentImg, PastImgs, Settings, About):
            frame = F(root, self)
            self.frames[F] = frame
            frame.grid(row = 1, column = 0, sticky = "NSEW")
        
#self.show_frame(Settings)

    # Input - page to display
    # Output - displays the page selected
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class AddButtons():

    def __init__(self, master, cls):
        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(master, image = self.cphoto, width = 125, height = 125,
                        command = lambda: cls.show_frame(CurrentImg))
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic_square.png")
        self.p = Button(master, image = self.pphoto, width = 125, height = 125,
                        command = lambda: cls.show_frame(PastImgs))
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic_square.png")
        self.s = Button(master, image = self.sphoto, width = 125, height = 125,
                        command = lambda: cls.show_frame(Settings))
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic_square.png")
        self.a = Button(master, image = self.aphoto, width = 125, height = 125,
                        command = lambda: cls.show_frame(About))
        self.a.grid(row = 0, column = 3, sticky = "N")


class CurrentImg(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Current Image", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)


class PastImgs(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Past Images", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)


class Settings(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Settings", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)


class About(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="About", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)


app = Application()
app.mainloop()
