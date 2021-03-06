from game_library import Room, Item
from game_constants import *

# the candle is a special object
class Candle(Item):
    def __init__(self, name=OBJ_CANDLE):
        super (Candle, self).__init__(name)
        self.turns_left = 20
        self.lit = False

    def burn(self):
        if (self.lit):
            if (self.turns_left > 0):
                self.turns_left -= 1
            if (self.turns_left == 0):
                display("The candle burns out.")
                self.lit = False

    def use(self, player, others=[]):
        lighter = [x for x in others if x.name == OBJ_LIGHTER]
        if self.lit:
            if len(lighter) > 0:
                display("The candle is already lit!")
            else:
                self.lit = False
                display("You put out the candle.")
        else:
            if len(lighter) > 0:
                display("You use the lighter to light the candle.")
                self.lit = True
            else:
                display("What will you light the candle with?")

    def descr(self):
        if self.lit:
            return "The candle is lit."
        else:
            return "The candle is not lit."


candle = Candle()

# the spray can has only 3 uses
class SprayCan(Item):
    def __init__(self, name=OBJ_WD40):
        super (SprayCan, self).__init__(name)
        self.uses = 3

    def descr(self):
        if self.uses > 0:
            return "There is still something left in the spray can."
        else:
            "The spray can is empty."

    def use(self, player, others=[]):
        lighter = [x for x in others if x.name == OBJ_LIGHTER]
        if self.uses > 0:
            s = "You spray a little from the can."
            if len(lighter) > 0:
                s += " The spray catches fire as it passes the lighter, and you somehow manage not to burn off your own hand."
            display(s)
        else:
            display("You press the button on the can, but there seems to be no spray left.")
 
can_VC60 = SprayCan()

cleaver = Item(OBJ_CLEAVER)

key = Item(OBJ_KEY)

note = Item(OBJ_NOTE)
note.description = "It reads 'YZZYX'"

dresser = Item(OBJ_DRESSER)
dresser.is_portable = False
dresser.can_open = True
dresser.contents.append(note)
dresser.is_open = False
dresser.is_broken = False

grindstone = Item(OBJ_GRINDSTONE)
grindstone.is_portable = False
grindstone.description = "It looks a little worn, and very heavy."

lighter = Item(OBJ_LIGHTER)
lighter.description = "A small red cigarette lighter."


compass = Item(OBJ_COMPASS)
compass.description = "A tiny magnetic compass. It seems to be working."

#the window depends on where it is!
class Window(Item):
    def __init__(self, name=OBJ_WINDOW):
        super(Window, self).__init__(name)
        self.is_portable = False
        self.can_open = True

    def describe(self, player=None):
        display("You see a window. "+self.descr())

    def descr(self):
        word = "open"
        if not self.is_open:
            word = "closed"

        return "The window is "+word+"."

    def open(self, player=None):
        if self.current_room.name == RM_LIVING:
            self.is_open = True
            display("The window comes open, with some effort.")
        else:
            display("You nearly strain yourself trying to open the window, but it seems sealed shut.")

    def close(self, player=None):
        if self.is_open:
            display("You close the window.")
            self.is_open = False
        else:
            display("The window is already closed!")

    def use(self, player=None):
        if self.is_open:
            self.close(player)
        else:
            self.open(player)

class Oven(Item):
    def __init__(self, name=OBJ_OVEN):
        super(Oven, self).__init__(name)
        self.is_portable = False
        self.is_on = True

    def use(self, player=None):
        word = ''
        if self.is_on:
            self.is_on = False
            word = 'off'
        else:
            self.is_on = True
            word = 'on'
        display('The oven is now '+word+'.')

    
oven = Oven()
oven.contents.append(key)

door = Item(OBJ_DOOR)   
door.is_portable = False     

# set up the map! i was tempted to make some impossible topology... but why hurt myself?

kitchen = Room(RM_KITCHEN)
bathroom = Room(RM_BATH)
bedroom = Room(RM_BED)
closet = Room(RM_CLOSET)
attic = Room(RM_ATTIC)
foyer = Room(RM_FOYER)
living_room = Room(RM_LIVING)

living_room.exits = {DIR_SOUTH: kitchen, DIR_EAST: foyer}
living_room.place_object(candle)

kitchen.exits = {DIR_NORTH: living_room, DIR_EAST: bathroom}
kitchen.place_object(cleaver)
kitchen.place_object(grindstone)

bathroom.exits = {DIR_WEST: kitchen, DIR_NORTH: closet, DIR_EAST: bedroom}
bathroom.place_object(can_VC60)

closet.exits = {DIR_SOUTH: bathroom}
closet.place_object(compass)

bedroom.exits = {DIR_WEST: bathroom, DIR_NORTH: foyer}
bedroom.place_object(lighter)

foyer.exits = {DIR_WEST: living_room, DIR_SOUTH: bedroom, DIR_UP: attic}
foyer.place_object(dresser)
foyer.place_object(door) #TBD - interaction btwn dresser and door

attic.exits = {DIR_DOWN: foyer}


# now for the windows
windows = []
main_window = None

for room in [kitchen, bathroom, bedroom, living_room]:
    w = Window()
    room.place_object(w)
    if room.name == RM_LIVING:
        main_window = w

object_map = {}
for o in [key, candle, cleaver, dresser, grindstone, lighter, oven, can_VC60, note, compass, door, oven]:
    object_map[o.name]=o


