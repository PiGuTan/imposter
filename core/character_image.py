import logging
from client import Image_Client

from PIL import Image
import io

class Character_Image:
    def __init__(self, url:str ,commands:str="", params:str=""):
        self.commands = commands.split(" ")
        self.url = url

        self.params = params

        self.image_client = None
        self.images_data = []
        self.image_gif = []

    def get_images(self, a_frames=None, e_frames=None):
        if len(self.images_data) > 0:
            return
        self.image_client = Image_Client(self.url, self.params)
        self.images_data = self.image_client.get_images(a_frames=a_frames, e_frames=e_frames)


    def process_image(self, a_frames=None, e_frames=None):
        self.get_images(a_frames=a_frames, e_frames=e_frames)
        if len(self.images_data) == 0:
            logging.error("No images found with {self.url}", self.url)
        images = [Image.open(io.BytesIO(i)) for i in self.images_data]
        io_byte = io.BytesIO()
        images[0].save(io_byte,
                       save_all=True, append_images=images[1:],
                       optimize=False, duration=500,format="gif",
                       loop=0, disposal=2)

        io_byte = io_byte.getvalue()
        return io_byte
