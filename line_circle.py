from tkinter import Tk, Frame, Button, Canvas, LEFT, ALL
from random import randint
from math import sqrt

CANVAS_SIZE = [640, 480]

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.canvas = Canvas(master, width=CANVAS_SIZE[0], height=CANVAS_SIZE[1])
        self.canvas.pack()

        self.canvas.create_rectangle(0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1], fill="grey")

        self.close_button = Button(self.master, text="New", command=self.show)
        self.close_button.pack(side=LEFT)


    def show(self):
        self.canvas.delete(ALL)
        radius = 100
        center = [200, 300]
        self.print_circle(center, radius)

        p0 = [randint(0, CANVAS_SIZE[0]), randint(0, CANVAS_SIZE[1])]
        p1 = [randint(0, CANVAS_SIZE[0]), randint(0, CANVAS_SIZE[1])]
        self.canvas.create_line(*p0, *p1)

        points = find_intersection(radius, center, p0, p1)

        for point in points:
            self.print_circle(point, 4, color="blue")

    def print_circle(self, center, radius, color="red"):
        self.canvas.create_oval(center[0] - radius, center[1] - radius,
                                center[0] + radius, center[1] + radius,
                                fill=color)


def find_intersection(radius, center, start_position, end_position):
    x_c, y_c = center
    x_l0, y_l0 = start_position
    x_l1, y_l1 = end_position
    x_l1 = x_l1 - x_l0
    y_l1 = y_l1 - y_l0

    c = (x_c ** 2) + (y_c ** 2) + (x_l0 ** 2) + (y_l0 ** 2) - (2 * ((x_c * x_l0) + (y_c * y_l0))) - (radius ** 2)
    b = 2 * ((x_l0 * x_l1) + (y_l0 * y_l1) - (x_l1 * x_c) - (y_l1 * y_c))
    a = (y_l1 ** 2) + (x_l1 ** 2)

    det = (b ** 2) - (4 * a * c)
    print(a, b, c, det)

    points = []
    if det >= 0:
        if a != 0:
            square_det = sqrt(det)
            if 0 <= (-b + square_det) / (2 * a) <= 1:
                points.append([x_l0 + (((-b + square_det) / (2 * a)) * x_l1),
                               y_l0 + (((-b + square_det) / (2 * a)) * y_l1)])
            if 0 <= (-b - square_det) / (2 * a) <= 1:
                points.append([x_l0 + (((-b - square_det) / (2 * a)) * x_l1),
                               y_l0 + (((-b - square_det) / (2 * a)) * y_l1)])
    return points


root = Tk()
my_gui = GUI(root)
root.mainloop()