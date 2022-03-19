from cgi import test
from logging.config import listen
from re import template
import arcade
import sys
import numpy
import pyglet
import time
import json
import numpy
from utilities import Utilities
from utilities import Point
from utilities import Edge
import pickle

#BACKGROUND = arcade.load_texture("resizedMap.png")
BACKGROUND = arcade.load_texture("resizedTopomapRoute.png")
SCREEN_WIDTH = BACKGROUND.size[0]
SCREEN_HEIGHT = BACKGROUND.size[1]
SCREEN_TITLE = "Shortest Path Generator"

#fps
UPDATE_RATE = 1

#chosen Monitor
MONITOR_NUM = 0
MONITORS = pyglet.canvas.Display().get_screens()
MONITOR = MONITORS[MONITOR_NUM]



class MyProject(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

    def setup(self):

        #increase recursion limit
        sys.setrecursionlimit(30000)

        #set fps
        self.set_update_rate(UPDATE_RATE)

        #center the window on start
        self.center_on_screen()     
        self.points = list()

        lat1 = 51.93209
        long1 = 8.05978
        lat2 = 51.966093452681605
        long2 = 8.105107524499527 
        
        self.connect = False
        self.firstPoint = None
        self.secondPoint = None
        self.counter = 0
        self.path = list()
        self.visited = list()
        self.visitedEdges = list()
        self.edges = list()
        self.pathEdges = list()        

        pass

    def on_draw(self):
        #draw the maze
        self.clear()
        arcade.start_render()
        arcade.draw_texture_rectangle(round(BACKGROUND.size[0]/2), round(BACKGROUND.size[1]/2),BACKGROUND.size[0], BACKGROUND.size[1], BACKGROUND)
        for p in self.points:
            p.draw()
            

        if(len(self.path) != 0):
            if(self.counter < len(self.path)):
                arcade.draw_circle_filled(self.path[self.counter].xPix, self.path[self.counter].yPix, 15, arcade.color.PURPLE)
                self.visited.append(self.path[self.counter])

                if(self.counter < len(self.pathEdges)):
                    arcade.draw_line(self.pathEdges[self.counter].a.xPix, self.pathEdges[self.counter].a.yPix, self.pathEdges[self.counter].b.xPix, self.pathEdges[self.counter].b.yPix, arcade.color.ORANGE, 10)
                    self.visitedEdges.append(self.pathEdges[self.counter])
                self.counter += 1
                for v in self.visited:
                    arcade.draw_circle_filled(v.xPix, v.yPix, 10, arcade.color.GREEN)

                for e in self.visitedEdges:
                    arcade.draw_line(e.a.xPix, e.a.yPix, e.b.xPix, e.b.yPix, arcade.color.YELLOW, 3)
                time.sleep(0.3)
            else:
                self.var = list()
                self.counter = 0
                self.visited = list()
                self.visitedEdges = list()

        arcade.finish_render()


    def on_update(self, delta_time):

        pass
    def on_key_press(self, key, key_modifiers):

        #Key R - generate new sudoku board
        if key == arcade.key.R:
            self.points = Utilities.load_data("points.dat")
            self.edges = Utilities.getAllEdges(self.points[0])
            print(len(self.edges))


        elif key == arcade.key.S:
            Utilities.save_data(self.points, "points.dat")
        elif key == arcade.key.X:
           del self.points[-1]
        elif key == arcade.key.T:
            connected = Utilities.areAllPointsReachable(self.points[0])
            self.edges = Utilities.getAllEdges(self.points[0])

            cost = None
            self.path, cost = Utilities.braedth_best_search(connected[0], self.edges, connected, 32)
            #self.path, cost = Utilities.AStar(connected[0], self.edges, connected, 32)
            if(len(self.path) != 0 and cost != -1):
                self.pathEdges = list()
                for i in range(len(self.path)):
                    if(i < len(self.path) - 1):
                        self.pathEdges.append(Edge(self.path[i], self.path[i + 1]))
                    
                print("Success")
                print(cost)
                Utilities.save_data(self.path, "solution.dat")
            else:
                print("Failure")
            

       
        pass
    def on_mouse_press(self, x, y, button, key_modifiers):
        if(button == arcade.MOUSE_BUTTON_LEFT):
            self.points.append(Point(x, y))

        elif(button == arcade.MOUSE_BUTTON_RIGHT):
            if(not self.connect):
                self.firstPoint = Utilities.findClosesPoint(x, y, self.points)
                print(Utilities.findClosesPoint(x, y, self.points).x, Utilities.findClosesPoint(x, y, self.points).y)
                self.connect = not self.connect
            else:
                self.secondPoint = Utilities.findClosesPoint(x, y, self.points)
                if(self.firstPoint != self.secondPoint):
                    self.firstPoint.addNeighbour(self.secondPoint)
                    self.secondPoint.addNeighbour(self.firstPoint)
                    self.connect = not self.connect
            
        pass

    def center_on_screen(self):
        _left = MONITOR.width // 2 - self.width // 2
        _top = (MONITOR.height // 2 - self.height // 2)
        self.set_location(_left, _top)

def main():
    project = MyProject(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    project.setup()

    arcade.run()




if __name__ == "__main__":
    main()