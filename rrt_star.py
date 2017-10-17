from tkinter import Tk, Frame, Button, Canvas, LEFT, ALL
from random import randint
from math import sqrt
from time import time

CANVAS_SIZE = [640, 480]
MAX_LOOP = 500000
POINT_RADIUS = 1
ARRIVAL_RADIUS = 20


class Node:
    def __init__(self, position):
        self._position = position
        self._cost = 0
        self._parent = None
        self._nodes = []

    def get_cost(self):
        return self._cost

    def set_cost(self, cost):
        self._cost = cost

    def set_parent(self, node: "Node"):
        self._parent = node

    def remove_node(self, node: 'Node'):
        self._nodes.remove(node)

    def reconnect(self, node: 'Node'):
        self._parent.remove_node(self)
        self._parent = node
        self._parent.add_node(self)

    def add_node(self, node: "Node"):
        node.set_parent(self)
        self._nodes.append(node)

    def print(self, canvas: Canvas):
        canvas.create_oval(self._position[0] - POINT_RADIUS, self._position[1] - POINT_RADIUS,
                           self._position[0] + POINT_RADIUS, self._position[1] + POINT_RADIUS,
                           fill="green")
        for node in self._nodes:
            self.print_line(canvas, self._position, node.get_position())
            node.print(canvas)

    def print_path_to_root(self, canvas):
        if self._parent:
            self.print_line(canvas, self._position, self._parent.get_position(), fill="red", width=2.0)
            self._parent.print_path_to_root(canvas)

    def get_position(self):
        return self._position

    @staticmethod
    def print_line(canvas, first_position, last_position, fill="black", width=1.0):
        canvas.create_line(first_position[0], first_position[1],
                           last_position[0], last_position[1],
                           fill=fill, width=width)

    @staticmethod
    def nodes_distance(first_node, second_node):
        first_x, first_y = first_node.get_position()
        second_x, second_y = second_node.get_position()

        return sqrt((first_x - second_x) ** 2 + (first_y - second_y) ** 2)


class Obstacle:
    def __init__(self, radius, center):
        self._radius = radius
        self._center = center

    def is_point_in(self, node: Node, safety=1.0):
        position = node.get_position()
        return (((position[0] - self._center[0]) ** 2 + (position[1] - self._center[1]) ** 2)
                < ((self._radius ** 2) * safety))

    def does_line_intersect(self, start_position, end_position, safety=1):
        radius = self._radius * safety
        x_c, y_c = self._center
        x_l0, y_l0 = start_position
        x_l1, y_l1 = end_position
        x_l1 = x_l1 - x_l0
        y_l1 = y_l1 - y_l0

        c = (x_c ** 2) + (y_c ** 2) + (x_l0 ** 2) + (y_l0 ** 2) - (2 * ((x_c * x_l0) + (y_c * y_l0))) - (radius ** 2)
        b = 2 * ((x_l0 * x_l1) + (y_l0 * y_l1) - (x_l1 * x_c) - (y_l1 * y_c))
        a = (y_l1 ** 2) + (x_l1 ** 2)

        det = (b ** 2) - (4 * a * c)

        if det >= 0:
            if a != 0:
                square_det = sqrt(det)
                if 0 <= (-b + square_det) / (2 * a) <= 1:
                    return True
                if 0 <= (-b - square_det) / (2 * a) <= 1:
                    return True
                return False
            else:
                return True
        else:
            return False

    def print(self, canvas):
        canvas.create_oval(self._center[0] - self._radius, self._center[1] - self._radius,
                           self._center[0] + self._radius, self._center[1] + self._radius,
                           fill="red")

