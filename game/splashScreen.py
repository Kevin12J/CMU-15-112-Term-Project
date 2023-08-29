from game import *
from cmu_112_graphics import *
#################################################
# Splash Screen Mode
#################################################
def splashScreenMode_mousePressed(app,event):
    x=event.x
    y=event.y
    if(290<=x<=460 and 325<=y<=375):
        app.mode='leaderboardMode'
    elif(290<=x<=460 and 380<=y<=430 and len(app.username)>0):
        app.mode='gameMode'
        app.inGame=True
    elif(290<=x<=460 and 435<=y<=485 and len(app.username)>0):
        app.mode='gameMode'
        app.inGame=True
        app.cheats=True
    elif(90<=x<=260 and 435<=y<=485):
        app.mode='guideMode'
    elif(90<=x<=260 and 380<=y<=430):
        app.username=app.getUserInput('What is your name?')

size=0
def splashScreenMode_redrawAll(app,canvas):
    font = 'Terminal 12 bold'
    global size
    size+=1
    canvas.create_rectangle(0,0,app.width,app.height,fill='chartreuse4')
    canvas.create_image(app.width/2,150,image=ImageTk.PhotoImage(app.homeImage))
    canvas.create_rectangle(290,325,460,375,fill='black')
    canvas.create_text(150, 350, text='Tank Battle!', font=f'Terminal {size%20} bold',fill='black')
    canvas.create_text(300,350,text='Leaderboard',font=font,fill='yellow',anchor='w')
    canvas.create_rectangle(290,380,460,430,fill='black')
    canvas.create_text(320,405,text='Play Game',font=font,fill='green',anchor='w')
    canvas.create_rectangle(90,380,260,430,fill='black')
    canvas.create_text(100,405,text=f'Name:{app.username}',font=font,fill='green',anchor='w')
    canvas.create_text(100,420,text='enter name to start game',font='Terminal 8 bold',fill='green',anchor='w')
    canvas.create_rectangle(290,435,460,485,fill='black')
    canvas.create_text(300,460,text='Play With Cheats',font='Terminal 10 bold',fill='red',anchor='w')
    canvas.create_rectangle(90,435,260,485,fill='black')
    canvas.create_text(135,460,text='Guide',font=font,fill='blue',anchor='w')

