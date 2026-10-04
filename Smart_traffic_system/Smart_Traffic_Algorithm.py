# ============================================================
# SMART_TRAFFIC_ALGORITHM.PY
# This file has ALL the logic / AI part of the project.
#
#   PART 1 -> Settings      (numbers used by the algorithm)
#   PART 2 -> TrafficAI     (the AI agent: decides which lane gets green)
#   PART 3 -> Car           (one car and how it moves)
#   PART 4 -> TrafficSystem (traffic lights + all cars together)
#
# There is NO pygame code here. Drawing is done in Traffic_Ui.py
# ============================================================

import random


# ============================================================
# PART 1: SETTINGS
# ============================================================

# Names of the four roads
LANES = ["NORTH", "EAST", "SOUTH", "WEST"]

# Car settings
CAR_SPEED = 1.5
SAFE_GAP = 14

# Traffic light timing (in seconds)
YELLOW_TIME = 2
MIN_GREEN_TIME = 3
MAX_GREEN_TIME = 15

# Chance of a new car in every frame (smaller number = fewer cars)
SPAWN_RATE = {
    "NORTH": 0.0035,
    "SOUTH": 0.0025,
    "EAST": 0.0025,
    "WEST": 0.002
}

# Different car colours
CAR_COLORS = [
    (235, 77, 75),
    (74, 144, 226),
    (245, 183, 73),
    (240, 240, 245),
    (165, 177, 194),
    (235, 94, 40),
    (162, 155, 254),
    (0, 184, 148)
]


