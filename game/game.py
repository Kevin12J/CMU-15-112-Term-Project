#################################################
# Term Project
# Your name: Kevin Jacob
# Your andrew id: kjacob
#################################################
#This file is the main game
import math, copy, random
from cmu_112_graphics import *
from splashScreen import *
from leaderboard import *
from projectiles import *
from enemyTank import *
from guide import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def playTanks():
    runApp(width=500,height=500)

def appStarted(app):
    app._root.resizable(False, False)
    app.mode = 'splashScreenMode'
    #Leaderboard
    app.players=readPlayerScores('scores.txt')
    ###########
    app.username=''
    app.cheats=False
    app.neverDie=False
    app.inGame= False
    app.gameOver=False
    app.forceField=0
    app.score=0
    app.level=1
    app.coins=0
    app.slowDown=20
    app.doubleBarrel=False
    app.airStrike=False
    app.airStrikeX=0
    app.nextHasBarrier=False
    #coordinates of board
    app.boardX0=0
    app.boardX1=app.width
    app.boardY0=0
    app.boardY1=app.height
    #image for homepage
    app.homeImage=app.loadImage('homepage.jpg')
    #image for board
    app.boardImage=app.loadImage('dessert.jpg')
    #image for wall
    app.wallImage=app.loadImage('wall.jpg')
    #image for coin
    app.coinImage=app.loadImage('coin.png')
    #image for plane
    app.planeImage=app.loadImage('plane.png')
    #image for guide
    app.guideImage=app.loadImage('guide.jpg')
    #position of user tank
    app.tankX=(app.boardX0+app.boardX1)//2
    app.tankY=(app.boardY0+app.boardY1)//2
    app.tankWidth=20
    app.tankPoints=[[app.tankX-app.tankWidth,app.tankY-app.tankWidth],
                    [app.tankX+app.tankWidth,app.tankY-app.tankWidth],
                    [app.tankX+app.tankWidth,app.tankY+app.tankWidth],
                    [app.tankX-app.tankWidth,app.tankY+app.tankWidth]]
    app.trackColors=['grey','grey','grey','grey','yellow','grey','grey','grey','grey','grey']
    app.tankDirection=0
    app.tankSlope=None
    app.tankHealth=500
    app.returnToArea=False
    app.burst=False
    #mouse
    app.mouseX=0
    app.mouseY=0
    #projectiles
    app.projectiles=[]
    #enemy turrets
    app.enemyX=[]
    app.enemyY=[]
    app.movements=0
    app.frequency=20
    #enemy tanks
    app.enemyTanks=[]
    #walls
    app.walls={}
    #level markers
    app.levelMarkers=[0]
    setUpMap(app,250,100)

#reading scores file
def readFile(path):
    with(open(path,'rt')) as f:
        return f.readlines()

def readPlayerScores(path):
    result=dict()
    s=readFile(path)
    s=[line.rstrip() for line in s]
    for l in s:
        if(l!=''):
            k=int(l.split(',')[0])
            p=l.split(',')[1]
            result[k]=p
    return result

################################################
#Creating up the board
################################################
def setUpMap(app,x,y):
    app.enemyX,app.enemyY,app.walls=board(app,250,250)
    app.nextHasBarrier=True
    topX,topY,topW=board(app,250,-250)
    app.enemyX+=topX
    app.enemyY+=topY
    wallKeys=dict()
    for key in app.walls:
        wallKeys[key]=app.walls[key]
    for key in topW:
        wallKeys[key]=topW[key]
    app.walls=wallKeys

def board(app,x,y):
    enemyX=[20,480]*5+[20]
    enemyY=list(range(y-230,y+230,45))
    walls={(100,y):5,(400,y):5,(250,y+100):5,(250,y-100):5}
    if(app.nextHasBarrier):
        walls[(100,y-250)]=5
        walls[(400,y-250)]=5
        addEnemyTanks(app,x,y-340)
    return enemyX,enemyY,walls

