import random
from math import sqrt
import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.window import FPSDisplay

# Window Settings
window = pyglet.window.Window()
keys = key.KeyStateHandler()
window.push_handlers(keys)
window.set_caption("Deep Learning")
window.set_size(800, 800)
window.set_vsync(0)


# Rectangle Class
class Rectangle:
    def __init__(self, x, y, width, height, Color=(26, 255, 26)):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.Color = Color
        self.Highlight = False
        self.Clicked = False
        self.HighlightColor = (0, 0, 0)
        self.NoMidlle = False
        self.draw = self.Draw

    def Draw(self):
        if self.Highlight or self.Clicked:
            if not self.Clicked:
                self.HighlightColor = (150, 150, 150)
            else:
                self.HighlightColor = (0, 0, 0)
            TextDis = [self.width, self.height, self.x, self.y]
            if self.width < 0:
                TextDis[0] *= -1
                TextDis[2] = self.x - TextDis[0]
            if self.height < 0:
                TextDis[1] *= -1
                TextDis[3] = self.y - TextDis[1]
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [TextDis[2] - 4, TextDis[3] - 4, TextDis[2] + TextDis[0] + 4,
                                                          TextDis[3] - 4,
                                                          TextDis[2] + TextDis[0] + 4,
                                                          TextDis[3] + TextDis[1] + 4, TextDis[2] - 4,
                                                          TextDis[3] + TextDis[1] + 4]),
                                 ('c3B', (self.HighlightColor * 4)))

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                     [self.x, self.y, self.x + self.width, self.y, self.x + self.width,
                                                      self.y + self.height, self.x, self.y + self.height]),
                             ('c3B', (self.Color * 4)))

        if (self.Highlight or self.Clicked) and not self.NoMidlle:
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [int(self.x + self.width / 2) - 3, self.y,
                                                          int(self.x + self.width / 2) + 3, self.y,
                                                          int(self.x + self.width / 2) + 3, self.y + self.height,
                                                          int(self.x + self.width / 2) - 3, self.y + self.height]),
                                 ('c3B', (self.HighlightColor * 4)))

            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [self.x, int(self.y + self.height / 2) - 3,
                                                          self.x, int(self.y + self.height / 2) + 3,
                                                          self.x + self.width, int(self.y + self.height / 2) + 3,
                                                          self.x + self.width, int(self.y + self.height / 2) - 3]),
                                 ('c3B', (self.HighlightColor * 4)))


class Button(Rectangle):
    def __init__(self, x, y, width, height, color=(255, 242, 0), colorOn=(26, 255, 26),
                 mode="Lever", var=None, change=0):
        super().__init__(x, y, width, height, color)
        self.Pressed = False
        self.ColorOn = colorOn
        self.ColorOff = color
        self.Color = self.ColorOff
        if self.Pressed:
            self.Color = self.ColorOn
        self.Highlight = True
        self.NoMidlle = True
        self.Mode = mode
        self.Var = var
        self.Change = change

    def Update(self, x, y, press=True):
        if Intersects(self, x, y):
            if self.Mode == "Lever":
                self.Pressed = not self.Pressed
                if self.Pressed:
                    self.Color = self.ColorOn
                else:
                    self.Color = self.ColorOff
            elif self.Mode == "Button":
                if self.Pressed != press:
                    self.Pressed = press
                    if self.Pressed:
                        self.Var[0] += self.Change
                        self.Color = self.ColorOn
                    else:
                        self.Color = self.ColorOff
        elif self.Mode == "Button" and not press:
            self.Color = self.ColorOff
            self.Pressed = press


# Variables
# Directions = [[10, 10], [10, 0], [10, -10], [0, 10], [0, -10], [-10, 10], [-10, 0], [-10, -10]]  # Map for the Objects
Directions = [[10, 0], [0, 10], [0, -10], [-10, 0]]  # Map for the Objects
Gen = 0  # The current gen
Succeeded = False  # If at least one object ever succeeded
SucceededGen = 0
AvailableMoves = 0  # How mach moves can a object use
TheList = [[]]
MouseBuzy = False
MoveLEFT = False
MoveMIDDLE = False
MoveRIGHT = False
SelectedIconNum = 0
SelectedIconDelay = 0.2
EndPointOGxy = [0, 0]
StartPointOGxy = [0, 0]
Mode = 1
KeyDelay = 1
Blockers = []  # Rectangle(0, 200, 700, 100), Rectangle(window.width-700, 500, window.width, 100)
NewestBlocker = None
BestFitness = 0
MutationRate = [20]

