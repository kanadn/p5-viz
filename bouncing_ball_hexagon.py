import pygame
import math
import sys

# Initialize pygame
pygame.init()

# Screen parameters
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball in a Spinning Hexagon")

# Colors
BG_COLOR = (30, 30, 30)
HEX_COLOR = (200, 200, 200)
BALL_COLOR = (255, 50, 50)

# Clock for frame rate control
clock = pygame.time.Clock()
FPS = 60

# Hexagon parameters
hex_center = (WIDTH // 2, HEIGHT // 2)
hex_radius = 250    # distance from center to vertex
hex_sides = 6
hex_angle = 0       # current rotation angle (in radians)
angular_speed = 0.5  # radians per second

# Ball parameters
ball_radius = 15
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [150.0, 0.0]  # initial velocity in pixels/second

# Physics parameters
gravity = 400.0      # pixels per second squared downward
restitution = 0.9    # bounciness coefficient
wall_friction = 0.98 # friction on tangential component upon collision
dt = 1 / FPS       # time step

def get_hexagon_vertices(center, radius, base_angle):
    """Return list of vertices for a regular hexagon rotated by base_angle."""
    vertices = []
    for i in range(hex_sides):
        angle = base_angle + i * 2 * math.pi / hex_sides
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def closest_point_on_segment(a, b, p):
    """
    Returns the closest point on segment ab to point p.
    a, b, p are (x, y) tuples.
    """
    ax, ay = a
    bx, by = b
    px, py = p
    abx, aby = bx - ax, by - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return a
    t = ((px - ax) * abx + (py - ay) * aby) / ab_len_sq
    t = max(0, min(1, t))
    closest = (ax + t * abx, ay + t * aby)
    return closest

def reflect_velocity(ball_v, wall_n, v_rel):
    """
    Reflect ball velocity from a wall with normal wall_n.
    v_rel is the ball's velocity relative to the wall.
    The reflection is computed in the wall's rest frame.
    """
    # Only reflect if the ball is moving into the wall:
    v_dot_n = v_rel[0] * wall_n[0] + v_rel[1] * wall_n[1]
    if v_dot_n >= 0:
        # The ball is moving away from the wall: no collision response.
        return ball_v

    # Reflect the relative velocity along the normal
    # v_rel_new = v_rel - (1 + restitution) * (v_rel dot n) * n
    factor = (1 + restitution) * v_dot_n
    v_rel_new = (v_rel[0] - factor * wall_n[0], v_rel[1] - factor * wall_n[1])
    
    # Add friction on the tangential component:
    # Decompose into normal and tangential parts:
    # (v_new dot n) is the normal component, and subtracting that gives tangential.
    normal_component = (v_rel_new[0] * wall_n[0], v_rel_new[1] * wall_n[1])
    tangential_component = (v_rel_new[0] - normal_component[0],
                              v_rel_new[1] - normal_component[1])
    tangential_component = (tangential_component[0] * wall_friction,
                            tangential_component[1] * wall_friction)
    v_rel_new = (normal_component[0] + tangential_component[0],
                 normal_component[1] + tangential_component[1])
    
    return v_rel_new

def vector_length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def main():
    global hex_angle, ball_pos, ball_vel

    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update hexagon rotation
        hex_angle += angular_speed * dt
        vertices = get_hexagon_vertices(hex_center, hex_radius, hex_angle)

        # Update ball physics: apply gravity
        ball_vel[1] += gravity * dt
        # Update ball position using current velocity
        ball_pos[0] += ball_vel[0] * dt
        ball_pos[1] += ball_vel[1] * dt

        # Check for collision with each wall of the hexagon.
        # Each wall is the segment between two consecutive vertices.
        for i in range(len(vertices)):
            a = vertices[i]
            b = vertices[(i + 1) % len(vertices)]
            closest = closest_point_on_segment(a, b, ball_pos)
            dx = ball_pos[0] - closest[0]
            dy = ball_pos[1] - closest[1]
            dist = math.hypot(dx, dy)

            if dist < ball_radius:
                # Compute the normal: from wall to ball
                if dist == 0:
                    # Avoid division by zero; choose the wall normal (perpendicular to wall)
                    wall_dx, wall_dy = b[0] - a[0], b[1] - a[1]
                    wall_length = math.hypot(wall_dx, wall_dy)
                    if wall_length == 0:
                        continue
                    wall_n = (-wall_dy / wall_length, wall_dx / wall_length)
                else:
                    wall_n = (dx / dist, dy / dist)

                # Compute wall velocity at the collision point.
                # Since the hexagon rotates about hex_center with angular speed,
                # the velocity at any point p is given by:
                #    v = angular_speed x (p - hex_center)
                # For 2D, cross product with scalar angular_speed gives:
                #    v = angular_speed * (-dy, dx)
                cp_x, cp_y = closest
                rel_x = cp_x - hex_center[0]
                rel_y = cp_y - hex_center[1]
                wall_vel = ( -angular_speed * rel_y, angular_speed * rel_x )

                # Compute ball velocity relative to wall
                v_rel = (ball_vel[0] - wall_vel[0], ball_vel[1] - wall_vel[1])
                
                # Reflect the relative velocity across the wall normal
                v_rel_new = reflect_velocity(ball_vel, wall_n, v_rel)
                
                # Now, update the ball velocity by adding back the wall velocity:
                ball_vel = [v_rel_new[0] + wall_vel[0], v_rel_new[1] + wall_vel[1]]
                
                # Separate the penetration: push the ball out so it is not stuck.
                overlap = ball_radius - dist
                ball_pos[0] += wall_n[0] * overlap
                ball_pos[1] += wall_n[1] * overlap

        # Clear screen
        screen.fill(BG_COLOR)

        # Draw hexagon
        pygame.draw.polygon(screen, HEX_COLOR, vertices, width=3)

        # Draw ball
        pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