def addEnemyTanks(app,x,y):
    downCount=2+app.level//5
    sideCount=1+app.level//5
    trackCount=app.level//7
    for i in range(downCount):
        interval=500/(downCount+1)
        app.enemyTanks.append(enemyTank(interval+interval*i,y,'down'))
    for j in range(sideCount):
        interval=500/(sideCount+1)
        app.enemyTanks.append(enemyTank(interval+interval*j,y,'side'))
    for k in range(trackCount):
        interval=500/(trackCount+1)
        app.enemyTanks.append(enemyTank(interval+interval*k,y,'track'))

#returns change in x and y between two points
def slope(x0,y0,x1,y1):
    changeX=(x1-x0)
    changeY=(y1-y0)
    return changeX,changeY

#draws tank on the board
def drawTank(app,canvas):
    x0=app.tankPoints[0][0]
    y0=app.tankPoints[0][1]
    x1=app.tankPoints[1][0]
    y1=app.tankPoints[1][1]
    x2=app.tankPoints[2][0]
    y2=app.tankPoints[2][1]
    x3=app.tankPoints[3][0]
    y3=app.tankPoints[3][1]
    canvas.create_polygon(x0,y0,x1,y1,x2,y2,x3,y3,fill='green')
    canvas.create_line(x0,y0,x1,y1,width=2,fill='blue')

#returns direction that tank is facing
def getDir(app):
    x0=app.tankPoints[0][0]
    x1=app.tankPoints[1][0]
    x2=app.tankPoints[2][0]
    x3=app.tankPoints[3][0]
    if(x0<x3 and x1<x2):
        return 'w'
    if(x0>x3 and x1>x2):
        return 'e'

#moves objects down or up as tank moves
def moveObjects(app,cY):
    if(cY>0):
        for i in range(len(app.enemyY)):
            app.enemyY[i]+=cY
        newWall=dict()
        for key in app.walls:
            x=key[0]
            y=key[1]
            newY=key[1]+cY
            value=app.walls[key]
            newWall[(x,newY)]=value
        app.walls=newWall
        for p in app.projectiles:
            p.y+=cY
        for l in range(len(app.levelMarkers)):
            app.levelMarkers[l]+=cY
        for t in app.enemyTanks:
            t.y+=cY

#Updates tanks positions for specified movement
def moveTank(app,direction):
    face=getDir(app)
    x0=app.tankPoints[0][0]
    y0=app.tankPoints[0][1]
    x3=app.tankPoints[3][0]
    y3=app.tankPoints[3][1]
    changeX,changeY=slope(x0,y0,x3,y3)  
    changeX/=app.slowDown
    changeY/=app.slowDown
    if(almostEqual(changeX,0)):
        s=None
    else:
        s=changeY/changeX
    if(direction=='forward'):
        for i in range(len(app.tankPoints)):
            if(s==None):
                moveObjects(app,changeY)
            elif(face=='e'):
                if(almostEqual(s,0)):
                    app.tankPoints[i][0]-=changeX
                elif(s<0):
                    app.tankPoints[i][0]-=changeX
                    moveObjects(app,changeY)
                else:
                    moveObjects(app,changeY)
            else:
                if(almostEqual(s,0)):
                    app.tankPoints[i][0]-=changeX
                elif(s<0):
                    moveObjects(app,changeY)
                else:
                    app.tankPoints[i][0]-=changeX
                    moveObjects(app,changeY)
        updateCenter(app)
        app.trackColors.append(app.trackColors.pop(0))
    else:
        for i in range(len(app.tankPoints)):
            if(s==None):
                moveObjects(app,-changeY)
            elif(face=='e'):
                if(almostEqual(s,0)):
                    app.tankPoints[i][0]+=changeX
                elif(s<0):
                    moveObjects(app,-changeY)
                else:
                    app.tankPoints[i][0]+=changeX
                    moveObjects(app,-changeY)
            else:
                if(almostEqual(s,0)):
                    app.tankPoints[i][0]+=changeX
                elif(s<0):
                    app.tankPoints[i][0]+=changeX
                    moveObjects(app,-changeY)
                else:
                    moveObjects(app,-changeY)
        updateCenter(app)
        app.trackColors.insert(0,app.trackColors.pop(-1))

