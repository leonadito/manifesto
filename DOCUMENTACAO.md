# Documentação do Projeto — Agitare Django

Registro completo de todas as decisões, implementações e mudanças executadas na migração do site Agitare de React/Vite para Django + HTMX.

---

## Contexto

O site Agitare era uma SPA React/Vite com 6 páginas, CSS Modules, GSAP, canvas animation e dois componentes de estado complexo (AIChatBot e formulário multi-step). O objetivo foi migrar para uma stack Django + HTMX + Alpine.js, mantendo 100% da identidade visual e simplificando a infraestrutura para Python puro.

**Repositório React original (referência):** `c:\Users\Leonardo\Documents\agitare`
**Projeto Django:** `c:\Users\Leonardo\Documents\agitare_django`
**Venv obrigatória:** `c:\Users\Leonardo\Documents\agitare_django\venv`

---

## Decisões de Arquitetura

| Camada | Escolha | Motivo |
|--------|---------|--------|
| Backend | Django 6.0 | Routing, ORM, admin, views |
| Interatividade | HTMX 2.x | Swaps parciais sem JS framework |
| Micro-interações | Alpine.js 3.x | Mobile menu, tab state, hover — sem React |
| Ícones | Lucide UMD (CDN) | Mesmo set de ícones do React |
| Animações | GSAP 3 + ScrollTrigger | Extraído do React para JS estático |
| Canvas background | neural-bg.js (vanilla) | Extraído do componente NeuralNetworkBg.tsx |
| Templates | Django Templates | Herança de layout, `{% url %}`, `{% static %}` |
| CSS | Global (sem scoping) | CSS Modules eliminados; cada página carrega seu `.css` |
| Estado de demos | HTMX hx-vals | Sem sessão; estado passa pelo próprio elemento |
| CSRF em HTMX | Cookie + configRequest | Handler global no base.html |

---

## Fase 1 — Setup e Páginas Estáticas

### O que foi feito
- `django-admin startproject config .` + `python manage.py startapp core`
- Configuração de `TEMPLATES`, `STATICFILES_DIRS`, `STATIC_URL` em `settings.py`
- Cópia de todos os CSS do React para `static/css/` como arquivos globais
- Criação de `base.html` com blocos `content`, `extra_css`, `extra_js`
- Implementação das páginas **Serviços** e **Portfólio** (loop de dados do ORM)

### Modelos criados (`core/models.py`)

```python
class Service(Model):
    order, title, icon_name, description
    tech_stack (JSONField)
    roi_label, roi_value
    roi_metric_1_label, roi_metric_1_value
    roi_metric_2_label, roi_metric_2_value

class CaseStudy(Model):
    order, title, tag, description
    techs (JSONField)
    result

class BlogPost(Model):
    title, excerpt, category, read_time, published_at, body
    CATEGORIES = [IA, DevOps, Arquitetura, Conversao]

class Lead(Model):
    goal, business_type, revenue, email, created_at

class ContactSubmission(Model):
    name, email, company, revenue_range, service, tools, challenge, created_at
```

### Estrutura de templates

```
templates/
├── base.html
├── pages/
│   ├── home.html
│   ├── services.html
│   ├── products.html
│   ├── portfolio.html
│   ├── blog.html
│   ├── contact.html
│   └── contact_success.html
└── partials/
    ├── _header.html
    ├── _footer.html
    ├── _blog_grid.html
    ├── _demo_map.html
    ├── _demo_chat.html
    └── _demo_kanban.html
```

---

## Fase 2 — Home e Blog

### Header
- Alpine.js `x-data="{ open: false }"` para mobile menu
- Scroll behavior: `window.addEventListener('scroll')` → toggle classe `.scrolled`
- Link ativo: condicional `{% if request.resolver_match.url_name == 'X' %}` direto no template

