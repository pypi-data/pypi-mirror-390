#######################################################################################
# gui.py       Version 1.0     13-May-2025
# Taj Ballinger, Trevor Ritchie, Bill Manaris, and Dana Hughes
#
#######################################################################################
#
# [LICENSING GOES HERE]
#
#######################################################################################
#
#
#######################################################################################
import PySide6.QtWidgets as _QtWidgets
import PySide6.QtGui as _QtGui
import PySide6.QtCore as _QtCore
import PySide6.QtOpenGLWidgets as _QtOpenGL
import numpy as np
#######################################################################################

### QT
# PySide6 is a Python binding for Qt, a popular C++ framework for GUI
# development.  QApplication is the heart of this framework.

# In a typical GUI, the QApplication is created early in the main script,
#  and its .exec() method is called at the end of the program to start
#  the event loop.
# However, we want to allow the user to run and execute scripts dynamically,
#  so we can't call .exec() without occupying the main thread.  Fortunately,
#  Qt has an alternative event loop that runs in a separate thread, but only
#  while the Python interpreter is running.
# To hide the Qt event loop from the user, and allow dynamic scripting, we
#  require the user to run scripts with the -i option, which enables this
#  secondary, hidden event loop, and always makes the interpreter available.

if "_QTAPP_" not in globals():
   _QTAPP_ = None  # claim global variable for QApplication

if "_DISPLAYS_" not in globals():
   _DISPLAYS_ = []  # track all displays created


def _ensureApp():
   """Guarantee that a QApplication is running."""
   # this function is called whenever we create a new display,
   # or queue a function that modifies the display (or the display's items)
   global _QTAPP_
   if _QTAPP_ is None:
      # try to find an existing QApplication instance
      _QTAPP_ = _QtWidgets.QApplication.instance()
      if _QTAPP_ is None:
         # if no existing QApplication, create a new instance
         _QTAPP_ = _QtWidgets.QApplication([])
         _QTAPP_.setApplicationName("CreativePython")
         _QTAPP_.setStyleSheet(  # force ToolTip font color to black
            """
            QToolTip {
               color: black;
            }
            """)

_ensureApp()

#######################################################################################
# Virtual Key Constants
#######################################################################################
# Java 8 VK codes            PySide6 (Qt) key codes
VK_0                         = _QtCore.Qt.Key.Key_0
VK_1                         = _QtCore.Qt.Key.Key_1
VK_2                         = _QtCore.Qt.Key.Key_2
VK_3                         = _QtCore.Qt.Key.Key_3
VK_4                         = _QtCore.Qt.Key.Key_4
VK_5                         = _QtCore.Qt.Key.Key_5
VK_6                         = _QtCore.Qt.Key.Key_6
VK_7                         = _QtCore.Qt.Key.Key_7
VK_8                         = _QtCore.Qt.Key.Key_8
VK_9                         = _QtCore.Qt.Key.Key_9

VK_A                         = _QtCore.Qt.Key.Key_A
VK_B                         = _QtCore.Qt.Key.Key_B
VK_C                         = _QtCore.Qt.Key.Key_C
VK_D                         = _QtCore.Qt.Key.Key_D
VK_E                         = _QtCore.Qt.Key.Key_E
VK_F                         = _QtCore.Qt.Key.Key_F
VK_G                         = _QtCore.Qt.Key.Key_G
VK_H                         = _QtCore.Qt.Key.Key_H
VK_I                         = _QtCore.Qt.Key.Key_I
VK_J                         = _QtCore.Qt.Key.Key_J
VK_K                         = _QtCore.Qt.Key.Key_K
VK_L                         = _QtCore.Qt.Key.Key_L
VK_M                         = _QtCore.Qt.Key.Key_M
VK_N                         = _QtCore.Qt.Key.Key_N
VK_O                         = _QtCore.Qt.Key.Key_O
VK_P                         = _QtCore.Qt.Key.Key_P
VK_Q                         = _QtCore.Qt.Key.Key_Q
VK_R                         = _QtCore.Qt.Key.Key_R
VK_S                         = _QtCore.Qt.Key.Key_S
VK_T                         = _QtCore.Qt.Key.Key_T
VK_U                         = _QtCore.Qt.Key.Key_U
VK_V                         = _QtCore.Qt.Key.Key_V
VK_W                         = _QtCore.Qt.Key.Key_W
VK_X                         = _QtCore.Qt.Key.Key_X
VK_Y                         = _QtCore.Qt.Key.Key_Y
VK_Z                         = _QtCore.Qt.Key.Key_Z

VK_NUMPAD0                   = _QtCore.Qt.Key.Key_0
VK_NUMPAD1                   = _QtCore.Qt.Key.Key_1
VK_NUMPAD2                   = _QtCore.Qt.Key.Key_2
VK_NUMPAD3                   = _QtCore.Qt.Key.Key_3
VK_NUMPAD4                   = _QtCore.Qt.Key.Key_4
VK_NUMPAD5                   = _QtCore.Qt.Key.Key_5
VK_NUMPAD6                   = _QtCore.Qt.Key.Key_6
VK_NUMPAD7                   = _QtCore.Qt.Key.Key_7
VK_NUMPAD8                   = _QtCore.Qt.Key.Key_8
VK_NUMPAD9                   = _QtCore.Qt.Key.Key_9

VK_F1                        = _QtCore.Qt.Key.Key_F1
VK_F2                        = _QtCore.Qt.Key.Key_F2
VK_F3                        = _QtCore.Qt.Key.Key_F3
VK_F4                        = _QtCore.Qt.Key.Key_F4
VK_F5                        = _QtCore.Qt.Key.Key_F5
VK_F6                        = _QtCore.Qt.Key.Key_F6
VK_F7                        = _QtCore.Qt.Key.Key_F7
VK_F8                        = _QtCore.Qt.Key.Key_F8
VK_F9                        = _QtCore.Qt.Key.Key_F9
VK_F10                       = _QtCore.Qt.Key.Key_F10
VK_F11                       = _QtCore.Qt.Key.Key_F11
VK_F12                       = _QtCore.Qt.Key.Key_F12

VK_ESCAPE                    = _QtCore.Qt.Key.Key_Escape
VK_TAB                       = _QtCore.Qt.Key.Key_Tab
VK_CAPS_LOCK                 = _QtCore.Qt.Key.Key_CapsLock
VK_SHIFT                     = _QtCore.Qt.Key.Key_Shift
VK_CONTROL                   = _QtCore.Qt.Key.Key_Control
VK_ALT                       = _QtCore.Qt.Key.Key_Alt
VK_SPACE                     = _QtCore.Qt.Key.Key_Space
VK_ENTER                     = _QtCore.Qt.Key.Key_Return
VK_BACK_SPACE                = _QtCore.Qt.Key.Key_Backspace
VK_DELETE                    = _QtCore.Qt.Key.Key_Delete
VK_HOME                      = _QtCore.Qt.Key.Key_Home
VK_END                       = _QtCore.Qt.Key.Key_End
VK_PAGE_UP                   = _QtCore.Qt.Key.Key_PageUp
VK_PAGE_DOWN                 = _QtCore.Qt.Key.Key_PageDown
VK_UP                        = _QtCore.Qt.Key.Key_Up
VK_DOWN                      = _QtCore.Qt.Key.Key_Down
VK_LEFT                      = _QtCore.Qt.Key.Key_Left
VK_RIGHT                     = _QtCore.Qt.Key.Key_Right

VK_INSERT                    = _QtCore.Qt.Key.Key_Insert
VK_PAUSE                     = _QtCore.Qt.Key.Key_Pause
VK_PRINTSCREEN               = _QtCore.Qt.Key.Key_Print
VK_SCROLL_LOCK               = _QtCore.Qt.Key.Key_ScrollLock
VK_NUM_LOCK                  = _QtCore.Qt.Key.Key_NumLock
VK_SEMICOLON                 = _QtCore.Qt.Key.Key_Semicolon
VK_EQUALS                    = _QtCore.Qt.Key.Key_Equal
VK_COMMA                     = _QtCore.Qt.Key.Key_Comma
VK_MINUS                     = _QtCore.Qt.Key.Key_Minus
VK_PERIOD                    = _QtCore.Qt.Key.Key_Period
VK_SLASH                     = _QtCore.Qt.Key.Key_Slash
VK_BACK_SLASH                = _QtCore.Qt.Key.Key_Backslash
VK_OPEN_BRACKET              = _QtCore.Qt.Key.Key_BracketLeft
VK_CLOSE_BRACKET             = _QtCore.Qt.Key.Key_BracketRight
VK_QUOTE                     = _QtCore.Qt.Key.Key_Apostrophe
VK_BACK_QUOTE                = _QtCore.Qt.Key.Key_QuoteLeft

# Arc Constants (in degrees)
PI      = 180
HALF_PI = 90
TWO_PI  = 360

# Arc Style Constants
PIE   = 0
OPEN  = 1
CHORD = 2

# Label Constants
LEFT   = _QtCore.Qt.AlignmentFlag.AlignLeft
CENTER = _QtCore.Qt.AlignmentFlag.AlignCenter
RIGHT  = _QtCore.Qt.AlignmentFlag.AlignRight

# Widget Orientation Constants
HORIZONTAL = _QtCore.Qt.Orientation.Horizontal
VERTICAL   = _QtCore.Qt.Orientation.Vertical

#######################################################################################
# Color
#######################################################################################
class Color:
   """
   Color class for creating and manipulating colors.

   This class provides functionality for creating and manipulating RGB colors.
   It mirrors Java's Color class functionality from JythonMusic, including:
   - RGB color creation with optional alpha
   - Color constants (RED, BLUE, etc.)
   - Color manipulation (brighter, darker)
   - Conversion to various formats
   """
   def __init__(self, red, green, blue, alpha=255):
      # store color values as 0-255 integers
      self.red   = int(red)
      self.green = int(green)
      self.blue  = int(blue)
      self.alpha = int(alpha)

   def __str__(self):
      return f'Color(red = {self.getRed()}, green = {self.getGreen()}, blue = {self.getBlue()}, alpha = {self.getAlpha()})'

   def __repr__(self):
      return str(self)

   def getRed(self):
      """
      Returns the red value of the color.
      """
      return self.red

   def getGreen(self):
      """
      Returns the green value of the color.
      """
      return self.green

   def getBlue(self):
      """
      Returns the blue value of the color.
      """
      return self.blue

   def getAlpha(self):
      """
      Returns the alpha value of the color.
      """
      return self.alpha

   def getRGB(self):
      """
      Returns the color as a tuple of RGB values.
      """
      return (self.red, self.green, self.blue)

   def getRGBA(self):
      """
      Returns the color as a tuple of RGBA values.
      """
      return (self.red, self.green, self.blue, self.alpha)

   def getHex(self):
      """
      Returns the color as a hex string.
      """
      hex = f'#{self.red:02x}{self.green:02x}{self.blue:02x}'  # base hex string
      if self.alpha != 255:
         hex += f'{self.alpha:02x}'  # add alpha if not fully opaque
      return hex

   def brighter(self):
      # increase each component by 10% while keeping within 0-255
      return Color(
         min(255, int(self.red * 1.1)),
         min(255, int(self.green * 1.1)),
         min(255, int(self.blue * 1.1)),
         self.alpha
      )

   def darker(self):
      # decrease each component by 10% while keeping within 0-255
      return Color(
         max(0, int(self.red * 0.9)),
         max(0, int(self.green * 0.9)),
         max(0, int(self.blue * 0.9)),
         self.alpha
      )

   @staticmethod
   def _fromQColor(qColor):
      """
      Creates a new Color object from a QColor.
      """
      r = qColor.red()
      g = qColor.blue()
      b = qColor.red()
      a = qColor.alpha()
      return Color(r, g, b, a)


# preset colors defined as global properties, mirroring JColor syntax
Color.BLACK      = Color(  0,   0,   0)
Color.BLUE       = Color(  0,   0, 255)
Color.CYAN       = Color(  0, 255, 255)
Color.DARK_GRAY  = Color( 44,  44,  44)
Color.GRAY       = Color(128, 128, 128)
Color.GREEN      = Color(  0, 255,   0)
Color.LIGHT_GRAY = Color(211, 211, 211)
Color.MAGENTA    = Color(255,   0, 255)
Color.ORANGE     = Color(255, 165,   0)
Color.PINK       = Color(255, 192, 203)
Color.RED        = Color(255,   0,   0)
Color.WHITE      = Color(255, 255, 255)
Color.YELLOW     = Color(255, 255,   0)
Color.CLEAR      = Color(  0,   0,   0,   0)

#######################################################################################
# Color gradient
#
# A color gradient is a smooth color progression from one color to another,
# which creates the illusion of continuity between the two color extremes.
#
# The following auxiliary function may be used used to create a color gradient.
# This function returns a list of RGB colors (i.e., a list of lists) starting with color1
# (e.g., [0, 0, 0]) and ending (without including) color2 (e.g., [251, 147, 14], which is orange).
# The number of steps equals the number of colors in the list returned.
#
# For example, the following creates a gradient list of 12 colors:
#
# >>> colorGradient([0, 0, 0], [251, 147, 14], 12)
# [[0, 0, 0], [20, 12, 1], [41, 24, 2], [62, 36, 3], [83, 49, 4], [104, 61, 5], [125, 73, 7],
# [146, 85, 8], [167, 98, 9], [188, 110, 10], [209, 122, 11], [230, 134, 12]]
#
# Notice how the above excludes the final color (i.e.,  [251, 147, 14]).  This allows to
# create composite gradients (without duplication of colors).  For example, the following
#
# black = [0, 0, 0]         # RGB values for black
# orange = [251, 147, 14]   # RGB values for orange
# white = [255, 255, 255]   # RGB values for white
#
# cg = colorGradient(black, orange, 12) + colorGradient(orange, white, 12) + [white]
#
# creates a list of gradient colors from black to orange, and from orange to white.
# Notice how the final color, white, has to be included separately (using list concatenation).
# Now, gc contains a total of 25 unique gradient colors.
#
# For convenience, colorGradient() also works with Color objects, in which case
# it returns a list of Color objects.
#
#######################################################################################
def colorGradient(color1, color2, steps):
   """
   Returns a list of RGB colors creating a "smooth" gradient between 'color1'
   and 'color2'.  The amount of smoothness is determined by 'steps', which specifies
   how many intermediate colors to create. The result includes 'color1' but not
   'color2' to allow for connecting one gradient to another (without duplication
   of colors).
   """
   gradientList = []   # holds RGB lists of individual gradient colors

   # check if using Color objects
   if isinstance(color1, Color) and isinstance(color2, Color):
      # extract RGB values
      red1, green1, blue1 = color1.getRed(), color1.getGreen(), color1.getBlue()
      red2, green2, blue2 = color2.getRed(), color2.getGreen(), color2.getBlue()

   else:  # otherwise, assume RGB list
      # extract RGB values
      red1, green1, blue1 = color1
      red2, green2, blue2 = color2

   # find difference between color extremes
   differenceR = red2   - red1     # R component
   differenceG = green2 - green1   # G component
   differenceB = blue2  - blue1    # B component

   # interpolate RGB values between extremes
   for i in range(steps):
      gradientR = red1   + i * differenceR / steps
      gradientG = green1 + i * differenceG / steps
      gradientB = blue1  + i * differenceB / steps

      # ensure color values are integers
      gradientList.append([int(gradientR), int(gradientG), int(gradientB)])
   # now, gradient list contains all the intermediate colors, including color1
   # but not color2

   # if input was Color objects (e.g., Color.RED), return Color objects
   # otherwise, keep as RGB lists (e.g., [255, 0, 0]
   if isinstance(color1, Color):
      gradientList = [Color(rgb[0], rgb[1], rgb[2]) for rgb in gradientList]

   return gradientList


########################################################################################
# Font
########################################################################################
class Font:
   PLAIN      = (_QtGui.QFont.Weight.Normal, False)
   BOLD       = (_QtGui.QFont.Weight.Bold,   False)
   ITALIC     = (_QtGui.QFont.Weight.Normal, True)
   BOLDITALIC = (_QtGui.QFont.Weight.Bold,   True)

   def __init__(self, fontName, style=PLAIN, fontSize=-1):
      self._name  = fontName
      self._style = style
      self._size  = fontSize

   def __str__(self):
      return f'Font(fontName = "{self.getName()}", style = {self.getStyle()}, fontSize = {self.getFontSize()})'

   def __repr__(self):
      return str(self)

   def _getQFont(self):
      qFont = _QtGui.QFont(self._name, self._size)
      qFont.setWeight(self._style[0])
      qFont.setItalic(self._style[1])
      return qFont

   def getName(self):
      return self._name

   def getStyle(self):
      return self._style

   def getFontSize(self):
      return self._size


#######################################################################################
# Event Dispatcher
#######################################################################################
class Event():
   """
   Generic Event class for storing relevant event data.
   """
   def __init__(self, type="", *args):
      self.type    = str(type)
      self.args    = list(args)
      self.handled = False

   def __str__(self):
      return f'Event(type = {self.type}, args = {self.args})'