# Background && Objects
background_batch = pyglet.graphics.Batch()  # Batches and groups
edit_batch = pyglet.graphics.Batch()
run_batch = pyglet.graphics.Batch()
gui_batch = pyglet.graphics.Batch()
objects_batch = pyglet.graphics.Batch()
B = pyglet.graphics.OrderedGroup(0)
F = pyglet.graphics.OrderedGroup(1)
fps_display = FPSDisplay(window)
fps_display.label.font_size = 50

MostashImg = pyglet.image.load('..\\Img\\Mostash.png')  # Loading Images
MostashBestImg = pyglet.image.load('..\\img\\MostashBest.png')
BackGroundImg = pyglet.image.load('..\\img\\Backgound.png')
EndPointImg = pyglet.image.load('..\\img\\EndPoint.png')
StartPointImg = pyglet.image.load('..\\img\\The Start.png')
SquareImg = pyglet.image.load('..\\img\\The Square.png')
MouseImg = pyglet.image.load('..\\img\\The Mouse.png')
SelectedIconImgList = [SquareImg, StartPointImg, EndPointImg, MouseImg]  # Icon list for the edit mode
BricksImg = pyglet.image.load('..\\img\\Full Bricks Dark.png')

SelectedIcon = [pyglet.sprite.Sprite(SquareImg, x=800 - 40, y=800 - 40, batch=edit_batch, group=F)]  # icons sprites
for i in range(1, 3):
    SelectedIcon.append(
        pyglet.sprite.Sprite(SelectedIconImgList[i], x=800 - 40 - 25 * i, y=800 - 40, batch=edit_batch, group=F))
    SelectedIcon[-1].scale = 0.5
BackGround = pyglet.sprite.Sprite(BackGroundImg, x=0, y=0, batch=background_batch, group=B)  # Background
Wall = pyglet.sprite.Sprite(BricksImg, x=0, y=698, batch=gui_batch, group=B)
EndPoint = pyglet.sprite.Sprite(EndPointImg, x=20, y=window.height - 102 - 50, batch=gui_batch, group=F)  # gui
StartPoint = pyglet.sprite.Sprite(StartPointImg, x=500, y=20, batch=gui_batch, group=F)

EditTexts = [
    pyglet.text.Label("Width - ", x=100, y=760, bold=True, italic=True, batch=edit_batch, font_size=15),
    pyglet.text.Label("Height - ", x=100, y=720, bold=True, italic=True, batch=edit_batch, font_size=15),
    pyglet.text.Label("X - ", x=300, y=760, bold=True, italic=True, batch=edit_batch, font_size=15),
    pyglet.text.Label("Y - ", x=300, y=720, bold=True, italic=True, batch=edit_batch, font_size=15),
    pyglet.text.Label("Left Click to Destroy", x=435, y=745, bold=True, italic=True, font_size=15),
    Rectangle(430, 739, 220, 25, (255, 0, 0))]
EditTexts[-1].Clicked = True
EditTexts[-1].NoMidlle = True

RunTexts = [
    pyglet.text.Label("Gen - ", x=100, y=760, bold=True, italic=True, font_size=15),
    pyglet.text.Label("Best Fitness - ", x=100, y=720, bold=True, italic=True, font_size=15),
    pyglet.text.Label("Moves Available - ", x=300, y=760, bold=True, italic=True, font_size=15),
    pyglet.text.Label("Objects Alive - ", x=300, y=720, bold=True, italic=True, font_size=15),
    pyglet.text.Label("Mutation Rate - 1/", x=510, y=760, bold=True, italic=True, font_size=15),
    Button(x=730, y=760, width=20, height=20, mode="Button", var=MutationRate, change=-1, color=(255, 0, 0), colorOn=(220, 20, 60)),
    Button(x=767, y=760, width=20, height=20, mode="Button", var=MutationRate, change=1, color=(26, 255, 26), colorOn=(34, 139, 34)),
    Button(x=20, y=720, width=60, height=60)]


