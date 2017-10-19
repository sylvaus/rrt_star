from tkinter import Tk, Frame, Button, Canvas, LEFT, ALL
from random import randint
from node import Node
from obstacle import Obstacle
from ellipse import Ellipse

CANVAS_SIZE = [640, 480]
MAX_LOOP = 500000
ARRIVAL_RADIUS = 20


class RRStarAlgo:
    def __init__(self, init_position, final_position):
        self._init_position = init_position
        self._final_position = final_position
        self._tree = Node(init_position)
        self._nodes = [self._tree]
        self._obstacles = [Obstacle(randint(10, 30), [randint(50, CANVAS_SIZE[0] - 50),
                                                      randint(50, CANVAS_SIZE[1] - 50)]) for _ in range(20)]
        self._arrival = None
        self._ellipse = None
        self._counter = 0

    def step(self):
        new_node = self.create_random_node()

        for obstacle in self._obstacles:
            if obstacle.is_point_in(new_node, 2):
                return

        if self._ellipse:
            if not self._ellipse.is_point_in(new_node.get_position()):
                return

        best_node, near_nodes = self.choose_parent(new_node)
        self.insert_node(best_node, new_node)

        if not best_node:
            return
        near_nodes.remove(best_node)
        self.rewire(near_nodes, new_node)

        if self.is_final_node(new_node):
            self.update_arrival_node(new_node)
            self._ellipse = Ellipse(self._init_position, self._final_position, new_node.get_cost()/2)

    def choose_parent(self, new_node):
        best_node = None
        near_nodes = self.find_near(new_node, 50)
        best_cost = None

        for node in near_nodes:
            cost = node.get_cost() + Node.nodes_distance(node, new_node)

            if (best_cost is None) or (cost < best_cost):

                if self.does_line_intersect(new_node.get_position(), node.get_position()):
                    continue

                best_cost = cost
                best_node = node

        return best_node, near_nodes

    def insert_node(self, best_node, new_node):
        if best_node:
            new_node.set_cost(best_node.get_cost() + Node.nodes_distance(best_node, new_node))
            best_node.add_node(new_node)
            self._nodes.append(new_node)
        else:
            nearest_node = self.find_nearest(new_node)
            if not self.does_line_intersect(nearest_node.get_position(), new_node.get_position()):
                new_node.set_cost(nearest_node.get_cost() + Node.nodes_distance(nearest_node, new_node))
                nearest_node.add_node(new_node)
                self._nodes.append(new_node)

    def rewire(self, near_nodes, new_node):
        if near_nodes:
            new_code_cost = new_node.get_cost()
            for node in near_nodes:
                if node.get_cost() > (new_code_cost + Node.nodes_distance(node, new_node)):
                    if self.does_line_intersect(new_node.get_position(), node.get_position()):
                        continue

                    node.set_cost(new_code_cost + Node.nodes_distance(node, new_node))
                    node.reconnect(new_node)

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

        self.algo = RRStarAlgo([620, 440], [30, 30])

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