# ============================================================
# PART 2: THE AI AGENT
# Simple idea:
#   1. Count waiting cars
#   2. Check which lane has more cars
#   3. Give green to that lane when needed
# ============================================================
class TrafficAI:

    def __init__(self):
        # [TIMER] used to check the traffic regularly
        self.check_time = 0

        # [TEXT] reason of the last decision (shown on the dashboard)
        self.reason = "Starting the traffic system"

    # --------------------------------------------------------
    # [SENSE] Count the waiting cars of every lane
    # --------------------------------------------------------
    def count_cars(self, cars):

        waiting = {"NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0}

        for car in cars:
            # Only count cars that are waiting
            if car.waiting and not car.passed:
                waiting[car.direction] += 1

        return waiting

    # --------------------------------------------------------
    # [SENSE] Find the lane with the most waiting cars
    # --------------------------------------------------------
    def find_busy_lane(self, waiting):

        best_lane = "NORTH"

        for lane in LANES:
            if waiting[lane] > waiting[best_lane]:
                best_lane = lane

        return best_lane

    # --------------------------------------------------------
    # [THINK] Main AI decision (uses 4 rules)
    # Returns the lane which should get the green light
    # --------------------------------------------------------
    def choose_lane(self, cars, current_lane, green_time):

        waiting = self.count_cars(cars)

        # [RULE 1] Keep the current green light for at least 3 seconds
        if green_time < MIN_GREEN_TIME:
            self.reason = "RULE 1: Minimum green time - keeping " + current_lane + " green"
            return current_lane

        # Find the lane with the most waiting cars
        busy_lane = self.find_busy_lane(waiting)

        # [RULE 2] If another lane has more waiting cars, switch to it
        if busy_lane != current_lane:
            if waiting[busy_lane] > waiting[current_lane]:
                self.reason = "RULE 2: More waiting cars - " + busy_lane + " has " + str(waiting[busy_lane]) + " cars"
                return busy_lane

        # [RULE 3] If green was on for too long, give the busy lane a turn
        if green_time >= MAX_GREEN_TIME:
            if waiting[busy_lane] > 0:
                self.reason = "RULE 3: Maximum green time - giving " + busy_lane + " a turn"
                return busy_lane

        # [RULE 4] Otherwise keep the current lane green
        self.reason = "RULE 4: No higher demand - keeping " + current_lane + " green"
        return current_lane


# ============================================================
# PART 3: CAR CLASS
# Each car knows its position, if it is waiting, and if it
# has already crossed the junction.
# ============================================================
class Car:

    def __init__(self, direction):

        self.direction = direction

        # Random colour for the car
        self.color = random.choice(CAR_COLORS)

        # Information about the car
        self.waiting = False
        self.wait_time = 0
        self.passed = False

        # [START POSITION] depends on the road
        if direction == "NORTH":
            self.x = 351
            self.y = -34
        elif direction == "SOUTH":
            self.x = 431
            self.y = 800
        elif direction == "WEST":
            self.x = -34
            self.y = 431
        else:  # EAST
            self.x = 800
            self.y = 351

    # --------------------------------------------------------
    # [MOVE] Move the car, or make it wait
    # --------------------------------------------------------
    def update(self, dt, light, front_car):

        can_move = True

        # [CHECK 1] Stop near the stop line when the light is not green
        if not self.passed and light != "GREEN":

            if self.direction == "NORTH":
                if self.y + 34 >= 305 and self.y + 34 <= 325:
                    can_move = False
            elif self.direction == "SOUTH":
                if self.y <= 495 and self.y >= 475:
                    can_move = False
            elif self.direction == "WEST":
                if self.x + 34 >= 305 and self.x + 34 <= 325:
                    can_move = False
            elif self.direction == "EAST":
                if self.x <= 495 and self.x >= 475:
                    can_move = False

        # [CHECK 2] Do not hit the car in front
        if front_car is not None:

            if self.direction == "NORTH":
                distance = front_car.y - (self.y + 34)
            elif self.direction == "SOUTH":
                distance = self.y - (front_car.y + 34)
            elif self.direction == "WEST":
                distance = front_car.x - (self.x + 34)
            else:
                distance = self.x - (front_car.x + 34)

            if distance < SAFE_GAP:
                can_move = False

        # [MOVE OR WAIT]
        if can_move:

            self.waiting = False

            if self.direction == "NORTH":
                self.y += CAR_SPEED
            elif self.direction == "SOUTH":
                self.y -= CAR_SPEED
            elif self.direction == "WEST":
                self.x += CAR_SPEED
            else:
                self.x -= CAR_SPEED

            # [PASSED] Once the car has crossed the junction
            if self.direction == "NORTH" and self.y > 480:
                self.passed = True
            elif self.direction == "SOUTH" and self.y < 320:
                self.passed = True
            elif self.direction == "WEST" and self.x > 480:
                self.passed = True
            elif self.direction == "EAST" and self.x < 320:
                self.passed = True

        else:
            self.waiting = True
            self.wait_time += dt

    # --------------------------------------------------------
    # [OUTSIDE] Check if the car has left the screen
    # --------------------------------------------------------
    def outside(self):

        if self.direction == "NORTH" and self.y > 820:
            return True
        if self.direction == "SOUTH" and self.y < -50:
            return True
        if self.direction == "WEST" and self.x > 820:
            return True
        if self.direction == "EAST" and self.x < -50:
            return True

        return False


# ============================================================
# PART 4: TRAFFIC SYSTEM
# Controls the traffic lights, creates cars, moves cars.
# ============================================================
class TrafficSystem:

    def __init__(self):

        self.cars = []

        # First green light is NORTH
        self.current_lane = "NORTH"
        self.next_lane = "NORTH"

        self.light = "GREEN"    # "GREEN" or "YELLOW"
        self.time = 0           # seconds since the light last changed

    # --------------------------------------------------------
    # [RESET] Start everything again
    # --------------------------------------------------------
    def reset(self):

        self.cars = []
        self.current_lane = "NORTH"
        self.next_lane = "NORTH"
        self.light = "GREEN"
        self.time = 0

    # --------------------------------------------------------
    # [COUNT] Waiting and approaching cars of every lane
    # --------------------------------------------------------
    def get_counts(self):

        counts = {}

        for lane in LANES:
            counts[lane] = {"waiting": 0, "approaching": 0}

        for car in self.cars:
            if not car.passed:
                counts[car.direction]["approaching"] += 1
                if car.waiting:
                    counts[car.direction]["waiting"] += 1

        return counts

    # --------------------------------------------------------
    # [ACT] Start the yellow light before changing the lane
    # --------------------------------------------------------
    def change_lane(self, new_lane):

        if new_lane != self.current_lane:
            self.next_lane = new_lane
            self.light = "YELLOW"
            self.time = 0

    # --------------------------------------------------------
    # [LIGHTS] Update the traffic light (ask the AI when green)
    # --------------------------------------------------------
    def update_lights(self, dt, ai):

        self.time += dt

        # If yellow is on, wait until yellow time is over
        if self.light == "YELLOW":

            if self.time >= YELLOW_TIME:
                self.current_lane = self.next_lane
                self.light = "GREEN"
                self.time = 0

            return

        # Ask the AI for a decision (every 0.8 seconds)
        ai.check_time += dt

        if ai.check_time >= 0.8:

            ai.check_time = 0

            new_lane = ai.choose_lane(self.cars, self.current_lane, self.time)

            if new_lane != self.current_lane:
                self.change_lane(new_lane)

    # --------------------------------------------------------
    # [LIGHTS] Colour of the light for every lane
    # Only one lane is GREEN/YELLOW, the others are RED
    # --------------------------------------------------------
    def get_lights(self):

        lights = {"NORTH": "RED", "SOUTH": "RED", "EAST": "RED", "WEST": "RED"}

        lights[self.current_lane] = self.light

        return lights

    # --------------------------------------------------------
    # [SPAWN] Create new cars randomly
    # --------------------------------------------------------
    def add_cars(self):

        for lane in LANES:

            if random.random() < SPAWN_RATE[lane]:

                can_add = True

                # Do not put a new car too close to another car
                for car in self.cars:
                    if car.direction == lane:
                        if lane == "NORTH" and car.y < 50:
                            can_add = False
                        elif lane == "SOUTH" and car.y > 750:
                            can_add = False
                        elif lane == "WEST" and car.x < 50:
                            can_add = False
                        elif lane == "EAST" and car.x > 750:
                            can_add = False

                if can_add:
                    self.cars.append(Car(lane))

    # --------------------------------------------------------
    # [UPDATE] Update everything (called every frame)
    # --------------------------------------------------------
    def update(self, dt, ai):

        self.update_lights(dt, ai)
        self.add_cars()

        lights = self.get_lights()

        # Move the cars of each lane
        for lane in LANES:

            lane_cars = []
            for car in self.cars:
                if car.direction == lane:
                    lane_cars.append(car)

            for i in range(len(lane_cars)):
                front_car = None
                if i > 0:
                    front_car = lane_cars[i - 1]

                lane_cars[i].update(dt, lights[lane], front_car)

        # Remove cars that have left the screen
        new_cars = []
        for car in self.cars:
            if not car.outside():
                new_cars.append(car)

        self.cars = new_cars
