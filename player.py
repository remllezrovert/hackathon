import pygame
import sys
import os

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

'''
Objects
'''

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

        self.images.add(self.load_animation_frames('images/Soldier_1/Attack.png', 128, 128, 3, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Dead.png', 128, 128, 4, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Explosion.png', 128, 128, 8, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Grenade.png', 128, 128, 9, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Hurt.png', 128, 128, 3, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Idle.png', 128, 128, 7, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Recharge.png', 128, 128, 13, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Run.png', 128, 128, 8, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Shot_1.png', 128, 128, 4, scale_factor=2))  # Scale sprite
        self.images.add(self.load_animation_frames('images/Soldier_1/Shot_2.png', 128, 128, 4, scale_factor=2))  # Scale sprite



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
        else:
            self.velocity_y = 0  # reset gravity when on the ground

        # Move player with velocity
        self.rect.x += self.movex
        self.rect.y += self.velocity_y

        # Prevent going below the floor (and handle jumping)
        if self.rect.y >= FLOOR_HEIGHT - self.rect.height:
            self.rect.y = FLOOR_HEIGHT - self.rect.height
            self.on_ground = True
        else:
            self.on_ground = False

        # Player animation (moving left and right)
        if self.movex < 0:  # moving left
            self.frame += 1
            if self.frame >= len(self.images) * ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)
        elif self.movex > 0:  # moving right
            self.frame += 1
            if self.frame >= len(self.images) * ani:
                self.frame = 0
            self.image = self.images[self.frame // ani]
        else:  # idle animation when not moving
            self.image = self.images[0]  # If idle, show the first frame

    def jump(self):
        """
        Make the player jump if on the ground
        """
        # self.velocity_y = -15  # Jump force
        if self.on_ground:
            print("Jumping!")
            self.velocity_y = -15  # Jump force
        self.velocity_y = -15  # Jump force

'''
Setup
'''

backdrop = pygame.image.load(os.path.join('images', 'stage.png'))
clock = pygame.time.Clock()
pygame.init()
backdropbox = world.get_rect()
main = True

player = Player()  # spawn player
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10

'''
Main Loop
'''

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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)

    # Clear previous frames manually to prevent smearing
    world.fill(BLACK)  # Clear screen before redrawing (now just filling with black)

    # Draw the backdrop
    world.blit(backdrop, backdropbox)
    
    # Draw the floor (you can adjust the color of the floor)
    pygame.draw.rect(world, (0, 0, 0), (0, FLOOR_HEIGHT, worldx, worldy - FLOOR_HEIGHT))  # Black floor
    
    # Update player position and sprite
    player.update()

    # Manually draw the player sprite using blit
    world.blit(player.image, player.rect)

    pygame.display.flip()
    clock.tick(fps)