class RRStarAlgo:
    def __init__(self, init_position, final_position):
        self._init_position = init_position
        self._final_position = final_position
        self._tree = Node(init_position)
        self._nodes = [self._tree]
        self._obstacles = [Obstacle(30, [randint(50, CANVAS_SIZE[0] - 50),
                                         randint(50, CANVAS_SIZE[1] - 50)]) for _ in range(20)]
        self._arrival = None
        self._ellipse = None

    def step(self):
        new_node = self.create_random_node()

        for obstacle in self._obstacles:
            if obstacle.is_point_in(new_node, 2):
                return

        best_node, near_nodes = self.chooseParent(new_node)

        if best_node:
            new_node.set_cost(best_node.get_cost() + Node.nodes_distance(best_node, new_node))
            best_node.add_node(new_node)
            self._nodes.append(new_node)

            near_nodes.remove(best_node)
        else:
            return


        if near_nodes:
            new_code_cost = new_node.get_cost()
            for node in near_nodes:
                if node.get_cost() > (new_code_cost + Node.nodes_distance(node, new_node)):
                    if self.does_line_intersect(new_node.get_position(), node.get_position()):
                        continue

                    node.set_cost(new_code_cost + Node.nodes_distance(node, new_node))
                    node.reconnect(new_node)

        if self.is_final_node(new_node):
            self.update_arrival_node(new_node)

    def chooseParent(self, new_node):
        best_node = None
        near_nodes = self.find_near(new_node, 100)
        best_cost = None

        for node in near_nodes:
            cost = node.get_cost() + Node.nodes_distance(node, new_node)

            if (best_cost is None) or (cost < best_cost):

                if self.does_line_intersect(new_node.get_position(), node.get_position()):
                    continue

                best_cost = cost
                best_node = node

        return best_node, near_nodes

    def does_line_intersect(self, start_position, end_position):
        for obstacle in self._obstacles:
            if obstacle.does_line_intersect(start_position, end_position):
                return True
        return False

    def print_tree(self, canvas: Canvas):
        self._tree.print(canvas)

    def print_obstacles(self, canvas: Canvas):
        for obstacle in self._obstacles:
            obstacle.print(canvas)

    def print_arrival(self, canvas: Canvas):
        if self._arrival:
            position = self._final_position
            canvas.create_oval(position[0] - ARRIVAL_RADIUS, position[1] - ARRIVAL_RADIUS,
                               position[0] + ARRIVAL_RADIUS, position[1] + ARRIVAL_RADIUS,
                               fill="blue")

    def print_solution(self, canvas: Canvas):
        if self._arrival:
            self._arrival.print_path_to_root(canvas)

    def find_nearest(self, node: Node):
        return min(self._nodes, key=lambda x: Node.nodes_distance(x, node))

    def find_near(self, node: Node, radius):
        return list(filter(lambda x: Node.nodes_distance(x, node) < radius, self._nodes))

    def is_final_node(self, node: Node):
        position = node.get_position()
        return (((position[0] - self._final_position[0]) ** 2 + (position[1] - self._final_position[1]) ** 2)
                < (ARRIVAL_RADIUS ** 2))

    def update_arrival_node(self, node: Node):
        if self._arrival:
            if self._arrival.get_cost() > node.get_cost():
                self._arrival = node
        else:
            self._arrival = node


    @staticmethod
    def create_random_node():
        return Node([randint(0, CANVAS_SIZE[0]), randint(0, CANVAS_SIZE[1])])


class RRTStarUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.canvas = Canvas(master, width=CANVAS_SIZE[0], height=CANVAS_SIZE[1])
        self.canvas.pack()

        self.canvas.create_rectangle(0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1], fill="grey")

        self.frame = Frame(master)
        self.frame.pack()

        self.close_button = Button(self.frame, text="Close", command=master.quit)
        self.close_button.pack(side=LEFT)

        self._loop_counter = 0

        self.algo = RRStarAlgo([620, 440], [10, 10])

        self.cyclic_call()

    def cyclic_call(self):

        for _ in range(100):
            self.algo.step()
            self._loop_counter += 1

        self.canvas.delete(ALL)
        self.canvas.create_rectangle(0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1], fill="grey")
        self.algo.print_tree(self.canvas)
        self.algo.print_obstacles(self.canvas)
        self.algo.print_arrival(self.canvas)
        self.algo.print_solution(self.canvas)

        if self._loop_counter < MAX_LOOP:
            if self.algo._arrival:
                print(self.algo._arrival.get_cost())
            self.master.after(1, self.cyclic_call)



root = Tk()
my_gui = RRTStarUI(root)
root.mainloop()