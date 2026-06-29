import re
from django import forms
from django.core.exceptions import ValidationError


def _validate_br_phone(value):
    digits = re.sub(r'\D', '', value)
    if len(digits) not in (10, 11):
        raise ValidationError('Informe um número válido com DDD, ex: (51) 99999-9999.')


REVENUE_CHOICES = [
    ('Até R$ 50k/mês', 'Até R$ 50k/mês'),
    ('R$ 50k a R$ 200k/mês', 'R$ 50k a R$ 200k/mês'),
    ('Acima de R$ 200k/mês', 'Acima de R$ 200k/mês'),
]

SERVICE_CHOICES = [
    ('Arquitetura de Software', 'Arquitetura de Software'),
    ('Inteligência Artificial', 'Inteligência Artificial'),
    ('Automação de Processos', 'Automação de Processos'),
    ('Marketing de Conversão', 'Marketing de Conversão'),
    ('Engenharia de Sites', 'Engenharia de Sites'),
]


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    whatsapp = forms.CharField(max_length=20, validators=[_validate_br_phone])
    company = forms.CharField(max_length=120)
    revenue = forms.ChoiceField(choices=REVENUE_CHOICES)
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    tools = forms.CharField(required=False, max_length=500, widget=forms.Textarea)
    challenge = forms.CharField(widget=forms.Textarea)
