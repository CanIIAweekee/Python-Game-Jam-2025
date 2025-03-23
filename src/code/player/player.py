"""Class representing the player with animations and movement."""

import pygame
import os


class Player(pygame.sprite.Sprite):
    """Handles the logic and animations of the player."""

    def __init__(self, pos, animation_paths, speed=5, scale=1.0):
        """Initializes the player with position and animations."""
        super().__init__()
        self.speed = speed
        self.scale = scale  
        self.animation_frames = {}
        self.animation_speeds = {
            'idle': 0.1,      
            'walking': 0.08,  
            'attack': 0.05,   
        }
        self.load_animations(animation_paths)
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.facing_right = True
        

        if self.current_animation in self.animation_frames and len(self.animation_frames[self.current_animation]) > 0:
            self.image = self.animation_frames[self.current_animation][0]['original']
        else:
            # Create a fallback image if animations aren't loaded
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))  # Magenta for visibility
            
        self.rect = self.image.get_rect(center=pos)
        self.debug = False  

    def load_animations(self, animation_paths):
        """Loads animations from files."""
        for animation_name, path in animation_paths.items():
            frames = []
            
            # Safety check for path existence
            if not os.path.exists(path):
                print(f"Warning: Animation path does not exist: {path}")
                continue
                
            try:
                files = [f for f in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path, f))]
                
                for frame_name in files:
                    frame_path = os.path.join(path, frame_name)

                    try:
                        frame_image = pygame.image.load(frame_path).convert_alpha()

                        if self.scale != 1.0:
                            width = int(frame_image.get_width() * self.scale)
                            height = int(frame_image.get_height() * self.scale)
                            frame_image = pygame.transform.scale(frame_image, (width, height))
                            

                        frames.append({
                            'original': frame_image,
                            'flipped': pygame.transform.flip(frame_image, True, False)
                        })
                        
                    except Exception as e:
                        print(f"Error loading frame {frame_path}: {e}")

                if frames:
                    self.animation_frames[animation_name] = frames
                    if self.debug:
                        print(f"Loaded {len(frames)} frames for {animation_name}")
                else:
                    print(f"Warning: No frames loaded for animation: {animation_name}")
                    
            except Exception as e:
                print(f"Error processing animation {animation_name}: {e}")
        
        # Create a placeholder if no animations were loaded
        if not self.animation_frames:
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for visibility
            self.animation_frames['idle'] = [{'original': placeholder, 'flipped': placeholder}]
            print("Warning: No animations loaded. Using placeholder.")
            
        for anim_name in self.animation_frames:
            if anim_name not in self.animation_speeds:
                self.animation_speeds[anim_name] = 0.1  # Default speed
                print(f"Set default speed for animation: {anim_name}")

    def get_current_animation_speed(self):
        """Returns the speed for the current animation."""
        return self.animation_speeds.get(self.current_animation, 0.1)  # Default to 0.1 if not found

    def animate(self, dt):
        """Updates the player's animation frame."""
        # Check if animation exists
        if self.current_animation not in self.animation_frames:
            if self.debug:
                print(f"Animation '{self.current_animation}' not found!")
            return
            
        current_speed = self.get_current_animation_speed()
            
        self.animation_timer += dt
        frames_count = len(self.animation_frames[self.current_animation])
        
        if self.animation_timer >= current_speed:
            while self.animation_timer >= current_speed:
                self.animation_timer -= current_speed
                self.frame_index = (self.frame_index + 1) % frames_count
                
            # Update the image based on direction
            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
            else:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['flipped']
                
            if self.debug:
                print(f"Animation: {self.current_animation}, Frame: {self.frame_index}, Speed: {current_speed}, Timer: {self.animation_timer:.3f}")

    def update(self, dt):
        """Updates the player's position and animation."""
        dt = max(dt, 0.001)
        
        # Update animation
        self.animate(dt)
        
        # Update position
        if self.direction.length() > 0:
            normalized_dir = self.direction.normalize()
            self.rect.x += normalized_dir.x * self.speed * dt
            self.rect.y += normalized_dir.y * self.speed * dt

    def set_animation(self, animation_name):
        """Changes the player's current animation."""
        # Only change if the animation exists and is different
        if (animation_name in self.animation_frames and 
            self.current_animation != animation_name):
            
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0

            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][0]['original']
            else:
                self.image = self.animation_frames[self.current_animation][0]['flipped']
                
            if self.debug:
                print(f"Changed animation to: {animation_name}")

    def move(self, direction):
        """Moves the player in a specific direction."""
        # Store previous direction to detect changes
        prev_direction = self.direction.copy()
        
        # Update direction
        self.direction = direction.copy()
        
        # Update animation based on movement state
        if self.direction.length() > 0:
            self.set_animation('walking')
            
            if self.direction.x > 0:
                self.facing_right = True
            elif self.direction.x < 0:
                self.facing_right = False
        else:
            self.set_animation('idle')
            
        # Force image update if direction changed
        if prev_direction != self.direction:
            frames = self.animation_frames[self.current_animation]
            if self.facing_right:
                self.image = frames[self.frame_index]['original']
            else:
                self.image = frames[self.frame_index]['flipped']

    def attack(self):
        """Starts the attack animation."""
        self.set_animation('attack')
        
    def set_animation_speed(self, animation_name, speed):
        """Sets the speed for a specific animation."""
        self.animation_speeds[animation_name] = speed
        
    def set_all_animation_speeds(self, speed_dict):
        """Sets speeds for multiple animations at once.
        
        Args:
            speed_dict: Dictionary mapping animation names to speed values
        """
        for anim_name, speed in speed_dict.items():
            self.animation_speeds[anim_name] = speed