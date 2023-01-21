from wtforms.widgets import TextInput



latex_div = """
<div id="input_group_{id}" class="render-katex">
  <span class="latex-hint">LaTeX-Mathe möglich in $...$</span>
  {markup}<br />
  <span class="katex-output"></span>
</div>
"""


class LatexInput(TextInput):
    input_type = 'latex'

    def __call__(self, field, **kwargs):
        markup = super().__call__(field, **kwargs)
        return latex_div.format(id=field.id, markup=markup)
