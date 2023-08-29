#Class for enemy tanks
#'side'=side to side movement-red
#'down'=drives down-pink
#'track'=drives to user-purple
class enemyTank(object):
    def __init__(self,x,y,movement,damage=20,health=10,track=False):
        self.x=x
        self.y=y
        self.movement=movement
        self.damage=damage
        self.health=health
        self.track=False
        if(movement=='side'):
            self.color='red'
            self.cX=7
            self.cY=0
        elif(movement=='down'):
            self.color='pink'
            self.cX=0
            self.cY=5
        elif(movement=='track'):
            self.color='purple'
            self.track=True
            self.health=50
            self.damage=50
            self.cX=0
            self.cY=0

    def updateTracker(self,x,y):
        if(self.movement=='track'):
            self.cX=x/20
            self.cY=y/20

    def move(self):
        if(self.movement=='side'):
            self.x+=self.cX
            if(self.x>500 or self.x<0):
                self.cX*=-1
        elif(self.movement=='down'):
            self.y+=self.cY
        elif(self.movement=='track'):
            self.x+=self.cX
            self.y+=self.cY

    def projectileIntersects(self,p):
        x0=self.x-20
        y0=self.y-20
        x1=self.x+20
        y1=self.y-20
        x2=self.x+20
        y2=self.y+20
        x3=self.x-20
        y3=self.y+20
        pX=p.getX()
        pY=p.getY()
        case1=(x0<=pX<=x1)and(x3<=pX<=x2)and(y0<=pY<=y3)and(y1<=pY<=y2)
        case2=(x3<=pX<=x1)and(y0<=pY<=y2)
        case3=(x0<=pX<=x2)and(y1<=pY<=y3)
        case4=(x2<=pX<=x0)and(y3<=pY<=y1)
        case5=(x1<=pX<=x3)and(y2<=pY<=y0)
        case6=(x1<=pX<=x2)and(x0<=pX<=x3)and(y1<=pY<=y0)and(y2<=pY<=y3)
        if(case1 or case2 or case3 or case4 or case5 or case6):
            self.health-=p.getDamage()
            return True
        return False