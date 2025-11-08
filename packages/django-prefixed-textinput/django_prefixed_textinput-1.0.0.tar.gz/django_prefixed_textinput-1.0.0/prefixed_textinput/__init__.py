from django.forms.widgets import TextInput


class PrefixedTextInput(TextInput):
    template_name = 'widget.html'

    class Media:
        css = {
            'all': ('css/widget.css',),
        }

    def __init__(self, attrs=None, prefix=''):
        self.prefix = prefix
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["prefix"] = self.prefix
        return context