# Functions
def Intersects(self, x=50, y=50, Object=None, TowPoints=None):
    if Object is not None:  # Object to Object Intersect
        if ((self.x > Object.x + Object.width) or (self.x + self.width < Object.x) or
                (self.y > Object.y + Object.height) or (self.y + self.height < Object.y)):
            return False
        return True
    elif TowPoints is not None:  # Object to Imaginary Rectangle Intersect[[x,y],[x+w,y+h]]
        if ((self.x > TowPoints[1][0]) or (self.x + self.width < TowPoints[0][0]) or
                (self.y > TowPoints[1][1]) or (self.y + self.height < TowPoints[0][1])):
            return False
        return True
    else:  # Object to on point
        if self.x < x < self.x + self.width and self.y < y < self.y + self.height:
            return True
    return False


def ScoreTheBoard():
    global TheList
    TheList = [[-1 for i in range(int(window.width / 5))] for j in
               range(int((window.height - 102) / 5))]  # 2D array the size of the screen

    TheList[int(int(EndPoint.y + EndPoint.height / 2) / 5)][
        int(int(EndPoint.x + EndPoint.width / 2) / 5)] = 0  # EndPoint

    # Drawing the blockers in the list
    for Blocker in Blockers:
        for x in range(int(Blocker.width / 5)):
            for y in range(int(Blocker.height / 5)):
                if 0 <= y + int(Blocker.y / 5) < len(TheList) and 0 <= x + int(Blocker.x / 5) < len(TheList[0]):
                    TheList[y + int(Blocker.y / 5)][x + int(Blocker.x / 5)] = -9

    # Setting every clear place to his score
    Score = 0
    while [Line.count(-1) == 0 for Line in TheList].count(False) != 0:
        for y in range(len(TheList)):
            for x in range(len(TheList[0])):
                if TheList[y][x] == Score:
                    if x > 0 and TheList[y][x - 1] == -1:
                        TheList[y][x - 1] = Score + 1
                    if y > 0 and TheList[y - 1][x] == -1:
                        TheList[y - 1][x] = Score + 1
                    if x < len(TheList[0]) - 1 and TheList[y][x + 1] == -1:
                        TheList[y][x + 1] = Score + 1
                    if y < len(TheList) - 1 and TheList[y + 1][x] == -1:
                        TheList[y + 1][x] = Score + 1
        Score += 1

    # Making the the blockers place higher then normal places by adding 2 to the highest near place
    NewList = [[dig for dig in line] for line in TheList]
    for y in range(len(TheList)):
        for x in range(len(TheList[0])):
            if TheList[y][x] == -9:
                Best = 0
                if x > 0 and TheList[y][x - 1] > Best:
                    Best = TheList[y][x - 1]
                if y > 0 and TheList[y - 1][x] > Best:
                    Best = TheList[y - 1][x]
                if x < len(TheList[0]) - 1 and TheList[y][x + 1] > Best:
                    Best = TheList[y][x + 1]
                if y < len(TheList) - 1 and TheList[y + 1][x] > Best:
                    Best = TheList[y + 1][x]
                NewList[y][x] = Best

    print(end="\n\n\n")
    for Line in NewList:
        print(Line)

    TheList = NewList


def UpdateIcons():
    print(SelectedIconNum)
    for i in range(len(SelectedIcon)):
        Num = SelectedIconNum + i
        if Num > 2:
            Num -= 3
        SelectedIcon[i].image = SelectedIconImgList[Num]
    global Blockers  # Removing highlight and clicked from the blockers
    for Blocker in Blockers:
        Blocker.Highlight = False
        Blocker.Clicked = False


