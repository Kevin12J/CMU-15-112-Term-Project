from game import *
#################################################
# Leaderboard Mode
#################################################
def leaderboardMode_keyPressed(app,event):
    if(event.key=='b'):
        if(app.inGame):
            app.mode='pauseMode'
        else:
            app.mode='splashScreenMode'

def getTop10(app):
    score=[]
    players=[]
    k=app.players.keys()
    k=sorted(k)
    i=-1
    while(len(score)<=10 and i>=len(k)*-1):
        if(not app.players[k[i]] in players):
            score.append(k[i])
            players.append(app.players[k[i]])
        i-=1
    return score,players

def leaderboardMode_redrawAll(app,canvas):
    font = 'Terminal 20 bold'
    canvas.create_text(app.width/2, 20, text='Leaderboard!', font=font)
    scores,players=getTop10(app)
    if(len(scores)==0):
        canvas.create_text(app.width/2, app.height/2, text='no scores :(', font=font)
    for i in range(len(scores)):
        canvas.create_text(app.width/2,70+40*i,text=f'{players[i]}: {scores[i]}',font=font)
    canvas.create_text(app.width/2, 480, text='-press b to go back-', font=font)
