from django.db import models

import logging
logger = logging.getLogger()


class VideoData(models.Model):
    vimeo_id = models.PositiveIntegerField(blank=True, null=True)
    # Duración del video en segundos para poder determinar si el usuario lo vio completo.
    duration = models.PositiveIntegerField(editable=False, null=True)

    class Meta:
        abstract = True

    # carga los datos del video de vimeo y devuelve el thumb_path
    def load_from_vimeo(self):
        video_data = get_vimeo_video_data(self.vimeo_id)
        self.duration = video_data.get('duration', self.duration)
        pictures = video_data.get('pictures', None)
        return {
            'duration': self.duration,
            'thumb_path': pictures['sizes'][-1]['link'] if pictures else None  # Agarro la más grande
        }


class VimeoAPIException(Exception):
    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.pop('status_code', None)
        self.vimeo_id = kwargs.pop('vimeo_id', None)
        super().__init__(*args, **kwargs)


def get_vimeo_video_data(vimeo_id):
    import vimeo

    # TODO: Sacar esto a .env!!!!
    v = vimeo.VimeoClient(
        token='b6698638ed9792787ee1ede1b927ef4c',
        key='e3a67ae98ccf9f2041d9db6ce40dc025cd0fc6ab',
        secret='/n/AtgiTRdJGL0K8jkd2qXTmNOlBjjt7zTkc2a16LUvJlcJA5l402pkdBjwTqIuNbaIv+56OCSYOlAfaJMDFtrIVWpJSFAU4MjNdppTRGNuL4SsuEC1QPpFhQpuFm84o'
    )

    # Make the request to the server for the "/videos" endpoint.
    video = v.get(f'https://api.vimeo.com/videos/{vimeo_id}')

    if video.status_code != 200:
        raise VimeoAPIException(status_code=video.status_code, vimeo_id=vimeo_id)

    # TODO: Handle errors

    # Load the body's JSON data.
    video_data = video.json()
    return video_data