class EventDispatcher(_QtCore.QObject):
   """
   EventDispatchers attach to Displays, connecting Qt's events to JythonMusic events.
      QT EVENTS    -> JYTHONMUSIC EVENTS
      MousePress   -> onMouseDown
      MouseRelease -> onMouseUp + onMouseClick (if mouse didn't move)
      MouseMove    -> onMouseMove or onMouseDrag (if mouse is pressed)
      MouseEnter   -> onMouseEnter
      MouseLeave   -> onMouseExit
      KeyPress     -> onKeyDown + onKeyType
      KeyRelease   -> onKeyUp

   When an event occurs, the Display always sees the event first.
   Mouse events deliver to the topmost item at the event's position, that has a corresponding callback.
   Key events deliver to the most recent, topmost item that a mouseDown event occurred at
      ("the last item you clicked on").
   """

   def __init__(self, owner):
      super().__init__()
      self.owner           = owner  # Group or Display this dispatcher listens for
      self.draggingItem    = None   # last item mouseDown was over (cleared on mouseUp)
      self.lastMouseDown   = None   # last mouseDown coordinates (cleared on mouseUp)
      self.lastMouseMove   = None   # last known mouse movement/position
      self.itemsUnderMouse = set()  # item set under last known mouse position (always on)
      self.moveThreshold   = 5      # max distance for a mouseClick to trigger

      if isinstance(owner, Display):
         self.owner._view.viewport().installEventFilter(self)  # redirect mouse events
         self.owner._view.installEventFilter(self)             # redirect key events

      # EventDispatcher keeps track of its owner's items that have event callbacks.
      # Each list corresponds to a type of event, sorted by z-order.
      # Lists are updated when an item is added or removed from the owner,
      # or when a new event callback is registered to an item in the group.
      # Maintaining these lists significantly speeds up event processing by reducing
      # the items searched to just the items who can actually handle the current event.
      self.eventHandlers = {
         'mouseDown':    [],
         'mouseUp':      [],
         'mouseClick':   [],
         'mouseMove':    [],
         'mouseDrag':    [],
         'mouseEnter':   [],
         'mouseExit':    [],
         'keyType':      [],
         'keyDown':      [],
         'keyUp':        []
      }

      # For ease of use, each qEvent type we listen for is paired with its internal handler
      self._qMouseEventDict = {
         _QtCore.QEvent.Type.MouseButtonPress   : self._handleQMousePress,
         _QtCore.QEvent.Type.MouseButtonRelease : self._handleQMouseRelease,
         _QtCore.QEvent.Type.MouseMove          : self._handleQMouseMove,
         _QtCore.QEvent.Type.Enter              : self._handleQMouseEnter,
         _QtCore.QEvent.Type.Leave              : self._handleQMouseLeave
      }
      self._qKeyEventDict = {
         _QtCore.QEvent.Type.KeyPress           : self._handleQKeyPress,
         _QtCore.QEvent.Type.KeyRelease         : self._handleQKeyRelease
      }

   def add(self, object):
      """
      Adds an Interactable to each listener list they have a callback for.
      The item is inserted into each list according to its z-order on the display.
      """
      if not isinstance(object, Interactable):  # do some basic error checking
         raise TypeError(f'EventDispatcher.add(): object should be an Interactable (it was {type(object)}).')
      eventList   = object._callbackFunctions.keys()  # list of object's registered events
      ownerItems  = self.owner._itemList              # list of owner's objects
      objectIndex = ownerItems.index(object)          # object index in owner's z-order

      for eventType in eventList:                        # for each event type,
         if eventType in self.eventHandlers.keys():      # ...that is a known event type,
            handlerList = self.eventHandlers[eventType]  # ...get appropriate handler list

            if object not in handlerList:  # skip if this callback is already registered
               inserted = False

               if objectIndex == 0:        # object is on top, so insert in front
                  handlerList.insert(0, object)
                  inserted = True

               else:                       # otherwise, scan for its position
                  i = 0
                  while not inserted and i < len(handlerList) - 1:
                     neighbor = handlerList[i]
                     neighborIndex = self.owner.getOrder(neighbor)
                     if objectIndex < neighborIndex:
                        handlerList.insert(i, object)  # insert on top of neighbor
                        inserted = True
                     i = i + 1

               if not inserted:            # if we couldn't find a position, add to bottom
                  handlerList.append(object)

   def remove(self, object):
      """
      Removes the object from each listener list they're in.
      """
      for eventType in self.eventHandlers.keys():         # for each known event type,
         if object in self.eventHandlers[eventType]:      # ... if object is registered,
            self.eventHandlers[eventType].remove(object)  # ... remove it from corresponding handler list

   def eventFilter(self, object, qEvent):
      """
      eventFilter is a Qt-defined method that implements our custom event handler logic.
      While attached to a Display, we receive key events from _view, and mouse events from
      the _view's viewport.  (Mouse events from _view don't always have coordinates.)
      eventFilter()'s job is to convert qEvents into corresponding CreativePython events.
      After that, deliverEvent() will handle propagating that event to our items.
      """
      eventHandled = False

      ##### MOUSE EVENTS #####
      if object == self.owner._view.viewport():  # event from viewport, so check for mouse events
         if qEvent.type() in self._qMouseEventDict.keys():  # mouse event, so we need (x,y) coordinates
            if hasattr(qEvent, 'position') and callable(qEvent.position):
               x = int(qEvent.position().x())   # use qEvent coordinates, if possible
               y = int(qEvent.position().y())
            elif self.lastMouseMove is not None:
               x = self.lastMouseMove[0]        # fallback to last known position
               y = self.lastMouseMove[1]
            else:
               x = 0                            # if no mouse movement, use origin
               y = 0

            handlerFunction = self._qMouseEventDict[qEvent.type()]
            eventHandled    = handlerFunction(x, y)  # deliver mouse event

      ##### KEY EVENTS #####
      elif object == self.owner._view:  # event from _view, so check for key events
         if qEvent.type() in self._qKeyEventDict.keys():  # key event, so we need the key and character
            if not qEvent.isAutoRepeat():               # skip repeated keys
               key = qEvent.key()       # key code
               if qEvent.text():        # not all keys have a character (e.g. Shift)
                  char = qEvent.text()
               else:
                  char = ""
               handlerFunction = self._qKeyEventDict[qEvent.type()]
               eventHandled    = handlerFunction(key, char)  # deliver key event

      return eventHandled

   def deliverEvent(self, event, candidateList=None):
      """
      Tries to deliver events to this EventDispatcher's items.
      If candidateList is specified, we deliver to that list instead.
      We stop looking early after the event is handled.
      """
      if event.type in self.eventHandlers.keys() and not event.handled:
         if candidateList is None:
            candidateList = self.eventHandlers[event.type]  # get event type's candidates, if needed

         if event.type.startswith('mouse'):
            # mouse events only deliver to items at the event location
            x, y = event.args
            i = 0

            while not event.handled and (i < len(candidateList)):
               item = candidateList[i]
               if item.contains(x, y):
                  if isinstance(item, Group):
                     item._eventDispatcher.deliverEvent(event)  # propagate down to Group children
                  item._receiveEvent(event)  # deliver to item, whether the event was handled or not
               i = i + 1

         else:
            # key events can deliver to any item, regardless of location
            # (we still stop looking after the event is handled!)
            i = 0
            while not event.handled and (i < len(candidateList)):
               item = candidateList[i]
               if isinstance(item, Group):
                  item._eventDispatcher.deliverEvent(event)  # propagate down to Group children
               item._receiveEvent(event)  # deliver to item, whether the event was handled or not
               i = i + 1

   def _handleQMousePress(self, x, y):
      """
      Generates mouseDown events and propagates them.
      """
      self.lastMouseDown = (x, y)  # store mouse down position

      i = 0  # find the topmost item with a mouseDrag callback at event coordinates
      while self.draggingItem is None and i < len(self.eventHandlers['mouseDrag']):
         item = self.eventHandlers['mouseDrag'][i]
         if item.contains(x, y):
            self.draggingItem = item  # store topmost item
         else:
            i = i + 1

      ##### MOUSE DOWN #####
      mouseDownEvent = Event('mouseDown', x, y)  # generate event
      self.deliverEvent(mouseDownEvent)          # send to items
      self.owner._receiveEvent(mouseDownEvent)   # send to owner

      return mouseDownEvent.handled

   def _handleQMouseRelease(self, x, y):
      """
      Generates mouseUp and mouseClick events and propagates them.
      mouseUp    events happen whenever the mouse is released.
      mouseClick events only happen when the mouse is released close to where it was pressed.
      """
      isMouseClick = False
      if self.lastMouseDown is not None:       # is the mouse down right now?
         dx = abs(x - self.lastMouseDown[0])   # yes, calculate how far mouse moved since it was pressed
         dy = abs(y - self.lastMouseDown[1])
         withinX = (dx <= self.moveThreshold)
         withinY = (dy <= self.moveThreshold)
         if withinX and withinY:               # is the movement under our moveThreshold?
            isMouseClick = True                # yes, this is also a mouseClick

      self.lastMouseDown = None  # clear mouse down position
      self.draggingItem  = None  # clear dragging item

      ##### MOUSE UP #####
      mouseUpEvent = Event('mouseUp', x, y)   # generate event
      self.deliverEvent(mouseUpEvent)         # send to items
      self.owner._receiveEvent(mouseUpEvent)  # send to owner

      ##### MOUSE CLICK #####
      if isMouseClick:
         mouseClickEvent = Event('mouseClick', x, y)  # generate event
         self.deliverEvent(mouseClickEvent)           # send to items
         self.owner._receiveEvent(mouseClickEvent)    # send to owner

      return mouseUpEvent.handled

   def _handleQMouseMove(self, x, y):
      """
      Generates mouseMove, mouseDrag, mouseEnter, and mouseExit events and propagates them.
      mouseMove  events happen whenever the mouse moves, unless the mouse is held down.
      mouseDrag  events happen whenever the mouse moves while the mouse is held down.
      mouseEnter events happen whenever the mouse enters the boundaries of an object.
      mouseExit  events happen whenever the mouse exits the boundaries of an object.
      * mouseEnter and mouseExit events for Displays are their own qEvent type.
      """
      self.lastMouseMove = (x, y)          # store current mouse position
      self._updateCoordinateTooltip(x, y)  # refresh tooltip coordinates (if needed)

      ##### MOUSE MOVE #####
      if self.lastMouseDown is None:       # mouse is up, so this is a mouseMove event
         mouseMoveEvent = Event('mouseMove', x, y)  # generate event
         self.deliverEvent(mouseMoveEvent)          # send to items
         self.owner._receiveEvent(mouseMoveEvent)   # send to owner

      ##### MOUSE DRAG #####
      else:                                # mouse is down, so this is a mouseDrag event
         mouseMoveEvent = Event('mouseDrag', x, y)  # generate event
         if self.draggingItem is not None:          # only send to first item under mouse
            self.draggingItem._receiveEvent(mouseMoveEvent)
         self.owner._receiveEvent(mouseMoveEvent)   # send to owner

      ##### MOUSE ENTER/EXIT #####
      # we use sets for efficient difference calculations
      # the caveat is that sets aren't ordered, so we can't guarantee z-order for enter/exit events
      # NOTE: contains() uses a spatial hit test, but this search is still expensive with large Displays.
      #  consider adding a disable toggle?
      itemsUnderMouseNow = set()
      for item in self.owner._itemList:
         if item.contains(x, y):
            itemsUnderMouseNow.add(item)

      movedIntoSet  = itemsUnderMouseNow.difference(self.itemsUnderMouse)
      movedOutOfSet = self.itemsUnderMouse.difference(itemsUnderMouseNow)
      self.itemsUnderMouse = itemsUnderMouseNow

      enterHandlers = set(self.eventHandlers['mouseEnter']).intersection(movedIntoSet)
      exitHandlers  = set(self.eventHandlers['mouseExit']).intersection(movedOutOfSet)

      ##### MOUSE ENTER #####
      mouseEnterEvent = Event('mouseEnter', x, y)  # generate event
      for item in list(enterHandlers):             # send to ALL items, instead of just one
         item._receiveEvent(mouseEnterEvent)

      ##### MOUSE EXIT #####
      mouseExitEvent = Event('mouseExit', x, y)    # generate event
      for item in list(exitHandlers):              # send to ALL items, instead of just one
         item._receiveEvent(mouseExitEvent)

      return mouseMoveEvent.handled

   def _handleQMouseEnter(self, x, y):
      """
      Generates mouseEnter events and propagates them to the Display.
      This event can only trigger from a Display's event dispatcher,
      so it can only deliver events to a Display.
      """
      mouseEnterEvent = Event("mouseEnter", x, y)
      self.owner._receiveEvent(mouseEnterEvent)

      return mouseEnterEvent.handled

   def _handleQMouseLeave(self, x, y):
      """
      Generates mouseExit events and propagates them to the Display.
      This event can only trigger from a Display's event dispatcher,
      so it can only deliver events to a Display.
      """
      mouseExitEvent = Event("mouseExit", x, y)
      self.owner._receiveEvent(mouseExitEvent)

      return mouseExitEvent.handled

   def _handleQKeyPress(self, key, char):
      """
      Generates keyDown and keyType events and propagates them.
      keyDown uses the numeric code for the pressed key.
      keyType uses the typed character for the pressed key (if any).
      """
      ##### KEY DOWN #####
      keyDownEvent = Event("keyDown", key)        # generate event
      for item in self.eventHandlers['keyDown']:  # send to ALL items, instead of just one
         item._receiveEvent(keyDownEvent)
      self.owner._receiveEvent(keyDownEvent)      # send to owner

      ##### KEY TYPE #####
      keyTypeEvent = Event("keyType", char)       # generate event
      for item in self.eventHandlers['keyType']:  # send to ALL items, instead of just one
         item._receiveEvent(keyTypeEvent)
      self.owner._receiveEvent(keyTypeEvent)      # send to owner

      return keyDownEvent.handled or keyTypeEvent.handled

   def _handleQKeyRelease(self, key, char):
      """
      Generates keyUp events and propagates them.
      keyUp uses the numeric code for the pressed key.
      """
      ##### KEY DOWN #####
      keyUpEvent = Event("keyUp", key)          # generate event
      for item in self.eventHandlers['keyUp']:  # send to ALL items, instead of just one
         item._receiveEvent(keyUpEvent)
      self.owner._receiveEvent(keyUpEvent)      # send to owner

      return keyUpEvent.handled

   def _updateCoordinateTooltip(self, x, y):
      """
      Implementation of Display's showCoordinates method.
      Whenever this triggers, manually update the display's tooltip to show the current coordinates.
      """
      if self.owner._showCoordinates:  # if showing coordinates
         # override any set tooltips to show mouse coordinates instead
         # QToolTips have a delay before appearing, and automatically disappear
         #   after a short time, so we force the tooltip to show immediately,
         #   and refresh it whenever the mouse moves
         globalPos   = self.owner._view.mapToGlobal(_QtCore.QPoint(x, y))
         toolTipText = f"({x}, {y})"
         _QtWidgets.QToolTip.showText(globalPos, toolTipText, self.owner._view, self.owner._view.rect(), 10000)


#######################################################################################
# Interactable
#######################################################################################
class Interactable:
   """
   Base abstract class for interactive objects.
   Interactables can track callback functions for keyboard, mouse, and display events.
   """
   def __init__(self):
      self._parent = None
      self._callbackFunctions = {}

   def __str__( self ):
      return f'Interactable()'

   def __repr__( self ):
      return str(self)

   def _receiveEvent(self, event):
      """
      This method is called by the Display when an event occurs.
      It filters events and calls the corresponding callback function,
      if it has been defined.
      """
      if event.type in self._callbackFunctions:          # is event defined?
         callback = self._callbackFunctions[event.type]  # yes, get callback
         if callable(callback):                          # is callback callable?
            callback(*event.args)                        # yes, call it with args
            event.handled = True                         # mark event as handled

   def _hasCallback(self, type=""):
      return self._callbackFunctions.get(type) is not None

   def _registerCallback(self):
      if isinstance(self._parent, (Display, Group)):  # if this object is in/on Display or Group,
         self._parent._eventDispatcher.add(self)  # register event with event dispatcher

   def onMouseClick(self, function):
      """
      Set callback for mouse click events (click means both press and release).
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse click.
      """
      self._callbackFunctions['mouseClick'] = function
      self._registerCallback()

   def onMouseDown(self, function):
      """
      Set callback for mouse button press events.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse press.
      """
      self._callbackFunctions['mouseDown'] = function
      self._registerCallback()

   def onMouseUp(self, function):
      """
      Set callback for mouse button release events.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse release.
      """
      self._callbackFunctions['mouseUp'] = function
      self._registerCallback()

   def onMouseMove(self, function):
      """
      Set callback for mouse movement events within this object.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse movement.
      """
      self._callbackFunctions['mouseMove'] = function
      self._registerCallback()

   def onMouseDrag(self, function):
      """
      Set callback for mouse drag events within this object.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse movement.
      """
      self._callbackFunctions['mouseDrag'] = function
      self._registerCallback()

   def onMouseEnter(self, function):
      """
      Set callback for when mouse enters this object's bounds.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of where the mouse entered.
      """
      self._callbackFunctions['mouseEnter'] = function
      self._registerCallback()

   def onMouseExit(self, function):
      """
      Set callback for when mouse exits this object's bounds.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of where the mouse exited.
      """
      self._callbackFunctions['mouseExit'] = function
      self._registerCallback()

   def onKeyType(self, function):
      """
      Set callback for key type events.
      The callback function should accept one parameter (a character),
      which is the character typed.
      """
      self._callbackFunctions['keyType'] = function
      self._registerCallback()

   def onKeyDown(self, function):
      """
      Set callback for key press events.
      The callback function should accept one parameter (an int),
      which is the virtual key code of the key pressed.
      """
      self._callbackFunctions['keyDown'] = function
      self._registerCallback()

   def onKeyUp(self, function):
      """
      Set callback for key release events.
      The callback function should accept one parameter (an int),
      which is the virtual key code of the key released.
      """
      self._callbackFunctions['keyUp'] = function
      self._registerCallback()


