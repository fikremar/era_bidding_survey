from django import forms
from .models import Answer, Response

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['yes_no', 'text', 'bid_amount']
        widgets = {
            'yes_no': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'bid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }