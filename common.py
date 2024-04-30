from typing import NamedTuple
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import random
import numpy as np
import imageio

plt.style.use('dark_background')

class State(NamedTuple):
    x: float
    y: float

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return str(self)

    def __add__(self, other: "State"):
        return State(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: "State"):
        return State(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: float):
        return State(self.x * other, self.y * other)
    
    def __truediv__(self, other: float):
        return State(self.x / other, self.y / other)

    def __eq__(self, other: "State"):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: "State"):
        return not self.__eq__(other)

    def __pow__(self, other: float):
        return State(self.x ** other, self.y ** other)

    def norm(self):
        return (self.x**2 + self.y**2)**0.5

    @staticmethod
    def dummy():
        return State(0, 0)

class Node:
    def __init__(self, state: State, parent: "Node" = None):
        self.state = state
        self.parent = None
        if parent is not None:
            self.set_parent(parent)
        self.childs = []

    def set_parent(self, parent: "Node"):
        if self.parent is not None:
            self.parent.remove_child(self)

        parent.add_child(self)
        self.parent = parent

    def add_child(self, child: "Node"):
        self.childs.append(child)

    def remove_child(self, child: "Node"):
        self.childs.remove(child)

    @property
    def id(self):
        return id(self)

    def __str__(self):
        return f"Node({self.state})"

    def __repr__(self):
        return str(self)

class Tree:
    def __init__(self, init_state: State):
        self.nodes = [Node(init_state)]

    def select_node(self, policy: callable):
        return policy(self.nodes)

    def add(self, child: Node):
        parent = child.parent

        assert parent is not None, "Child node must have a parent"
        assert parent in self.nodes, f"Parent node {parent} not in the tree"

        self.nodes.append(child)

    def get_path(self, node: Node):
        path = []
        while node is not None:
            path.append(node)
            node = node.parent
        return path[::-1]

class Object:
    def __init__(self, radius: int, state: State, color: str = None) -> None:
        self.radius = radius
        self.state = state
        self.color = "blue" if color is None else color

    def __str__(self):
        return f"Object(r={self.radius}, {self.state})"

    def __repr__(self):
        return str(self)

    def set_state(self, state: State):
        self.state = state

    def collide(self, other: "Object") -> bool:
        distance = (self.state - other.state).norm()
        radius_sum = self.radius + other.radius
        return distance <= radius_sum

    def draw(self, ax: plt.Axes, label = None):
        ax.add_artist(plt.Circle((self.state.x, self.state.y), self.radius, color=self.color, label = label))

class Robot(Object):
    pass

class Obstacle(Object):
    pass

class Environment:
    @staticmethod
    def dummy():
        width = 10
        height = 10
        env = Environment(width, height)
        env.add_objects([
            # Obstacle(0.2, State(2, 2)),
            # Obstacle(0.2, State(3, 3)),
            # Obstacle(0.2, State(4, 4)),
            # Obstacle(0.2, State(5, 5)),
            # Obstacle(0.2, State(6, 6)),
            # Obstacle(0.2, State(7, 7)),
            # Obstacle(0.2, State(8, 8)),
            Obstacle(1, State(6, 4)),
            Obstacle(0.8, State(6.5, 5)),
            Obstacle(0.6, State(7, 6)),
            Obstacle(0.4, State(7, 6.8)),
            Obstacle(0.3, State(7, 7.3)),
            Obstacle(0.8, State(5, 3.5)),
            Obstacle(0.6, State(4, 3)),
            Obstacle(0.4, State(3.2, 3)),
            Obstacle(0.3, State(2.7, 3)),
        ])
        env.set_init_and_goal_state(
            State(1, 9),
            State(9, 1),
        )
        return env

    @staticmethod
    def random():
        width = 10
        height = 10
        env = Environment(width, height)
        num_obstacles = random.randint(3, 7)
        for _ in range(num_obstacles):
            env.add_objects([
                Obstacle(random.uniform(0, 2), State(random.uniform(0, width), random.uniform(0, height)))
            ])
        env.set_init_and_goal_state()
        return env

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.objects = []
        self.init_state = None
        self.goal_state = None
        self.init_radius = 0.25
        self.goal_radius = 0.25
        self.collision_counter = 0

    def add_objects(self, objects: list[Object]):
        self.objects.extend(objects)

    def set_init_and_goal_state(self, init_state: State = None, goal_state: State = None) -> State:
        if init_state is not None:
            self.init_state = init_state
            if self.check_collision(Object(self.init_radius, self.init_state)):
                raise ValueError("Initial state collides with an object")
        else:
            self.init_state = self.generate_random_state(
                Object(self.goal_radius, State.dummy())
            )
        if goal_state is not None:
            self.goal_state = goal_state
            if self.check_collision(Object(self.goal_radius, self.goal_state)):
                raise ValueError("Goal state collides with an object")
        else:
            self.goal_state = self.generate_random_state(
                Object(self.goal_radius, State.dummy())
            )

    def draw(self, tree=None, path=None, title=None, show = True):
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        for obj in self.objects:
            obj.draw(ax)

        if self.init_state is not None and self.goal_state is not None:
            Object(self.init_radius, self.init_state, color="white").draw(ax, label="Initial")
            Object(self.goal_radius, self.goal_state, color="cyan").draw(ax, label="Goal")

        if tree is not None:
            lines = []
            points = []
            for node in tree.nodes:
                if node.parent is not None:
                    lines.append([(node.state.x, node.state.y), (node.parent.state.x, node.parent.state.y)])
                    # ax.plot([node.state.x, node.parent.state.x], [node.state.y, node.parent.state.y], color="pink")
                points.append((node.state.x, node.state.y))
            lc = mc.LineCollection(lines, colors="pink", linewidths=1)
            ax.add_collection(lc)
            ax.scatter(*zip(*points), color="pink")

        if path is not None and len(path) > 0:
            lines = []
            for i in range(len(path) - 1):
                lines.append([(path[i].state.x, path[i].state.y), (path[i+1].state.x, path[i+1].state.y)])
                # ax.plot([path[i].state.x, path[i+1].state.x], [path[i].state.y, path[i+1].state.y], color="purple")
            lines.append([(path[-1].state.x, path[-1].state.y), (self.goal_state.x, self.goal_state.y)])
            # ax.plot([path[-1].state.x, self.goal_state.x], [path[-1].state.y, self.goal_state.y], color="purple")
            ax.scatter(self.goal_state.x, self.goal_state.y, color="pink")
            lc = mc.LineCollection(lines, colors="purple", linewidths=2)
            ax.add_collection(lc)

        fig.legend()
        # loc='center left', bbox_to_anchor=(0.9, 0.5))
        if title is not None:
            ax.set_title(title)
        fig.tight_layout()
        if show:
            plt.show()

        return fig

    def check_collision(self, obj: Object):
        if obj.state.x - obj.radius < 0 or obj.state.x + obj.radius > self.width:
            self.collision_counter += 1
            return True

        if obj.state.y - obj.radius < 0 or obj.state.y + obj.radius > self.height:
            self.collision_counter += 1
            return True

        for other in self.objects:
            self.collision_counter += 1
            if obj.collide(other):
                return True
        return False

    def reached_goal(self, robot: Robot):
        return robot.collide(
            Object(self.goal_radius, self.goal_state)
        )

    def generate_random_state(self, obj: Object) -> State:
        while True:
            state = State(random.uniform(0, self.width), random.uniform(0, self.height))
            obj.set_state(state)
            collides = self.check_collision(obj)
            if not collides:
                return obj.state

class GIFGenerator:
    def __init__(self):
        self.images = []

    def add_frame(self, fig: plt.Figure):
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        self.images.append(image)
        plt.close()

    def save(self, filename: str):
        imageio.mimsave(filename, self.images, fps=60)
        print(f"Saved GIF to {filename}")
