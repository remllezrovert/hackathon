import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_path, frame_width, frame_height, num_frames, scale_factor=2):
        pygame.sprite.Sprite.__init__(self)
        
        # Load the sprite sheet and set up the frames
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.frames = self.load_animation_frames(sprite_path, frame_width, frame_height, num_frames, scale_factor)
        self.current_frame = 0  # Start with the first frame
        self.image = self.frames[self.current_frame]
        
        # Set the enemy's initial position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Horizontal movement speed and initial velocity
        self.movex = 2
        self.movey = 0  # Vertical speed starts at 0
        self.facing = 'left'  # Initially facing left
        
        # Gravity and jump settings
        self.gravity = 0.5  # How much gravity affects the enemy each frame
        self.jump_strength = -10  # How much force is applied for a jump
        self.on_ground = False  # Tracks if the enemy is on the ground

        # Set an animation speed
        self.animation_speed = 20
        self.animation_counter = 0  # To control the speed of animation updates
        
        # Set boundaries for back-and-forth movement
        self.left_bound = 100
        self.right_bound = 600

        # Ground level (You can modify this to make the enemy land on different y-values)
        self.ground_level = 400  # Example ground level

    def load_animation_frames(self, sprite_path, frame_width, frame_height, num_frames, scale_factor=2):
        """
        Load and scale the sprite sheet frames into a list.
        """
        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()  # Load sprite sheet
        frames = []
        sprite_sheet_width, sprite_sheet_height = sprite_sheet.get_size()

        for i in range(num_frames):
            x = i * frame_width
            y = 0  # All frames are in the first row
            frame = sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))

            # Scale the frame (increase the size of the sprite)
            frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
            frames.append(frame)

        return frames

    def control(self, x, y):
        """
        Control enemy movement.
        """
        self.movex += x
        self.movey += y

    def update(self):
        """
        Update the enemy's position and animation.
        """
        # Gravity effect (add vertical speed)
        if not self.on_ground:  # Only apply gravity if not on the ground
            self.movey += self.gravity

        # Move the enemy
        self.rect.x += self.movex
        self.rect.y += self.movey

        # Check for collision with the ground (or any surface)
        if self.rect.bottom >= self.ground_level:
            self.rect.bottom = self.ground_level  # Stop at the ground level
            self.movey = 0  # Stop vertical movement when hitting the ground
            self.on_ground = True  # Mark that the enemy is on the ground

        # Check if the enemy has hit the boundaries horizontally
        if self.rect.x <= self.left_bound:
            self.movex = abs(self.movex)  # Move right if left boundary is reached
            self.facing = 'right'
        elif self.rect.x >= self.right_bound:
            self.movex = -abs(self.movex)  # Move left if right boundary is reached
            self.facing = 'left'

        # Update the animation when moving
        if self.movex != 0:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                
                if self.facing == 'right':
                    self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
                else:
                    self.image = self.frames[self.current_frame]
        else:
            # If the enemy is not moving, display idle animation (first frame)
            self.image = self.frames[0]

    def jump(self):
        """
        Make the enemy jump by applying a negative vertical speed.
        """
        if self.on_ground:
            self.movey = self.jump_strength  # Apply jump force
            self.on_ground = False  # Mark that the enemy is no longer on the ground