# Deep learning Functions
class Object:
    def __init__(self, Moves, First=False):
        self.Moves = Moves  # List of instructions that gide the object
        self.Place = 0  # the place in the list of
        self.x, self.y = StartPoint.x - 5, StartPoint.y - 5  # place of the Object
        if not RunTexts[-1].Pressed:
            self.Sprite = pyglet.sprite.Sprite(MostashImg, x=self.x, y=self.y, batch=objects_batch, group=B)  # The draw
            self.Sprite.update(scale=0.8)  # Scale the img to 40x40
        else:
            self.Sprite = None
        self.First = None
        if First:  # Draw differently the best from the last gen
            self.First = True
            self.Sprite = pyglet.sprite.Sprite(MostashImg, x=self.x, y=self.y, batch=objects_batch, group=B)  # The draw
            self.Sprite.image = MostashBestImg
            self.Sprite.group = F
            self.Sprite.update(scale=0.8)  # Scale the img to 40x40
        self.width = 40  # self.Sprite.width  # setting for the Intersects function
        self.height = 40  # self.Sprite.height
        self.Alive = True  # If the object is alive or not
        self.FitnessScore = None  # The fitness score of the object
        self.Finish = False  # If the object finish the course or failed
        self.Dead = False  # If the object run out of moves or died from a wall
        self.MLeft = 0  # Number of moves that the object didn't use

    def Fitness(self):
        self.MLeft = AvailableMoves - self.Place
        if self.Finish:
            self.FitnessScore = 1400 + self.MLeft * 5
        else:
            if True:
                global TheList
                if self.Dead:
                    self.FitnessScore = 990 - TheList[int(self.y / 5)][int(self.x / 5)]
                else:
                    self.FitnessScore = 1000 - TheList[int(self.y / 5)][int(self.x / 5)]
            else:
                if self.Dead:
                    self.FitnessScore = 1000 - sqrt((self.x - (EndPoint.x + EndPoint.width / 2)) ** 2 + (
                            self.y - (EndPoint.y + EndPoint.height / 2)) ** 2) - 400
                self.FitnessScore = 1000 - sqrt((self.x - (EndPoint.x + EndPoint.width / 2)) ** 2 + (
                        self.y - (EndPoint.y + EndPoint.height / 2)) ** 2)

    def Update(self):
        if self.Alive:
            global Blockers
            # Checks if the object intersects with a wall
            if [Intersects(self, Object=blocker) for blocker in Blockers].count(True) != 0:
                self.Alive = False
                self.Dead = True
            # Checks if the object touched the edge of the map
            elif self.x <= 0 or self.x + self.width >= window.width or self.y <= 0 or self.y + self.height >= window.height - 102:
                self.Alive = False
                self.Dead = True
                if self.x < 0:  # the object was getting fitness score of -1 
                    self.x = 0
                if self.y < 0:
                    self.y = 0
            # Checks if the object intersects with the end point
            elif Intersects(self, Object=EndPoint):
                global AvailableMoves
                self.Finish = True
                self.Alive = False
                self.MLeft = AvailableMoves - self.Place  # Check how mach moves the object used
                self.Moves = self.Moves[:self.Place]  # Remove the unused parts
            # If the object is in a clear way, move the object by the instructions
            elif self.Place < len(self.Moves):
                self.x += Directions[self.Moves[self.Place]][0]
                self.y += Directions[self.Moves[self.Place]][1]
                self.Place += 1
                if self.Sprite is not None:
                    self.Sprite.x = self.x
                    self.Sprite.y = self.y
            # If the instructions is done KILL the object
            else:
                self.Alive = False