#Updates points during rotation
def rotate(app,r):
    if(r!=0):
        newPoints=[]
        r=math.radians(r)
        for point in app.tankPoints:
            oldX=app.tankX
            oldY=app.tankY
            point[0]-=app.tankX
            point[1]-=app.tankY
            newX=point[0]*math.cos(r)-point[1]*math.sin(r)
            newY=point[1]*math.cos(r)+point[0]*math.sin(r)
            newPoints.append([newX+oldX,newY+oldY])
        app.tankPoints=newPoints
    updateCenter(app)

#updates point for center of tank
def updateCenter(app):
    app.tankX=(app.tankPoints[0][0]+app.tankPoints[1][0]+app.tankPoints[2][0]+app.tankPoints[3][0])/4
    app.tankY=(app.tankPoints[0][1]+app.tankPoints[1][1]+app.tankPoints[2][1]+app.tankPoints[3][1])/4

#returns the distance between two points
def distance(x0,y0,x1,y1):
    return ((x1-x0)**2+(y1-y0)**2)**0.5

#Returns point for turret
def getOtherPoints(x,y,x1,y1):
    if(almostEqual(x,x1)):
        if(y1>y):
            return x,y-30
        else:
            return x,y+30
    angle=math.atan((y1-y)/(x1-x))
    d=distance(x,y,x1,y1)
    r=d/30
    t=d/r
    if(x1>x):
        newX=x+t*math.cos(angle)
        newY=y+t*math.sin(angle)
        return newX,newY
    else:
        newX=x-t*math.cos(angle)
        newY=y-t*math.sin(angle)
        return newX,newY
 
#Draws the turret of the tank
def drawTurret(app,canvas):
    pointX,pointY=getOtherPoints(app.tankX,app.tankY,app.mouseX,app.mouseY)
    canvas.create_line(app.tankX,app.tankY,pointX,pointY,width=6)
    if(app.doubleBarrel):
        oppX=app.tankX-abs(app.tankX-pointX)
        oppY=app.tankY-abs(app.tankY-pointY)
        if(app.mouseX<app.tankX):
            oppX=app.tankX+abs(app.tankX-pointX)
        if(app.mouseY<app.tankY):
            oppY=app.tankY+abs(app.tankY-pointY)    
        canvas.create_line(app.tankX,app.tankY,oppX,oppY,width=6)
    canvas.create_oval(app.tankX-10,app.tankY-10,app.tankX+10,app.tankY+10,fill='grey')

#returns True of the tank drives over a wall
def tankIntersectsWall(app):
    for key in app.walls:
        if(app.walls[key]>0):
            wX=key[0]
            wY=key[1]
            x0=wX-50
            y0=wY-25
            x1=wX+50
            y1=wY+25
            if(x0<=app.tankX<=x1 and y0<=app.tankY<=y1):
                app.walls[key]-=1
                return True
    return False

#returns True if the tank intersects with the enemy turret
def tankIntersectsEnemy(app):
    for i in range(len(app.enemyX)):
        d=distance(app.tankX,app.tankY,app.enemyX[i],app.enemyY[i])
        if(d<=40):
            app.enemyX.pop(i)
            app.enemyY.pop(i)
            app.score+=10
            return True
    return False

#Draws enemy turrets
def drawEnemy(app,canvas):
    for i in range(len(app.enemyX)):
        x=app.enemyX[i]
        y=app.enemyY[i]
        canvas.create_rectangle(x-20,y-20,x+20,y+20,fill='grey')
        pointX,pointY=getOtherPoints(x,y,app.tankX,app.tankY)
        if(pointX==x):
            if(y<pointY):
                canvas.create_line(x,y,pointX,y-30,width=6)
            else:
                canvas.create_line(x,y,pointX,y+30,width=6)
            canvas.create_oval(x-10,y-10,x+10,y+10,fill='black')
        else:
            canvas.create_line(x,y,pointX,pointY,width=6)
            canvas.create_oval(x-10,y-10,x+10,y+10,fill='black')