### Home
- Hero com GSAP ScrollTrigger extraído para `static/js/gsap-hero.js`
- Canvas NeuralNetworkBg extraído para `static/js/neural-bg.js` (vanilla canvas)
- CaseStudies carregados do ORM: `CaseStudy.objects.all()[:4]`

### Blog
- Filtro de categorias via HTMX: `hx-get="/blog/?cat=IA"` retorna o partial `_blog_grid.html`
- A view detecta `request.htmx` e retorna o partial ou a página completa:

```python
def blog(request):
    category = request.GET.get('cat', '')
    posts = BlogPost.objects.all()
    if category:
        posts = posts.filter(category=category)
    if request.htmx:
        return render(request, 'partials/_blog_grid.html', context)
    return render(request, 'pages/blog.html', context)
```

---

## Fase 3 — Formulário de Contato Multi-Step

### Formulário (`core/forms.py`)

```python
class ContactForm(forms.Form):
    name      = CharField(max_length=120)
    email     = EmailField()
    company   = CharField(max_length=120)
    revenue   = ChoiceField(choices=REVENUE_CHOICES)   # 3 faixas
    service   = ChoiceField(choices=SERVICE_CHOICES)   # 5 serviços
    tools     = CharField(required=False, widget=Textarea)
    challenge = CharField(widget=Textarea)
```

### Lógica da view (`contact`)
- Step 1: nome, email, empresa
- Step 2: faturamento, serviço
- Step 3: ferramentas atuais, desafio
- Ao fazer POST com form válido: cria `ContactSubmission` no banco e salva dados em `request.session['contact_success']`
- Redireciona para `/contato/sucesso/` que exibe os dados da sessão e limpa (`session.pop`)
- Em caso de erro, a view detecta qual step tem o erro e retorna `initial_step` correto

### Progresso no front-end
- Alpine.js gerencia `step` ativo; os passos avançam com `@click` nos botões
- O progresso é visual (CSS), sem HTMX — o form inteiro é submetido no passo 3

---

## Fase 4 — Página de Produtos (Demos Interativos)

### Estrutura da página

A página `/produtos/` tem 3 seções:

1. **Intro + Features Grid** — 3 cards (compass, message-square, kanban)
2. **Demo Section** — sidebar com tabs Alpine + painel de conteúdo HTMX
3. **Tech Section** — 3 cards de especificações (server, key, shield-check)

### Padrão Alpine + HTMX nas tabs

```html
<div class="demoGrid" x-data="{tab:'MAP'}">
  <div class="demoTab"
       :class="{demoTabActive: tab === 'MAP'}"
       @click="tab = 'MAP'"
       hx-get="{% url 'htmx_products_map' %}"
       hx-target="#demo-panel"
       hx-swap="innerHTML">
    ...
  </div>

  <div id="demo-panel"
       hx-get="{% url 'htmx_products_map' %}"
       hx-trigger="load"
       hx-target="this"
       hx-swap="innerHTML">
  </div>
</div>
```

- Alpine gerencia classe visual `.demoTabActive`
- HTMX faz o swap do conteúdo no painel
- `hx-trigger="load"` no painel carrega o MAP automaticamente ao abrir a página

### Demo MAP

**Partial:** `templates/partials/_demo_map.html`

- Form com `hx-post` → view retorna o mesmo partial com `leads` populados
- Sem leads: exibe instrução de busca
- Com leads: exibe 3 pulse points no mapa + lista de empresas capturadas

**Views:**
```python
def htmx_products_map(request):          # GET — estado inicial sem leads
def htmx_products_map_search(request):   # POST — retorna leads hardcoded
```

**Dados hardcoded (`_MAP_LEADS`):**
```python
[
    {'company': 'Construtora Litoral RS', 'source': 'Google Maps API',       'status': 'CAPTURED'},
    {'company': 'Imóveis Prime Torres',   'source': 'Facebook Business',      'status': 'CAPTURED'},
    {'company': 'Hotel Mar Azul',         'source': 'Google Search Scraping', 'status': 'CAPTURED'},
]
```

### Demo CHAT