def NextGen(size, BestObj=None):
    global Gen, Succeeded, AvailableMoves, SucceededGen
    if BestObj is None:  # If it the fist gen make an random 100 moves for each one
        global Objects
        Objects = [Object([random.randint(0, 3) for i in range(100)]) for i in range(size)]
        AvailableMoves = 100  # Set the Max move for the amount of moves in each object
    else:
        if BestObj.Finish:  # If at least one of the objects finished the cures don't add moves
            if not Succeeded:
                Succeeded = True
                SucceededGen = Gen
            AvailableMoves = len(BestObj.Moves)  # Set the max move form the best object
        Objects = [Object(BestObj.Moves, True)]  # Make a new gen but the best one from the last gen will stay
        if Gen % 15 == 0 and not Succeeded:
            AvailableMoves += 50
            Objects = [Object(BestObj.Moves + [random.randint(0, 3) for i in range(50)], True)]
            print(Objects[0].Moves)
        for i in range(size):
            Moves = [i for i in BestObj.Moves]  # Make the new gen from the basic of the best object from last gen
            for j in range(len(Moves)):
                if random.randint(0, MutationRate[0]) == 0:  # Mutate the move by a random chance
                    Moves[j] = random.randint(0, 3)
            if Gen % 15 == 0 and not Succeeded:  # if it the 5th gen at 50 more random moves
                # if it the 5th gen at 50 more random moves
                if not BestObj.Dead:
                    Moves = [i for i in BestObj.Moves]
                for k in range(50):
                    Moves.append(random.randint(0, 3))
            Objects.append(Object(Moves))
    Gen += 1  # Increase the ge num :D


# Object creation
Objects = []  # Array of objects


# Drawing The Screen
@window.event
def on_draw():
    window.clear()  # Clear the window
    background_batch.draw()  # Draw the background(B-background) and end point(F-front)
    for Blocker in Blockers:  # Draw the walls
        Blocker.Draw()
    gui_batch.draw()
    if Mode == 1:
        for Blocker in Blockers:  # Draw the walls again with the highlight
            if Blocker.Clicked or Blocker.Highlight:
                Blocker.Draw()
        if SelectedIconNum == 0:
            EditTexts[-1].draw()
            EditTexts[-2].draw()
        edit_batch.draw()
        if NewestBlocker is not None:
            NewestBlocker.Draw()
    else:
        for Run in RunTexts:
            Run.draw()
        objects_batch.draw()  # Draw the Object (The green one is in F and the yellow ones are in B)

    fps_display.draw()


# Mouse staff
@window.event
def on_mouse_motion(x, y, dx, dy):
    if Mode == 1 and SelectedIconNum == 0:
        Highlighted = False
        for Blocker in Blockers:
            Blocker.Highlight = False
            if Intersects(Blocker, x, y) and not Highlighted:
                Blocker.Highlight = True
                Highlighted = True
    pass