#adds a projectile fired from the enemy
def addEnemyProjectile(app):
    if(len(app.enemyX)>=1):
        num=random.randint(0,len(app.enemyX)-1)
        endOfTurretX,endOfTurretY=getOtherPoints(app.enemyX[num],app.enemyY[num],app.tankX,app.tankY)
        cX,cY=slope(app.enemyX[num],app.enemyY[num],endOfTurretX,endOfTurretY)
        if(app.level>=15):
            if(app.level>=20):
                app.projectiles.append(Projectile(endOfTurretX,endOfTurretY,cX,cY,20,True))
            else:
                app.projectiles.append(Projectile(endOfTurretX,endOfTurretY,cX,cY,True))
        else:
            app.projectiles.append(Projectile(endOfTurretX,endOfTurretY,cX,cY))
        app.score+=1

#makes all the enemy tanks fire
def addEnemyTankProjectile(app):
    count=0
    for t in app.enemyTanks:
        endOfTurretX,endOfTurretY=getOtherPoints(t.x,t.y,app.tankX,app.tankY)
        cX,cY=slope(t.x,t.y,endOfTurretX,endOfTurretY)
        if(t.movement=='track' or count%2==0):
            app.projectiles.append(Projectile(endOfTurretX,endOfTurretY,cX,cY,t.damage,t.track))
            count+=1
        app.score+=1

#draws the projectiles
def drawProjectiles(app,canvas):
    for p in app.projectiles:
        x=p.getX()
        y=p.getY()
        canvas.create_oval(x-2,y-2,x+2,y+2,fill='black')

#updates the position of the projectiles
def moveProjectiles(app):
    for p in app.projectiles:
        if(not p.move(app) or projectileIntersectsWall(app,p) or projectileIntersectsTurret(app,p) or projectileIntersectsTank(app,p) or projectileIntersectsEnemyTank(app,p)):
            app.projectiles.remove(p)
        if(p.tracking):
            adjustProjectile(app,p)

#updates enemy tanks based on movement properties
def moveEnemyTanks(app):
    for t in app.enemyTanks:
        t.move()
        if(t.movement=='track'):
            endOfTurretX,endOfTurretY=getOtherPoints(t.x,t.y,app.tankX,app.tankY)
            cX,cY=slope(t.x,t.y,endOfTurretX,endOfTurretY)
            t.updateTracker(cX,cY)

#Adjusts the projectile direction
def adjustProjectile(app,p):
    endOfTurretX,endOfTurretY=getOtherPoints(p.getX(),p.getY(),app.tankX,app.tankY)
    cX,cY=slope(p.getX(),p.getY(),endOfTurretX,endOfTurretY)
    p.cX=cX
    p.cY=cY

#returns True if a projectile hits one of the enemy tanks
def projectileIntersectsEnemyTank(app,p):
    for t in app.enemyTanks:
        if(t.projectileIntersects(p)):
            if(t.movement=='track'):
                app.score+=50
            else:
                app.score+=20
            app.coins+=20
            return True
    return False

#returns True if a projectile intersects the tank
def projectileIntersectsTank(app,p):
    x0=app.tankPoints[0][0]
    y0=app.tankPoints[0][1]
    x1=app.tankPoints[1][0]
    y1=app.tankPoints[1][1]
    x2=app.tankPoints[2][0]
    y2=app.tankPoints[2][1]
    x3=app.tankPoints[3][0]
    y3=app.tankPoints[3][1]
    pX=p.getX()
    pY=p.getY()
    case1=(x0<=pX<=x1)and(x3<=pX<=x2)and(y0<=pY<=y3)and(y1<=pY<=y2)
    case2=(x3<=pX<=x1)and(y0<=pY<=y2)
    case3=(x0<=pX<=x2)and(y1<=pY<=y3)
    case4=(x2<=pX<=x0)and(y3<=pY<=y1)
    case5=(x1<=pX<=x3)and(y2<=pY<=y0)
    case6=(x1<=pX<=x2)and(x0<=pX<=x3)and(y1<=pY<=y0)and(y2<=pY<=y3)
    if(case1 or case2 or case3 or case4 or case5 or case6):
        if(app.forceField>0):
            app.forceField-=5
        else:
            app.tankHealth-=p.getDamage()
        return True
    return False

