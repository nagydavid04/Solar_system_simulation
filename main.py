import math
import time
import pygame
pygame.init()

class Planet:
    def __init__(self, x, y, radius, mass, color, screen_radius, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass

        self.sun = False
        self.distance_to_sun = 0
        self.distance_to_earth_x = 0
        self.distance_to_earth_y = 0

        # m/s
        self.x_vel = 0
        self.y_vel = 0

        self.color = color
        self.screen_radius = screen_radius
        self.name = name
        self.image = pygame.transform.scale(pygame.image.load(f"planetpics/{name}.png").convert_alpha(), (screen_radius*2, screen_radius*2))
        self.rect = None

    def attraction(self, planet):
        dis_x = planet.x - self.x
        dis_y = planet.y - self.y
        distance = (dis_x ** 2 + dis_y ** 2) ** 0.5

        force = G * planet.mass * self.mass / distance ** 2
        angle = math.atan2(dis_y, dis_x)

        if planet.sun:
            self.distance_to_sun = distance
            self.sun_angle = angle

        if planet.name == "Earth" and self.name == "Moon":
            self.distance_to_earth_x = dis_x
            self.distance_to_earth_y = dis_y

        force_x = math.cos(angle) * force
        force_y = math.sin(angle) * force

        return force_x, force_y

    def update_position(self):
        total_fx = 0
        total_fy = 0

        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * TIMESTEP_UNIVERSE
        self.y_vel += total_fy / self.mass * TIMESTEP_UNIVERSE

        self.x += self.x_vel * TIMESTEP_UNIVERSE
        self.y += self.y_vel * TIMESTEP_UNIVERSE

    def draw_on_screen(self):
        x = WIDTH / 2 + (self.x + self.distance_to_earth_x * -75) * SCALE_UNIVERSE
        y = HEIGHT / 2 + (self.y + self.distance_to_earth_y * -75) * SCALE_UNIVERSE

        self.rect = pygame.Rect(x-self.screen_radius, y-self.screen_radius, self.screen_radius * 2, self.screen_radius * 2)

        screen.blit(self.image, (x-self.screen_radius, y-self.screen_radius))

        if not self.sun and show_information:
            text_name = font1.render(self.name, True, colors["white"])
            screen.blit(text_name, (x + self.screen_radius, y - space_between_planet_information_text * 4))

            text_distance_to_sun = font1.render(f"{round(self.distance_to_sun / AU, 2)}au", True, colors["white"])
            screen.blit(text_distance_to_sun, (x+self.screen_radius, y - space_between_planet_information_text * 2))

            text_velocity = font1.render(f"{round((self.x_vel ** 2 + self.y_vel ** 2) ** 0.5 / 1000, 2)}km/s", True, colors["white"])
            screen.blit(text_velocity, (x + self.screen_radius, y))


class Space:
    def __init__(self, g, name):
        self.g = g
        self.name = name

        self.g_text = pygame.font.SysFont("arial", WIDTH // 30).render(f"{g} m/s^2", True, colors["white"])
        self.name_text = pygame.font.SysFont("georgia", WIDTH // 15).render(name, True, colors["white"])

        self.bg = pygame.transform.scale(pygame.image.load(f"surfacepics/{name}.png").convert_alpha(), (WIDTH, HEIGHT))
        self.const = g * TIMESTEP_REAL
        self.objects = []

    def update_screen(self):
        screen.blit(self.bg, (0, 0))
        screen.blit(self.g_text, (WIDTH / 2 - self.g_text.get_width() // 2, HEIGHT // 30 * 5))
        screen.blit(self.name_text, (WIDTH/2 - self.name_text.get_width() // 2, HEIGHT//30))
        for ob in self.objects:
            ob.update_position(self.const)
            ob.draw()
        pygame.display.update()


class Object:
    def __init__(self, x, y, width, height, path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.vel_y = 0  # m/s

        self.image = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (width*SCALE_REAL, height*SCALE_REAL))

    def update_position(self, const):
        self.y += (self.vel_y + const/2) * TIMESTEP_REAL
        self.vel_y += const

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a] and self.x > 0:
            self.x -= 0.01
        if keys_pressed[pygame.K_d] and self.x + self.width < WIDTH / SCALE_REAL:
            self.x += 0.01

        if self.y + self.height > HEIGHT / SCALE_REAL:
            self.y = HEIGHT / SCALE_REAL - self.height
            self.vel_y = 0

    def draw(self):
        height_text = pygame.font.SysFont("arial", WIDTH // 60).render(f"{round(HEIGHT/SCALE_REAL - self.y, 2)}m", True, colors["white"])
        screen.blit(height_text, ((self.x+1) * SCALE_REAL, self.y * SCALE_REAL - height_text.get_height() // 2))

        pygame.draw.line(screen, colors["white"], ((self.x+0.25) * SCALE_REAL, self.y * SCALE_REAL), ((self.x+0.95) * SCALE_REAL, self.y * SCALE_REAL), width=2)

        screen.blit(self.image, (self.x*SCALE_REAL, self.y*SCALE_REAL))


colors = {"yellow": (255, 255, 0),
          "grey": (160, 160, 160),
          "white": (255, 255, 255),
          "blue": (0, 0, 255),
          "red": (255, 0, 0),
          "brown": (153, 76, 0),
          "cream": (255, 204, 153),
          "light_blue": (153, 204, 255),
          }

DISPLAY_INFO = pygame.display.Info()
WIDTH, HEIGHT = DISPLAY_INFO.current_w, DISPLAY_INFO.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

AU = 149_597_870.7 * 1000
G = 6.67408e-11
FPS = 100
TIMESTEP_UNIVERSE = 3600 * 24 / FPS
SCALE_UNIVERSE = WIDTH / 68 / AU
TIMESTEP_REAL = 1 / FPS
SCALE_REAL = HEIGHT / 6
SCALE_PLANETS = WIDTH // 192
font1 = pygame.font.SysFont("arial", WIDTH // 120)
font2 = pygame.font.SysFont("arial", WIDTH // 100)
space_between_planet_information_text = WIDTH // 210

timer = 0
timer_is_running = False
show_information = True

sun = Planet(0, 0, 696_340_000, 1.9891e30, colors["yellow"], SCALE_PLANETS*5, "Sun")
sun.sun = True

mercury = Planet(65_411_000*1000, 0, 2_439_700, 3.285e23, colors["grey"], SCALE_PLANETS*2, "Mercury")
mercury.y_vel = 47*1000

venus = Planet(108_010_000*1000, 0, 6_051.8*1000, 4.867e24, colors["white"], SCALE_PLANETS*2.5, "Venus")
venus.y_vel = 35.02*1000

earth = Planet(149_597_870.7*1000, 0, 6_371*1000, 5.972e24, colors["blue"], SCALE_PLANETS*3, "Earth")
earth.y_vel = 29.78*1000

mars = Planet(244_900_000*1000, 0, 3_389.5*1000, 6.39e23, colors["red"], SCALE_PLANETS*2.3, "Mars")
mars.y_vel = 24.077*1000

jupiter = Planet(740_740_000*1000, 0, 69_911*1000, 1.898e27, colors["brown"], SCALE_PLANETS*3, "Jupiter")
jupiter.y_vel = 13.07*1000

saturn = Planet(1.4672e9*1000, 0, 58_232*1000, 5.683e26, colors["cream"], SCALE_PLANETS*5, "Saturn")
saturn.y_vel = 9.69*1000

uranus = Planet(2.9402e9*1000, 0, 25_362*1000, 8.68103e25, colors["light_blue"], SCALE_PLANETS*5, "Uranus")
uranus.y_vel = 6.8*1000

neptune = Planet(4.4734e9*1000, 0, 24_622*1000, 1.024e26, colors["blue"], SCALE_PLANETS*3, "Neptune")
neptune.y_vel = 5.4*1000

moon = Planet(149_597_870.7*1000 + 384_400_000, 0, 1740*1000, 7.34767309e22, colors["white"], SCALE_PLANETS*1.25, "Moon")
moon.y_vel = 29.78*1000 + 1000

planets = [sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune]


human = Object(WIDTH/SCALE_REAL/2-0.25, HEIGHT/SCALE_REAL-2, 0.5, 2, "surfacepics/human.png")

sun_space = Space(274, "Sun")
sun_space.objects.append(human)

mercury_space = Space(3.7, "Mercury")
mercury_space.objects.append(human)

venus_space = Space(8.87, "Venus")
venus_space.objects.append(human)

earth_space = Space(9.80665, "Earth")
earth_space.objects.append(human)

mars_space = Space(3.721, "Mars")
mars_space.objects.append(human)

jupiter_space = Space(24.79, "Jupiter")
jupiter_space.objects.append(human)

saturn_space = Space(10.44, "Saturn")
saturn_space.objects.append(human)

uranus_space = Space(8.87, "Uranus")
uranus_space.objects.append(human)

neptune_space = Space(11.15, "Neptune")
neptune_space.objects.append(human)

moon_space = Space(1.62, "Moon")
moon_space.objects.append(human)

spaces = [sun_space, mercury_space, venus_space, earth_space, mars_space, jupiter_space, saturn_space, uranus_space, neptune_space, moon_space]


def show_solar_system():
    global G, TIMESTEP_UNIVERSE, SCALE_UNIVERSE, timer, timer_is_running, show_information

    run = True

    planet_to_show = None

    while run:
        clock.tick(FPS)

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_KP7]:
            G *= 0.99
        elif keys_pressed[pygame.K_KP9]:
            G *= 1.01
        elif keys_pressed[pygame.K_KP4]:
            TIMESTEP_UNIVERSE *= 0.99
        elif keys_pressed[pygame.K_KP6]:
            TIMESTEP_UNIVERSE *= 1.01
            if TIMESTEP_UNIVERSE > 25920:
                TIMESTEP_UNIVERSE = 25920
        elif keys_pressed[pygame.K_KP1]:
            SCALE_UNIVERSE *= 0.99
        elif keys_pressed[pygame.K_KP3]:
            SCALE_UNIVERSE *= 1.01

        screen.fill((0, 0, 0))

        screen.blit(font2.render(f"Gravity: {round(G, 13)}", True, (255, 255, 255)), (WIDTH // 80, HEIGHT // 40))
        screen.blit(font2.render(f"Timestep: {round(TIMESTEP_UNIVERSE * FPS / 3600 / 24, 2)}d/s", True, (255, 255, 255)),
                    (WIDTH // 80, HEIGHT // 40 * 3))
        screen.blit(font2.render(f"Scale: {round(SCALE_UNIVERSE, 12)}px/m", True, (255, 255, 255)), (WIDTH // 80, HEIGHT // 40 * 5))
        screen.blit(font2.render(f"Show information: {show_information}", True, (255, 255, 255)),
                    (WIDTH // 80, HEIGHT // 40 * 7))
        screen.blit(font2.render(f"Timer: {round(time.time() - timer, 2) if timer_is_running else timer}s", True,
                                 (255, 255, 255)), (WIDTH // 80, HEIGHT // 40 * 9))

        i = 1
        for text in ["7 - 9", "4 - 6", "1 - 3", "   8", "   5",]:
            screen.blit(font2.render(text, True, (255, 255, 255)), (WIDTH // 7, HEIGHT // 40 * i))
            i += 2

        for planet in planets:
            planet.update_position()
            planet.draw_on_screen()

        pygame.display.update()

        for planet in planets:
            mouse_pos = pygame.mouse.get_pos()
            if planet.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                run = False
                planet_to_show = planet.name
                break

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                elif event.key == pygame.K_KP5:
                    if not timer_is_running:
                        timer = time.time()
                        timer_is_running = True
                    else:
                        timer = round(time.time() - timer, 2)
                        timer_is_running = False

                elif event.key == pygame.K_KP8:
                    if not show_information:
                        show_information = True
                    else:
                        show_information = False

    if planet_to_show is not None:
        show_planet_surface(planet_to_show)

def show_planet_surface(name):

    space = None

    for sp in spaces:
        if sp.name == name:
            space = sp

    human.x = WIDTH/SCALE_REAL/2-0.25
    human.y = HEIGHT/SCALE_REAL-2
    human.vel_y = 0

    run = True
    while run:
        clock.tick(FPS)

        space.update_screen()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                elif event.key == pygame.K_w:
                    if human.vel_y == 0:
                        human.vel_y = -(9.80665 * 0.6) ** 0.5

    show_solar_system()

show_solar_system()
