from dataclasses import dataclass


@dataclass
class Coords:
    x: float = 0.0
    y: float = 0.0


@dataclass
class MovementVector:
    direction: float
    """ The direction of movement, in radians. """

    velocity: float
    """ The rate of movement, in units per frame. """


class Ball:
    """ Data representation of a physical juggling ball. """

    name: str
    """ An identifier for this ball instance. Only used for debugging purposes. """

    coords: Coords
    """ 
    The current position of the ball in the plane perpendicular to the observer's line of sight. The plane is defined
    such that a higher X-coordinate means the ball is moving right relative to the observer, and a higher Y-coordinate
    means the ball is moving upwards (against gravity) in physical space.
    """

    movement: MovementVector
    """
    The last-recorded movement vector for this ball. Defined such that a direction of 0 radians equates to movement
    to the right relative to the observer.
    """

    def __init__(self, name: str):
        name = name.strip()
        if len(name.split()) > 1:
            raise ValueError('Ball name cannot contain whitespace')

        self.name = name
        self.coords = Coords()

    def __str__(self):
        return f'{self.name}({self.coords.x, self.coords.y})'
