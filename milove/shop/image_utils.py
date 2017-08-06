from imagekit import ImageSpec
from imagekit.processors import ResizeToFill


class ThumbnailSmall(ImageSpec):
    processors = [ResizeToFill(120, 120)]
    format = 'JPEG'
    options = {'quality': 80}


class ThumbnailMedium(ImageSpec):
    processors = [ResizeToFill(360, 360)]
    format = 'JPEG'
    options = {'quality': 100}
