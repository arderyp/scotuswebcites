from django import forms
from citations.models import Citation

class VerifyCitationForm(forms.Form):
    validated = forms.URLField()
    scrape_evaluation = forms.ChoiceField(Citation.SCRAPE_EVALUATIONS)
