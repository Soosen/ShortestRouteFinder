from importlib.resources import path
import math
import numpy
import arcade
import pickle
from collections import deque


BACKGROUND = arcade.load_texture("resizedTopomapRoute.png")
SCREEN_WIDTH = BACKGROUND.size[0]
SCREEN_HEIGHT = BACKGROUND.size[1]

""" LEFT = 7.99444469584035
BOTTOM = 51.913459988168185
RIGHT = 8.091850568917282
TOP = 51.96304377377246  """

LEFT = 7.99470
BOTTOM = 51.91529
RIGHT = 8.09310
TOP = 51.96261
class Utilities:

    @staticmethod
    def toRadians(degree):
        one_deg = (math.pi) / 180
        return (one_deg * degree)

    @staticmethod
    def distance(lat1, long1, lat2, long2):
        lat1 = Utilities.toRadians(lat1)
        long1 = Utilities.toRadians(long1)
        lat2 = Utilities.toRadians(lat2)
        long2 = Utilities.toRadians(long2)
        
        dlong = long2 - long1
        dlat = lat2 - lat1
    
        ans = math.pow(math.sin(dlat / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlong / 2), 2)
    
        ans = 2 * math.asin(math.sqrt(ans))
    
        R = 6371
        
        ans = ans * R
    
        return ans

    @staticmethod
    def toPixels(long, lat):
        FULLWIDTH = RIGHT - LEFT
        FULLHEIGHT = TOP - BOTTOM

        curX = long - LEFT
        curY = lat - BOTTOM

        xRatio = curX/FULLWIDTH
        yRatio = curY/FULLHEIGHT

        return round(SCREEN_WIDTH * xRatio), round(SCREEN_HEIGHT * yRatio)

    @staticmethod
    def toGeographical(x, y):
        FULLWIDTH = RIGHT - LEFT
        FULLHEIGHT = TOP - BOTTOM

        xRatio = x/SCREEN_WIDTH
        yRatio = y/SCREEN_HEIGHT

        return LEFT + (xRatio * FULLWIDTH), BOTTOM + (yRatio * FULLHEIGHT)

    @staticmethod
    def pytagoras(x1, y1, x2, y2):
        return math.sqrt(math.pow((x1-x2), 2) + math.pow((y1-y2), 2))

    @staticmethod
    def findClosesPoint(x, y, points):
        closestPoint = None
        closestDistance = 9999999
        for p in points:
            if(Utilities.pytagoras(p.xPix, p.yPix, x, y) < closestDistance):
                closestPoint = p
                closestDistance = Utilities.pytagoras(p.xPix, p.yPix, x, y)

        return closestPoint
    
    @staticmethod
    def listToJson(list):
        retList = numpy.array([])
        for e in list:
            retList = numpy.append(retList, e.toJson())
        
        return retList

    @staticmethod
    def load_data(path):
        try:
            with open(path, "rb") as f:
                x = pickle.load(f)
        except Exception as e:
            print(e)
            x = []
        return x

    @staticmethod
    def save_data(data, path):
        with open(path, "wb") as f:
            pickle.dump(data, f)

    @staticmethod
    def isInList(element, list):
        for e in list:
            if(element == e):
                return True
        return False

    @staticmethod
    def areAllPointsReachable(startingPoint):
        queue = deque()
        visited = list()
        queue.append(startingPoint)
        
        while queue:
            current = queue.pop()

            if(not Utilities.isInList(current, visited)):
                visited.append(current)

            for n in current.neighbours:
                if(not Utilities.isInList(n, visited)):
                    queue.append(n)

        return visited

    @staticmethod
    def cleanPoints(connected, all):
        for a in all:
            if(not Utilities.isInList(a, connected)):
                for c in connected:
                    c.neighbours.remove(a)

                all.remove(a)

        return all

    @staticmethod
    def allPointsVisited(visited, toVisit):
        for tv in toVisit:
            if(not Utilities.isInList(tv, visited)):
                return False

        return True

    @staticmethod
    def countUniqueElements(listA):
        temp = list()
        for e in listA:
            if e not in temp:
                temp.append(e)
        
        return len(temp)

    @staticmethod
    def findIndexWithHighestHeurusticValue(nodes):
        highestValue = -1
        highestIndex = -1

        for i in range(nodes.size):
            if(nodes[i].heurustic > highestValue or highestValue == -1):
                highestValue = nodes[i].heurustic
                highestIndex = i

        return highestIndex

    @staticmethod
    def findIndexWithLowestHeurusticValue(nodes):
        lowestValue = -1
        lowestIndex = -1

        for i in range(nodes.size):
            if(nodes[i].heurustic < lowestValue or lowestValue == -1):
                lowestValue = nodes[i].heurustic
                lowestIndex = i

        return lowestIndex

    @staticmethod
    def braedth_best_search(startingPoint, points):
        queue = deque()
        bestPath = None
        bestCost = 9999999999
        counter = 0
        couningHashMap = {}
        for p in points:
            couningHashMap[p.hashPoint()] = 0

        root = Node(startingPoint, list(), 0.0000001, couningHashMap)
        nodes = numpy.array([])
        nodes = numpy.append(nodes, root)

        test = list()

        while nodes.size != 0:
            current = nodes[Utilities.findIndexWithLowestHeurusticValue(nodes)]
            nodes = numpy.delete(nodes, Utilities.findIndexWithLowestHeurusticValue(nodes))
            test.append(current.point)

            
            if(counter % 1000 == 0):
                print(counter)

            counter += 1

            if(Utilities.countUniqueElements(current.path) == len(points)):
                return current.path
                if(current.cost < bestCost):
                    bestCost = current.cost
                    bestPath = current.path

            
            else:
                for n in current.point.neighbours:

                    if(current.countingHashMap[n.hashPoint()] > len(n.neighbours) + 1 or (len(current.path) > 2 and current.path[-2] == n and len(current.point.neighbours) != 1)):
                        continue

                    newNode = Node(n, current.path, (current.cost + Utilities.distance(current.point.x, current.point.y, n.x, n.y)), current.countingHashMap)

                    if(newNode.cost < bestCost):
                        nodes = numpy.append(nodes, newNode)

        return bestPath






class Point:
    def __init__(self, x, y):
       self.xPix = x
       self.yPix = y
       self.x, self.y = Utilities.toGeographical(self.xPix, self.yPix)
       self.neighbours = list()

    def addNeighbour(self, n):
        self.neighbours.append(n)

    def draw(self):
        arcade.draw_circle_filled(self.xPix, self.yPix, 5, arcade.color.BLUE)
        for n in self.neighbours:
            arcade.draw_line(self.xPix, self.yPix, n.xPix, n.yPix, arcade.color.BLUE, 3)

    def hashPoint(self):
        return hash((self.x, self.y))

class Node:
    def __init__(self, p, path, c, hm):
        self.point = p
        self.path = path.copy()
        self.path.append(self.point)
        self.cost = c 
        self.countingHashMap = hm.copy()
        self.countingHashMap[self.point.hashPoint()] += 1
        #self.heurustic = Utilities.countUniqueElements(self.path)/self.cost
        self.heurustic = self.cost

        pass

