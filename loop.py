import time
import pygame
import sys
import os
from math import *

# Variables
worldx = 960
worldy = 720
fps = 40
ani = 4
world = pygame.display.set_mode([worldx, worldy])

BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)
ALPHA = (0, 255, 0)
FLOOR_HEIGHT = 600  # Floor level (adjust as needed)

# Camera class to handle centering the screen on the player
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.world_size = pygame.Rect(0, 0, 2000, 1000)  # Size of the world (adjust this if needed)
        self.bounds = pygame.Rect(0, 0, width, height)

    def apply(self, entity):
        """
        Moves the entity's rect relative to the camera's position.
        """
        if isinstance(entity, pygame.sprite.Sprite):
            return entity.rect.move(self.camera.topleft)
        elif isinstance(entity, pygame.Rect):
            return entity.move(self.camera.topleft)
        else:
            raise ValueError("entity must be a pygame.sprite.Sprite or pygame.Rect")

    def update(self, target):
        """
        Update the camera's position to follow the target (the player).
        """
        x = -target.rect.centerx + int(self.camera.width / 2)
        y = -target.rect.centery + int(self.camera.height / 2)

        # Keep the camera inside the world bounds
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.world_size.width - self.camera.width), x)
        y = max(-(self.world_size.height - self.camera.height), y)

        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)
     