**Partial:** `templates/partials/_demo_chat.html`

- Exibe mensagens acumuladas até o step atual
- Botão "Avançar" passa `chat_step` via `hx-vals` e recebe o partial com uma mensagem a mais
- Botão "Resetar" volta ao step 0
- Botão "Avançar" desabilitado quando `step >= 5`

**Views:**
```python
def htmx_products_chat(request):          # GET — step 0, 1 mensagem
def htmx_products_chat_advance(request):  # POST — incrementa step, retorna mensagens[:step+1]
def htmx_products_chat_reset(request):    # POST — volta a step 0
```

**6 mensagens hardcoded (`_CHAT_MESSAGES`)** simulam conversa entre agente IA e lead imobiliário.

### Demo KANBAN (auto-ciclo)

**Partial:** `templates/partials/_demo_kanban.html`

Solução para replicar o `setInterval` do React sem JS:

```html
<div id="kanban-container"
     hx-get="{% url 'htmx_products_kanban' %}"
     hx-trigger="every 2s"
     hx-vals='{"stage": "{{ next_stage }}"}'
     hx-target="this"
     hx-swap="outerHTML">
```

- `hx-trigger="every 2s"` — HTMX faz GET a cada 2 segundos
- `hx-vals` carrega o `next_stage` embutido no próprio elemento
- `hx-swap="outerHTML"` — o elemento inteiro é substituído, incluindo o novo `hx-vals` com o próximo stage
- Cada stage (0→1→2→3→0) move o card "Imóveis Prime" entre colunas

**View:**
```python
def htmx_products_kanban(request):
    stage = int(request.GET.get('stage', 0))
    return render(request, 'partials/_demo_kanban.html', {
        'stage': stage,
        'next_stage': (stage + 1) % 4,
    })
```

### Rotas adicionadas (`core/urls.py`)

```python
path('htmx/products/map/',          views.htmx_products_map,          name='htmx_products_map'),
path('htmx/products/map/search/',   views.htmx_products_map_search,   name='htmx_products_map_search'),
path('htmx/products/chat/',         views.htmx_products_chat,         name='htmx_products_chat'),
path('htmx/products/chat/advance/', views.htmx_products_chat_advance, name='htmx_products_chat_advance'),
path('htmx/products/chat/reset/',   views.htmx_products_chat_reset,   name='htmx_products_chat_reset'),
path('htmx/products/kanban/',       views.htmx_products_kanban,       name='htmx_products_kanban'),
```

### CSS da página (`static/css/products.css`)

Classes principais convertidas do `Products.module.css` React:
`.productsPage`, `.prodIntro`, `.featuresGrid`, `.featureCard`, `.featureIcon`,
`.demoSection` (com `::before`/`::after` para linhas de gradiente superior/inferior),
`.demoGrid`, `.demoSidebar`, `.demoTab`, `.demoTabActive`, `.demoContentPanel`,
`.mapSimulator`, `.mapTitle`, `.mapVisual`, `.pulsePoint`, `.leadList`, `.leadRow`, `.leadStatus`,
`.chatSimulator`, `.chatMessages`, `.chatMsg`, `.chatMsgAgent`, `.chatMsgLead`,
`.kanbanSimulator`, `.kanbanCol`, `.kanbanColTitle`, `.kanbanCard` (com animação `slideIn`),
`.techSection`, `.techTitle`

---

## Hero — Vídeo de Fundo com Scroll-Scrub

A hero da home recebeu um vídeo de fundo que **não toca sozinho**: ele avança e retrocede quadro a quadro conforme o usuário rola a página, sincronizado com a timeline GSAP que já animava os 3 steps de texto.

### Arquitetura final

- **Elemento:** `<video id="hero-video">` nativo (HTML5), **não** iframe/Vimeo.
- **Camadas no `.heroContainer`:** `.heroVideoBg` (vídeo, `z-index:0`) → `.heroBg` (gradiente translúcido, `z-index:1`) → `.heroOverlay` (`z-index:2`) → `.heroContent` (texto, `z-index:3`).
- **Controle:** `static/js/gsap-hero.js`.

