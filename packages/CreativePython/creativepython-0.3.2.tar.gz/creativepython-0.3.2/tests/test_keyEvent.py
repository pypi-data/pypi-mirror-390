from gui import *

d = Display()

# c1 = d.drawCircle(300, 200, 100, fill=False)
# c2 = d.drawCircle(300, 200, 200, fill=False)

#c1 = Circle(300, 200, 100, fill=False)
c2 = Circle(300, 200, 200, fill=True)


def printChar(char):
   print(char)

#c1.onKeyDown(printChar)
c2.onKeyDown(printChar)
#c1.onKeyType(printChar)
c2.onKeyType(printChar)
d.onKeyDown(printChar)
d.onKeyType(printChar)

#d.add(c1)
d.add(c2)
