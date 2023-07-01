import cv2
import numpy as np
import pandas as pd
import pygame

pygame.init()

# Read the CSV file with color information
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)  # -1 plays the music on loop
begin_sound = pygame.mixer.Sound("begin.wav")
lose_sound = pygame.mixer.Sound("lost.wav")


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        self.velocity = np.random.uniform(-2, 2, size=2)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.radius -= 0.1

    def is_alive(self):
        return self.radius > 0

# List to store active particles
particles = []

# Function to create particles at a given position
def create_particles(x, y):
    num_particles = 30
    for _ in range(num_particles):
        particle = Particle(x, y)
        particles.append(particle)

game_state = "menu"
clicked = False
r = g = b = xpos = ypos = 0
color_name = ""
points = 0
user_input = ""
result_text = ""
correct_color_text = ""
difficulty = ""

# Function to find the color name from BGR values
def find_color(R, G, B):
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            color_name = csv.loc[i, "color_name"]
    return color_name

# Function to handle mouse events
def find_nearest_basic_color(rgb):
    # Define a dictionary of basic colors and their RGB values
    basic_colors = {
        "Red": (255, 0, 0),
        "Green": (0, 128, 0),
        "Blue": (0, 0, 255),
        "Yellow": (255, 255, 0),
        "Cyan": (0, 255, 255),
        "Magenta": (255, 0, 255),
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
    }

    # Calculate the Euclidean distance between the given RGB value and the basic colors
    color_distances = {}
    for color, rgb_value in basic_colors.items():
        distance = sum((a - b) ** 2 for a, b in zip(rgb, rgb_value))
        color_distances[color] = distance

    # Find the closest basic color
    closest_color = min(color_distances, key=color_distances.get)

    return closest_color

def draw_function(event, x, y, flags, param):
    global game_state, clicked, xpos, ypos, color_name, b, g, r, points, user_input, result_text, correct_color_text, difficulty
    if event == cv2.EVENT_LBUTTONDOWN:
        if game_state == "menu":
            if 220 <= x <= 420 and 200 <= y <= 250:
                game_state = "choose_difficulty"
                clicked = False
                user_input = ""
                result_text = ""
                correct_color_text = ""
                points = 0
                create_particles(x, y)
                begin_sound.play()
            elif 220 <= x <= 420 and 300 <= y <= 350:
                game_state = "quit"
        elif game_state == "choose_difficulty":
            if 220 <= x <= 320 and 300 <= y <= 350:
                difficulty = "easy"
                game_state = "play"
                clicked = False
                user_input = ""
                result_text = ""
                correct_color_text = ""
                points = 0
                create_particles(x, y)
            elif 320 <= x <= 420 and 300 <= y <= 350:
                difficulty = "hard"
                game_state = "play"
                clicked = False
                user_input = ""
                result_text = ""
                correct_color_text = ""
                points = 0
                create_particles(x, y)
        elif game_state == "play":
            clicked = True
            xpos = x
            ypos = y
            b, g, r = frame[y, x]
            b = int(b)
            g = int(g)
            r = int(r)
            if difficulty == "easy":
                color_name = find_nearest_basic_color((r, g, b))
            else:
                color_name = find_color(r, g, b)
            result_text = ""
            correct_color_text = ""

        elif game_state == "lose":
            
            if 220 <= x <= 420 and 330 <= y <= 380:
                game_state = "menu"
                clicked = False
                user_input = ""
                result_text = ""
                correct_color_text = ""
                points = 0
                create_particles(x, y)
            elif 220 <= x <= 420 and 330 <= y <= 380:
                game_state = "quit"

# Open the webcam
cap = cv2.VideoCapture(0)

cv2.namedWindow('Color Detection',cv2.WINDOW_NORMAL)
cv2.resizeWindow('Color Detection', 600,600)
cv2.setMouseCallback('Color Detection', draw_function)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    for particle in particles:
        if particle.is_alive():
            particle.update()
            cv2.circle(frame, (int(particle.x), int(particle.y)), int(particle.radius), particle.color, -1)
        else:
            particles.remove(particle)
    if not ret:
        break

    # Resize the frame for better performance (optional)
    frame = cv2.resize(frame, (640, 480))

    # Draw the menu screen
    if game_state == "menu":
        cv2.rectangle(frame, (220, 200), (420, 250), (255, 255, 255), -1)
        cv2.putText(frame, "Play Game", (255, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.rectangle(frame, (220, 300), (420, 350), (255, 255, 255), -1)
        cv2.putText(frame, "Quit Game", (255, 335), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    elif game_state == "choose_difficulty":
       cv2.rectangle(frame, (220, 300), (320, 350), (255, 255, 255), -1)
       cv2.putText(frame, "Easy", (245, 335), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

       cv2.rectangle(frame, (320, 300), (420, 350), (255, 255, 255), -1)
       cv2.putText(frame, "Hard", (355, 335), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)


    elif game_state == "quit":
        break

    # Draw the lose screen
    elif game_state == "lose":
        lose_sound.play()
        cv2.putText(frame, "YOU LOSE!!", (215, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        cv2.putText(frame, f"Points: {points}", (255, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Correct Color: {correct_color_text}", (205, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.rectangle(frame, (220, 330), (420, 380), (255, 255, 255), -1)
        cv2.putText(frame, "Retry", (295, 365), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        

    # Display the color name at the clicked position
    elif game_state == "play":
        cv2.putText(frame, "Click to guess the color", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Points: {points}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Enter your guess:", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, user_input, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if clicked:
            cv2.putText(frame, "Enter your guess", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if result_text != "" and correct_color_text != "":
            cv2.putText(frame, result_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, correct_color_text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the frame with color information
    cv2.imshow('Color Detection', frame)

    # Check for keyboard events
    key = cv2.waitKey(1)

    # Handle keyboard events
    if key == 27:  # ESC key
        pygame.mixer.music.stop()
        break
    elif key == 8:  # Backspace key
        if game_state == "play" and user_input != "":
            user_input = user_input[:-1]
    elif game_state == "play":
        try:
            if 32 <= key <= 126:
                user_input += chr(key)
        except ValueError:
            pass
        else:
            if key == 13 and clicked:
                user_guess = user_input.strip().lower()
                user_input = ""

                if user_guess == color_name.lower():
                    result_text = "Correct!"
                    points += 1
                else:
                    result_text = "Wrong!"
                    game_state = "lose"

                correct_color_text = f"{color_name}"
                clicked = False

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