@window.event
def on_mouse_press(x, y, button, modifiers):
    if Mode == 1:
        global MouseBuzy
        if not MouseBuzy:
            if button & mouse.LEFT:
                # Creating a rectangle
                global SelectedIconNum
                if Intersects(EndPoint, x, y):
                    SelectedIconNum = 2
                    UpdateIcons()
                elif Intersects(StartPoint, x, y):
                    SelectedIconNum = 1
                    UpdateIcons()
                elif not SelectedIconNum == 0:
                    for Blocker in Blockers:
                        if Intersects(Blocker, x, y):
                            SelectedIconNum = 0
                            UpdateIcons()
                            break

                if SelectedIconNum == 0:
                    Test = True  # Trying to save unnecessary rectangles
                    for Blocker in Blockers:
                        if Intersects(Blocker, x, y):
                            Test = False
                    if Test:
                        global NewestBlocker, MoveLEFT
                        MoveLEFT = True
                        # print(x, y, "First")
                        NewestBlocker = Rectangle(x, y, 10, 10)
                        MouseBuzy = True
                        for Blocker in Blockers:
                            Blocker.Clicked = False
                            Blocker.Highlight = False
                        NewestBlocker.Clicked = True
                    else:
                        Pressed = False
                        for Blocker in Blockers:
                            Blocker.Clicked = False
                            if Blocker.Highlight and not Pressed:
                                Pressed = False
                                Blocker.Clicked = True
                    pass

                # Moving the start point
                elif SelectedIconNum == 1:
                    global MoveMIDDLE, StartPointOGxy
                    MoveMIDDLE = True
                    # print(x, y, "First")
                    StartPointOGxy = [StartPoint.x, StartPoint.y]
                    StartPoint.x = x - StartPoint.width / 2
                    StartPoint.y = y - StartPoint.height / 2
                    MouseBuzy = True

                # Moving the end point
                elif SelectedIconNum == 2:
                    global MoveRIGHT, EndPointOGxy
                    MoveRIGHT = True
                    # print(x, y, "First")
                    EndPointOGxy = [EndPoint.x, EndPoint.y]
                    EndPoint.x = x - EndPoint.width / 2
                    EndPoint.y = y - EndPoint.height / 2
                    MouseBuzy = True

                # Editing the Blockers
                elif SelectedIconNum == 0:
                    Pressed = False
                    for Blocker in Blockers:
                        Blocker.Clicked = False
                        if Blocker.Highlight and not Pressed:
                            Pressed = False
                            Blocker.Clicked = True

            if button & mouse.RIGHT:
                for Blocker in Blockers:
                    if Blocker.Clicked:
                        Blockers.remove(Blocker)
                        break
    else:
        RunTexts[-1].Update(x, y)
        RunTexts[-2].Update(x, y)
        RunTexts[-3].Update(x, y)
        if MutationRate[0] < 0:
            MutationRate[0] = 0
    pass


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if Mode == 1:
        if buttons & mouse.LEFT:
            if MoveLEFT:
                NewestBlocker.width = x - NewestBlocker.x
                NewestBlocker.height = y - NewestBlocker.y
                # print(x, y)
                pass

            if MoveMIDDLE:
                # print(x, y)
                StartPoint.x = x - StartPoint.width / 2
                StartPoint.y = y - StartPoint.height / 2
                if StartPoint.x < 0:
                    StartPoint.x = 0
                if StartPoint.x > window.width - StartPoint.width:
                    StartPoint.x = window.width - StartPoint.width
                if StartPoint.y < 0:
                    StartPoint.y = 0
                if StartPoint.y > window.height - 102 - StartPoint.height:
                    StartPoint.y = window.height - 102 - StartPoint.height
                pass

            if MoveRIGHT:
                # print(x, y)
                EndPoint.x = x - EndPoint.width / 2
                EndPoint.y = y - EndPoint.height / 2
                if EndPoint.x < 0:
                    EndPoint.x = 0
                if EndPoint.x > window.width - EndPoint.width:
                    EndPoint.x = window.width - EndPoint.width
                if EndPoint.y < 0:
                    EndPoint.y = 0
                if EndPoint.y > window.height - 102 - EndPoint.height:
                    EndPoint.y = window.height - 102 - EndPoint.height
                pass
    pass