# Player class
class Player(pygame.sprite.Sprite):
    """
    Spawn a player from a sprite sheet
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0
        self.frame = 0
        self.images = self.load_animation_frames('images/Soldier_1/Walk.png', 128, 128, 7, scale_factor=2)  # Scale sprite
        self.image = self.images[0]  # Set the first frame initially
        self.rect = self.image.get_rect()
        self.rect.x = 100  # Starting X position
        self.rect.y = FLOOR_HEIGHT - self.rect.height  # Starting Y position (on the floor)
        
        self.velocity_y = 0  # For gravity
        self.on_ground = False

        self.shooting = False  # Flag to control the shooting action
        self.sphere_radius = 5
        self.graphs = []  # Store multiple graphs
        self.sphere_indices = []  # Store the sphere index for each graph
        self.graph_creation_times = []  # Store the creation time for each graph

        self.facing = 'right'  # New variable to track which direction the character is facing

        self.explosions = pygame.sprite.Group() # store active explosions
        self.explosion_frames = self.load_explosion_frames('images/PNG/Explosion_9', 10, scale_factor = 0.1)

    def load_animation_frames(self, image_path, frame_width, frame_height, num_frames, scale_factor=2):
        """
        Chop the sprite sheet into individual frames and scale them.
        Args:
            image_path (str): Path to the sprite sheet image.
            frame_width (int): Width of each frame in the sprite sheet.
            frame_height (int): Height of each frame in the sprite sheet.
            num_frames (int): Number of frames in the sprite sheet.
            scale_factor (int): Factor by which to scale the frames (default is 2).
        Returns:
            List of surfaces containing each frame.
        """
        try:
            sprite_sheet = pygame.image.load(image_path).convert_alpha()  # Load sprite sheet
        except pygame.error:
            print(f"Error loading image: {image_path}")
            sys.exit()  # Exit if image can't be loaded

        frames = []
        sprite_sheet_width, sprite_sheet_height = sprite_sheet.get_size()

        # Extract frames from sprite sheet
        for i in range(num_frames):  # Assuming frames are arranged in a single row
            x = i * frame_width
            y = 0  # All frames are in the first row
            frame = sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))

            # Scale the frame (increase the size of the sprite)
            frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))

            frames.append(frame)

        print(f"Loaded {len(frames)} frames from the sprite sheet.")
        return frames

    def control(self, x, y):
        """
        Control player movement
        """
        self.movex += x
        self.movey += y

    def update(self):
        """
        Update sprite position.
        Handle gravity and movement.
        """

        # Apply gravity only if not on the ground
        if not self.on_ground:
            self.velocity_y += 1  # gravity effect

        # Move player with velocity
        self.rect.x += self.movex
        self.rect.y += self.velocity_y

        self.hitbox = pygame.Rect(self.rect.x + 80, self.rect.y + 110, self.rect.width - 170, self.rect.height - 100)

        # Prevent going below the floor (and handle jumping)
        if self.rect.y >= FLOOR_HEIGHT - self.rect.height:
            self.rect.y = FLOOR_HEIGHT - self.rect.height
            self.on_ground = True
        else:
            self.on_ground = False

        # Update facing direction based on movement
        if self.movex < 0:  # Moving left
            self.facing = 'left'
            self.frame += 1
            if self.frame >= len(self.images) * ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)
        elif self.movex > 0:  # Moving right
            self.facing = 'right'
            self.frame += 1
            if self.frame >= len(self.images) * ani:
                self.frame = 0
            self.image = self.images[self.frame // ani]
        else:  # Idle animation when not moving
            if self.facing == 'left':  # Keep the left-facing frame if the player was last moving left
                self.image = self.images[0]  # First frame of the left-facing animation
                self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)
            else:  # Keep the right-facing frame if the player was last moving right
                self.image = self.images[0]  # First frame of the right-facing animation

    def jump(self):
        """
        Make the player jump if on the ground
        """
        if self.on_ground:
            self.velocity_y = -15  # Jump force

    def shootgun(self):
        """
        Start shooting and store graph points to follow
        Freeze the plotPoints
        """
        graph_points = self.drawgraph()  # Generate graph points
        self.graphs.append(graph_points)  # Store the graph
        self.sphere_indices.append(0)  # Add sphere index for the new graph
        self.graph_creation_times.append(time.time())  # Store the creation time of the graph

    def drawgraph(self, equationStr="d[0]=sin(50*x)*50"):
        plotPoints = []
        for x in range(self.rect.x, self.rect.x + 1000):  # Adjust range as needed
            d = [0]
            exec(equationStr)
            y = d[0]
            y = -y + self.rect.y + 155  # Adjust Y value to fit the floor
            plotPoints.append([x, y])

        if self.facing == 'left':
            plotPoints = plotPoints[::-1]  # Reverse the list
            plotPoints = [[x - 1000, y] for x, y in plotPoints]
        else:
            plotPoints = [[x + 180, y] for x, y in plotPoints]

        return plotPoints
    
    def load_explosion_frames(self, image_path, num_frames, scale_factor = 1):
        frames = []
        for i in range(1, num_frames + 1):
            image = pygame.image.load(f"{image_path}/Explosion_{i}.png").convert_alpha()
            image = pygame.transform.scale(image, (image.get_width() * scale_factor, image.get_height() * scale_factor))
            frames.append(image)
        return frames

# Explosion Class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, duration = 1000):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = duration / len(self.frames)

        self.animation_duration = duration 


    def update(self):
        # animate the explosion 
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.last_update = now
            self.index += 1
            
            if self.index >= len(self.frames):
                self.kill() # end explosion 
                return 
                
            self.image = self.frames[self.index]   

# Function to draw the graph (Fixed relative to the floor, affected by camera)
# Setup
backdrop = pygame.image.load(os.path.join('images', 'stage.png'))
clock = pygame.time.Clock()
pygame.init()
backdropbox = world.get_rect()
main = True

player = Player()  # spawn player
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10

# Camera setup
camera = Camera(worldx, worldy)

# Main Loop
while main:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                main = False

        if event.type == pygame.KEYDOWN:
            if event.key == ord('q'):
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    main = False
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.jump()  # Make the player jump when 'w' is pressed

            if event.key == ord(' '):
                player.shootgun()  # Make the player shoot

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)

    # Clear previous frames manually to prevent smearing
    world.fill(BLACK)  # Clear screen before redrawing (now just filling with black)

    # Update camera position based on player movement
    camera.update(player)

    # Draw the backdrop using the camera to apply the correct offset
    world.blit(backdrop, camera.apply(pygame.Rect(0, 0, worldx, worldy)))
    
    # Draw the floor (you can adjust the color of the floor)
    pygame.draw.rect(world, (0, 0, 0), (0, FLOOR_HEIGHT, worldx, worldy - FLOOR_HEIGHT))  # Black floor
    
    # Draw all graphs
    for i, graph in enumerate(player.graphs):
        # Create a surface to render the graph on
        graph_surface = pygame.Surface((worldx, worldy), pygame.SRCALPHA)  # Create a surface with alpha channel

        # Check if one second has passed since the graph was created
        elapsed_time = time.time() - player.graph_creation_times[i]
        
        # If more than 1 second has passed, make the graph transparent
        if elapsed_time >= 0.4:
            graph_color = (0, 0, 0, 0)  # Transparent
        elif elapsed_time >= 0.25:
            graph_color = (255, 0, 0, 25)  # Transparent
        elif elapsed_time >= 0.1:
            graph_color = (255, 255, 0, 50)  # Transparent
        elif elapsed_time >= 0.05:
            graph_color = (255, 255, 255, 200) 
        else:
            graph_color = (0, 0, 255)  # blue color for the graph

        # Draw the graph on the transparent surface
        transformed_points = [camera.apply(pygame.Rect(x, y, 0, 0)).topleft for x, y in graph]
        pygame.draw.lines(graph_surface, graph_color, False, transformed_points, 2)

        # Blit the graph surface to the main world (still with transparency if needed)
        world.blit(graph_surface, (0, 0))
        
        # Draw the spheres that follow the graph
        if player.sphere_indices[i] < len(graph):
            sphere_x, sphere_y = graph[player.sphere_indices[i]]
            sphere_rect = pygame.Rect(sphere_x - player.sphere_radius, sphere_y - player.sphere_radius, player.sphere_radius * 2, player.sphere_radius * 2)
            sphere_x, sphere_y = camera.apply(pygame.Rect(sphere_x, sphere_y, 0, 0)).topleft  # Apply camera to the sphere
            sphere_color = [0, 0, 255]  # Blue color for the sphere
            pygame.draw.circle(world, sphere_color, (int(sphere_x), int(sphere_y)), player.sphere_radius)
            
            # check for collision with the player
            if sphere_rect.colliderect(player.hitbox):
                print("Hit")
                explosion = Explosion(sphere_x, sphere_y, player.explosion_frames, duration = 400)
                player.explosions.add(explosion)

                player.graphs[i].pop(player.sphere_indices[i])

                player.sphere_indices[i] = len(player.graphs[i])
            
            player.sphere_indices[i] += 1

    # Update player position and sprite
    player.update()

    # pygame.draw.rect(world, (0, 255, 0), camera.apply(player.hitbox), 2)  # Green hitbox for debugging

    player.explosions.update()
    player.explosions.draw(world)

    # Manually draw the player sprite using the camera
    world.blit(player.image, camera.apply(player))

    pygame.display.flip()
    clock.tick(fps)
