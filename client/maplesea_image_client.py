import requests

class Image_Client:
    def __init__(self, url, params:str=None):
        self.url = url
        self.params = params
        self.images = []
        self.cached_images: {tuple:object} = {}


    def _call_openapi(self, params:str=None):
        if not self.url:
            return None

        """
        sample param (not processed here)
        {
            "action": "heal", # A10 (0~2 frame)
            "emption": "hum", # E16 (0~1 frame)
            "weapon": "gun", # W03
            "width": "",
            "height": "",
            "x": "",
            "y": "",
        }
        self.param will be "action=A10.{a_frame}}&emotion=E16.{e_frame}}&wmotion=W03
        """

        response = requests.request("GET", self.url, params=params)
        return response.content # is this correct?

    def _call_openapi_with_cache(self,params:str=None, a_frame:int=0, e_frame:int=0):
        if (a_frame, e_frame) in self.cached_images:
            return self.cached_images[(a_frame, e_frame)]
        params = params.format(a_frame=a_frame, e_frame=e_frame)
        image = self._call_openapi(params)
        self.cached_images[(a_frame, e_frame)] = image
        return image

    def get_images(self, params:str=None, a_frames=None, e_frames=None):
        if a_frames is None:
            a_frames = [0]
        if e_frames is None:
            e_frames = [0]
        images = []
        for a_frame,e_frame in a_frames,e_frames:
            image = self._call_openapi_with_cache(params,a_frame=a_frame,e_frame=e_frame)
            images.append(image)
        return images

