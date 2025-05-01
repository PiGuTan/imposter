import requests
import logging

class Image_Client:
    def __init__(self, url, params:str=""):
        self.url = url
        self.params = params
        self.images = []
        self.cached_images: {tuple:object} = {}
        logging.info(f"params: {params}")


    def _call_openapi(self, params:str=""):
        if not self.url:
            return None

        response = requests.request("GET", self.url + params)
        return response.content

    def _call_openapi_with_cache(self,params:str=None, a_frame:int=0, e_frame:int=0):
        if (a_frame, e_frame) in self.cached_images:
            return self.cached_images[(a_frame, e_frame)]
        params = params.format(a_frame=a_frame, e_frame=e_frame)
        image = self._call_openapi(params)
        self.cached_images[(a_frame, e_frame)] = image
        return image

    def get_images(self, a_frames=None, e_frames=None):
        if a_frames is None:
            a_frames = [0]
        if e_frames is None:
            e_frames = [0]
        if len(a_frames) != len(e_frames):
            # make both frame length equal
            a_frames *= len(e_frames)
            e_frames *= len(a_frames)
        images = []
        for a_frame,e_frame in zip(a_frames,e_frames):
            params = self.params.format(a_frame=a_frame, e_frame=e_frame)
            image = self._call_openapi_with_cache(params,a_frame=a_frame,e_frame=e_frame)
            images.append(image)
        return images

