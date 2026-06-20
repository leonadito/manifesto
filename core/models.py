from django.db import models


class Service(models.Model):
    order = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=120)
    icon_name = models.CharField(max_length=60)
    description = models.TextField()
    tech_stack = models.JSONField(default=list)
    roi_label = models.CharField(max_length=120)
    roi_value = models.CharField(max_length=120)
    roi_metric_1_label = models.CharField(max_length=120, blank=True)
    roi_metric_1_value = models.CharField(max_length=120, blank=True)
    roi_metric_2_label = models.CharField(max_length=120, blank=True)
    roi_metric_2_value = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class CaseStudy(models.Model):
    order = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True, verbose_name='URL do Projeto')
    tag = models.CharField(max_length=80)
    description = models.TextField()
    context = models.TextField(blank=True, verbose_name='Contexto Geral')
    problem = models.TextField(blank=True, verbose_name='Problema & Desafio')
    solution = models.TextField(blank=True, verbose_name='Solução Técnica')
    techs = models.JSONField(default=list)
    diagram_svg = models.TextField(blank=True, verbose_name='Diagrama SVG', help_text='Conteúdo interno do <svg viewBox="0 0 300 200"> (apenas os elementos, sem a tag svg)')
    metrics = models.JSONField(default=list, help_text='Lista de {label, value}, ex: [{"label": "Disponibilidade", "value": "99.99%"}]')
    result = models.CharField(max_length=120)
    logo = models.CharField(max_length=200, blank=True, help_text='Caminho relativo em static/, ex: media/cases-logo/cases-logo-tenisbrasil.svg')
    card_bg = models.CharField(max_length=200, blank=True, help_text='CSS de background do card, ex: linear-gradient(135deg, #2a4a7f 0%, #1e3560 100%)')

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Case Studies'

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    CATEGORIES = [
        ('IA', 'Inteligência Artificial'),
        ('DevOps', 'DevOps'),
        ('Arquitetura', 'Arquitetura'),
        ('Conversao', 'Conversão'),
    ]
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    category = models.CharField(max_length=40, choices=CATEGORIES)
    read_time = models.PositiveSmallIntegerField(help_text='minutos')
    published_at = models.DateField()
    body = models.TextField(blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Lead(models.Model):
    goal = models.CharField(max_length=120)
    business_type = models.CharField(max_length=120)
    revenue = models.CharField(max_length=120)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} — {self.goal}'


class ContactSubmission(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=120, blank=True)
    revenue_range = models.CharField(max_length=80, blank=True)
    service = models.CharField(max_length=80, blank=True)
    tools = models.CharField(max_length=200, blank=True)
    challenge = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} <{self.email}>'
