import pygame
import pytmx

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)

class TileMap:
    def __init__(self, tmx_file):
        """Initializes the tile map from a TMX file."""
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.tile_size = self.tmx_data.tilewidth
        self.width = self.tmx_data.width * self.tile_size
        self.height = self.tmx_data.height * self.tile_size
        
        # Crear grupo de sprites para los tiles
        self.tiles = pygame.sprite.Group()
        
        # Cargar los tiles del mapa
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        Tile((x * self.tile_size, y * self.tile_size), 
                            tile, 
                            self.tiles)
    
    def draw(self, surface):
        """Draws all tiles on the given surface."""
        self.tiles.draw(surface)
        
    def draw_with_camera(self, surface, camera):
        """Draws the map with camera offset.
        
        Args:
            surface: Surface to draw on
            camera: Camera object used to apply offsets
        """
        # Para cada tile en el mapa
        for tile in self.tiles:
            # Aplicar la cámara para obtener la posición ajustada del tile
            camera_applied_rect = camera.apply_rect(tile.rect)
            
            # Solo dibujar los tiles que son visibles en la pantalla
            if surface.get_rect().colliderect(camera_applied_rect):
                surface.blit(tile.image, camera_applied_rect)