import logging
from client import Image_Client

from random import choice as random_choice

from PIL import Image
import io

class Character_Image:
    def __init__(self, url:str ,commands:str="", params:str=""):
        self.commands = commands.split(" ")
        self.url = url

        self.params = params

        self._image_client = None
        self.images_data = []
        self.image_gif = []

    @property
    def image_client(self):
        if self._image_client:
            return self._image_client
        self._image_client = Image_Client(self.url, self.params)
        return self._image_client

    def get_images(self, a_frames=None, e_frames=None):
        if len(self.images_data) > 0:
            return
        self.images_data = self.image_client.get_images(a_frames=a_frames, e_frames=e_frames)

    def get_all_images(self, a_frames=None, e_frames=None):
        self.get_images(a_frames=a_frames, e_frames=e_frames)
        if len(self.images_data) == 0:
            logging.error(f"No images found with {self.url}", self.url)
        return [Image.open(io.BytesIO(i)) for i in self.images_data]

    def process_image(self, a_frames=None, e_frames=None):
        images = self.get_all_images(a_frames=a_frames, e_frames=e_frames)
        io_byte = io.BytesIO()
        if len(images) == 1:
            images[0].save(io_byte, format="png")
            return io_byte.getvalue(), "png"
        images[0].save(io_byte,
                       save_all=True, append_images=images[1:],
                       optimize=False, duration=500,format="gif",
                       loop=0, disposal=2)
        io_byte = io_byte.getvalue()
        return io_byte, "gif"

    def get_single_image(self, a_frames=None, e_frames=None):
        a_frame = random_choice(a_frames) if a_frames and len(a_frames)>0 else []
        e_frame = random_choice(e_frames) if e_frames and len(e_frames)>0 else []
        images = self.get_all_images(a_frames=[a_frame], e_frames=[e_frame])
        return images[0]

    def get_single_image_url(self, a_frames=None, e_frames=None):
        a_frame = random_choice(a_frames) if a_frames and len(a_frames)>0 else []
        e_frame = random_choice(e_frames) if e_frames and len(e_frames)>0 else []
        return self.url + self.params.format(a_frame=a_frame, e_frame=e_frame)