#returns True if a projectile intersects a turret
def projectileIntersectsTurret(app,p):
    pX=p.getX()
    pY=p.getY()
    for i in range(len(app.enemyX)):
        centerX=app.enemyX[i]
        centerY=app.enemyY[i]
        x0=centerX-20
        y0=centerY-20
        x1=centerX+20
        y1=centerY+20
        closestX=max(x0,min(pX,x1))
        closestY=max(y0,min(pY,y1))
        d=distance(pX,pY,closestX,closestY)
        if(d<=2):
            app.enemyX.pop(i)
            app.enemyY.pop(i)
            app.coins+=10
            app.score+=10
            return True
    return False

#returns True if a projectile intersects a wall
def projectileIntersectsWall(app,p):
    pX=p.getX()
    pY=p.getY()
    for key in app.walls:
        if(app.walls.get(key)!=0):
            centerX=key[0]
            centerY=key[1]
            x0=centerX-50
            y0=centerY-25
            x1=centerX+50
            y1=centerY+25
            #Closest point in wall to projectile
            closestX=max(x0,min(pX,x1))
            closestY=max(y0,min(pY,y1))
            d=distance(pX,pY,closestX,closestY)
            if(d<=2):
                app.walls[key]-=1
                return True
    return False

#adds a projectile fired from tank
def addProjectile(app):
    endOfTurretX,endOfTurretY=getOtherPoints(app.tankX,app.tankY,app.mouseX,app.mouseY)
    cX,cY=slope(app.tankX,app.tankY,endOfTurretX,endOfTurretY)
    app.projectiles.append(Projectile(endOfTurretX,endOfTurretY,cX,cY))
    if(app.doubleBarrel):
        oppX=app.tankX-abs(app.tankX-endOfTurretX)
        oppY=app.tankY-abs(app.tankY-endOfTurretY)
        if(app.mouseX<app.tankX):
            oppX=app.tankX+abs(app.tankX-endOfTurretX)
        if(app.mouseY<app.tankY):
            oppY=app.tankY+abs(app.tankY-endOfTurretY)
        c2X,c2Y=slope(app.tankX,app.tankY,oppX,oppY)
        app.projectiles.append(Projectile(oppX,oppY,c2X,c2Y))

#Draws the walls on board
def drawWalls(app,canvas):
    for key in app.walls:
        if(app.walls.get(key)!=0):
            x=key[0]
            y=key[1]
            canvas.create_image(x,y,image=ImageTk.PhotoImage(app.wallImage))

#draws the health status of tank
def drawHealth(app,canvas):
    canvas.create_line(0,495,500,495,width=10,fill='white')
    canvas.create_line(0,495,app.tankHealth,495,width=10,fill='red')
    canvas.create_text(3,495,text='HP',anchor='w',font='Terminal 8')

#Checks if tank is on the board
def inBounds(app):
    if(app.tankX<0 or app.tankX>500 or app.tankY<0 or app.tankY>500):
        app.returnToArea=True
    else:
        app.returnToArea=False

#Draws warning for user to return to area
def drawReturnWarning(app,canvas):
    canvas.create_rectangle(0,100,500,200,fill='red')
    canvas.create_text(250,150,text="Warning: return to map!",anchor='c',font='Terminal 15 bold')

#Draws text for when game ends
def drawGameOver(app,canvas):
    canvas.create_text(250,150,text="Game Over!",anchor='c',font='Terminal 20 bold')
    canvas.create_text(250,175,text="-go to pause menu to restart-",anchor='c',font='Terminal 15 bold')

