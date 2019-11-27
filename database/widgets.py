from wtforms.widgets import TextInput


class LatexInput(TextInput):
    input_type = 'latex'

    def __call__(self, field, **kwargs):
        kwargs['v-model'] = 'title'
        markup = super().__call__(field, **kwargs)
        return f'<div id="input_group_{field.id}" class="render-katex">{markup}<br /><span class="" v-html="title_html"></span></div>'
