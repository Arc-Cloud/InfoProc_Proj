from tkinter import *
from snake_run import *

username = ""
password = ""
usernameinput = ""
passwordeinput = ""

def login(SCREEN_W, SCREEN_H):
     global myscreen
     myscreen = Tk()
     myscreen.geometry(SCREEN_W+"x"+SCREEN_H)
     myscreen.title("Snake Log in")
     Label(text=" Please choose log in or register ", bg="Pink", width="300", height="2", font=("Times New Roman", 13)).pack() 
     Label(text="").pack() 

     Button(text="Login", height="2", width="30", command=login).pack() 
     Label(text="").pack() 

     Button(text="Register", height="2", width="30", command=register).pack() 
     myscreen.mainloop()
     login()
     
 
def register(SCREEN_W,SCREEN_H):
     regscreen=Toplevel(myscreen)
     regscreen.geometry(SCREEN_W+"x"+SCREEN_H)
     regscreen.title("Register")
     username=StringVar()
     password=StringVar()
     Label(register, text="Please enter your details", bg="pink").pack()
     Label(register, text="").pack()

     username_labeel=Label(register, text="Username:")
     username_labeel.pack()
     usernameinput=Entry(register, textvariable="username")
     usernameinput.pack()
     password_labeel=Label(register, text="Password:")
     password_labeel.pack()
     passwordeinput=Entry(register, textvariable="password", show="*")
     passwordeinput.pack()
     Label(register, text="").pack()
     Button(register, text="Register", width=10, height=1, bg="pink", command=register_user).pack()
     
def register_user():
    username_submitted=username.get()
    password_submitted=password.get()
    
 

    ####ADD THE DB CODE HERE#####
    Label(register, text="Registration succsesful", fg="green", font=("Times New Roman", 11)).pack() 
    
def login_user():
    username_submitted=username.get()
    password_submitted=password.get()
    
 

    ####ADD THE DB CODE HERE#####

    ###CLOSETKINYTERANDRUN PYGAME
    myscreen.quit()
    gamerun()