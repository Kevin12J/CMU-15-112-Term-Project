#class for projectiles
from game import *
class Projectile(object):
    def __init__(self,x,y,changeX,changeY,damage=10,tracking=False):
        self.x=x
        self.y=y
        self.cX=changeX
        self.cY=changeY
        self.damage=damage
        self.tracking=tracking
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y

    def getDamage(self):
        return self.damage
        
    def move(self,app):
        yVals=sorted(app.enemyY)
        self.x+=self.cX
        self.y+=self.cY
        if(self.x>0 or self.x<500 or self.y>yVals[0] or self.y<yVals[-1] or self.y>0 or self.y<500):
            return True
        else:
            return False
