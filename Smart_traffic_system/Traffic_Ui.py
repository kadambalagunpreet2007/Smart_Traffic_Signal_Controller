# ============================================================
# TRAFFIC_UI.PY
# This is the MAIN file. Run this file to start the project:
#       python Traffic_Ui.py
#
# It has everything related to pygame (window, drawing, dashboard).
# The AI and traffic logic is imported from Smart_Traffic_Algorithm.py
#
#   PART 1 -> Settings (window size and colours)
#   PART 2 -> Drawing functions (roads, lights, cars, dashboard)
#   PART 3 -> Main program (the simulation loop)
# ============================================================

import pygame

# Import the AI and traffic logic from the other file
from Smart_Traffic_Algorithm import TrafficSystem, TrafficAI, LANES


# ============================================================
# PART 1: SETTINGS
# ============================================================

# Window
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800
FPS = 60

# Colours
GRASS = (28, 120, 48)
ROAD = (42, 45, 52)
WHITE = (240, 240, 240)
YELLOW = (255, 204, 0)
PANEL = (22, 26, 34)
TEXT = (240, 245, 250)
BLUE = (0, 210, 255)
GREEN_TEXT = (46, 204, 113)

# Traffic light colours (ON = bright, OFF = dark)
RED_ON = (255, 50, 50)
RED_OFF = (60, 15, 15)
YELLOW_ON = (255, 220, 0)
YELLOW_OFF = (60, 55, 10)
GREEN_ON = (40, 255, 110)
GREEN_OFF = (10, 55, 25)


# ============================================================
# PART 2: DRAWING FUNCTIONS
# ============================================================

# --------------------------------------------------------
# [DRAW] Background, roads, center lines and stop lines
# --------------------------------------------------------
def draw_roads(screen):

    # Green background
    screen.fill(GRASS)

    # Vertical road and horizontal road
    pygame.draw.rect(screen, ROAD, (320, 0, 160, 800))
    pygame.draw.rect(screen, ROAD, (0, 320, 800, 160))

    # Yellow road center lines
    pygame.draw.line(screen, YELLOW, (400, 0), (400, 320), 3)
    pygame.draw.line(screen, YELLOW, (400, 480), (400, 800), 3)
    pygame.draw.line(screen, YELLOW, (0, 400), (320, 400), 3)
    pygame.draw.line(screen, YELLOW, (480, 400), (800, 400), 3)

    # White stop lines
    pygame.draw.line(screen, WHITE, (320, 320), (400, 320), 5)
    pygame.draw.line(screen, WHITE, (400, 480), (480, 480), 5)
    pygame.draw.line(screen, WHITE, (320, 400), (320, 480), 5)
    pygame.draw.line(screen, WHITE, (480, 320), (480, 400), 5)


# --------------------------------------------------------
# [DRAW] Road names (NORTH, SOUTH, EAST, WEST)
# --------------------------------------------------------
def draw_road_names(screen):

    font = pygame.font.SysFont("Arial", 18, bold=True)

    # Center position of the name of each road
    names = {
        "NORTH": (400, 30),
        "SOUTH": (400, 770),
        "WEST": (45, 400),
        "EAST": (755, 400)
    }

    for name in names:
        position = names[name]
        image = font.render(name, True, WHITE)
        box = image.get_rect(center=position)
        screen.blit(image, box)


# --------------------------------------------------------
# [DRAW] One traffic light (box + 3 bulbs)
# --------------------------------------------------------
def draw_light(screen, x, y, state):

    # Traffic light box
    pygame.draw.rect(screen, (18, 20, 24), (x, y, 26, 70))

    # Decide the colour of each bulb (bright if ON, dark if OFF)
    if state == "RED":
        red = RED_ON
    else:
        red = RED_OFF

    if state == "YELLOW":
        yellow = YELLOW_ON
    else:
        yellow = YELLOW_OFF

    if state == "GREEN":
        green = GREEN_ON
    else:
        green = GREEN_OFF

    # Draw the three bulbs
    pygame.draw.circle(screen, red, (x + 13, y + 14), 7)
    pygame.draw.circle(screen, yellow, (x + 13, y + 35), 7)
    pygame.draw.circle(screen, green, (x + 13, y + 56), 7)


