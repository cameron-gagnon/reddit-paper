#!/usr/bin/env python3.4

from tkinter import *


class Application(Tk):
    
    def __init__(self, master=None):
        Tk.__init__(self, master)
        
        # set title of application on titlebar
        self.wm_title("Reddit Paper") 
        
        # set up frame to hold widgets
        root = Frame(self)
        root.grid()

        # set minsize of application
        self.minsize(width = 500, height = 550)

        self.buttons = AddButtons(root)

class AddButtons():

    def __init__(self, master):
        # current image button
        self.cphoto = PhotoImage(file="./images/currentpic_square.png")
        self.c = Button(master, image = self.cphoto, width = 125, height = 125)
        self.c.grid(row = 0, column = 0, sticky = "N")

        # past image button
        self.pphoto = PhotoImage(file="./images/pastpic.ppm")
        self.p = Button(master, image = self.pphoto, width = 125, height = 125)
        self.p.grid(row = 0, column = 1, sticky = "N")

        # settings buttons
        self.sphoto = PhotoImage(file="./images/settingpic.gif")
        self.s = Button(master, image = self.sphoto, width = 125, height = 125)
        self.s.grid(row=0, column = 2, sticky = "N")

        # about buttons
        self.aphoto = PhotoImage(file="./images/aboutpic.pgm")
        self.a = Button(master, image = self.aphoto, width = 125, height = 125)
        self.a.grid(row = 0, column = 3, sticky = "N")


app = Application()
app.mainloop()