#Draws the score 
def drawScore(app,canvas):
    canvas.create_text(498,13,text=f'Score:{app.score}',anchor='e',font='Terminal 15 bold')

#Draws the level
def drawLevel(app,canvas):
    canvas.create_text(498,30,text=f'Level:{app.level}',anchor='e',font='Terminal 15 bold')

#Draws the coins
def drawCoins(app,canvas):
    canvas.create_text(470,50,text=f'{app.coins}',anchor='e',font='Terminal 15 bold')
    canvas.create_image(490,50,image=ImageTk.PhotoImage(app.coinImage))

#Draws the board consisting of a desert
def drawBoard(app,canvas):
    x=(app.boardX0+app.boardX1)/2
    y=(app.boardY0+app.boardY1)/2
    canvas.create_image(x,y,image=ImageTk.PhotoImage(app.boardImage))

#Spends coins for powerups
def buyItem(app,num):
    #mystery
    if num==1:
        cost=50
        if(app.coins-cost>=0):
            r=random.randint(1,6)
            if(r==1 or r==2):
                app.tankHealth-=20
            elif(r==3 or r==4):
                rebuildWalls(app)
            elif(r==5):
                app.tankHealth=500
            else:
                airStrike(app)
            app.coins-=cost
    #rebuild walls
    elif num==2:
        cost=100
        if(app.coins-cost>=0):
            rebuildWalls(app)
            app.coins-=cost
    #imcrease tank speed 
    elif num==3:
        cost=200
        if(app.coins-cost>=0 and app.slowDown>5):
            increaseSpeed(app)
            app.coins-=cost
    #Gain health back
    elif num==4:
        cost=300
        if(app.coins-cost>=0):
            app.coins-=cost
            app.tankHealth=500
    #air strike
    elif num==5:
        cost=500
        if(app.coins-cost>=0):
            airStrike(app)
            app.coins-=cost
    #force field
    elif num==6:
        cost=500
        if(app.coins-cost>=0):
            app.forceField+=100
            app.coins-=cost
    #double barrel
    elif num==7:
        cost=500
        if(app.coins-cost>=0):
            app.doubleBarrel=True
            app.coins-=cost

#Decreases app.slowDown in order to make the tank move faster
def increaseSpeed(app):
    app.slowDown-=5
    if(app.slowDown<5):
        app.slowDown=5

#puts walls back on the map
def rebuildWalls(app):
    for key in app.walls:
        app.walls[key]=5

#enemy turrets get destroyed from air strike
def airStrike(app):
    app.airStrike=True
    
#every enemy tank will become destroyed
def drawAirStrike(app,canvas):
    x=app.airStrikeX
    canvas.create_image(x,50,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x,150,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x,250,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x,350,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x,450,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x+50,100,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x+50,200,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x+50,300,image=ImageTk.PhotoImage(app.planeImage))
    canvas.create_image(x+50,400,image=ImageTk.PhotoImage(app.planeImage))

#Draws enemy tanks
def drawEnemyTanks(app,canvas):
    for t in app.enemyTanks:
        x=t.x
        y=t.y
        canvas.create_rectangle(x-20,y-20,x+20,y+20,fill=t.color)
        pointX,pointY=getOtherPoints(x,y,app.tankX,app.tankY)
        if(pointX==x):
            if(y<pointY):
                canvas.create_line(x,y,pointX,y-30,width=6)
            else:
                canvas.create_line(x,y,pointX,y+30,width=6)
        else:
            canvas.create_line(x,y,pointX,pointY,width='6')
        canvas.create_oval(x-10,y-10,x+10,y+10,fill='black')

#removes enemy tanks that are destroyed
def clearDestroyedEnemyTanks(app):
    new=[]
    for t in app.enemyTanks:
        if(t.health>0):
            new.append(t)
    app.enemyTanks=new

#draws the level markers    
def drawLevelMarker(app,canvas):
    for y in app.levelMarkers:
        canvas.create_line(0,y,500,y,width=5)

