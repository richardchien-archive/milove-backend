from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.core.files.storage import DefaultStorage
from imagekit.cachefiles import ImageCacheFile

from ..models.sell_request import *
from ..image_utils import ThumbnailSmall


class SellRequestAdmin(admin.ModelAdmin):
    def get_preview(self, instance: SellRequest):
        s = DefaultStorage()
        url = s.url('placeholders/120x120.png')
        if instance.image_paths:
            first_image_path = instance.image_paths[0]
            with s.open(first_image_path, 'rb') as f:
                cached = ImageCacheFile(ThumbnailSmall(f))
                cached.generate()
                url = cached.url
        return '<img src="%s" width="120" />' % url

    get_preview.short_description = _('preview')
    get_preview.allow_tags = True

    list_display = ('id', 'get_preview', 'user', 'brand', 'category', 'name',
                    'size', 'condition', 'purchase_year', 'original_price',
                    'status', 'sell_type')
    list_display_links = ('id', 'get_preview')
    list_filter = ('status', 'sell_type')
    ordering = ('-created_dt',)
    search_fields = ('id', 'user__username', 'user__email',
                     'brand', 'category', 'name', 'description')

    fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
              'size', 'condition', 'purchase_year', 'original_price',
              'attachments', 'description', 'status',
              'buy_back_valuation', 'sell_valuation', 'sell_type')
    readonly_fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
                       'size', 'condition', 'purchase_year', 'original_price',
                       'attachments', 'description',)


admin.site.register(SellRequest, SellRequestAdmin)