@window.event
def on_mouse_release(x, y, button, modifiers):
    if Mode == 1:
        global MoveLEFT, MouseBuzy, MoveRIGHT, MoveMIDDLE, NewestBlocker
        if button & mouse.LEFT:
            if MoveLEFT:
                MouseBuzy = False
                MoveLEFT = False

                # Positioning the rectangle to positive numbers
                if NewestBlocker.x < x:
                    NewestBlocker.width = x - NewestBlocker.x
                else:
                    NewestBlocker.width = NewestBlocker.x - x
                    NewestBlocker.x = x

                if y < NewestBlocker.y:
                    NewestBlocker.height = NewestBlocker.y - y
                    NewestBlocker.y = y
                else:
                    NewestBlocker.height = y - NewestBlocker.y

                # Cutting the unnecessary parts of the rectangle, out side the screen
                if NewestBlocker.x < 0:
                    NewestBlocker.width += NewestBlocker.x
                    NewestBlocker.x = -5
                if NewestBlocker.x + NewestBlocker.width > window.width:
                    NewestBlocker.width = window.width - NewestBlocker.x+5
                if NewestBlocker.y < 0:
                    NewestBlocker.height += NewestBlocker.y
                    NewestBlocker.y = 0
                if NewestBlocker.y + NewestBlocker.height > window.height - 98:
                    NewestBlocker.height = window.height - 98 - NewestBlocker.y

                # Adding the wall to the array only if it is big enough and,
                # not intersecting with the start and the end points
                if not (Intersects(NewestBlocker, Object=EndPoint) or Intersects(NewestBlocker, Object=StartPoint)):
                    if NewestBlocker.width > 15 and NewestBlocker.height > 15:
                        # Check if the new blocker "eat" anther blocker and delete it
                        ToRemove = []
                        for Blocker in Blockers:
                            if not (
                                    Blocker.x < NewestBlocker.x or Blocker.y < NewestBlocker.y or NewestBlocker.x + NewestBlocker.width < Blocker.x + Blocker.width or NewestBlocker.y + NewestBlocker.height < Blocker.y + Blocker.height):
                                ToRemove.append(Blocker)  # List of eaten blockers
                                # print("ONE HAVE BEEEN EATEN")
                        for Blocker in ToRemove:
                            Blockers.remove(Blocker)
                        Blockers.append(NewestBlocker)
                # print(x, y, "Last", NewestBlocker.width, NewestBlocker.height)
                NewestBlocker = None
                pass

            if MoveMIDDLE:
                MouseBuzy = False
                MoveMIDDLE = False
                if StartPoint.x < 0:
                    StartPoint.x = 0
                if StartPoint.x > window.width - StartPoint.width:
                    StartPoint.x = window.width - StartPoint.width
                if StartPoint.y < 0:
                    StartPoint.y = 0
                if StartPoint.y > window.height - 102 - StartPoint.height:
                    StartPoint.y = window.height - 102 - StartPoint.height
                for Blocker in Blockers:
                    if Intersects(StartPoint, Object=Blocker):
                        StartPoint.x = StartPointOGxy[0]
                        StartPoint.y = StartPointOGxy[1]
                        break
                if Intersects(StartPoint, Object=EndPoint):
                    StartPoint.x = StartPointOGxy[0]
                    StartPoint.y = StartPointOGxy[1]

            if MoveRIGHT:
                MouseBuzy = False
                MoveRIGHT = False
                if EndPoint.x < 0:
                    EndPoint.x = 0
                if EndPoint.x > window.width - EndPoint.width:
                    EndPoint.x = window.width - EndPoint.width
                if EndPoint.y < 0:
                    EndPoint.y = 0
                if EndPoint.y > window.height - 102 - EndPoint.height:
                    EndPoint.y = window.height - 102 - EndPoint.height
                for Blocker in Blockers:
                    if Intersects(EndPoint, Object=Blocker):
                        EndPoint.x = EndPointOGxy[0]
                        EndPoint.y = EndPointOGxy[1]
                        break
                if Intersects(EndPoint, Object=StartPoint):
                    EndPoint.x = EndPointOGxy[0]
                    EndPoint.y = EndPointOGxy[1]
    else:
        RunTexts[-2].Update(x, y, False)
        RunTexts[-3].Update(x, y, False)
    pass


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if Mode == 1 and not MouseBuzy:
        global SelectedIconNum, SelectedIconDelay
        if SelectedIconDelay == 0:
            if scroll_y > 0:
                SelectedIconNum += 1
            else:
                SelectedIconNum -= 1
            if SelectedIconNum == -1:
                SelectedIconNum = 2
            elif SelectedIconNum == 3:
                SelectedIconNum = 0
            SelectedIconDelay = 0.2
            UpdateIcons()
    pass