def clearBottom(app):
    newEnemyY=[]
    newEnemyX=[]
    for i in range(len(app.enemyY)):
        if(app.enemyY[i]<500):
            newEnemyY.append(app.enemyY[i])
            newEnemyX.append(app.enemyX[i])
        else:
            app.score-=5
            app.tankHealth-=5
    app.enemyY=newEnemyY
    app.enemyX=newEnemyX
    newWall=dict()
    for key in app.walls:
        x=key[0]
        y=key[1]
        if(y<500):
            value=app.walls[key]
            newWall[(x,y)]=value
    app.walls=newWall
    newProjectiles=[]
    for p in app.projectiles:
        if(p.y<500 and 0<=p.x<=500):
            newProjectiles.append(p)
    app.projectiles=newProjectiles
    newLevelMark=[]
    for l in range(len(app.levelMarkers)):
        if(app.levelMarkers[l]<500):
            newLevelMark.append(app.levelMarkers[l])
        else:
            newLevelMark.append(formNextLevel(app,app.levelMarkers[l]))
            app.level+=1
            app.score+=100
            app.coins+=50
    app.levelMarkers=newLevelMark
    for t in app.enemyTanks:
        if(t.y>500):
            app.enemyTanks.remove(t)
            app.score-=20

#Creates next level
def formNextLevel(app,l):
    d=abs(l-500)
    y=l-d-700
    topX,topY,topW=board(app,250,int(y-250))
    app.enemyX+=topX
    app.enemyY+=topY
    wallKeys=dict()
    for key in app.walls:
        wallKeys[key]=app.walls[key]
    for key in topW:
        wallKeys[key]=topW[key]
    app.walls=wallKeys
    return y

#Removes any enemies on the board
def removeEnemiesOnBoard(app):
    newX=[]
    newY=[]
    for i in range(len(app.enemyX)):
        if(0<=app.enemyX[i]<=500 and 0<=app.enemyY[i]<=500):
            pass
        else:
            newX.append(app.enemyX[i])
            newY.append(app.enemyY[i])
    app.enemyX=newX
    app.enemyY=newY

def drawForceField(app,canvas):
    if(app.forceField>0):
        if(app.forceField<10):
            canvas.create_oval(app.tankX-30,app.tankY-30,app.tankX+30,app.tankY+30,outline='red',width=3)
        elif(app.forceField<40):
            canvas.create_oval(app.tankX-30,app.tankY-30,app.tankX+30,app.tankY+30,outline='orange',width=3)
        elif(app.forceField<70):
            canvas.create_oval(app.tankX-30,app.tankY-30,app.tankX+30,app.tankY+30,outline='yellow',width=3)
        else:
            canvas.create_oval(app.tankX-30,app.tankY-30,app.tankX+30,app.tankY+30,outline='green',width=3)

#################################################
# Game Mode
#################################################
def gameMode_keyPressed(app,event):
    if(event.key=='p'):
        app.players=readPlayerScores('scores.txt')
        app.mode='pauseMode'
    if(not app.gameOver):
        if(event.key=='Tab'):
            app.burst=not app.burst
        if(event.key=="w"):
            moveTank(app,'forward')
        elif(event.key=="s"):
            moveTank(app,'backward')
        elif(event.key=='a'):
            rotate(app,-10)
        elif(event.key=='d'):
            rotate(app,10)
        elif(event.key.isnumeric() and 1<=int(event.key)<=7):
            buyItem(app,int(event.key))
    if(app.cheats):
        if(event.key=='c'):
            app.coins+=500
        elif(event.key=='v'):
            app.level+=1
            app.score+=100
        elif(event.key=='b'):
            app.tankHealth=500
            app.gameOver=False
        elif(event.key=='n'):
            app.neverDie=not app.neverDie
    