### Como o scrub funciona

```js
// onUpdate do ScrollTrigger (pinned) seta o alvo em segundos
onUpdate: function (self) {
  if (duration > 0) targetTime = self.progress * duration;
}

// gsap.ticker faz lerp suave e aplica em currentTime
gsap.ticker.add(function () {
  if (!duration) return;
  smoothTime += (targetTime - smoothTime) * 0.15;        // suavização
  if (Math.abs(targetTime - smoothTime) > 0.01) {
    video.currentTime = Math.min(smoothTime, duration - 0.05);
  }
});
```

### Carregamento via Blob (crítico)

O vídeo é baixado inteiro via `fetch` e servido de um object URL em memória:

```js
var srcUrl = video.currentSrc || video.getAttribute('src');
fetch(srcUrl)
  .then(function (r) { return r.blob(); })
  .then(function (blob) {
    video.src = URL.createObjectURL(blob);
    video.load();
  });
```

**Por quê:** o `runserver` do Django **não suporta HTTP Range requests**. Sem Range, o navegador marca o vídeo como não-"seekable" (`video.seekable.length === 0`) e **todo `currentTime =` é silenciosamente revertido para 0** — o scrub congela mesmo com o vídeo 100% carregado. Carregar como Blob coloca todos os bytes em memória, tornando o vídeo totalmente seekable independente do servidor. Em produção (nginx/WhiteNoise suportam Range), o Blob continua funcionando igual — e ter o clipe inteiro bufferizado é desejável para scrub.

### Reveal sem flash

`.heroVideoBg` começa em `opacity: 0` (CSS) e só recebe `opacity: 1` quando o primeiro frame está decodificado, evitando hero em branco no carregamento. Como o Blob recarrega o vídeo, os eventos (`loadeddata`, `loadedmetadata`) disparam **depois** dos listeners estarem anexados — resolvendo o bug de "evento já disparou antes do listener" que ocorre com vídeo local (carrega instantâneo).

### Keyframe denso — a chave da fluidez

H.264 só permite seek exato em keyframes; entre eles, o player decodifica em cadeia a partir do keyframe anterior. Com keyframes esparsos (padrão de qualquer exportação — CapCut, Vimeo, etc.) o scrub **trava** entre os pontos. O MP4 da hero foi reencodado com **um keyframe em cada frame**:

```
ffmpeg -i entrada.mp4 -an -c:v libx264 -crf 23 -g 1 -keyint_min 1 -movflags +faststart -pix_fmt yuv420p saida.mp4
```

- `-g 1 -keyint_min 1` → todo frame é keyframe (todo ponto é seekable instantâneo)
- `-an` → remove áudio (desnecessário no fundo)
- `-movflags +faststart` → moov atom no início (boa prática; irrelevante para o Blob, mas útil em outros contextos)
- Custo: arquivo all-intra fica maior (no caso, 3.97MB → 6.4MB para 10s/480p) — aceitável como download único.

**ffmpeg disponível via `imageio-ffmpeg`** (binário isolado, não mexe no sistema):
```
python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
```

> Ao trocar o vídeo da hero, **sempre reencodar com `-g 1`**, senão o scrub volta a travar.

### Caminho até a solução (o que NÃO funcionou)

Tentativas descartadas, registradas para não repetir:

1. **iframe Vimeo com `background=1`** — autoplay forçado (flash de play no load); pause via API é assíncrono e brigava com o modo background.
2. **iframe Vimeo sem `background=1`** — player "idle" não renderiza frame no seek; intermitente.
3. **Vimeo `setCurrentTime` via postMessage** — reverso travado; flood de seeks (sem aguardar a promise) fazia o player descartá-los e congelar.
4. **`<video>` nativo sem faststart** — `moov atom` no fim do arquivo → `duration` retornava `NaN`/`Infinity` até o download completo.
5. **`<video>` nativo direto pela URL estática** — `seekable: 0` por falta de Range no `runserver` → `currentTime` preso em 0.

