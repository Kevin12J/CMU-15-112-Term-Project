from game import *
from cmu_112_graphics import *
#################################################
# Guide Mode
#################################################
def guideMode_keyPressed(app,event):
    if(event.key=='b'):
        if(app.inGame):
            app.mode='pauseMode'
        else:
            app.mode='splashScreenMode'

def guideMode_redrawAll(app,canvas):
    canvas.create_image(app.width/2,app.height/2,image=ImageTk.PhotoImage(app.guideImage))