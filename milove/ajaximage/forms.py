from django import forms


class AjaxImageInput(forms.TextInput):
    template_name = 'ajaximage/widgets/ajax_image.html'

    class Media:
        css = {
            'all': (
                'ajaximage/css/bootstrap-progress.min.css',
                'ajaximage/css/styles.css',
            )
        }
        js = (
            'ajaximage/js/ajaximage.js',
        )


class AjaxImageField(forms.CharField):
    widget = AjaxImageInput()