A combinação vencedora: **`<video>` nativo + carga via Blob + MP4 com keyframe denso**.

---

## Base.html — Modificações

### CSRF global para HTMX POSTs

Adicionado após `lucide.createIcons()` no `base.html`:

```html
<script>
  document.body.addEventListener('htmx:configRequest', function (evt) {
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    if (m) evt.detail.headers['X-CSRFToken'] = m[1];
  });
</script>
```

Garante que **todos** os POSTs HTMX enviam o token CSRF automaticamente, sem precisar de `{% csrf_token %}` em botões fora de `<form>`.

### Lucide em conteúdo HTMX

Em `products.html` (e qualquer página com ícones em conteúdo swappado):

```html
{% block extra_js %}
<script>
document.body.addEventListener('htmx:afterSettle', function () {
  if (typeof lucide !== 'undefined') lucide.createIcons();
});
</script>
{% endblock %}
```

---

## Header — Iterações de Design

### Estado final (rollback para dark)

Fundo: `rgba(12, 15, 30, 0.78)` com `backdrop-filter: blur(16px)` — semi-transparente escuro sobre a neural network background.

### Iterações testadas e descartadas

1. **Fundo sólido `#F02D62`** (pink) — testado, revertido
   - Links mudados para branco
   - Active link: branco com underline branco
   - CTA: botão branco com texto pink (classe `.headerCta`)
   - Menu mobile: fundo `#21317A` (azul brand)

2. **Gradiente 135° `#F02D62 → #21317A`** — testado, revertido

3. **Gradiente vertical `to bottom #F02D62 → #21317A`** — testado, revertido

4. **Rollback completo** — voltou ao estado original dark com glassmorphism

### Estado final do header.css

- Fundo dark translúcido + blur
- Links: `var(--text-secondary)` → branco no hover
- Link ativo: `var(--brand-pink)` + underline `var(--gradient-brand)`
- Mobile menu: escuro `rgba(10,12,25,0.97)` + blur

---

## Logo

Substituída em header e footer de `agitare-logo.png` para `agitare-logo-fundo-0A192F.svg`.

**Arquivos disponíveis em `static/media/logos/`:**
- `agitare-logo.png` — logo antiga (PNG)
- `agitare-logo-A.png` — versão alternativa
- `agitare-logo-fundo-0A192F.svg` — **logo atual (SVG, fundo escuro)**

**Ocorrências atualizadas:**
- `templates/partials/_header.html`
- `templates/partials/_footer.html`

---

## Fase 5 — AIChatBot (pendente)

State machine em `request.session`, widget Alpine.js flutuante, salva `Lead` no banco.

**Estados planejados:** `WELCOME → GOAL_SELECTED → BIZ_TYPE_SELECTED → REVENUE_SELECTED → ASK_EMAIL → CONFIRMATION`

---

## Rotas Completas

| URL | View | Método |
|-----|------|--------|
| `/` | `home` | GET |
| `/servicos/` | `services` | GET |
| `/produtos/` | `products` | GET |
| `/portfolio/` | `portfolio` | GET |
| `/blog/` | `blog` | GET |
| `/contato/` | `contact` | GET / POST |
| `/contato/sucesso/` | `contact_success` | GET |
| `/htmx/products/map/` | `htmx_products_map` | GET |
| `/htmx/products/map/search/` | `htmx_products_map_search` | POST |
| `/htmx/products/chat/` | `htmx_products_chat` | GET |
| `/htmx/products/chat/advance/` | `htmx_products_chat_advance` | POST |
| `/htmx/products/chat/reset/` | `htmx_products_chat_reset` | POST |
| `/htmx/products/kanban/` | `htmx_products_kanban` | GET |

---

## Arquivos Estáticos

