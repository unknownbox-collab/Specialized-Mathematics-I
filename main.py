import math, random, copy, pygame, sys, sympy

WHITE   =  (255, 255, 255)
ORANGE  =  (255, 127, 0  )
YELLOW  =  (255, 255, 0  )
BLACK   =  (0,   0,   0  )
BLUE    =  (0,   0,   255)
RED     =  (255, 0,   0  )
SKYBLUE =  (135, 206, 235)
SLIVER  =  (192, 192, 192)
BROWN   =  (206, 139, 84 )

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500

INNER = 0
OUTER = 1

SPEED = 5

pygame.init()
pygame.display.set_caption("심화 수학 I")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def getDistance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

class Circle:
    def __init__(self,x,y,size,color = RED) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.skin = pygame.Surface((self.size,self.size),pygame.SRCALPHA)
        pygame.draw.circle(self.skin, color, (self.size*1/2, self.size*1/2), self.size/2, 4)

    def draw(self,screen):
        screen.blit(self.skin,(self.x-self.size/2,self.y-self.size/2))

class Line:
    def __init__(self, incline, x,y) -> None:
        self.incline = incline
        self.x = x
        self.y = y
    
    def getY(self, x):
        return self.incline * (x - self.x) + self.y

    def getX(self, y):
        return (y - self.y + self.incline * self.x)/(self.incline + 2e-16)

    def getPoint(self, line):
        m1 = self.incline
        m2 = line.incline
        t1 = self.x
        t2 = line.x
        p1 = self.y
        p2 = line.y
        x = (t1*m1 - t2*m2 + p2 - p1)/(m1-m2)
        return (x, self.getY(x))
    
    def getDistance(self,x, y):
        return abs(self.incline * x - y - self.incline * self.x + self.y)/math.sqrt(self.incline ** 2 + 1)
    
    def draw(self,screen):
        pygame.draw.line(screen, RED, (self.x, self.y), (self.x + 1000, self.y + 1000*self.incline), 1)
        pygame.draw.line(screen, RED, (self.x, self.y), (self.x - 1000, self.y - 1000*self.incline), 1)

class LineGetter:
    def __init__(self, circle, player, mod = INNER):
        self.circle = circle
        self.player = player
        self.mod = mod

        self.x1 = self.circle.x
        self.y1 = self.circle.y
        self.x2 = self.player.x
        self.y2 = self.player.y
        self.r1 = self.circle.size/2
        self.r2 = self.player.size/2
        self.l = getDistance((self.x1, self.y1), (self.x2, self.y2))

    def step1(self):
        if self.x2 != self.x1:
            varphi = math.atan((self.y2 - self.y1) / (self.x2 - self.x1))
            return varphi

    def step2(self):
        if self.l > 0:
            if (self.r1 + self.r2)/self.l != 0:
                if (self.r1 + self.r2) < self.l:
                    alpha = math.atan((self.r2 + self.r1)/math.sqrt(self.l**2 - self.r1**2 - 2*self.r1*self.r2 - self.r2**2))
                    if self.mod:
                        alpha = math.atan((self.r2 - self.r1)/math.sqrt(self.l**2 - self.r1**2 + 2*self.r1*self.r2 - self.r2**2))
                    return alpha
    
    def step3(self):
        varphi = self.step1()
        if varphi is not None:
            alpha = self.step2()
            if alpha is not None:
                a = self.x1 + self.r1 * math.cos(varphi)/math.sin(alpha)*abs(self.x2 - self.x1)/(self.x2 - self.x1)
                b = self.y1 + self.r1 * math.sin(varphi)/math.sin(alpha)*abs(self.x2 - self.x1)/(self.x2 - self.x1)
                return (a,b)
    
    def step4(self):
        varphi = self.step1()
        if varphi is not None:
            alpha = self.step2()
            if alpha is not None:
                a, b = self.step3()
                return Line(math.tan(varphi + alpha),a,b), Line(math.tan(varphi - alpha),a,b)
    
    def update(self,circle,player):
        self.circle = circle
        self.player = player
        
        self.x1 = self.circle.x
        self.y1 = self.circle.y
        self.x2 = self.player.x
        self.y2 = self.player.y
        self.r1 = self.circle.size/2
        self.r2 = self.player.size/2
        self.l = getDistance((self.x1, self.y1), (self.x2, self.y2))

def getDegree(circle, player, index):
    x = circle.x - circle.size/4 + 2 * index[0] * circle.size/4
    y = circle.y - circle.size/4 + 2 * index[1] * circle.size/4
    l = getDistance((x, y), (player.x, player.y))
    r = circle.size/4
    theta = math.atan(r/math.sqrt(l**2 - r**2))
    p = math.atan((y - player.y)/(x - player.x))
    return theta - p, theta + p

circle = Circle(500, 250, 300, color = BLUE)
player = Circle(0, 100, 100)
innerLineGetter = LineGetter(circle, player)
outerLineGetter = LineGetter(circle, player, INNER)

while True:
    clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]:
        player.y -= SPEED
    if pressed[pygame.K_DOWN]:
        player.y += SPEED
    if pressed[pygame.K_RIGHT]:
        player.x += SPEED
    if pressed[pygame.K_LEFT]:
        player.x -= SPEED
    screen.fill(WHITE)
    lineList = []
    innerLineGetter.update(circle, player)
    temp = innerLineGetter.step4()
    if temp is not None :
        lineList.append(temp[0])
        lineList.append(temp[1])
    outerLineGetter.update(circle, player)
    temp = outerLineGetter.step4()
    if temp is not None :
        lineList.append(temp[0])
        lineList.append(temp[1])
    
    circle.draw(screen)
    if lineList is not None:
        for i in lineList: i.draw(screen)
    player.draw(screen)

    pygame.display.update()