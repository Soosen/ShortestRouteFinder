from cgi import test
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
        self.var = list()

        pass

    def on_draw(self):
        #draw the maze
        self.clear()
        arcade.start_render()
        arcade.draw_texture_rectangle(round(BACKGROUND.size[0]/2), round(BACKGROUND.size[1]/2),BACKGROUND.size[0], BACKGROUND.size[1], BACKGROUND)
        for p in self.points:
            p.draw()

        if(len(self.var) != 0):
            if(self.counter < len(self.var)):
                arcade.draw_circle_filled(self.var[self.counter].xPix, self.var[self.counter].yPix, 15, arcade.color.PURPLE)
                self.counter += 1
                time.sleep(0.1)
            else:
                self.var = list()
                self.counter = 0

        arcade.finish_render()


    def on_update(self, delta_time):

        pass
    def on_key_press(self, key, key_modifiers):

        #Key R - generate new sudoku board
        if key == arcade.key.R:
            self.points = Utilities.load_data("points.dat")

            test = Utilities.areAllPointsReachable(self.points[0])
            for t in test:
                print(t.x, t.y)  


        elif key == arcade.key.S:
            Utilities.save_data(self.points, "points.dat")
        elif key == arcade.key.X:
           del self.points[-1]
        elif key == arcade.key.T:
            connected = Utilities.areAllPointsReachable(self.points[0])

            self.var = Utilities.braedth_best_search(connected[0], connected)

            Utilities.save_data(self.var, "solution.dat")
            test = Utilities.load_data("solution.dat")
            for t in test:
                print(t.x, t.y)

       
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