| Arquivo | Origem | Propósito |
|---------|--------|-----------|
| `static/css/index.css` | Design system | Variáveis CSS, reset, utilitários globais |
| `static/css/header.css` | Novo | Estilos do header fixo |
| `static/css/footer.css` | Novo | Estilos do footer |
| `static/css/home.css` | `Home.module.css` | Estilos da home |
| `static/css/services.css` | `Services.module.css` | Estilos de serviços |
| `static/css/portfolio.css` | `Portfolio.module.css` | Estilos do portfólio |
| `static/css/blog.css` | `Blog.module.css` | Estilos do blog |
| `static/css/contact.css` | `Contact.module.css` | Estilos do contato |
| `static/css/products.css` | `Products.module.css` | Estilos dos produtos |
| `static/js/neural-bg.js` | `NeuralNetworkBg.tsx` | Canvas animation |
| `static/js/gsap-hero.js` | `Home.tsx` (hero) | GSAP ScrollTrigger + scroll-scrub do vídeo |
| `static/media/agitare_imagem-video_flow.mp4` | — | Vídeo de fundo da hero (reencodado `-g 1` para scrub fluido) |
| `static/media/logos/agitare-logo-fundo-0A192F.svg` | — | Logo atual usada no site |

---

## Problemas Resolvidos

### Write tool — arquivo novo sem Read prévio
A ferramenta `Write` exige que o arquivo tenha sido lido antes. Para criar arquivos novos, o fluxo foi:
1. `Bash: echo "" > arquivo` para criar o arquivo vazio
2. `Read` o arquivo vazio
3. `Write` com conteúdo completo

### CSRF em botões HTMX fora de `<form>`
Os botões "Avançar" e "Resetar" do chat não estão dentro de `<form>`, impossibilitando `{% csrf_token %}`. Solução: handler global `htmx:configRequest` em `base.html` que lê o cookie e injeta o header em todos os POSTs.

### Lucide em conteúdo swappado por HTMX
Após um swap HTMX, elementos `data-lucide` recém inseridos não são processados. Solução: listener `htmx:afterSettle` que re-executa `lucide.createIcons()`.

### Kanban auto-ciclo sem setInterval no servidor
React usava `useState` + `setInterval`. Solução Django/HTMX: o próprio elemento retornado embute o próximo estado em `hx-vals`, e `hx-trigger="every 2s"` + `hx-swap="outerHTML"` cria o ciclo infinito sem nenhum JS customizado.

### Alpine + HTMX no mesmo elemento
Alpine processa `@click` e `:class`; HTMX processa `hx-get` e `hx-target`. Os dois coexistem no mesmo elemento sem conflito — cada biblioteca opera em seus próprios atributos.

### Scroll-scrub de vídeo na hero
Sintoma recorrente "vídeo parado no scroll" teve **várias causas encadeadas**, diagnosticadas com um HUD de debug temporário na tela (mostrando `duration`, `targetTime`, `currentTime`, `seekable`):
1. **`seekable: 0`** — `runserver` não suporta HTTP Range → seek não aplica. Solução: carregar o vídeo via Blob em memória.
2. **`duration: 0` com `rawDuration` válido** — eventos do `<video>` dispararam antes dos listeners (vídeo local carrega instantâneo). Solução: o reload pelo Blob redispara os eventos com listeners já ativos.
3. **Travadinhas** — keyframes esparsos no MP4. Solução: reencode `ffmpeg -g 1 -keyint_min 1`.

Detalhes completos na seção **"Hero — Vídeo de Fundo com Scroll-Scrub"**.

### MP4 sem faststart (`moov atom` no fim)
Vídeos exportados sem `+faststart` colocam o `moov atom` (índice/duração) no fim do arquivo, fazendo `video.duration` retornar `NaN`/`Infinity` até o download completo. Com a carga via Blob isso deixa de importar (todos os bytes ficam em memória), mas o reencode com `-movflags +faststart` é boa prática.
