from PIL import Image


class SpaceMap:
    def __init__(self, resolution, path):
        self.binmap = self.load_binmap(path)

    @staticmethod
    def load_binmap(path):
        map_img = Image.open(path)
        width, height = map_img.size

        temp = list(map_img.getdata())
        binmap = [temp[i * width:(i + 1) * width] for i in range(height)]

        return binmap
