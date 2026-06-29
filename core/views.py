from django.shortcuts import render, redirect
from .models import Service, CaseStudy, BlogPost, ContactSubmission
from .forms import ContactForm


def home(request):
    cases = CaseStudy.objects.all()[:4]
    return render(request, 'pages/home.html', {'cases': cases})


def services(request):
    services = Service.objects.all()
    return render(request, 'pages/services.html', {'services': services})


def products(request):
    return render(request, 'pages/products.html')


def portfolio(request):
    cases = CaseStudy.objects.all()
    return render(request, 'pages/portfolio.html', {'cases': cases})


def blog(request):
    category = request.GET.get('cat', '')
    posts = BlogPost.objects.all()
    if category:
        posts = posts.filter(category=category)
    context = {
        'posts': posts,
        'categories': BlogPost.CATEGORIES,
        'active_category': category,
    }
    if request.htmx:
        return render(request, 'partials/_blog_grid.html', context)
    return render(request, 'pages/blog.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            ContactSubmission.objects.create(
                name=d['name'],
                email=d['email'],
                whatsapp=d.get('whatsapp', ''),
                company=d['company'],
                revenue_range=d['revenue'],
                service=d['service'],
                tools=d.get('tools', ''),
                challenge=d['challenge'],
            )
            request.session['contact_success'] = {
                'name': d['name'],
                'email': d['email'],
                'company': d['company'],
                'revenue': d['revenue'],
                'service': d['service'],
            }
            return redirect('contact_success')
        step1_fields = {'name', 'email', 'company'}
        step2_fields = {'revenue', 'service'}
        if any(f in form.errors for f in step2_fields):
            initial_step = 2
        elif any(f in form.errors for f in {'tools', 'challenge'}):
            initial_step = 3
        else:
            initial_step = 1
        return render(request, 'pages/contact.html', {
            'form': form,
            'initial_step': initial_step,
            'initial_revenue': request.POST.get('revenue', ''),
            'initial_service': request.POST.get('service', ''),
        })
    return render(request, 'pages/contact.html', {
        'form': ContactForm(),
        'initial_step': 1,
        'initial_revenue': '',
        'initial_service': '',
    })


def contact_success(request):
    data = request.session.pop('contact_success', None)
    if not data:
        return redirect('contact')
    return render(request, 'pages/contact_success.html', {'data': data})


_CHAT_MESSAGES = [
    {'sender': 'agent', 'text': 'Olá, sou o qualificador autônomo da MetaLeads. Identificamos que você anunciou recentemente imóveis de alto padrão em Xangri-lá. Qual seu objetivo comercial principal?'},
    {'sender': 'lead',  'text': 'Olá! Precisamos aumentar o agendamento de visitas de clientes de Porto Alegre.'},
    {'sender': 'agent', 'text': 'Entendido. Para direcionarmos o atendimento ideal, qual o faturamento médio mensal de lançamentos da sua imobiliária?'},
    {'sender': 'lead',  'text': 'Faturamos na faixa de R$ 150 mil a R$ 300 mil mensais.'},
    {'sender': 'agent', 'text': 'Excelente! Sua empresa se qualifica para nosso plano Enterprise. Vou disparar uma agenda de reuniões. Por favor, confirme seu e-mail.'},
    {'sender': 'lead',  'text': 'Confirmado: diretor@imoveisprime.com'},
]

_MAP_LEADS = [
    {'company': 'Construtora Litoral RS',  'source': 'Google Maps API',         'status': 'CAPTURED'},
    {'company': 'Imóveis Prime Torres',    'source': 'Facebook Business',        'status': 'CAPTURED'},
    {'company': 'Hotel Mar Azul',          'source': 'Google Search Scraping',   'status': 'CAPTURED'},
]


def htmx_products_map(request):
    return render(request, 'partials/_demo_map.html', {
        'leads': [],
        'region': 'Porto Alegre / Litoral RS',
    })


def htmx_products_map_search(request):
    region = request.POST.get('region', 'Porto Alegre / Litoral RS')
    return render(request, 'partials/_demo_map.html', {
        'leads': _MAP_LEADS,
        'region': region,
    })


def htmx_products_chat(request):
    return render(request, 'partials/_demo_chat.html', {
        'step': 0,
        'messages': _CHAT_MESSAGES[:1],
    })


def htmx_products_chat_advance(request):
    step = min(int(request.POST.get('chat_step', 0)) + 1, len(_CHAT_MESSAGES) - 1)
    return render(request, 'partials/_demo_chat.html', {
        'step': step,
        'messages': _CHAT_MESSAGES[:step + 1],
    })


def htmx_products_chat_reset(request):
    return render(request, 'partials/_demo_chat.html', {
        'step': 0,
        'messages': _CHAT_MESSAGES[:1],
    })


def htmx_products_kanban(request):
    stage = int(request.GET.get('stage', 0))
    return render(request, 'partials/_demo_kanban.html', {
        'stage': stage,
        'next_stage': (stage + 1) % 4,
    })
