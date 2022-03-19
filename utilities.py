from errno import ESTALE
import math
import numpy
import arcade
import pickle
from collections import deque
from operator import attrgetter
import gc


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
    def edgeInList(edge, list):
        for elem in list:
            if(elem.compareEdges(edge)):
                return True

        return False

    @staticmethod
    def getAllEdges(startingPoint):

        queue = deque()
        visited = list()
        edges = list()
        queue.append(startingPoint)
        
        while queue:
            current = queue.pop()

            visited.append(current)

            for n in current.neighbours:
                if(not Utilities.isInList(n, visited)):
                    queue.append(n)
                    if(not Utilities.edgeInList(Edge(current, n), edges)):
                        edges.append(Edge(current, n))

        return edges

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
    def countUniqueEdges(listA):
        return len(listA)/2

        """  temp = list()
        for e in listA:
            if not Utilities.edgeInList(e, temp):
                temp.append(e) """
        
       

    @staticmethod
    def findIndexWithHighestHeurusticValue(nodes):
        """ highestValue = -1
        highestIndex = -1

        for i in range(nodes.size):
            if(nodes[i].heurustic > highestValue or highestValue == -1):
                highestValue = nodes[i].heurustic
                highestIndex = i

        return highestIndex """
        item = max(nodes,key=attrgetter('heurustic'))
        nodes = nodes[nodes != item] 

        return item, nodes

    @staticmethod
    def findIndexWithLowestHeurusticValue(nodes):
        item = min(nodes,key=attrgetter('heurustic'))
        nodes = nodes[nodes != item] 

        return item, nodes

    @staticmethod
    def braedth_best_search(startingPoint, edges, points, maxAllowedCost):
        queue = deque()
        bestPath = list()
        bestCost = maxAllowedCost
        counter = 0
        countingHashMap = {}
        """  for p in points:
           countingHashMap[p.hashPoint()] = 0 """
        for e in edges:
            countingHashMap[e.hashEdge()] = 0
            countingHashMap[e.hashCounterEdge()] = 0

        root = Node(startingPoint, list(), 0.0000001, countingHashMap, set())
        #nodes = numpy.array([])
        #nodes = numpy.append(nodes, root)
        queue.append(root)


        while queue:
            #current, nodes = Utilities.findIndexWithHighestHeurusticValue(nodes)
            #current = nodes[index]
            #nodes = numpy.delete(nodes, index)
            current = queue.popleft()
            if(current.cost > bestCost):
                del current
                continue

            if(counter % 100000 == 0):
                print("Queue Lenght = ", len(queue))
                print("Iterations = ", counter)
                gc.collect()

            counter += 1

            if(Utilities.countUniqueEdges(current.visitedEdges) == len(edges)):
                #return current.path, current.cost
                if(current.cost < bestCost):
                    bestCost = current.cost
                    bestPath = current.path

            
            else:
                for n in current.point.neighbours:

                    tempEdge = Edge(current.point, n)
                    #if(current.countingHashMap[n.hashPoint()] > len(n.neighbours) + 2)  or (len(current.path) > 2 and current.path[-2] == n and len(current.point.neighbours) != 1):
                    if(current.countingHashMap[tempEdge.hashEdge()] > 1  or (len(current.path) > 2 and current.path[-2] == n and len(current.point.neighbours) != 1)):   
                        continue

                    
                    tempVisitedEdges = current.visitedEdges.copy()
                    tempVisitedEdges.add(tempEdge.hashEdge())
                    tempVisitedEdges.add(tempEdge.hashCounterEdge())

                    tempCountingHashMap = current.countingHashMap.copy()
                    tempCountingHashMap[tempEdge.hashEdge()] += 1
                    tempCountingHashMap[tempEdge.hashCounterEdge()] += 1
                    newNode = Node(n, current.path, (current.cost + Utilities.distance(current.point.x, current.point.y, n.x, n.y)), tempCountingHashMap, tempVisitedEdges)

                    if(newNode.cost < bestCost):
                        #nodes = numpy.append(nodes, newNode)
                        queue.append(newNode)

            del current

        if(len(bestPath) == 0):
            return bestPath, -1
        else:
            return bestPath, bestCost 


    @staticmethod
    def AStar(startingPoint, edges, points, maxAllowedCost):
        queue = deque()
        bestPath = list()
        bestCost = maxAllowedCost
        counter = 0
        countingHashMap = {}
        """  for p in points:
           countingHashMap[p.hashPoint()] = 0 """
        for e in edges:
            countingHashMap[e.hashEdge()] = 0
            countingHashMap[e.hashCounterEdge()] = 0

        root = Node(startingPoint, list(), 0.0000001, countingHashMap, set())
        nodes = list()
        nodes.append(root)


        while len(nodes) != 0:
            #current, nodes = Utilities.findIndexWithHighestHeurusticValue(nodes)
            
            if(len(nodes) < 1000):
                item = max(nodes,key=attrgetter('heurustic'))
                index = nodes.index(item)
            else:  
                item = max(nodes[0:1001],key=attrgetter('heurustic'))
                index = nodes[0:1001].index(item)
            
            current = nodes.pop(index)

            #current = nodes[0]
            #nodes.pop(0)

            if(current.cost > bestCost):
                del current
                continue

            if(counter % 1000 == 0):
                nodes.sort(key=attrgetter('heurustic'))
                #print("List size= ", len(nodes))
                #print("Iterations = ", counter)
                print(current.heurustic)
                gc.collect()

            counter += 1

            if(Utilities.countUniqueEdges(current.visitedEdges) == len(edges)):
                return current.path, current.cost
                if(current.cost < bestCost):
                    bestCost = current.cost
                    bestPath = current.path

            
            else:
                for n in current.point.neighbours:

                    tempEdge = Edge(current.point, n)
                    #if(current.countingHashMap[n.hashPoint()] > len(n.neighbours) + 2)  or (len(current.path) > 2 and current.path[-2] == n and len(current.point.neighbours) != 1):
                    if(current.countingHashMap[tempEdge.hashEdge()] > 1  or (len(current.path) > 2 and current.path[-2] == n and len(current.point.neighbours) != 1)):   
                        continue

                    
                    tempVisitedEdges = current.visitedEdges.copy()
                    tempVisitedEdges.add(tempEdge.hashEdge())
                    tempVisitedEdges.add(tempEdge.hashCounterEdge())

                    tempCountingHashMap = current.countingHashMap.copy()
                    tempCountingHashMap[tempEdge.hashEdge()] += 1
                    tempCountingHashMap[tempEdge.hashCounterEdge()] += 1
                    newNode = Node(n, current.path, (current.cost + Utilities.distance(current.point.x, current.point.y, n.x, n.y)), tempCountingHashMap, tempVisitedEdges)

                    if(newNode.cost < bestCost):
                        if(len(nodes) > 1000 and newNode.heurustic < nodes[1000].heurustic):
                            nodes.insert(0, newNode)
                        else:
                            nodes.append(newNode)

            del current

        if(len(bestPath) == 0):
            return bestPath, -1
        else:
            return bestPath, bestCost 






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
    def __init__(self, p, path, c, hm, ve):
        self.point = p
        self.path = path.copy()
        self.path.append(self.point)
        self.visitedEdges = ve
        self.cost = c 
        self.countingHashMap = hm
        #self.countingHashMap[self.point.hashPoint()] += 1
        self.heurustic = Utilities.countUniqueElements(self.path)/self.cost
        #self.heurustic = Utilities.countUniqueEdges(self.visitedEdges)

        pass

class Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def compareEdges(self, edge):
        return (self.a.x == edge.a.x and self.a.y == edge.a.y and self.b.x == edge.b.x and self.b.y == edge.b.y) or (self.b.x == edge.a.x and self.b.y == edge.a.y and self.a.x == edge.b.x and self.a.y == edge.b.y)

    def hashEdge(self):
        return hash((self.a.x, self.a.y, self.b.x, self.b.y))

    def hashCounterEdge(self):
        return hash((self.b.x, self.b.y, self.a.x, self.a.y))

