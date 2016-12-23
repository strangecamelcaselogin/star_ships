from PIL import Image


class SpaceMap:
    def __init__(self, pygame, resolution, map_path):
        self.pygame = pygame

        map_path = './map/test.png'
        img = self.pygame.image.load(map_path)
        img = self.pygame.transform.scale(img, resolution)
        self.map_image = img.copy()

        # TODO scaled pygame image -> list(list())
        self.binmap = self.load_binmap(img)

    def load_binmap(self, img):
        pxarray = self.pygame.PixelArray(img).transpose()
        print(pxarray[0])
        return pxarray