# Updates
@window.event
def update(dt):
    global KeyDelay

    KeyDelay -= dt
    if KeyDelay < 0:
        KeyDelay = 0

    global Mode
    if Mode == 1:
        global SelectedIconDelay, Blockers
        SelectedIconDelay -= dt
        if SelectedIconDelay < 0:
            SelectedIconDelay = 0
        if keys[key.ENTER] and KeyDelay == 0:
            print("LETS GO!")
            Mode = 2
            ScoreTheBoard()
            NextGen(30)  # Make the first random gen
            KeyDelay = 1
            for Blocker in Blockers:  # Removing highlight and clicked from the blockers
                Blocker.Highlight = False
                Blocker.Clicked = False

        TextDis = []
        if SelectedIconNum == 3:
            Displied = None
            for Blocker in Blockers:
                if Blocker.Highlight:
                    Displied = Blocker
                if Blocker.Clicked:
                    Displied = Blocker
                    break
            if Displied is not None:
                TextDis = [Displied.width, Displied.height, Displied.x, Displied.y]
        elif SelectedIconNum == 1:
            TextDis = [StartPoint.width, StartPoint.height, StartPoint.x, StartPoint.y]
        elif SelectedIconNum == 2:
            TextDis = [EndPoint.width, EndPoint.height, EndPoint.x, EndPoint.y]
        elif SelectedIconNum == 0:
            if NewestBlocker is not None:
                # Positioning the rectangle to positive numbers
                TextDis = [NewestBlocker.width, NewestBlocker.height, NewestBlocker.x, NewestBlocker.y]
                if NewestBlocker.width < 0:
                    TextDis[0] *= -1
                    TextDis[2] = NewestBlocker.x - TextDis[0]
                if NewestBlocker.height < 0:
                    TextDis[1] *= -1
                    TextDis[3] = NewestBlocker.y - TextDis[1]
            else:
                Displied = None
                for Blocker in Blockers:
                    if Blocker.Highlight:
                        Displied = Blocker
                    if Blocker.Clicked:
                        Displied = Blocker
                        break
                if Displied is not None:
                    TextDis = [Displied.width, Displied.height, Displied.x, Displied.y]

        if TextDis:
            EditTexts[0].text = f"width - {TextDis[0]}"
            EditTexts[1].text = f"Height - {TextDis[1]}"
            EditTexts[2].text = f"X - {TextDis[2]}"
            EditTexts[3].text = f"Y - {TextDis[3]}"
        else:
            EditTexts[0].text = "width - None"
            EditTexts[1].text = "Height - None"
            EditTexts[2].text = "X - None"
            EditTexts[3].text = "Y - None"

    elif Mode == 2:
        global Objects, AvailableMoves, Gen, BestFitness, Succeeded, SucceededGen

        StillAlive = 0
        for Obj in Objects:
            Obj.Update()  # Update every object
            if Obj.Alive:  # If at least on object is alive
                StillAlive += 1

        # Text update
        RunTexts[0].text = f"Gen - {Gen}"
        if Succeeded:
            RunTexts[1].text = f"Progress - {int((BestFitness-1400)/5)}"
            RunTexts[0].text = f"Gen - {Gen}, F({SucceededGen})"
        else:
            RunTexts[1].text = f"Best Fitness - {BestFitness}"
        RunTexts[3].text = f"Moves Using - {AvailableMoves}"
        RunTexts[2].text = f"Objects Alive - {StillAlive}"
        RunTexts[4].text = f"Mutation Rate - 1/{MutationRate[0]+1}"

        if StillAlive == 0:  # If all Objects are dead/stopped
            print("Rip - Next gen is on! Gen Number ", Gen)
            BestScore = 0  # Best fitness from this gen
            BestObject = 0  # The number in the array of the object with the best fitness
            for i in range(len(Objects)):
                Objects[i].Fitness()  # Calculate the fitness for every object
                # if the object's fitness hit a new record, save it
                # * if the record is the same the a new one and don't continue if the one from last gen
                if Objects[i].FitnessScore >= BestScore:
                    BestScore = Objects[i].FitnessScore
                    BestObject = i
            print(BestScore, Objects[BestObject].FitnessScore, AvailableMoves, Objects[BestObject].Dead,
                  TheList[int(Objects[BestObject].y / 5)][int(Objects[BestObject].x / 5)],
                  int(Objects[BestObject].x / 5), int(Objects[BestObject].y / 5), Objects[BestObject].MLeft)
            NextGen(500, Objects[BestObject])  # Make a new gen with the best one from the current gen
            BestFitness = BestScore

        if keys[key.ENTER] and KeyDelay == 0:
            print("Job done :D")
            Mode = 1
            Objects = []
            Gen = 0
            Succeeded = False
            AvailableMoves = 0
            KeyDelay = 1
            BestFitness = 0
            SucceededGen = 0

        # Stating The Program


if __name__ == "__main__":
    # Starting the main loop
    pyglet.clock.schedule_interval(update, 1 / 999999999999)  # Loop speed
    pyglet.app.run()