def gameMode_redrawAll(app,canvas):
    drawBoard(app,canvas)
    drawEnemy(app,canvas)
    drawProjectiles(app,canvas)
    drawWalls(app,canvas)
    drawEnemyTanks(app,canvas)
    drawTank(app,canvas)
    drawForceField(app,canvas)
    drawLevelMarker(app,canvas)
    drawTurret(app,canvas)
    if(app.gameOver):
        drawGameOver(app,canvas)
    elif(app.returnToArea):
        drawReturnWarning(app,canvas)
    drawHealth(app,canvas)
    drawScore(app,canvas)
    drawLevel(app,canvas)
    drawCoins(app,canvas)
    if(app.airStrike):
        drawAirStrike(app,canvas)
    canvas.create_text(5,8,anchor='w',text='Press p to pause',font='Terminal 10 bold')

def gameMode_mouseMoved(app,event):
    app.mouseX=event.x
    app.mouseY=event.y

def gameMode_mousePressed(app,event):
    if(not app.gameOver):
        if(app.burst):
            for i in range(5):
                addProjectile(app)
                moveProjectiles(app)
        else:
            addProjectile(app)

#Updates app.frequency as time increases
def updateFiringSpeed(app):
    app.frequency=20-app.level
    if(app.frequency<1):
        app.frequency=1

def gameMode_timerFired(app):
    if(app.tankHealth<=0 and not app.neverDie):
        app.gameOver=True
    if(not app.gameOver):
        app.movements+=1
        moveEnemyTanks(app)
        clearDestroyedEnemyTanks(app)
        if(app.level>10):
            moveObjects(app,.2*app.level)
        if(app.movements%app.frequency==0):
            addEnemyProjectile(app)
            addEnemyTankProjectile(app)
        if(app.movements%5==0):
            tankIntersectsWall(app)
        if(app.returnToArea):
            app.tankHealth-=5
        moveProjectiles(app)
        inBounds(app)
        tankIntersectsEnemy(app)
        clearBottom(app)
        if(app.airStrike):
            app.airStrikeX+=5
        if(app.airStrike and app.airStrikeX>510):
            app.score+=10*len(app.enemyX)
            app.coins+=100
            removeEnemiesOnBoard(app)
            app.airStrike=False
        updateFiringSpeed(app)

#adds score to file once game ends
def addScoreToFile(app):
    if(not app.cheats):
        score=app.score
        player=app.username
        f=open('scores.txt','a')
        f.write(f'\n{score},{player}')
        f.close()

#################################################
# Pause Mode
#################################################
def pauseMode_mousePressed(app,event):
    x=event.x
    y=event.y
    if(150<=x<=350):
        if(150<=y<=200):
            app.mode='gameMode'
        elif(250<=y<=300):
            addScoreToFile(app)
            appStarted(app)
        elif(350<=y<=400):
            app.mode='guideMode'
        elif(450<=y<=500):
            app.mode='leaderboardMode'
        
def pauseMode_redrawAll(app,canvas):
    font = 'Terminal 15 bold'
    y=0
    interval=500/len(app.trackColors)
    for i in range(len(app.trackColors)):
        canvas.create_rectangle(0,y,500,y+interval,fill=app.trackColors[i])
        y+=interval
    canvas.create_text(app.width/2, 20, text='Paused!', font=font)
    canvas.create_text(app.width/2,60,text=f'Current Score: {app.score}',font=font)
    canvas.create_text(app.width/2,85,text=f'Current Level: {app.level}',font=font)
    canvas.create_rectangle(150,150,350,200,fill='black')
    canvas.create_text(175,175,anchor='w',text='Back to game',font=font,fill='green')
    canvas.create_rectangle(150,250,350,300,fill='black')
    canvas.create_text(180,275,anchor='w',text='Quit/Restart',font=font,fill='red')
    canvas.create_rectangle(150,350,350,400,fill='black')
    canvas.create_text(200,375,anchor='w',text='Guide',font=font,fill='blue')
    canvas.create_rectangle(150,450,350,500,fill='black')
    canvas.create_text(185,475,anchor='w',text='Leaderboard',font=font,fill='yellow')


#################################################
# main
#################################################
def main():
    playTanks()

if __name__ == '__main__':
    main()