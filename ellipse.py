from utils import distance


class Ellipse:
    def __init__(self, first_focus: [], second_focus: [], semi_major_axis: float):
        self._first_focus = first_focus
        self._second_focus = second_focus

        self._semi_major_axis2 = semi_major_axis * 2

    def is_point_in(self, point: []):
        return ((distance(self._first_focus, point)
                 + distance(self._second_focus, point)) <= self._semi_major_axis2)
