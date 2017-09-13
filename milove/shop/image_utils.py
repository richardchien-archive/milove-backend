import os

from imagekit import ImageSpec
from imagekit.cachefiles import ImageCacheFile
from imagekit.processors import ResizeToFill

from .file_storage import storage


class ThumbnailSmall(ImageSpec):
    processors = [ResizeToFill(120, 120)]
    format = 'JPEG'
    options = {'quality': 80}


class ThumbnailMedium(ImageSpec):
    processors = [ResizeToFill(360, 360)]
    format = 'JPEG'
    options = {'quality': 100}


def make_image_preview_tag(image_path, spec=ThumbnailSmall, width=120,
                           link_to_full=True):
    tag = '<img src="{preview}" width="{width}" />'
    if link_to_full:
        tag = '<a href="{full}" target="_blank">' + tag + '</a>'
    with storage.open(image_path, 'rb') as f:
        cache_generator = spec(f)
        cachefile_name = '/'.join((
            'CACHE/images',
            str(image_path),
            os.path.split(cache_generator.cachefile_name)[-1]
        ))
        cached = ImageCacheFile(cache_generator, name=cachefile_name)
        cached.generate()
        tag = tag.format(
            full=storage.url(image_path),
            preview=cached.url,
            width=width
        )
    return tag