#######################################################################################
# Display
#######################################################################################
class Display(Interactable):
   def __init__(self, title="", width=600, height=400, x=0, y=50, color=Color.WHITE):
      _ensureApp()             # make sure Qt is running
      _DISPLAYS_.append(self)  # add to global display list

      # initialize internal properties
      self._itemList         = []     # list of items in this display (front=top)
      self._zCount           = 0.0    # float count of Qt z-orders (bottom=top)
      self._toolTipText      = None   # tooltip text for this display
      self._showCoordinates  = False  # show mouse coordinates in tooltip?

      self._localX = 0     # root coordinates for coordinate calculations
      self._localY = 0     # (these should never change)
      self._parent = None

      Interactable.__init__(self)
      self._onClose     = None
      self._onPopupMenu = None

      window = _QtWidgets.QMainWindow()        # create window
      window.setWindowTitle(title)             # set window title
      window.setGeometry(x, y, width, height)  # set window position and size
      window.setFixedSize(width, height)       # prevent resizing
      window.setContextMenuPolicy( _QtCore.Qt.ContextMenuPolicy.CustomContextMenu)                       # disable default right-click menu
      window.show()

      # Display uses an OpenGLWidget to render 2D graphics.
      #   This moves graphics processing to the graphics card, drastically improving performance.
      # Note that only Graphics are rendered this way,
      #   Controls (such as dropbown boxes and text fields) are still rendered on the CPU.

      # set general rendering settings to QSurfaceFormat
      swapBehavior   = _QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer
      renderableType = _QtGui.QSurfaceFormat.RenderableType.OpenGL
      openGLProfile  = _QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile

      format = _QtGui.QSurfaceFormat()
      format.setSwapBehavior(swapBehavior)
      format.setRenderableType(renderableType)
      format.setProfile(openGLProfile)
      _QtGui.QSurfaceFormat.setDefaultFormat(format)

      # create rendering objects
      # - scene is the canvas for Drawables
      # - view renders scene to the display window
      scene  = _QtWidgets.QGraphicsScene(0, 0, width, height)  # create canvas
      view   = _QtWidgets.QGraphicsView(scene)                 # attach canvas to view
      openGL = _QtOpenGL.QOpenGLWidget()                       # create hardware accel widget
      view.setViewport(openGL)                                 # attach hardware accel to view
      window.setCentralWidget(view)                            # attach view to window

      # set scene and view properties
      sceneIndex     = _QtWidgets.QGraphicsScene.ItemIndexMethod.NoIndex # don't cache scene indices
      # updateMode     = _QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
      # updateMode     = _QtWidgets.QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate
      updateMode     = _QtWidgets.QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate
      hoverTracking  = _QtCore.Qt.WidgetAttribute.WA_Hover               # track mouse movement
      mouseTracking  = _QtCore.Qt.WidgetAttribute.WA_MouseTracking       # track mouse location
      scrollPolicy   = _QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff     # disable scroll bars
      shapeAntiAlias = _QtGui.QPainter.RenderHint.Antialiasing           # smooth shapes
      pixmapSmooth   = _QtGui.QPainter.RenderHint.SmoothPixmapTransform  # smooth images
      textAntiAlias  = _QtGui.QPainter.RenderHint.TextAntialiasing       # smooth text rendering

      scene.setItemIndexMethod(sceneIndex)
      view.setViewportUpdateMode(updateMode)
      view.setAttribute(hoverTracking, True)
      view.setAttribute(mouseTracking, True)
      view.setHorizontalScrollBarPolicy(scrollPolicy)
      view.setVerticalScrollBarPolicy(scrollPolicy)
      view.setRenderHint(shapeAntiAlias, True)
      view.setRenderHint(pixmapSmooth, True)
      view.setRenderHint(textAntiAlias, True)

      # remember window, scene and view objects
      self._window = window
      self._scene  = scene
      self._view   = view

      # create event dispatcher
      self._eventDispatcher = EventDispatcher(self)
      self.setColor(color)  # set display background color

   def __str__( self ):
      return f'Display(title = "{self.getTitle()}", width = {self.getWidth()}, height = {self.getHeight()}, x = {self.getPosition()[0]}, y = {self.getPosition()[1]}, color = {self.getColor()})'

   def _getLocalCornerPosition(self):
      return self._localX, self._localY

   def show(self):
      """Reveal the display."""
      self._window.show()

   def hide(self):
      """Hide the display."""
      self._window.hide()

   def add(self, object, x=None, y=None):
      """
      Same as place(), i.e., places an object in the display, at coordinates by x and y.
      If the object already appears on another display it is removed from there, first.
      """
      self.place(object, x, y)

   def addOrder(self, object, order, x, y):
      """
      Adds an object to the display at the specified order and coordinates.
      """
      self.place(object, x, y, order)

   def place(self, object, x=None, y=None, order=0):
      """
      Place a Drawable object on the Display.
      If the object already appears on another display, it is removed from there, first.
      'order' is relative to other items in this group,
      and is not preserved from previous Displays or Groups.
      """
      if not isinstance(object, Drawable):  # do some basic error checking
         raise TypeError(f'Display.place(): object must be a Drawable object (it was {type(object)})')

      if object._parent is not None:
         object._parent.remove(object)     # remove object from any other group or display
      object._parent = self                # tell object it is on this display

      # add item in CreativePython
      order = max(0, min(len(self._itemList), order))  # clamp order to possible indices
      self._itemList.insert(order, object)             # insert to items list
      self._eventDispatcher.add(object)                # register with event dispatcher

      # calculate Qt z-order
      if order == 0:  # adding to top...
         qtZValue = 1.0
         if(len(self._itemList) > 1):
            neighbor = self._itemList[1]               # find previous topmost object
            qtZValue = neighbor._qtZValue + 1.0        # get z-order above it

      elif order >= len(self._itemList) - 1:  # adding to bottom...
         qtZValue = 0.0
         if len(self._itemList) > 1:
            neighbor = self._itemList[-2]              # find previous bottommost object
            qtZValue = neighbor._qtZValue - 1.0        # get z-order underneath it

      else:  # inserting somewhere in middle... take average of neighbor z-orders
         frontNeighbor = self._itemList[order - 1]     # find front neighbor
         backNeighbor  = self._itemList[order + 1]     # find back neighbor
         zFront        = frontNeighbor._qtZValue       # find their Qt z-orders
         zBack         = backNeighbor._qtZValue
         qtZValue      = (zFront + zBack) / 2.0        # find average of neighbor z-orders

      # add object in Qt
      if isinstance(object, (Graphics, Group)):
         object._qtZValue = qtZValue               # remember zValue
         object._qtObject.setZValue(qtZValue)      # set object z-order
         self._scene.addItem(object._qtObject)     # add to scene
         cacheMode = _QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache
         object._qtObject.setCacheMode(cacheMode)  # set graphics caching strategy

      elif isinstance(object, Control):  # add QWidget object
         object._qtZValue = qtZValue               # remember zValue, but don't set it
         object._qtObject.setParent(self._window)  # attach widget to window
         object._qtObject.show()                   # ensure widget is visible

      # set position, if needed
      if x is not None:
         object.setX(x)
      if y is not None:
         object.setY(y)

   def remove(self, object):
      """
      Removes an object from the display.
      """
      if object in self._itemList:  # skip if object not on Display
         # remove object in CreativePython
         object._parent = None                 # tell object it's not on this Display
         self._itemList.remove(object)         # remove object from Display's internal list
         self._eventDispatcher.remove(object)  # de-register event callbacks

         # remove object in Qt
         if isinstance(object, (Graphics, Group)):
            self._scene.removeItem(object._qtObject)  # remove graphics object
         elif isinstance(object, Control):
            object._qtObject.setParent(None)          # remove QWidget object
            object._qtObject.hide()                   # ensure control is hidden

   def removeAll(self):
      """
      Removes all objects from the display.
      """
      self._view.setUpdatesEnabled(False)  # pause Display repainting
      for item in self._itemList:
         self.remove(item)
      self._view.setUpdatesEnabled(True)   # resume Display repainting
      self._view.viewport().update()       # repaint immediately

   def move(self, object, x, y):
      """
      Moves an object to the specified (x, y) coordinates.
      """
      if object in self._itemList:
         object.setPosition(x, y)

   def getOrder(self, object):
      """
      Returns the z-order of the specified Drawable in this display.
      """
      order = None

      if object in self._itemList:  # skip if not on Display
         order = self._itemList.index(object)

      return order

   def setOrder(self, object, order):
      """
      Sets the z-order of the specified Drawable in this display.
      """
      if object in self._itemList:  # skip if not on Display
         self.place(object, None, None, order)

   def setToolTipText(self, text=None):
      """
      Sets the tooltip text for this Display.
      If text is None, the tooltip is removed.
      """
      self._toolTipText = text
      self._view.setToolTip(text)

   def showMouseCoordinates(self):
      """
      Shows the mouse coordinates in the display's tooltip.
      """
      self._showCoordinates = True   # set flag to show coordinates
      self._view.setToolTip(None)    # remove any existing tooltip

      for object in self._itemList:  # suppress item tooltips
         object._qtObject.setToolTip(None)

   def hideMouseCoordinates(self):
      """
      Hides the mouse coordinates in the display's tooltip.
      """
      self._showCoordinates = False             # set flag to hide coordinates
      self._view.setToolTip(self._toolTipText)  # restore display tooltip

      for object in self._itemList:             # restore tooltips
         object._qtObject.setToolTip(object._toolTipText)

   def getColor(self):
      """
      Returns the background color of the display.
      """
      qColor = self._scene.backgroundBrush().color()
      return Color._fromQColor(qColor)

   def setColor(self, color):
      """
      Sets the background color of the display.
      """
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'Display.setColor(): color must be a Color object (it was {type(color)})')

      r, g, b, a = color.getRGBA()
      qColor     = _QtGui.QColor(r, g, b, a)
      brush      = _QtGui.QBrush(qColor)
      self._scene.setBackgroundBrush(brush)  # on Mac
      self._view.setBackgroundBrush(brush)   # on Windows

   def getTitle(self):
      """
      Returns the title of the display.
      """
      return self._window.windowTitle()

   def setTitle(self, title):
      """
      Sets the title of the display.
      """
      self._window.setWindowTitle(title)

   def getWidth(self):
      """
      Returns the width of the display.
      """
      return self._scene.width()

   def getHeight(self):
      """
      Returns the height of the display.
      """
      return self._scene.height()

   def setSize(self, width, height):
      """
      Sets the size of the display.
      """
      pos = self._window.pos()  # grab current window position

      self._scene.setSceneRect(0, 0, width, height)  # adjust scene canvas size
      self._window.setFixedSize(width, height)       # adjust window size
      self._window.move(pos)                         # ensure window doesn't move

   def getPosition(self):
      """
      Returns the position of the display on the screen.
      """
      return int(self._window.x()), int(self._window.y())

   def setPosition(self, x, y):
      """
      Sets the position of the display on the screen.
      """
      self._window.setGeometry(int(x), int(y), self.getWidth(), self.getHeight())

   def getItems(self):
      """
      Returns the list of items in the display.
      """
      return self._itemList

   def close(self):
      """
      Closes the display.
      """
      if 'onClose' in self._callbackFunctions:
         callback = self._callbackFunctions['onClose']
         if callable(callback):
            callback()         # call onClose function, if defined

      self._window.close()     # close window
      self.removeAll()         # remove all objects from display
      _DISPLAYS_.remove(self)  # remove from global display list

   def addMenu(self, menu):
      """Adds a menu to the display's taskbar."""
      if not isinstance(menu, Menu):  # do some basic error checking
         TypeError(f'Display.addMenu(): menu must be a Menu object (it was {type(menu)})')

      menuBar = self._window.menuBar()  # get this display's menuBar (or create one, if needed)
      menuBar.addMenu(menu._qtObject)   # add Qt menu to display's menu bar

   def addPopupMenu(self, menu):
      """Adds a context menu (right-click) to the display."""
      if not isinstance(menu, Menu):  # do some basic error checking
         raise TypeError(f'Display.addPopupMenu(): menu must be a Menu object (it was {type(menu)})')
      # attach popup menu callback - this tells popup menu where to appear
      self._onPopupMenu = lambda pos: menu._qtObject.exec(self._window.mapToGlobal(pos))  # set callback
      self._window.customContextMenuRequested.connect(self._onPopupMenu)  # connect to event signal

   def onClose(self, function):
      """
      Set callback for when the display is closed.
      """
      self._callbackFunctions['onClose'] = function

   ##### CONVENIENCE METHODS
   def drawOval(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """
      Draws an Oval with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      oval = Oval(x1, y1, x2, y2, color, fill, thickness, rotation)  # create oval
      self.add(oval)  # add it
      return oval     # and return it

   def drawCircle(self, x, y, radius, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """
      Draws a Circle with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      circle = Circle(x, y, radius, color, fill, thickness, rotation)  # create circle
      self.add(circle)  # add it
      return circle     # and return it

   def drawPoint(self, x, y, color=Color.BLACK):
      """
      Draws a Point with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      point = Point(x, y, color)  # create point
      self.add(point)  # add it
      return point     # and return it

   def drawArc(self, x1, y1, x2, y2, startAngle, endAngle, color = Color.BLACK, fill = False, thickness = 1):
      """
      Draws an Arc with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      arc = Arc(x1, y1, x2, y2, startAngle, endAngle, color, fill, thickness)  # create arc
      self.add(arc)  # add it
      return arc     # and return it

   def drawArcCircle(self, x, y, radius, startAngle=PI, endAngle=TWO_PI, style=OPEN, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """
      Draws an ArcCircle with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      arcCircle = ArcCircle(x, y, radius, startAngle, endAngle, style, color, fill, thickness, rotation)  # create arc circle
      self.add(arcCircle)  # add it
      return arcCircle     # and return it

   def drawPolyLine(self, xPoints, yPoints, color=Color.BLACK, thickness=1, rotation=0):
      """
      Draws a PolyLine with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      polyLine = PolyLine(xPoints, yPoints, color, thickness, rotation)  # create line
      self.add(polyLine)  # add it
      return polyLine     # and return it

   def drawLine(self, x1, y1, x2, y2, color=Color.BLACK, thickness=1, rotation=0):
      """
      Draws a Line with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      line = Line(x1, y1, x2, y2, color, thickness, rotation)  # create line
      self.add(line)  # add it
      return line     # and return it

   def drawPolygon(self, xPoints, yPoints, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """
      Draws a Polygon with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      polygon = Polygon(xPoints, yPoints, color, fill, thickness, rotation)  # create polygon
      self.add(polygon)  # add it
      return polygon     # and return it

   def drawRectangle(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """
      Draws a Rectangle with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      rectangle = Rectangle(x1, y1, x2, y2, color, fill, thickness, rotation)  # create rectangle
      self.add(rectangle)  # add it
      return rectangle     # and return it

   def drawIcon(self, filename, x, y, width=None, height=None, rotation=0):
      """
      Draws an Icon with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      icon = Icon(filename, width, height, rotation)  # load image (and rescale, if specified)
      self.add(icon, x, y)  # add it at given coordinates
      return icon           # and return it

   def drawImage(self, filename, x, y, width=None, height=None):
      """
      Same as drawIcon().
      Returns the created object (in case we want to move it or delete it later).
      """
      return self.drawIcon(filename, x, y, width, height)

   def drawLabel(self, text, x, y, color=Color.BLACK, font=None):
      """
      Draws a text Label with the given parameters and adds it to the Display.
      Returns the created object (in case we want to move it or delete it later).
      """
      label = Label(text, LEFT, color)  # create label
      if font is not None:
         label.setFont(font)
      self.add(label, x, y)  # add it
      return label           # and return it

   def drawText(self, text, x, y, color = Color.BLACK, font = None):
      """
      Same as drawLabel().
      Returns the created object (in case we want to move it or delete it later).
      """
      return self.drawLabel(text, x, y, color, font)


#######################################################################################
# Graphics Superclasses (Drawable, Graphics, Group, MusicControl, and Control)
#######################################################################################
# Drawable:     items that can be rendered on a Display
# Graphics:     simple geometric shapes, icons, and text labels
# Group:        a collection of Graphics that are manipulated as one object
# MusicControl: user-styled widgets
# Control:      system-styled widgets
class Drawable:
   """
   Base abstract class for all objects that can be added to a Display or Group.
   """
   def __init__(self):
      self._qtObject    = None  # the underlying QtGraphics/QWidget object
      self._qtZValue    = None  # qtObject's order in Qt
      self._parent      = None  # the display or group this object is on/in, if any
      self._localX      = 0     # local bounding box position, relative to our parent
      self._localY      = 0     # ...
      self._width       = 0     # bounding box dimensions
      self._height      = 0     # ...
      self._rotation    = 0     # ...
      self._toolTipText = None  # text to Display on mouse over (None == disabled)

   def __str__(self):
      return f'Drawable()'

   def __repr__(self):
      return str(self)

   ##### INTERNAL METHODS
   # These methods are hidden from the user, and do most of the work
   # for our user-facing class methods.
   # NOTE: These methods are the only way user-facing methods and
   # external classes should access or alter a Drawable's dimensions.
   # e.g. 'self._setLocalPosition(x, y)' instead of 'self._localX = x'
   def _isInGroup(self):
      return (self._parent is not None) and isinstance(self._parent, Group)

   def _getLocalCornerPosition(self):
      return self._localX, self._localY

   def _setLocalCornerPosition(self, x, y):
      self._localX = x
      self._localY = y
      self._qtObject.setPos(x, y)

   def _getGlobalCornerPosition(self):
      x, y   = self._getLocalCornerPosition()
      parent = self._parent
      while parent is not None:  # move up the parent chain until we hit a Display
         gx, gy = parent._getLocalCornerPosition()
         x = x + gx
         y = y + gy
         parent = parent._parent
      return x, y

   def _setGlobalCornerPosition(self, x, y):
      if self._isInGroup():  # calculate local coordinates, relative to parent group
         gx, gy = self._parent._getGlobalCornerPosition()
         x = x - gx
         y = y - gy
      self._setLocalCornerPosition(x, y)

   def _getCenterPosition(self):
      x, y = self._getGlobalCornerPosition()  # find corner
      x = x + (self._width  / 2)              # offset to find center
      y = y + (self._height / 2)
      return int(x), int(y)

   def _setCenterPosition(self, x, y):
      x = x - (self._width / 2)               # offset to find corner
      y = y - (self._height / 2)
      self._setGlobalCornerPosition(x, y)

   ##### DRAWABLE METHODS
   # These methods are user-facing, and are generally only overridden for behavior changes,
   # such as Circles, who use their center coordinate for position, not their top-left corner.
   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      # If the Drawable uses a position other than the top-left corner,
      # this method is overridden accordingly.  Since Drawable's position
      # getters all point here, we only need to override getPosition.
      x, y = self._getGlobalCornerPosition()
      return int(x), int(y)

   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      # If the Drawable uses a position other than the top-left corner,
      # this method is overridden accordingly.  Since Drawable's position
      # setters all point here, we only need to override setPosition.
      self._setGlobalCornerPosition(x, y)

   def getSize(self):
      """
      Returns the width and height of the shape's bounding box.
      """
      return int(self._width), int(self._height)

   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, stretching if needed.
      """
      oldWidth, oldHeight = self.getSize()
      widthDelta  = width  - oldWidth
      heightDelta = height - oldHeight
      if (int(widthDelta) != 0) or (int(heightDelta) != 0):  # skip if no significant change
         self._width  = width
         self._height = height
         self._qtObject.prepareGeometryChange()  # invalidate Qt hitbox
         self._qtObject.setRect(0, 0, width, height)

   def getRotation(self):
      """
      Returns the shape's current rotation angle in degrees.
      """
      return int(self._rotation)

   def setRotation(self, rotation):
      """
      Sets the shape's rotation angle in degrees.
      Rotation increases clockwise, with 0 degrees being the default orientation.
      Objects rotate around their x, y position (top-left corner, or center for circular shapes).
      """
      oldRotation = self.getRotation()
      rotationDelta = rotation - oldRotation
      if (int(rotationDelta) != 0):  # skip if no significant change
         self._rotation = rotation
         qtRotation = -rotation % 360  # reverse increasing direction (CCW -> clockwise)
         self._qtObject.prepareGeometryChange()  # invalidate Qt hitbox
         self._qtObject.setRotation(qtRotation)

   ##### CONVENIENCE METHODS
   # These methods are aliases for the methods above,
   # and shouldn't need to be changed significantly.
   def getX(self):
      """
      Returns the shape's x coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      x, _ = self.getPosition()
      return x

   def setX(self, x):
      """
      Sets the shape's x coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self.setPosition(x, self.getY())

   def getY(self):
      """
      Returns the shape's y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      _, y = self.getPosition()
      return y

   def setY(self, y):
      """
      Sets the shape's y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self.setPosition(self.getX(), y)

   def getWidth(self):
      """
      Returns the width of the shape's bounding box.
      """
      width, _ = self.getSize()
      return width

   def setWidth(self, width):
      """
      Sets the width of the shape's bounding box, stretching the shape if needed.
      """
      self.setSize(width, self.getHeight())

   def getHeight(self):
      """
      Returns the height of the shape's bounding box.
      """
      _, height = self.getSize()
      return height

   def setHeight(self, height):
      """
      Sets the height of the shape's bounding box, stretching the shape if needed.
      """
      self.setSize(self.getWidth(), height)

   def move(self, dx, dy):
      """
      Moves the shape by the given distances.
      """
      x, y = self.getPosition()
      self.setPosition(x + dx, y + dy)

   def rotate(self, angle):
      """
      Rotates the shape by the given angle in degrees.
      """
      self.setRotation(self.getRotation() + angle)

   ##### LOCATION TESTS
   # These methods help with hit testing and location detection.
   def encloses(self, other):
      """
      Returns True if this shape encloses the other shape.
      """
      if not isinstance(other, Drawable):  # do some basic error checking
         TypeError(f'Drawable.encloses(): other must be a Drawable object (it was {type(other)})')
      encloses = None

      qtA = self._qtObject
      qtB = other._qtObject
      bothGraphics = isinstance(self, (Graphics, Group)) and isinstance(other, (Graphics, Group))
      sameDisplay  = isinstance(self._parent, Display) and (self._parent == other._parent)

      if bothGraphics and sameDisplay:  # use Qt's spatial hit test
         pathA = qtA.mapToScene(qtA.shape())
         pathB = qtB.mapToScene(qtB.shape())
         encloses = pathA.contains(pathB)

      else:  # fallback to bounding box calculation
         x1, y1  = self._getGlobalCornerPosition()
         width, height = self.getSize()
         x2      = x1 + width
         y2      = y1 + height

         otherX1, otherY1 = other._getGlobalCornerPosition()
         otherWidth, otherHeight = other.getSize()
         otherX2 = otherX1 + otherWidth
         otherY2 = otherY1 + otherHeight

         xEncloses = (x1 <= otherX1 <= x2 and x1 <= otherX2 <= x2)
         yEncloses = (y1 <= otherY1 <= y2 and y1 <= otherY2 <= y2)
         encloses  = xEncloses and yEncloses

      return encloses

   def intersects(self, other):
      """
      Returns True if this shape intersects the other shape.
      """
      if not isinstance(other, Drawable):
         TypeError(f'Drawable.intersects(): other must be a Drawable object (it was {type(other)})')
      intersects = None

      qtA = self._qtObject
      qtB = other._qtObject
      bothGraphics = isinstance(self, (Graphics, Group)) and isinstance(other, (Graphics, Group))
      sameDisplay  = isinstance(self._parent, Display) and (self._parent == other._parent)

      if bothGraphics and sameDisplay:  # use Qt's spatial hit test
         pathA = qtA.mapToScene(qtA.shape())
         pathB = qtB.mapToScene(qtB.shape())
         intersects = pathA.intersects(pathB)

      else:  # fallback to bounding box calculation
         x1, y1  = self._getGlobalCornerPosition()
         width, height = self.getSize()
         x2      = x1 + width
         y2      = y1 + height

         otherX1, otherY1 = other._getGlobalCornerPosition()
         otherWidth, otherHeight = other.getSize()
         otherX2 = otherX1 + otherWidth
         otherY2 = otherY1 + otherHeight

         xIntersects = (x1 <= otherX1 <= x2 or
                        x1 <= otherX2 <= x2 or
                   otherX1 <= x1      <= otherX2)
         yIntersects = (y1 <= otherY1 <= y2 or
                        y1 <= otherY2 <= y2 or
                   otherY1 <= y1      <= otherY2)
         intersects  = xIntersects and yIntersects

      return intersects

   def contains(self, x, y):
      """Check if a point is in the shape's bounding box."""
      contains = None

      if hasattr(self._qtObject, "scene"):  # use Qt's spatial hit test for graphics items on a Display
         targetPoint = _QtCore.QPointF(x, y)
         targetPos   = self._qtObject.mapFromScene(targetPoint)
         contains    = self._qtObject.contains(targetPos)

      else:  # fallback to bounding box calculation
         x1, y1  = self._getGlobalCornerPosition()
         width, height = self.getSize()
         x2      = x1 + width
         y2      = y1 + height

         xContains = (x1 <= x <= x2)
         yContains = (y1 <= y <= y2)
         contains  = xContains and yContains

      return contains

   def setToolTipText(self, text=None):
      """
      Set the tooltip text for this shape.
      If text is None, the tooltip is removed.
      """
      self._toolTipText = text
      self._qtObject.setToolTip(text)

#######################################################################################
# Graphics
#######################################################################################
class Graphics(Drawable, Interactable):
   """
   Base abstract class for simple geometric shapes, icons, and text labels.
   """
   def __init__(self):
      Drawable.__init__(self)
      Interactable.__init__(self)
      self._color     = []    # rgba values
      self._fill      = None  # boolean, is this filled?
      self._thickness = None  # outline width

   def __str__(self):
      return f'Graphics(color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   ##### GRAPHICS METHODS
   def getColor(self):
      """
      Returns the shape's current color.
      """
      r, g, b, a = self._color
      return Color(r, g, b, a)

   def setColor(self, color):
      """
      Changes the shape's color to the specified color.
      If color parameter is omitted, a color selection dialog box will be presented.
      TODO: add color selection box
      """
      r, g, b, a  = color.getRGBA()
      self._color = [r, g, b, a]
      qColor      = _QtGui.QColor(r, g, b, a)

      qPen = self._qtObject.pen()
      qPen.setColor(qColor)
      self._qtObject.setPen(qPen)         # set object outline color

      if self.getFill():
         qBrush = self._qtObject.brush()
         qBrush.setColor(qColor)
         self._qtObject.setBrush(qBrush)  # set shape's fill color, if needed

   def getFill(self):
      """
      Returns whether the shape is filled or not.
      """
      return self._fill

   def setFill(self, value):
      """
      Sets whether the shape is filled or not.
      """
      self._fill = bool(value)

      if self._fill:  # use outline color
         qColor = self._qtObject.pen().color()
      else:           # use transparency
         qColor = _QtGui.QColor(0, 0, 0, 0)

      qBrush = _QtGui.QBrush(qColor)
      self._qtObject.setBrush(qBrush)

   def getThickness(self):
      """
      Returns the shape outline's current thickness.
      """
      return self._thickness

   def setThickness(self, thickness):
      """
      Changes the shape outline's thickness to the specified value.
      """
      self._thickness = int(thickness)
      qPen = self._qtObject.pen()
      qPen.setWidth(thickness)
      self._qtObject.setPen(qPen)   # set shape's outline thickness


#######################################################################################
# Group
#######################################################################################
class Group(Drawable, Interactable):
   """
   Groups represent a collection of Drawable objects.
   All items in a Group move as one.
   """
   def __init__(self, items=[]):
      Drawable.__init__(self)
      Interactable.__init__(self)

      self._qtObject        = _QtWidgets.QGraphicsItemGroup()  # graphics item container
      # self._qtWidget        = _QtWidgets.QWidget()             # widget container
      self._eventDispatcher = EventDispatcher(self)            # event dispatcher for group items
      self._itemList        = []                               # internal list of Drawable objects

      for item in reversed(items):  # add each item, back to front
         self.add(item)

      # Groups are added to their owner's event handler,
      # but items within the Group are not.
      # We initialize our event handlers to None to ensure that
      # the Group has a chance to pass events down to its items,
      # even if the Group doesn't have an event callback registered.
      self.onMouseClick(None)
      self.onMouseDown(None)
      self.onMouseUp(None)
      self.onMouseMove(None)
      self.onMouseDrag(None)
      self.onMouseEnter(None)
      self.onMouseExit(None)
      self.onKeyType(None)
      self.onKeyDown(None)
      self.onKeyUp(None)

   def __str__(self):
      return f'Group(items = {self._itemList})'

   ##### INTERNAL METHODS
   def _calculateSize(self):
      if len(self._itemList) == 0:
         self._width  = 0
         self._height = 0
      else:
         x1s = []
         y1s = []
         x2s = []
         y2s = []

         for child in self._itemList:
            lx, ly = child._getLocalCornerPosition()
            w,  h  = child.getSize()
            x1s.append(lx)
            y1s.append(ly)
            x2s.append(lx + w)
            y2s.append(ly + h)
         
         minX = min(x1s)
         minY = min(y1s)
         maxX = max(x2s)
         maxY = max(y2s)

         self._width  = maxX - minX
         self._height = maxY - minY

   def _updateHitbox(self):
      children = self._qtObject.childItems()
      if children is not None and len(children) > 0:
         rect = children[0].boundingRect().translated(children[0].pos())
         for child in children[1:]:
            rect = rect.united(child.boundingRect().translated(child.pos()))
         self._qtObject.prepareGeometryChange()
         dummy = children[0]
         self._qtObject.removeFromGroup(dummy)
         self._qtObject.addToGroup(dummy)

   def _setGlobalCornerPosition(self, x, y):
      oldX, oldY = self._getGlobalCornerPosition()
      dx = x - oldX
      dy = y - oldY
      self._setLocalCornerPosition(self._localX + dx, self._localY + dy)

      for child in self._itemList:  # rebase child items
         cx, cy = child._getLocalCornerPosition()
         child._setLocalCornerPosition(cx, cy)

   ##### OVERRIDE METHODS
   def getSize(self):
      """
      Returns the width and height of the shape's bounding box.
      """
      self._calculateSize()
      return int(self._width), int(self._height)

   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, stretching if needed.
      """
      if (width <= 0) or (height <= 0):
         print(f"{type(self)}.setSize: width and height must be positive, non-zero integers (they were {width} and {height}).")
      else:
         oldWidth, oldHeight = self.getSize()

         if oldWidth != 0:  # don't divide by zero
            ratioX = width / oldWidth
         else:
            ratioX = 1
         
         if oldWidth != 0:  # don't divide by zero
            ratioY = height / oldHeight
         else:
            ratioY = 1

         if (ratioX != 1) or (ratioY != 1):  # skip if no significant change
            for child in self._itemList:
               w, h = child.getSize()
               newW = w * ratioX
               newH = h * ratioY

               x, y = child._getLocalCornerPosition()
               newX = x * ratioX
               newY = y * ratioY

               child.setSize(newW, newH)
               child._setLocalCornerPosition(newX, newY)
            self._updateHitbox()

   ##### NEW GROUP METHODS
   def add(self, object):
      """
      Adds a Drawable object to the Group.
      """
      self.addOrder(object, 0)

   def addOrder(self, object, order=0):
      """
      Adds a Drawable object to the Group.
      If the object already appears on another display, it is removed from there, first.
      'order' is relative to other items in this group,
      and is not preserved from previous Displays or Groups.
      """
      if not isinstance(object, Drawable):  # do some basic type checking
         raise TypeError(f'Group.add(): item should be a Drawable object (it was {type(object)}).')

      if isinstance(object._parent, (Group, Display)):
         object._parent.remove(object)  # remove object from any other group or display
      object._parent = self             # tell object it's in this group now

      # add item in CreativePython
      order = max(0, min(len(self._itemList), order))   # clamp order to possible indices
      self._itemList.insert(order, object)              # insert to items list
      self._eventDispatcher.add(object)                 # register with event dispatcher
      gx, gy = object._getGlobalCornerPosition()        # calculate item's local coordinates in Group
      px, py = self._getGlobalCornerPosition()
      object._setLocalCornerPosition(gx - px, gy - py)
      self._calculateSize()
      self._updateHitbox()

      # calculate Qt z-order
      if order == 0:  # adding to top...
         qtZValue = 1.0
         if(len(self._itemList) > 1):
            neighbor = self._itemList[1]                   # find previous topmost object
            qtZValue = neighbor._qtZValue + 1.0            # get z-order above it

      elif order >= len(self._itemList) - 1:  # adding to bottom...
         qtZValue = 0.0
         if len(self._itemList) > 1:
            neighbor = self._itemList[-2]                  # find previous bottommost object
            qtZValue = neighbor._qtZValue - 1.0            # get z-order underneath it

      else:  # inserting somewhere in middle... take average of neighbor z-orders
         frontNeighbor = self._itemList[order - 1]         # find front neighbor
         backNeighbor  = self._itemList[order + 1]         # find back neighbor
         zFront        = frontNeighbor._qtZValue           # find their Qt z-orders
         zBack         = backNeighbor._qtZValue
         qtZValue      = (zFront + zBack) / 2.0            # find average of neighbor z-orders

      # add object in Qt
      if isinstance(object, (Graphics, Group)):
         object._qtZValue = qtZValue                    # remember zValue
         object._qtObject.setZValue(qtZValue)           # set object z-order
         self._qtObject.addToGroup(object._qtObject)
         cacheMode = _QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache
         object._qtObject.setCacheMode(cacheMode)       # set graphics caching strategy

      elif isinstance(object, Control):  # add QWidget object
         object._qtZValue = qtZValue               # remember zValue, but don't set it
         object._qtObject.setParent(self._window)  # attach widget to window
         object._qtObject.show()                   # ensure widget is visible
      elif isinstance(object, Control):
         print(f"{type(self)}.add(): 'Control' objects cannot be added to Groups.")
      #    object._qtZValue = qtZValue                 # remember zValue, but don't set it
      #    object._qtObject.setParent(self._qtWidget)  # attach widget to Group
      #    object._qtObject.show()                     # ensure widget is visible

   def remove(self, object):
      """
      Removes a Drawable object from the Group.
      """
      if object in self._itemList:  # skip if object not in Group
         # remove object in CreativePython
         object._parent = None                 # tell object it's not in this Group
         self._itemList.remove(object)         # remove object from Group's internal list
         self._eventDispatcher.remove(object)  # de-register event callbacks
         self._calculateSize()
         self._updateHitbox()

         # remove object in Qt
         if isinstance(object, (Graphics, Group)):
            self._qtObject.removeFromGroup(object._qtObject)  # remove graphics object
         # elif isinstance(object, Control):  # Controls have special methods to remove
         #    object._qtObject.setParent(None)                  # remove QWidget object
         #    object._qtObject.hide()                           # make sure control is hidden

         # add object to this Group's parent
         if self._parent is not None:
            self._parent.add(object)

   def getOrder(self, object):
      """
      Returns the z-order of the specified Drawable in this group.
      """
      order = None

      if object in self._itemList:  # skip if not in Group
         order = self._itemList.index(object)

      return order

   def setOrder(self, object, order):
      """
      Sets the z-order of the specified Drawable in this group.
      """
      if (object in self._itemList): # skip if not in Group
         self.addOrder(object, order)


#######################################################################################
# Music Control
#######################################################################################
class MusicControl(Group):
   """
   Base abstract class for all CreativePython-defined interactable objects.
   MusicControl objects are Groups with predefined behaviors, such as Faders and Push Buttons.
   """
   def __init__(self, updateFunction=None):
      Group.__init__(self)
      self._value           = None
      self._function        = updateFunction
      self._foregroundShape = None
      self._backgroundShape = None
      self._outlineShape    = None

   def __str__(self):
      return f'Control(startValue = {self._value}, updateFunction = {self._function})'

   def _receiveEvent(self, event):
      """
      Injects control-specific events to the event handler.
      Each Control should override this method based on their function.
      """
      Group._receiveEvent(self, event)

   ##### MUSICCONTROL METHODS
   def getValue(self):
      """
      Returns the current value of the control.
      """
      return self._value

   def setValue(self, value):
      """
      Sets the current value of the control, and updates its appearance.
      """
      if (self._value != value):  # skip if value isn't different
         self._value = value
         if self._function is not None and callable(self._function):
            self._function(self._value)  # call user function


#######################################################################################
# Control
#######################################################################################
class Control(Drawable, Interactable):
   """
   Base abstract class for all Qt-defined interactable objects.
   Controls represent objects with predefined, usually system-wide, behavior.
   Their underlying QObjects are QWidgets, not QGraphicsItems, and they sit
   on top of the Display - they can't be layered under Graphics items.
   """
   def __init__(self):
      Drawable.__init__(self)
      Interactable.__init__(self)

   def __str__(self):
      return f'Control()'

   ##### OVERRIDDEN METHODS
   # Controls have the same properties and methods as Drawables, but we have to
   # implement their position and dimension properties differently in Qt, since
   # QGraphicsItems and QWidgets only share some syntax.
   def _setLocalCornerPosition(self, x, y):
      self._localX = x
      self._localY = y
      self._qtObject.move(x, y)  # .move() instead of .setPos()

   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, stretching if needed.
      """
      oldWidth, oldHeight = self.getSize()
      widthDelta  = width  - oldWidth
      heightDelta = height - oldHeight
      if (int(widthDelta) != 0) or (int(heightDelta) != 0):  # skip if no significant change
         self._width  = width
         self._height = height
         self._qtObject.setFixedSize(width, height)

   def setRotation(self, rotation):
      """
      Sets the shape's rotation angle in degrees.
      Rotation increases clockwise, with 0 degrees being the default orientation.
      Objects rotate around their x, y position (top-left corner, or center for Circle and ArcCircle).
      """
      # TODO
      print(f"{type(self)}.setRotation(): rotation of Controls cannot be set yet.")


#######################################################################################
# Graphics Objects (Geometric shapes, text, and images)
#######################################################################################
class Rectangle(Graphics):
   """
   Rectangles are linear Graphics defined by its bounding box.
   """
   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      self._qtObject = _QtWidgets.QGraphicsRectItem(0, 0, width, height)

      # We explicitly call this class's methods to ensure it initializes correctly,
      # even if its called from a subclass's constructor.
      # Drawable
      Rectangle.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      Rectangle.setRotation(self, rotation)
      # Graphics
      Rectangle.setColor(self, color)
      Rectangle.setFill(self, fill)
      Rectangle.setThickness(self, thickness)

   def __str__(self):
      x2 = self.getX() + self.getWidth()
      y2 = self.getY() + self.getHeight()
      return f'Rectangle(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Oval(Graphics):
   """
   Ovals are curved Graphics defined by its bounding box.
   """
   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new oval."""
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      self._qtObject = _QtWidgets.QGraphicsEllipseItem(0, 0, width, height)

      # We explicitly call this class's methods to ensure it initializes correctly,
      # even if its called from a subclass's constructor.
      # Drawable
      Oval.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      Oval.setRotation(self, rotation)
      # Graphics
      Oval.setColor(self, color)
      Oval.setFill(self, fill)
      Oval.setThickness(self, thickness)

   def __str__(self):
      x2 = self.getX() + self.getWidth()
      y2 = self.getY() + self.getHeight()
      return f'Oval(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Circle(Oval):
   """
   Circles are ovals defined by a center point and radius.
   """
   def __init__(self, x, y, radius, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Circle."""
      x1 = x - radius  # calculate Oval dimensions
      y1 = y - radius
      x2 = x + radius
      y2 = y + radius
      Oval.__init__(self, x1, y1, x2, y2, color, fill, thickness, rotation)

   def __str__(self):
      return f'Circle(x = {self.getX()}, y = {self.getY()}, radius = {self.getRadius()}, color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      x, y = self._getCenterPosition()
      return int(x), int(y)

   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self._setCenterPosition(x, y)

   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      if width != height:
         print(f"{type(self)}.setSize: width and height must be equal.")
      else:
         Oval.setSize(self, width, height)

   ##### CIRCLE METHODS
   def getRadius(self):
      """
      Returns the shape's radius.
      """
      return int(self.getWidth() / 2)

   def setRadius(self, radius):
      """
      Sets the shape's radius.
      """
      self.setWidth(radius*2)  # actually, set its diameter


class Point(Circle):
   """
   Points are individual pixels defined by their coordinate.
   """
   def __init__(self, x, y, color=Color.BLACK):
      """Create a new Point."""
      Circle.__init__(self, x, y, 1, color, True, 1, 0)

   def __str__(self):
      return f'Point(x = {self.getX()}, y = {self.getY()}, color = {self.getColor()})'

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      print(f"{type(self)}.setSize: Can't set the width or height of a Point.")

   def setRadius(self, radius):
      """
      Sets the shape's radius.
      """
      print(f"{type(self)}.setRadius: Can't set the radius of a Point.")

   def setFill(self, value):
      """
      Sets whether the shape is filled or not.
      """
      print(f"{type(self)}.setFill: Can't set the fill of a Point.")

   def setThickness(self, thickness):
      """
      Changes the shape outline's thickness to the specified value.
      """
      print(f"{type(self)}.setThickness: Can't set the thickness of a Point.")


class Arc(Graphics):
   """
   Arcs are curved lines defined by a bounding box, and the angles of its endpoints within that box.
   """
   def __init__(self, x1, y1, x2, y2, startAngle=PI, endAngle=TWO_PI, style=OPEN, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Arc."""
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      # calculate shape
      arcWidth = -(endAngle - startAngle)   # Qt angles increase opposite ours, so negate
      path = _QtGui.QPainterPath()                           # create new path
      path.arcMoveTo(0, 0, width, height, startAngle)        # move to start angle
      path.arcTo(0, 0, width, height, startAngle, arcWidth)  # draw arc

      if style == PIE:
         centerX = width  // 2
         centerY = height // 2
         path.lineTo(centerX, centerY)  # connect arc to center
         path.closeSubpath()            # return to start point
      elif style == CHORD:
         path.closeSubpath()            # return to start point
      elif style == OPEN:
         pass                           # leave open

      self._qtObject   = _QtWidgets.QGraphicsPathItem(path)
      self._startAngle = startAngle
      self._endAngle   = endAngle
      self._style      = style

      # We explicitly call this class's methods to ensure it initializes correctly,
      # even if its called from a subclass's constructor.
      # Drawable
      Arc.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      Arc.setRotation(self, rotation)
      # Graphics
      Arc.setColor(self, color)
      Arc.setFill(self, fill)
      Arc.setThickness(self, thickness)

   def __str__(self):
      x2 = self.getX() + self.getWidth()
      y2 = self.getY() + self.getHeight()
      return f'Arc(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, startAngle = {self._startAngle}, endAngle = {self._endAngle}, style = {self._style}, color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      if (width <= 0) or (height <= 0):
         print(f"{type(self)}.setSize: width and height must be positive, non-zero integers (they were {width} and {height}).")
      else:
         if self._width != 0:  # don't divide by zero
            ratioX = width / self._width
         else:
            ratioX = 1
         
         if self._height != 0:  # don't divide by zero
            ratioY = height / self._height
         else:
            ratioY = 1

         if (ratioX != 1) or (ratioY != 1):  # skip if no significant change
            self._width  = width              # store dimensions
            self._height = height

            oldPath   = self._qtObject.path()
            oldRect   = oldPath.boundingRect()
            transform = _QtGui.QTransform()
            transform.translate(-oldRect.x(), -oldRect.y())  # move to origin
            transform.scale(ratioX, ratioY)                  # scale to new size
            transform.translate(oldRect.x(), oldRect.y())    # return to original position
            newPath = transform.map(oldPath)                 # apply transformation to path
            self._qtObject.prepareGeometryChange()           # invalidate old hitbox
            self._qtObject.setPath(newPath)                  # overwrite old path


class ArcCircle(Arc):
   """
   ArcCircles are Arcs defined by a center point, radius, and the angles of its endpoints around its center.
   """
   def __init__(self, x, y, radius, startAngle=PI, endAngle=TWO_PI, style=OPEN, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new ArcCircle."""
      x1 = x - radius  # calculate Arc dimensions
      y1 = y - radius
      x2 = x + radius
      y2 = y + radius
      Arc.__init__(self, x1, y1, x2, y2, startAngle, endAngle, style, color, fill, thickness, rotation)

   def __str__(self):
      return f'ArcCircle(x = {self.getX()}, y = {self.getY()}, radius = {self.getRadius()}, startAngle = {self._startAngle}, endAngle = {self._endAngle}, style = {self._style}, color = {self.getColor()}, fill = {self.getFill()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self._getCenterPosition()

   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self._setCenterPosition(x, y)

   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      if width != height:
         print(f"{type(self)}.setSize: width and height must be equal.")
      else:
         Arc.setSize(self, width, height)

   ##### ARCCIRCLE METHODS
   def getRadius(self):
      """
      Returns the shape's radius.
      """
      return int(self.getWidth() / 2)

   def setRadius(self, radius):
      """
      Sets the shape's radius.
      """
      self.setWidth(radius*2)  # actually, set its diameter


class Line(Graphics):
   """
   Lines are straight paths between two endpoints.
   """
   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, thickness=1, rotation=0):
      """Create a new Line."""
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      self._qtObject = _QtWidgets.QGraphicsLineItem(x1, y1, x2, y2)

      # We explicitly call this class's methods to ensure it initializes correctly,
      # even if its called from a subclass's constructor.
      # Drawable
      Line.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      Line.setRotation(self, rotation)
      # Graphics
      Line.setRotation(self, rotation)
      Line.setColor(self, color)
      Line.setThickness(self, thickness)

   def __str__(self):
      line = self._qtObject.line()
      x1 = int(line.x1())
      y1 = int(line.y1())
      x2 = int(line.x2())
      y2 = int(line.y2())
      return f'Line(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, stretching the shape if needed.
      """
      if (width < 0) or (height < 0):
         print(f"{type(self)}.setSize: width and height must be positive integers (they were {width} and {height}).")
      else:
         oldWidth, oldHeight = self.getSize()

         if oldWidth == 0:
            if width == 0:
               ratioX = 0  # stay flat
            else:
               ratioX = 1  # scale normally
         else:
            ratioX = width / oldWidth  # calculate scale

         if oldHeight == 0:
            if height == 0:
               ratioY = 0  # stay flat
            else:
               ratioY = 1  # scale normally
         else:
            ratioY = height / oldHeight  # calculate scale

         if (ratioX != 1) or (ratioY != 1):  # skip if no significant change
            self._width  = width          # store dimensions
            self._height = height
            line = self._qtObject.line()  # scale line's internal points
            x1   = line.x1() * ratioX
            y1   = line.y1() * ratioY
            x2   = line.x2() * ratioX
            y2   = line.y2() * ratioY
            self._qtObject.prepareGeometryChange()  # invalidate old hitbox
            self._qtObject.setLine(x1, y1, x2, y2)

   def getFill(self):
      """
      Returns whether the shape is filled or not.
      """
      return False

   def setFill(self, value):
      """
      Sets whether the shape is filled or not.
      """
      print(f"{type(self)}.setFill: Can't set the fill of a Line.")

   ##### LINE METHODS
   def getLength(self):
      """
      Returns the length of the Line.
      """
      return self._qtObject.line().length()

   def setLength(self, length):
      """
      Sets the length of the line.
      """
      self._qtObject.line().setLength(length)
      # TODO: calculate width and height

      # # manual calculation, maintaining the leftmost point and extended right
      # oldLine = self._qtObject.line()
      # angle   = oldLine.angle()                          # starts at 3 o'clock, increases CCW
      # newLine = _QtCore.QLineF.fromPolar(length, angle)  # generate new line
      # newLine.translate(oldLine.p1())                    # anchor starting point
      # self._qtObject.setLine(newLine)


class PolyLine(Graphics):
   """
   PolyLines are straight paths between a series of endpoints.
   """
   def __init__(self, xPoints, yPoints, color=Color.BLACK, thickness=1, rotation=0):
      """Create a new Polyline."""
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(xPoints)
      cornerY = min(yPoints)
      width   = max(xPoints) - cornerX
      height  = max(yPoints) - cornerY
      self._scaleX  = 1.0  # how much the shape has changed since creation
      self._scaleY  = 1.0
      self._xPoints = []   # store xPoints and yPoints as local coordinates
      self._yPoints = []   # when we need them, we recalculate global coordinates

      # calculate shape
      path = _QtGui.QPainterPath()      # create blank path
      x = xPoints[0] - cornerX          # get first point, relative to bounding box
      y = yPoints[0] - cornerY
      self._xPoints.append(x)
      self._yPoints.append(y)
      path.moveTo(x, y)                 # move to first point
      for i in range(1, len(xPoints)):  # for every other point...
         x = xPoints[i] - cornerX       # get next point, relative to bounding box
         y = yPoints[i] - cornerY
         self._xPoints.append(x)
         self._yPoints.append(y)
         path.lineTo(x, y)              # connect last point to next point

      self._qtObject = _QtWidgets.QGraphicsPathItem(path)

      # We explicitly use this class's methods to ensure subclasses initialize correctly.
      # Otherwise, 'self.setPosition' uses the subclass's setPosition,
      # even if its called from this constructor.
      # Drawable
      PolyLine.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      PolyLine.setRotation(self, rotation)
      # Graphics
      PolyLine.setColor(self, color)
      PolyLine.setThickness(self, thickness)

   def __str__(self):
      xPoints, yPoints = self._getPoints()
      return f'PolyLine(xPoints = {xPoints}, yPoints = {yPoints}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   def _getPoints(self):
      """
      Rebuilds xPoints and yPoints, scaling by the appropriate factor and offset back to global coordinates.
      """
      cornerX, cornerY = self.getPosition()
      xPoints = []
      yPoints = []

      for i in range(len(self._xPoints)):  # unpack points to global coordinates
         x = int(cornerX + (self._xPoints[i] * self._scaleX))
         y = int(cornerY + (self._yPoints[i] * self._scaleY))
         xPoints.append(x)
         yPoints.append(y)

      return xPoints, yPoints

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      if (width <= 0) or (height <= 0):
         print(f"{type(self)}.setSize: width and height must be positive, non-zero integers (they were {width} and {height}).")
      else:
         if self._width != 0:  # don't divide by zero
            ratioX = width / self._width
         else:
            ratioX = 1
         
         if self._height != 0:  # don't divide by zero
            ratioY = height / self._height
         else:
            ratioY = 1

         if (ratioX != 1) or (ratioY != 1):  # skip if no significant change
            self._width  = width             # store dimensions
            self._height = height
            self._scaleX = self._scaleX * ratioX
            self._scaleY = self._scaleY * ratioY

            oldPath = self._qtObject.path()
            oldRect = oldPath.boundingRect()
            transform = _QtGui.QTransform()
            transform.translate(-oldRect.x(), -oldRect.y())  # move to origin
            transform.scale(ratioX, ratioY)                  # scale to new size
            transform.translate(oldRect.x(), oldRect.y())    # return to original position
            newPath = transform.map(oldPath)                 # apply transformation to path
            self._qtObject.prepareGeometryChange()           # invalidate old hitbox
            self._qtObject.setPath(newPath)                  # overwrite old path


class Polygon(Graphics):
   """
   Polygons are defined by linear paths between a series of connected endpoints.
   """
   def __init__(self, xPoints, yPoints, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Polygon."""
      Graphics.__init__(self)

      # calculate bounding box dimensions
      cornerX = min(xPoints)
      cornerY = min(yPoints)
      width   = max(xPoints) - cornerX
      height  = max(yPoints) - cornerY
      self._scaleX  = 1.0  # how much the shape has changed since creation
      self._scaleY  = 1.0
      self._xPoints = []  # store xPoints and yPoints as local coordinates
      self._yPoints = []  # when we need them, we recalculate global coordinates

      # calculate shape
      polygon = _QtGui.QPolygonF()              # create blank polygon
      for i in range(len(xPoints)):             # for every point...
         x = xPoints[i] - cornerX               # get point, relative to bounding box
         y = yPoints[i] - cornerY
         self._xPoints.append(x)
         self._yPoints.append(y)
         polygon.append(_QtCore.QPointF(x, y))  # add point to polygon

      self._qtObject = _QtWidgets.QGraphicsPolygonItem(polygon)

      # We explicitly use this class's methods to ensure subclasses initialize correctly.
      # Otherwise, 'self.setPosition' uses the subclass's setPosition,
      # even if its called from this constructor.
      # Drawable
      Polygon.setPosition(self, cornerX, cornerY)
      self._width  = width
      self._height = height
      Polygon.setRotation(self, rotation)
      # Graphics
      Polygon.setColor(self, color)
      Polygon.setFill(self, fill)
      Polygon.setThickness(self, thickness)

   def __str__(self):
      xPoints, yPoints = self._getPoints()
      return f'Polygon(xPoints = {xPoints}, yPoints = {yPoints}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   def _getPoints(self):
      """
      Rebuilds xPoints and yPoints, scaling by the appropriate factor and offset back to global coordinates.
      """
      cornerX, cornerY = self.getPosition()
      xPoints = []
      yPoints = []

      for i in range(len(self._xPoints)):  # unpack points to global coordinates
         x = int(cornerX + (self._xPoints[i] * self._scaleX))
         y = int(cornerY + (self._yPoints[i] * self._scaleY))
         xPoints.append(x)
         yPoints.append(y)

      return xPoints, yPoints

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height):
      """
      Sets the width and height of the shape's bounding box, scaling and stretching the shape if needed.
      """
      if (width <= 0) or (height <= 0):
         print(f"{type(self)}.setSize: width and height must be positive, non-zero integers (they were {width} and {height}).")
      else:
         if self._width != 0:  # don't divide by zero
            ratioX = width / self._width
         else:
            ratioX = 1
         
         if self._height != 0:  # don't divide by zero
            ratioY = height / self._height
         else:
            ratioY = 1

         if (ratioX != 1) or (ratioY != 1):  # skip if no significant change
            self._width  = width             # store dimensions
            self._height = height
            self._scaleX = self._scaleX * ratioX
            self._scaleY = self._scaleY * ratioY

            oldPolygon = self._qtObject.polygon()   # get existing dimensions
            oldRect    = oldPolygon.boundingRect()
            transform = _QtGui.QTransform()
            transform.translate(-oldRect.x(), -oldRect.y())  # move to origin
            transform.scale(ratioX, ratioY)                  # scale to new size
            transform.translate(oldRect.x(), oldRect.y())    # return to original position
            newPolygon = transform.map(oldPolygon)           # apply transformation to polygon
            self._qtObject.prepareGeometryChange()           # invalidate old hitbox
            self._qtObject.setPolygon(newPolygon)            # overwrite old polygon


class Icon(Graphics):
   """
   Icons are shapes rendered from .png or .jpg files, and/or drawn pixel-by-pixel.
   """
   def __init__(self, filename, width=None, height=None, rotation=0):
      """Create a new Icon."""
      Graphics.__init__(self)
      try:     # create pixmap from file
         pixmap = _QtGui.QPixmap(filename)

         if width is None and height is None:
            width  = pixmap.width()                                   # no scaling needed
            height = pixmap.height()
         elif width is None:
            width = int(pixmap.width() * (height / pixmap.height()))  # scale width to height
         elif height is None:
            height = int(pixmap.height() * (width / pixmap.width()))  # scale height to width

         scaledPixmap = pixmap.scaled(width, height)  # scale new pixmap

      except:  # ... or create blank pixmap
         if width is None:
            width = 600
         if height is None:
            height = 400
         pixmap = _QtGui.QPixmap(width, height)       # save original pixmap
         scaledPixmap = pixmap.scaled(width, height)  # alias a "scaled" pixmap

      self._qtObject = _QtWidgets.QGraphicsPixmapItem(scaledPixmap)
      self._filename = filename
      self._pixmap   = pixmap
      # Drawable
      Icon.setPosition(self, 0, 0)
      self._width  = width
      self._height = height
      Icon.setRotation(self, rotation)
      # Graphics
      self._color = [0, 0, 0, 0]

   def __str__(self):
      return f'Icon(filename = "{self._filename}", width = {self.getWidth()}, height = {self.getHeight()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def setSize(self, width, height=None):
      """
      Set the icon's size.
      """
      if height is None:  # scale height to width
         height = int(self._pixmap.height() * (width / self._pixmap.width()))

      oldWidth, oldHeight = self.getSize()

      if (width != oldWidth) or (height != oldHeight):
         pixmap = self._pixmap.scaled(width, height)  # scale new pixmap
         self._qtObject.prepareGeometryChange()       # invalidate old hitbox
         self._qtObject.setPixmap(pixmap)             # set scaled pixmap to object
         self._width  = int(width)
         self._height = int(height)  # Icons internally represent width and height as integers

   def setFill(self, value):
      """
      Sets whether the shape is filled or not.
      """
      print(f"{type(self)}.setFill: Can't set the fill of an Icon.")

   def setThickness(self, thickness):
      """
      Changes the shape outline's thickness to the specified value.
      """
      print(f"{type(self)}.setThickness: Can't set the thickness of an Icon.")

   ##### ICON METHODS
   def crop(self, x, y, width, height):
      """
      Crop the icon to the specified rectangle.
      Coordinates are relative to the icon's top-left corner.
      """
      self._pixmap = self._pixmap.copy(x, y, width, height)  # crop internal pixmap

      pixmap = self._pixmap.scaled(width, height)   # create scaled copy of pixmap
      self._qtObject.setPixmap(pixmap)              # set scaled pixmap to object
      self._qtObject.moveBy((width/2), (height/2))  # keep icon centered in place

   def getPixel(self, col, row):
      """Get the color of a pixel in the icon as a [r, g, b] list."""
      image = self._pixmap.toImage()      # convert pixmap to image
      color = image.pixelColor(col, row)  # get pixel color
      r = color.red()                     # extract RGB values
      g = color.green()
      b = color.blue()
      a = color.alpha()
      return [r, g, b]

   def setPixel(self, col, row, color):
      """Set the color of a pixel in the icon."""
      r, g, b = color  # extract RGB values
      a = 255          # set alpha to 255 (fully opaque)
      qtColor = _QtGui.QColor(r, g, b, a)     # create color object

      image = self._pixmap.toImage()          # convert pixmap to image
      image.setPixelColor(col, row, qtColor)  # set pixel color

      self._pixmap = _QtGui.QPixmap(image)    # create new pixmap from image

      scaledPixmap = self._pixmap.scaled(self.getWidth(), self.getHeight())  # create scaled copy of pixmap
      self._qtObject.setPixmap(scaledPixmap)   # set scaled pixmap to object

   def getPixels(self):
      """Get the color of all pixels in the icon as a 2D array of [r, g, b] values."""
      # we could iterate through pixels and extract each color,
      # but we can get better performance by converting the icon to a numpy array
      # and extracting pixels from there.
      image  = self._pixmap.toImage()                                # convert pixmap to image data
      image  = image.convertToFormat(_QtGui.QImage.Format_RGBA8888)  # convert to RGBA format
      ptr    = image.bits()                                          # get pointer bits to image data
      buffer = ptr.tobytes()                                         # safely convert to bytes
      arr    = np.frombuffer(buffer, dtype=np.uint8)                 # generate numpy array from image
      arr    = arr.reshape((image.height(), image.width(), 4))       # reshape to image dimensions
      rgb    = arr[:, :, :3]                                         # slice array to only RGB values
      return rgb.tolist()                                            # return as list

   def setPixels(self, pixels):
      """Set the color of all pixels in the icon."""
      # reversing the process in getPixels()...
      arr = np.array(pixels, dtype=np.uint8)  # generate numpy array from pixel list
      height, width, channels = arr.shape     # extract image dimensions

      if channels == 3:                       # add alpha channel, if not present
         alpha = np.full((height, width, 1), 255, dtype=np.uint8)
         arr   = np.concatenate((arr, alpha), axis=2)

      arr   = np.ascontiguousarray(arr)       # ensure contiguous array
      image = _QtGui.QImage(arr.data, width, height, width * 4, _QtGui.QImage.Format_RGBA8888)  # generate image
      image = image.copy()                    # detach image from numpy array (important!!)

      self._pixmap = _QtGui.QPixmap(image)                         # store image as pixmap
      scaledPixmap = self._pixmap.scaled(self.width, self.height)  # scale to expected dimensions
      self._qtObject.setPixmap(scaledPixmap)                       # set scaled pixmap


class Label(Graphics):
   """
   Labels are text with an included background box.
   """
   def __init__(self, text, alignment=LEFT, foregroundColor=Color.BLACK, backgroundColor=Color.CLEAR, rotation=0):
      """Create a new Label."""
      Graphics.__init__(self)

      textObject = _QtWidgets.QGraphicsTextItem(str(text))  # create foreground text
      r, g, b, a = foregroundColor.getRGBA()                # get color values
      qtForegroundColor = _QtGui.QColor(r, g, b, a)         # create Qt color
      textObject.setDefaultTextColor(qtForegroundColor)     # set foreground color

      background = _QtWidgets.QGraphicsRectItem(textObject.boundingRect())  # create background rectangle
      r, g, b, a = backgroundColor.getRGBA()        # get color values
      backgroundColor = _QtGui.QColor(r, g, b, a)   # create Qt color
      background.setBrush(backgroundColor)          # set background color
      background.setPen(_QtCore.Qt.PenStyle.NoPen)  # remove border

      self._qtObject  = _QtWidgets.QGraphicsItemGroup()
      self._qtObject.addToGroup(background)  # add background to group
      self._qtObject.addToGroup(textObject)  # add foreground to group

      self._qtTextObject       = textObject
      self._qtBackgroundObject = background
      Label.setAlignment(self, alignment)
      Label.setRotation(self, rotation)

   def __str__(self):
      return f'Label(text = "{self.getText()}", alignment = {self.getAlignment()}, foregroundColor = {self.getForegroundColor()}, backgroundColor = {self.getBackgroundColor()}, rotation = {self.getRotation()})'

   ##### OVERRIDDEN METHODS
   def setColor(self, color):
      """
      Changes the shape's color to the specified color.
      If color parameter is omitted, a color selection dialog box will be presented.
      TODO: add color selection box
      """
      r, g, b, a  = color.getRGBA()
      self._color = [r, g, b, a]
      qColor      = _QtGui.QColor(r, g, b, a)
      self._qtTextObject.setDefaultTextColor(qColor)

   def setFill(self, value):
      """
      Sets whether the shape is filled or not.
      """
      self._fill = bool(value)

      if self._fill:  # use outline color
         qColor = self._qtBackgroundObject.pen().color()
      else:           # use transparency
         qColor = _QtGui.QColor(0, 0, 0, 0)

      qBrush = _QtGui.QBrush(qColor)
      self._qtBackgroundObject.setBrush(qBrush)

   def setThickness(self, thickness):
      """
      Changes the shape outline's thickness to the specified value.
      """
      self._thickness = int(thickness)
      qPen = self._qtBackgroundObject.pen()
      qPen.setWidth(thickness)
      self._qtBackgroundObject.setPen(qPen)   # set shape's outline thickness

   ##### LABEL METHODS
   def getText(self):
      """
      Returns the label's text.
      """
      return self._qtTextObject.toPlainText()

   def setText(self, text):
      """
      Sets the label's text.
      """
      self._qtTextObject.setPlainText(str(text))

   def getForegroundColor(self):
      """
      Returns the label's foreground color.
      """
      return self.getColor()

   def setForegroundColor(self, color):
      """
      Sets the label's foreground color.
      """
      self.setColor(color)

   def getBackgroundColor(self):
      """
      Returns the label's background color.
      """
      r, g, b, a = self._backgroundColor
      return Color(r, g, b, a)

   def setBackgroundColor(self, color):
      """
      Sets the label's background color.
      """
      r, g, b, a = color.getRGBA()
      self._backgroundColor = [r, g, b, a]
      qColor = _QtGui.QColor(r, g, b, a)
      self._qtBackgroundObject.setBrush(qColor)

   def getAlignment(self):
      """
      Returns the label's horizontal text alignment.
      """
      return self._alignment

   def setAlignment(self, alignment):
      """
      Sets the label's horizontal text alignment.
      """
      self._alignment = alignment
      document        = self._qtTextObject.document()  # extract internal document
      textOption      = document.defaultTextOption()   # extract text formatting
      textOption.setAlignment(alignment)          # adjust alignment
      document.setDefaultTextOption(textOption)   # apply formatting changes

   def getFont(self):
      """
      Returns the label's font.
      """
      name, style, size = self._font
      return Font(name, style, size)

   def setFont(self, font):
      """
      Sets the label's font.
      """
      if not isinstance(font, Font):  # do some basic error checking
         raise TypeError(f'Label.setFont(): font must be a Font object (it was {type(font)})')

      name  = font.getName()
      style = font.getStyle()
      size  = font.getFontSize()
      self._font = [name, style, size]

      qFont = font._getQFont()
      self._qtTextObject.setFont(qFont)


#######################################################################################
# Music Controls
#######################################################################################
class HFader(MusicControl):
   """
   HFaders are horizontal, linear controls.
   """
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
                updateFunction=None, foreground=Color.RED, background=Color.BLACK,
                outline=Color.BLACK, thickness=3, rotation=0):
      """Creates a new HFader."""
      startValue = ((minValue + maxValue)//2) if startValue is None else startValue
      MusicControl.__init__(self, updateFunction)

      # calculate bounding box dimensions
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self._itemList
      self._backgroundShape = Rectangle(
         0, 0, width, height,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._foregroundShape = Rectangle(
         0, 0, width, height,
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._outlineShape = Rectangle(
         0, 0, width, height,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self._backgroundShape)
      self.add(self._foregroundShape)
      self.add(self._outlineShape)

      self.setPosition(cornerX, cornerY)
      self.setRotation(rotation)

      self._minValue = minValue
      self._maxValue = maxValue
      self.setValue(startValue)

   def __str__(self):
      x1, y1          = self._backgroundShape._getGlobalCornerPosition()
      width, height   = self._backgroundShape.getSize()
      x2              = x1 + width
      y2              = y1 + height
      foregroundColor = self._foregroundShape.getColor()
      backgroundColor = self._backgroundShape.getColor()
      outlineColor    = self._outlineShape.getColor()
      thickness       = self._outlineShape.getThickness()
      rotation        = self.getRotation()
      return f'HFader(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self._minValue}, maxValue = {self._maxValue}, startValue = {self.getValue()}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject fader-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add fader behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update fader value based on mouse position (args = [x, y])
         x = event.args[0] - self._backgroundShape.getX()  # get coordinates relative to fader
         valueRatio = x / self._backgroundShape.getWidth()        # calculate value ratio (0.0 to 1.0)
         valueRatio = max(0.0, min(1.0, valueRatio))              # clamp value ratio to range [0.0, 1.0]
         valueRange = self._maxValue - self._minValue             # calculate range of possible values
         value = int(self._minValue + (valueRatio * valueRange))  # calculate value within that range
         self.setValue(value)                                     # set fader value
         event.handled = True                                     # report event handling

   def setValue(self, value):
      """
      Sets the current value of the control, and update its appearance.
      """
      value = max(self._minValue, min(self._maxValue, value))  # clamp value to range
      MusicControl.setValue(self, value)  # update value and call user function

      # update appearance
      valueRatio = (value - self._minValue) / (self._maxValue - self._minValue)  # (0.0 to 1.0)

      width, height = self._backgroundShape.getSize()
      x,     y      = self._backgroundShape._getGlobalCornerPosition()
      padding       = self._outlineShape.getThickness() / 2

      fWidth  = (width  - (2 * padding))  # find maximum fader bar dimensions
      fHeight = (height - (2 * padding))
      fx      = x + padding
      fy      = y + padding

      fWidth  = fWidth * valueRatio  # adjust for value

      self._foregroundShape.setPosition(fx, fy)
      self._foregroundShape.setSize(fWidth, fHeight)


class VFader(HFader):
   """
   VFaders are vertical, linear controls.
   """
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
               updateFunction=None, foreground=Color.RED, background=Color.BLACK,
               outline=Color.BLACK, thickness=3, rotation=0):
      """Creates a new VFader."""
      # call parent constructor
      HFader.__init__(self, x1, y1, x2, y2, minValue, maxValue, startValue,
                      updateFunction, foreground, background,
                      outline, thickness, rotation)

   def __str__(self):
      x1, y1          = self._backgroundShape._getGlobalCornerPosition()
      width, height   = self._backgroundShape.getSize()
      x2              = x1 + width
      y2              = y1 + height
      foregroundColor = self._foregroundShape.getColor()
      backgroundColor = self._backgroundShape.getColor()
      outlineColor    = self._outlineShape.getColor()
      thickness       = self._outlineShape.getThickness()
      rotation        = self.getRotation()
      return f'VFader(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self._minValue}, maxValue = {self._maxValue}, startValue = {self.getValue()}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject fader-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add fader behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update fader value based on mouse position (args = [x, y])
         y = event.args[1] - self._backgroundShape.getY()   # get coordinates relative to fader
         valueRatio = 1 - (y / self._backgroundShape.getHeight())  # calculate value ratio (0.0 to 1.0)
         valueRatio = max(0.0, min(1.0, valueRatio))               # clamp value ratio to range [0.0, 1.0]
         valueRange = self._maxValue - self._minValue              # calculate range of possible values
         value = int(self._minValue + (valueRatio * valueRange))   # calculate value within that range
         self.setValue(value)                                      # set fader value
         event.handled = True                                      # report event handling

   def setValue(self, value):
      """
      Sets the current value of the control, and update its appearance.
      """
      value = max(self._minValue, min(self._maxValue, value))  # clamp value to range
      MusicControl.setValue(self, value)  # update value and call user function

      # update appearance
      valueRatio = (value - self._minValue) / (self._maxValue - self._minValue)  # (0.0 to 1.0)

      width, height = self._backgroundShape.getSize()
      x,     y      = self._backgroundShape._getGlobalCornerPosition()
      padding       = self._outlineShape.getThickness() / 2

      fWidth  = (width  - (2 * padding))  # find maximum fader bar dimensions
      fHeight = (height - (2 * padding))
      fx      = x + padding
      fy      = y + padding

      fy      = fy + int((fHeight * (1 - valueRatio)) / 2)  # adjust for value
      fHeight = fHeight * valueRatio

      self._foregroundShape.setPosition(fx, fy)
      self._foregroundShape.setSize(fWidth, fHeight)


class Rotary(MusicControl):
   """
   Rotaries are circular controls.
   """
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
               updateFunction=None, foreground=Color.RED, background=Color.BLACK,
               outline=Color.BLUE, thickness=3, arcWidth=300, rotation=0):
      """Creates a new Rotary."""
      # calculate startValue if one isn't provided
      startValue = ((minValue + maxValue)//2) if startValue is None else startValue
      MusicControl.__init__(self, updateFunction)

      # calculate bounding box
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      startAngle = 90 + arcWidth//2
      endAngle   = startAngle + arcWidth

      # store direct references to each default component
      # since users can manipulate the Group by adding and removing items,
      # we need a way to identify the original components without referencing self.items
      self._backgroundShape = Arc(
         0, 0, width, height,
         startAngle, endAngle,
         style=PIE,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._foregroundShape = Arc(
         0, 0, width, height,
         startAngle, endAngle,
         style=PIE,
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._outlineShape = Arc(
         0, 0, width, height,
         startAngle, endAngle,
         style=PIE,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self._backgroundShape)  # add each component to group
      self.add(self._foregroundShape)
      self.add(self._outlineShape)

      self.setPosition(cornerX, cornerY)
      self.setRotation(rotation)

      self._minValue = minValue
      self._maxValue = maxValue
      self._arcWidth = arcWidth
      self.setValue(startValue)

   def __str__(self):
      x1, y1          = self._backgroundShape._getGlobalCornerPosition()
      width, height   = self._backgroundShape.getSize()
      x2              = x1 + width
      y2              = y1 + height
      foregroundColor = self._foregroundShape.getColor()
      backgroundColor = self._backgroundShape.getColor()
      outlineColor    = self._outlineShape.getColor()
      thickness       = self._outlineShape.getThickness()
      rotation        = self.getRotation()
      return f'Rotary(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self._minValue}, maxValue = {self._maxValue}, startValue = {self.getValue()}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, arcWidth = {self._arcWidth}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject rotary-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add rotary behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update rotary value based on mouse position (args = [x, y])
         x1, y1 = event.args                                # event position
         x2, y2 = self._backgroundShape.getPosition()       # rotary position
         x = x1 - x2                            # event position, relative to rotary position
         y = y1 - y2
         dx = x - (self._backgroundShape.getWidth() // 2)   # get vector from center to mouse
         dy = (self._backgroundShape.getHeight() // 2) - y
         mouseAngle = np.degrees(np.arctan2(dy, dx)) % 360  # angle in degrees
         startAngle = 90 + self._arcWidth//2                # starting angle of rotary
         arcWidth   = (startAngle - mouseAngle) % 360       # arcWidth from start angle to mouse angle

         if 0 <= arcWidth <= self._arcWidth:
            # mouse is within arc, calculate value
            valueRatio = arcWidth / self._arcWidth       # calculate value ratio (0.0 to 1.0)
            valueRatio = max(0.0, min(1.0, valueRatio))  # clamp value ratio to range [0.0, 1.0]
            valueRange = self._maxValue - self._minValue
            value = int(np.round(self._minValue + (valueRatio * valueRange)))
            self.setValue(value)                         # set rotary value
            event.handled = True

   def setValue(self, value):
      """
      Sets the current value of the control, and update its appearance.
      """
      value = max(self._minValue, min(self._maxValue, value))  # clamp value to range
      MusicControl.setValue(self, value)  # update value and call user function

      # since Arc can't adjust its arcWidth, we need to redraw the Arc
      # we could create a new Arc object, but since we expect this to update rapidly,
      # we want to be a little more memory efficient... so we update the Qt object directly
      valueRatio    = (value - self._minValue) / (self._maxValue - self._minValue)  # 0.0 to 1.0
      width, height = self._backgroundShape.getSize()
      startAngle    = self._backgroundShape._startAngle
      arcWidth      = self._arcWidth * valueRatio

      path = _QtGui.QPainterPath()                           # create new path
      path.arcMoveTo(0, 0, width, height, startAngle)        # first point
      path.arcTo(0, 0, width, height, startAngle, -arcWidth)  # arc to end point
      path.lineTo(width//2, height//2)                       # line to center
      path.closeSubpath()                                    # back to start
      self._foregroundShape._qtObject.setPath(path)          # set new arc path


class Push(MusicControl):
   """
   Pushes are rectangular buttons that reset when released.
   """
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, thickness=3, rotation=0):
      """Creates a new Push button."""
      MusicControl.__init__(self, updateFunction)

      # calculate bounding box
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      padding = thickness//2 + 1

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.items
      self._backgroundShape = Rectangle(
         0, 0, width, height,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._foregroundShape = Rectangle(
         padding, padding, (width - padding), (height - padding),
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._outlineShape = Rectangle(
         0, 0, width, height,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self._backgroundShape)  # add each component to group
      self.add(self._foregroundShape)
      self.add(self._outlineShape)

      self.setPosition(cornerX, cornerY)
      self.setRotation(rotation)

      self.setValue(False)

   def __str__(self):
      x1, y1          = self._backgroundShape._getGlobalCornerPosition()
      width, height   = self._backgroundShape.getSize()
      x2              = x1 + width
      y2              = y1 + height
      foregroundColor = self._foregroundShape.getColor()
      backgroundColor = self._backgroundShape.getColor()
      outlineColor    = self._outlineShape.getColor()
      thickness       = self._outlineShape.getThickness()
      rotation        = self.getRotation()
      return f'Push(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject push button-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add push button behavior
      if event.type in ["mouseDown"]:
         self.setValue(True)
         event.handled = True

      elif event.type in ["mouseUp", "mouseExit"]:
         self.setValue(False)
         event.handled = True

   def setValue(self, value):
      MusicControl.setValue(self, value)

      # update appearance
      if value:
         self._foregroundShape._qtObject.show()
      else:
         self._foregroundShape._qtObject.hide()


class Toggle(Push):
   """
   Toggles are rectangular buttons that change when clicked.
   """
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, thickness=3, rotation=0):
      """
      Creates a new Toggle button.
      """
      Push.__init__(self, x1, y1, x2, y2, updateFunction, foreground, background, outline, thickness, rotation)

   def __str__(self):
      x1, y1          = self._backgroundShape._getGlobalCornerPosition()
      width, height   = self._backgroundShape.getSize()
      x2              = x1 + width
      y2              = y1 + height
      foregroundColor = self._foregroundShape.getColor()
      backgroundColor = self._backgroundShape.getColor()
      outlineColor    = self._outlineShape.getColor()
      thickness       = self._outlineShape.getThickness()
      rotation        = self.getRotation()
      return f'Toggle(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject toggle-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add toggle button behavior
      if event.type in ["mouseDown"]:
         self.setValue(not self.getValue())
         event.handled = True


class XYPad(MusicControl):
   """
   XYPads are grids that track values in two dimensions.
   """
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, outlineThickness=2, trackerRadius=10, crosshairsThickness=None, rotation=0):
      """
      Creates a new XYPad.
      """
      MusicControl.__init__(self, updateFunction)

      if crosshairsThickness is None:
         crosshairsThickness = outlineThickness

      # calculate bounding box
      cornerX = min(x1, x2)
      cornerY = min(y1, y2)
      width   = abs(x1 - x2)
      height  = abs(y1 - y2)

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.items
      self._backgroundShape = Rectangle(
         0, 0, width, height,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self._trackerXLine = Line(
         0, 0, 0, height,  # vertical line
         color=foreground,
         thickness=crosshairsThickness,
         rotation=0
      )
      self._trackerYLine = Line(
         0, 0, width, 0,  # horizontal line
         color=foreground,
         thickness=crosshairsThickness,
         rotation=0
      )
      self._foregroundShape = Circle(
         width/2, height/2,
         trackerRadius,
         color=foreground,
         fill=False,
         thickness=crosshairsThickness,
         rotation=0
      )
      self._outlineShape = Rectangle(
         0, 0, width, height,
         color=outline,
         fill=False,
         thickness=outlineThickness,
         rotation=0
      )

      self.add(self._backgroundShape)
      self.add(self._trackerXLine)
      self.add(self._trackerYLine)
      self.add(self._foregroundShape)
      self.add(self._outlineShape)

      centerX, centerY = self._backgroundShape._getCenterPosition()
      self.setValue(centerX, centerY)

      # Drawable
      self.setPosition(cornerX, cornerY)
      self.setRotation(rotation)

   def __str__(self):
      x1, y1              = self._backgroundShape._getGlobalCornerPosition()
      width, height       = self._backgroundShape.getSize()
      x2                  = x1 + width
      y2                  = y1 + height
      foregroundColor     = self._foregroundShape.getColor()
      backgroundColor     = self._backgroundShape.getColor()
      outlineColor        = self._outlineShape.getColor()
      outlineThickness    = self._outlineShape.getThickness()
      trackerRadius       = self._foregroundShape.getRadius()
      crosshairsThickness = self._foregroundShape.getThickness()
      rotation            = self.getRotation()

      return f'XYPad(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self._function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, outlineThickness = {outlineThickness}, trackerRadius = {trackerRadius}, crosshairsThickness = {crosshairsThickness}, rotation = {rotation})'

   # OVERRIDDEN METHODS
   def _receiveEvent(self, event):
      """
      Inject XYPad-specific events to the event handler.
      """
      # first, look for user event handlers
      MusicControl._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add XYPad behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         x1, y1 = self._backgroundShape.getPosition()  # XYpad position
         x2, y2 = event.args                           # event location
         x = x2 - x1                                   # local event coordinates, relative to XYPad
         y = y2 - y1

         self.setValue(x, y)
         event.handled = True

   def setValue(self, x, y):
      """
      Sets the current (x,y) position of the XYPad tracker.
      """
      width, height = self._backgroundShape.getSize()
      x = max(0, min(x, width))  # clamp to XYPad bounds
      y = max(0, min(y, height))
      MusicControl.setValue(self, [x, y])  # set value and call user function

      # update appearance
      x1, y1 = self._backgroundShape.getPosition()
      x = x + x1  # get global coordinates
      y = y + y1

      self._trackerXLine.setX(x)
      self._trackerYLine.setY(y)
      self._foregroundShape._setCenterPosition(x, y)


#######################################################################################
# Controls (Event behavior defined by Qt)
#######################################################################################
class Button(Control):
   def __init__(self, text="", function=None):
      Control.__init__(self)

      # create qt object
      qtObject = _QtWidgets.QPushButton(text)
      qtObject.adjustSize()                    # adjust size to fit text
      qtObject.clicked.connect(function)       # connect button to function

      # initialize internal properties
      self._qtObject = qtObject
      self._function = function
      self.setColor(Color.LIGHT_GRAY)

   def __str__(self):
      return f'Button(text = "{self.getText()}", function = {self._function})'

   def setColor(self, color):
      """Set the button color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')

      self._qtObject.setStyleSheet(
         f"""
         QPushButton {{
            background-color: {color.getHex()};
            color: black;
         }}
         QPushButton::pressed {{
            background-color: {color.darker().getHex()};
         }}
         """)

   def getText(self):
      """Returns the Button's text string."""
      return self._qtObject.text()

   def setText(self, text):
      """Sets the Button's text string."""
      self._qtObject.setText(text)


class CheckBox(Control):
   def __init__(self, text="", function=None):
      Control.__init__(self)

      qtObject = _QtWidgets.QCheckBox(text)
      qtObject.adjustSize()                    # adjust size to fit text
      qtObject.stateChanged.connect(function)  # connect checkbox to function

      self._qtObject = qtObject
      self._function = function
      self.setColor(Color.CLEAR)

   def __str__(self):
      return f'CheckBox(text = "{self.getText()}", function = {self._function})'

   def isChecked(self):
      """Returns True if the checkbox is checked, False otherwise."""
      return self._qtObject.isChecked()

   def check(self):
      """Checks the checkbox."""
      self._qtObject.setChecked(True)

   def uncheck(self):
      """Unchecks the checkbox."""
      self._qtObject.setChecked(False)

   def setColor(self, color):
      """Set the checkbox background color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')

      self._qtObject.setStyleSheet(
         f"""
         QCheckBox {{
            background-color: {color.getHex()};
            color: black;
         }}
         """)


class Slider(Control):
   def __init__(self, orientation=HORIZONTAL, lower=0, upper=100, start=None, function=None):
      Control.__init__(self)

      start = start if start is not None else ((lower + upper)//2)

      qtObject = _QtWidgets.QSlider(orientation)
      qtObject.setRange(lower, upper)
      qtObject.setValue(start)                 # set default value
      qtObject.adjustSize()                    # adjust size
      qtObject.valueChanged.connect(function)  # connect slider to function

      # initialize internal properties
      self._qtObject    = qtObject
      self._function    = function
      self._orientation = orientation
      self._lower       = lower
      self._upper       = upper
      # self.setColor(Color.BLACK)

   def __str__(self):
      return f'Slider(orientation = {self._orientation}, lower = {self._lower}, upper = {self._upper}, start = {self.getValue()}, function = {self._function})'

   def getValue(self):
      """Returns the current value of the slider."""
      return self._qtObject.value()

   def setValue(self, value):
      """Sets the current value of the slider."""
      self._qtObject.setValue(value)

   def setColor(self, color):
      """Set the slider color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')
      ## TODO: set color of slider - which part??
      print(f"{type(self)}.setColor(): setColor not yet implemented.")


class DropDownList(Control):
   def __init__(self, items=[], function=None):
      Control.__init__(self)

      qtObject = _QtWidgets.QComboBox()
      qtObject.addItems(items)
      qtObject.activated.connect(self._callback)  # connect dropdown to function
      qtObject.adjustSize()                       # adjust size to fit text

      self._qtObject = qtObject
      self._items    = items
      self._function = function
      self.setColor(Color.LIGHT_GRAY)  # set default color

   def __str__(self):
      return f'DropDownList(items = {self._items}, function = {self._function})'

   def _callback(self, index):
      """Calls user function using item at given index."""
      if self._function is not None and callable(self._function):
         self._function(self._items[index])  # call function with selected item

   def setColor(self, color):
      """Set the dropdown list color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')

      self._qtObject.setStyleSheet(
         f"""
         QComboBox {{
            background-color: {color.getHex()};
            color: black;
         }}
         QComboBox QAbstractItemView {{
            background-color: {color.getHex()};
            color: black;
         }}
         """)


class TextField(Control):
   def __init__(self, text="", columns=8, function=None):
      Control.__init__(self)

      self._qtObject = _QtWidgets.QLineEdit(str(text))
      self._qtObject.returnPressed.connect(self._callback)
      self._columns  = columns
      self._function = function

      # calculate width and height, based on default font and system-specific margins and framing
      fontMetrics = self._qtObject.fontMetrics()
      charWidth   = fontMetrics.horizontalAdvance('M')
      charHeight  = fontMetrics.lineSpacing()
      margins     = self._qtObject.textMargins()

      frameOption = _QtWidgets.QStyleOptionFrame()  # grab and set system text box frame
      self._qtObject.initStyleOption(frameOption)
      frame       = self._qtObject.style().pixelMetric(
         _QtWidgets.QStyle.PixelMetric.PM_DefaultFrameWidth, frameOption, self._qtObject
      )

      horizontalMargins = margins.left() + margins.right()
      verticalMargins   = margins.top() + margins.bottom()

      self._width  = (charWidth * columns) + horizontalMargins + (2 * frame)
      self._height = (charHeight) + verticalMargins + (2 * frame)

      self._qtObject.setFixedSize(self._width, self._height)

      self.setColor(Color.WHITE)

   def __str__(self):
      return f'TextField(text = "{self.getText()}", columns = {self._columns}, function = {self._function})'

   def _callback(self):
      """Calls user function using text in field."""
      if self._function is not None and callable(self._function):
         self._function(self._qtObject.text())  # call function with text in field

   def setColor(self, color):
      """Set the text field color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')

      self._qtObject.setStyleSheet(
         f"""
         QLineEdit {{
            background-color: {color.getHex()};
            color: black;
         }}
         """)

   def getText(self):
      """Returns the text in the field."""
      return self._qtObject.text()

   def setText(self, text):
      """Sets the text in the field."""
      self._qtObject.setText(text)

   def setFont(self, font, resize=True):
      """
      Sets the font of the text field.
      'resize' controls whether the text field automatically adjusts its width and height.
      """
      if not isinstance(font, Font):  # do some basic error checking
         raise TypeError(f'TextField.setFont(): font must be a Font object (it was {type(font)})')

      qFont = font._getQFont()
      self._qtObject.setFont(qFont)  # update font

      if resize:
         fontMetrics = _QtGui.QFontMetrics(qFont)  # get font information
         charWidth   = fontMetrics.horizontalAdvance('M')
         charHeight  = fontMetrics.lineSpacing()
         margins     = self._qtObject.textMargins()

         frameOption = _QtWidgets.QStyleOptionFrame()  # grab and set system text box frame
         self._qtObject.initStyleOption(frameOption)
         frame       = self._qtObject.style().pixelMetric(
            _QtWidgets.QStyle.PixelMetric.PM_DefaultFrameWidth, frameOption, self._qtObject
         )

         horizontalMargins = margins.left() + margins.right()
         verticalMargins   = margins.top() + margins.bottom()

         self._width  = (charWidth) + horizontalMargins + (2 * frame)
         self._height = (charHeight) + verticalMargins + (2 * frame)

         self._qtObject.setFixedSize(self._width, self._height)

class TextArea(Control):
   def __init__(self, text="", columns=8, rows=5):
      Control.__init__(self)

      self._qtObject = _QtWidgets.QTextEdit(str(text))
      self._columns  = columns
      self._rows     = rows
      self.setColor(Color.WHITE)  # set default color

   def __str__(self):
      return f'TextArea(text = "{self.getText()}", columns = {self._columns}, rows = {self._rows})'

   def setColor(self, color):
      """Set the text area color."""
      if not isinstance(color, Color):  # do some basic error checking
         raise TypeError(f'{type(self)}.setColor(): color must be a Color object (it was {type(color)})')

      self._qtObject.setStyleSheet(
         f"""
         QTextEdit {{
            background-color: {color.getHex()};
            color: black;
         }}
         """)

   def getText(self):
      """Returns the text in the field."""
      return self._qtObject.toPlainText()

   def setText(self, text):
      """Sets the text in the field."""
      self._qtObject.setText(text)

   def setFont(self, font, resize=True):
      """
      Sets the font of the text field.
      'resize' controls whether the text field automatically adjusts its width and height.
      """
      if not isinstance(font, Font):  # do some basic error checking
         raise TypeError(f'{type(self)}.setFont(): font must be a Font object (it was {type(font)})')

      qFont = font._getQFont()
      self._qtObject.setFont(qFont)  # update font

      if resize:
         fontMetrics = _QtGui.QFontMetrics(qFont)  # get font information
         charWidth   = fontMetrics.horizontalAdvance('M')
         charHeight  = fontMetrics.lineSpacing()
         margins     = self._qtObject.textMargins()

         frameOption = _QtWidgets.QStyleOptionFrame()  # grab and set system text box frame
         self._qtObject.initStyleOption(frameOption)
         frame       = self._qtObject.style().pixelMetric(
            _QtWidgets.QStyle.PixelMetric.PM_DefaultFrameWidth, frameOption, self._qtObject
         )

         horizontalMargins = margins.left() + margins.right()
         verticalMargins   = margins.top() + margins.bottom()

         self._width  = (charWidth) + horizontalMargins + (2 * frame)
         self._height = (charHeight) + verticalMargins + (2 * frame)

         self._qtObject.setFixedSize(self._width, self._height)


class Menu():
   def __init__(self, menuName):
      self._qtObject = _QtWidgets.QMenu(menuName)
      self._name     = menuName

   def __str__(self):
      return f'Menu(menuName = "{self._name}")'

   def __repr__(self):
      return str(self)

   def addItem(self, item="", functionName=None):
      """Add an item to the menu."""
      qtAction = _QtGui.QAction(item, self._qtObject)  # create new action
      if callable(functionName):
         qtAction.triggered.connect(functionName)      # attach callback, if any
      self._qtObject.addAction(qtAction)               # add action to menu

   def addItemList(self, itemList=[""], functionNameList=[None]):
      """Add a list of items to the menu."""
      for i in range(len(itemList)):
         # get item and function (if available, None otherwise)
         item         = itemList[i]
         functionName = functionNameList[i] if i < len(functionNameList) else None
         self.addItem(item, functionName)

   def addSeparator(self):
      """Add a separator to the menu."""
      separator = _QtGui.QAction(self._qtObject)  # create new action
      separator.setSeparator(True)                # set action as separator
      self._qtObject.addAction(separator)         # add separator to menu

   def addSubmenu(self, menu):
      """Add a submenu to this menu."""
      if not isinstance(menu, Menu):  # do some basic error checking
         raise TypeError(f'{type(self)}.addSubmenu(): menu must be a Menu object (it was {type(menu)})')
      self._qtObject.addMenu(menu._qtObject)  # add submenu to this menu

   def enable(self):
      """Enable the menu."""
      self._qtObject.setEnabled(True)

   def disable(self):
      """Disable the menu."""
      self._qtObject.setEnabled(False)


#######################################################################################
# Test
#######################################################################################

if __name__ == "__main__":

   def testMenu():
      d = Display()

      menu = Menu("Test Menu")
      menu.addItem("Test Item 1", lambda: print("Test Item 1 clicked"))
      menu.addSeparator()
      menu.addItem("Test Item 2", lambda: print("Test Item 2 clicked"))

      submenu = Menu("Test Submenu")
      submenu.addItem("Submenu Item 1", lambda: print("Submenu Item 1 clicked"))
      submenu.addItem("Submenu Item 2", lambda: print("Submenu Item 2 clicked"))
      menu.addSubmenu(submenu)

      menu.addItem("Test Item 3", lambda: print("Test Item 3 clicked"))
      menu.addSeparator()
      menu.addItem("Test Item 4", lambda: print("Test Item 4 clicked"))

      # menu.disable()
      # submenu.disable()

      d.addMenu(menu)
      d.addPopupMenu(menu)


   def testShapes():
      d = Display()

      oval = Oval(50, 50, 150, 100, color=Color.RED, fill=True)
      d.add(oval)

      circle = Circle(200, 200, 50, color=Color.BLUE, fill=False)
      d.add(circle)

      point = Point(300, 300, color=Color.BLACK)
      d.add(point)

      arc = Arc(350, 50, 450, 150, startAngle=0, endAngle=270, style=OPEN, color=Color.ORANGE, fill=True)
      d.add(arc)

      arcCircle = ArcCircle(500, 200, 50, startAngle=0, endAngle=180, style=PIE, color=Color.GRAY, fill=True)
      d.add(arcCircle)

      line = Line(50, 200, 150, 300, color=Color.MAGENTA, thickness=2)
      d.add(line)

      polyline = PolyLine([50, 50, 150], [50, 100, 25], color=Color.GREEN, thickness=2)
      d.add(polyline)

      polygon = Polygon([200, 250, 300], [50, 150, 100], color=Color.YELLOW, fill=True)
      d.add(polygon)

      rectangle = Rectangle(350, 50, 450, 150, color=Color.CYAN, fill=False)
      d.add(rectangle)

      icon = Icon("images/de-brazzas-monkey.jpg", 100, 100)
      d.add(icon)


   def testEvents():
      d = Display()

      centerX = d.getWidth()/2
      centerY = d.getHeight()/2
      length  = 100
      shape = Rectangle(0, 0, length, length, Color.RED, True)
      shape.setPosition(centerX-length/2, centerY-length/2)
      d.add(shape)

      d.onMouseClick(lambda x,y: print("Display Mouse Click at", x, y))
      shape.onMouseClick(lambda x,y: print("Shape Mouse Click at", x, y))

      d.onMouseDown(lambda x,y: print("Display Mouse Down at", x, y))
      shape.onMouseDown(lambda x,y: print("Shape Mouse Down at", x, y))

      d.onMouseUp(lambda x,y: print("Display Mouse Up at", x, y))
      shape.onMouseUp(lambda x,y: print("Shape Mouse Up at", x, y))

      d.onMouseMove(lambda x,y: print("Display Mouse Move at", x, y))
      shape.onMouseMove(lambda x,y: print("Shape Mouse Move at", x, y))

      d.onMouseDrag(lambda x,y: print("Display Mouse Drag at", x, y))
      shape.onMouseDrag(lambda x,y: print("Shape Mouse Drag at", x, y))

      d.onMouseEnter(lambda x,y: print("Display Mouse Enter at", x, y))
      shape.onMouseEnter(lambda x,y: print("Shape Mouse Enter at", x, y))

      d.onMouseExit(lambda x,y: print("Display Mouse Exit at", x, y))
      shape.onMouseExit(lambda x,y: print("Shape Mouse Exit at", x, y))

      d.onKeyDown(lambda x: print("Display Key Down", x))
      shape.onKeyDown(lambda x: print("Shape Key Down", x))

      d.onKeyUp(lambda x: print("Display Key Up", x))
      shape.onKeyUp(lambda x: print("Shape Key Up", x))

      d.onKeyType(lambda x: print("Display Key Type", x))
      shape.onKeyType(lambda x: print("Shape Key Type", x))


   def testToolTip():
      d = Display()
      d.setToolTipText("This is a display tooltip")

      label = Label("Hello World!", LEFT, Color.BLACK, Color.CYAN)
      label.setPosition(50, 50)
      label.setToolTipText("This is a label tooltip")
      d.add(label)

      icon = Icon("images/de-brazzas-monkey.jpg", 100, 100)
      icon.setPosition(200, 50)
      icon.setToolTipText("This is an icon tooltip")
      d.add(icon)

      circle = Circle(300, 100, 50, Color.RED, True)
      circle.setToolTipText("This is a circle tooltip")
      d.add(circle)


   def testWidgets():
      d = Display()

      button = Button("Click Me", lambda: print("Button clicked!"))
      button.setPosition(50, 50)
      d.add(button)

      checkbox = CheckBox("Check Me", lambda: print(f'Checkbox state: {checkbox.isChecked()}!'))
      checkbox.setPosition(50, 100)
      d.add(checkbox)

      hSlider = Slider(HORIZONTAL, 0, 100, 50, lambda: print(f'Horizontal slider value: {hSlider.getValue()}!'))
      hSlider.setPosition(50, 150)
      d.add(hSlider)

      vSlider = Slider(VERTICAL, 0, 200, 50, lambda: print(f'Vertical slider value: {vSlider.getValue()}!'))
      vSlider.setPosition(150, 50)
      d.add(vSlider)

      dropdown = DropDownList(["Option 1", "Option 2", "Option 3"], lambda s: print(f'Dropdown selected: {s}!'))
      dropdown.setPosition(50, 250)
      d.add(dropdown)

      textField = TextField("Type here", 20, lambda s: print(f'Text field input: {s}!'))
      textField.setPosition(50, 300)
      d.add(textField)

      textArea = TextArea("Type here", 20, 5)
      textArea.setPosition(300, 50)
      d.add(textArea)


   def testControls():
      d = Display()

      hFader = HFader(50, 50, 150, 100, 0, 100, 50, lambda v: print(f'Horizontal fader value: {v}!'))
      d.add(hFader)

      vFader = VFader(50, 150, 100, 250, 0, 100, 50, lambda v: print(f'Vertical fader value: {v}!'))
      d.add(vFader)

      rotary = Rotary(50, 275, 150, 375, 0, 100, 50, lambda v: print(f'Rotary value: {v}!'))
      d.add(rotary)

      push = Push(200, 50, 250, 100, lambda v: print(f'Push button value: {v}!'))
      d.add(push)

      toggle = Toggle(200, 150, 250, 200, lambda v: print(f'Toggle button value: {v}!'))
      d.add(toggle)

      xyPad = XYPad(300, 50, 400, 150, lambda x,y: print(f'XYPad value: {x}, {y}!'))
      d.add(xyPad)

   def testZOrder():
      d = Display()

      # Create two overlapping rectangles
      rect1 = Rectangle(50, 50, 150, 150, Color.RED, True)
      rect2 = Rectangle(100, 100, 200, 200, Color.BLUE, True)
      rect3 = Rectangle(150, 150, 250, 250, Color.GREEN, True)

      # Add them to the display
      d.add(rect1)
      d.add(rect2)
      d.add(rect3)


      print(f'Initial Z-Orders:')
      print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # remove rectangle 2
      d.remove(rect2)

      print(f'\nAfter removing Rectangle 2:')
      print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # add rectangle 2 back to front
      # d.add(rect2)

      # print(f'\nAfter adding Rectangle 2 to front:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # remove rectangle 3
      # d.remove(rect3)

      # print(f'\nAfter removing Rectangle 3:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')

      # # insert rectangle 3 to middle
      # d.addOrder(rect3, 1)
      # print(f'\nAfter inserting Rectangle 3 to middle:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # remove rectangle 1
      # d.remove(rect1)

      # print(f'\nAfter removing Rectangle 1:')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # add rectangle 1 to back
      # d.addOrder(rect1, 99)

      # print(f'\nAfter adding Rectangle 1 to back:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')


   # testMenu()
   # testShapes()
   # testEvents()
   # testToolTip()
   # testWidgets()
   # testControls()
   # testZOrder()
