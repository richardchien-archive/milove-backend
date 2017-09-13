from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from ..models.sell_request import *
from ..image_utils import make_image_preview_tag


class SellRequestSenderAddressInline(admin.StackedInline):
    model = SellRequestSenderAddress

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SellRequestForm(forms.ModelForm):
    class Meta:
        model = SellRequest
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.initial and 'status' in self.initial:
            choice_set = set(get_direct_dst_statuses(self.initial['status']))
            self.fields['status'].choices = map(
                lambda choice: (choice[0], '√ %s' % choice[1])
                if choice[0] in choice_set
                else (choice[0], '× %s' % choice[1]),
                SellRequest.STATUSES
            )


class SellRequestAdmin(admin.ModelAdmin):
    def get_preview(self, instance: SellRequest):
        image = 'placeholders/120x120.png'
        if instance.image_paths:
            image = instance.image_paths[0]
        return make_image_preview_tag(image, link_to_full=False)

    get_preview.short_description = _('preview')
    get_preview.allow_tags = True

    def get_all_images_preview(self, instance: SellRequest):
        tags = []
        for image_path in instance.image_paths:
            tags.append(make_image_preview_tag(image_path))
        return ' '.join(tags) if tags else '-'

    get_all_images_preview.short_description = _('images')
    get_all_images_preview.allow_tags = True

    form = SellRequestForm

    list_display = ('id', 'get_preview', 'user', 'brand', 'category', 'name',
                    'size', 'condition', 'purchase_year', 'original_price',
                    'status', 'buy_back_valuation', 'sell_valuation',
                    'sell_type', 'tracking_number')
    list_display_links = ('id', 'get_preview')
    list_filter = ('status', 'sell_type')
    ordering = ('-created_dt',)
    search_fields = ('id', 'user__username', 'user__email',
                     'brand', 'category', 'name', 'description',
                     'tracking_number')

    fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
              'size', 'condition', 'purchase_year', 'original_price',
              'attachments', 'description', 'get_all_images_preview',
              'status', 'denied_reason', 'buy_back_valuation',
              'sell_valuation', 'valuated_dt', 'sell_type', 'shipping_label',
              'express_company', 'tracking_number')
    readonly_fields = ('id', 'created_dt', 'user', 'brand', 'category', 'name',
                       'size', 'condition', 'purchase_year', 'original_price',
                       'attachments', 'description', 'get_all_images_preview',
                       'valuated_dt')
    inlines = (SellRequestSenderAddressInline,)

    def has_add_permission(self, request):
        # only users can create sell requests
        if request.user.is_superuser:
            # except superuser
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # no one can delete sell requests
        if request.user.is_superuser:
            # except superuser
            return True
        return False


admin.site.register(SellRequest, SellRequestAdmin)