# --------------------------------------------------------
# [DRAW] All four traffic lights
# --------------------------------------------------------
def draw_all_lights(screen, lights):

    draw_light(screen, 288, 244, lights["NORTH"])
    draw_light(screen, 486, 486, lights["SOUTH"])
    draw_light(screen, 288, 486, lights["WEST"])
    draw_light(screen, 486, 244, lights["EAST"])


# --------------------------------------------------------
# [DRAW] One car (tall on up-down roads, wide on left-right roads)
# --------------------------------------------------------
def draw_car(screen, car):

    if car.direction == "NORTH" or car.direction == "SOUTH":
        pygame.draw.rect(screen, car.color, (car.x, car.y, 18, 34))
    else:
        pygame.draw.rect(screen, car.color, (car.x, car.y, 34, 18))


# --------------------------------------------------------
# [DRAW] Side dashboard (counts, green lane, AI decision)
# --------------------------------------------------------
def draw_dashboard(screen, counts, traffic, ai):

    # Dashboard background
    pygame.draw.rect(screen, PANEL, (800, 0, 300, 800))

    title_font = pygame.font.SysFont("Arial", 20, bold=True)
    font = pygame.font.SysFont("Arial", 16)
    small_font = pygame.font.SysFont("Arial", 14)

    # [TITLE]
    title = title_font.render("Smart Traffic Light", True, BLUE)
    screen.blit(title, (825, 25))

    # [COUNTS] Waiting and approaching cars of each lane
    y = 110

    for lane in LANES:

        waiting = counts[lane]["waiting"]
        approaching = counts[lane]["approaching"]

        text = lane + ": Waiting " + str(waiting) + " | Approaching " + str(approaching)

        image = font.render(text, True, TEXT)
        screen.blit(image, (815, y))

        y += 55

    # [GREEN LANE] Which lane has green right now
    y += 20

    image = font.render("GREEN: " + traffic.current_lane, True, GREEN_TEXT)
    screen.blit(image, (815, y))

    # [AI DECISION] The reason of the AI (rule used)
    y += 55

    rule_title = font.render("AI Decision:", True, BLUE)
    screen.blit(rule_title, (815, y))

    # The reason can be long, so split it into two lines
    y += 30

    words = ai.reason.split(" ")

    line1 = ""
    line2 = ""

    for word in words:
        if len(line1) < 35:
            line1 += word + " "
        else:
            line2 += word + " "

    image1 = small_font.render(line1, True, TEXT)
    image2 = small_font.render(line2, True, TEXT)

    screen.blit(image1, (815, y))
    screen.blit(image2, (815, y + 25))

    # [INSTRUCTION]
    instruction = small_font.render("Press R to reset", True, TEXT)
    screen.blit(instruction, (815, 750))


# ============================================================
# PART 3: MAIN PROGRAM
# ============================================================
def main():

    # [START] Start pygame and create the window
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Smart Traffic Light System")

    clock = pygame.time.Clock()

    # [CREATE] The traffic system and the AI agent
    traffic = TrafficSystem()
    ai = TrafficAI()

    running = True

    # ========================================================
    # MAIN LOOP (runs again and again until the window closes)
    # ========================================================
    while running:

        # [EVENTS] Check keyboard / window events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # Press R to reset
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    traffic.reset()

        # [TIME] Seconds passed since the last frame
        dt = clock.tick(FPS) / 1000

        # [UPDATE] Move cars and update lights (the AI decides here)
        traffic.update(dt, ai)

        # Get number of cars of every lane
        counts = traffic.get_counts()

        # [DRAW] Draw everything
        draw_roads(screen)
        draw_road_names(screen)
        draw_all_lights(screen, traffic.get_lights())

        for car in traffic.cars:
            draw_car(screen, car)

        draw_dashboard(screen, counts, traffic, ai)

        # Show the final frame
        pygame.display.update()

    # [END] Close pygame
    pygame.quit()


# Start the program
if __name__ == "__main__":
    main()
