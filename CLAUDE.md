# Agitare Django — CLAUDE.md

## Ambiente

- **Python venv**: `c:\Users\Leonardo\Documents\agitare_django\venv`
- Sempre ativar antes de qualquer comando: `.\venv\Scripts\activate`
- Rodar servidor: `python manage.py runserver`
- Verificar erros: `python manage.py check`
- Admin: `/admin` — usuário `admin`

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 6.0 |
| Interatividade | HTMX 2.x |
| Micro-interações | Alpine.js 3.x |
| Ícones | Lucide (UMD via CDN) |
| Animações | GSAP 3 + ScrollTrigger |
| Canvas bg | neural-bg.js (vanilla JS) |
| Vídeo hero | `<video>` nativo com scroll-scrub (gsap-hero.js) |
| Banco | SQLite (dev) |

## Estrutura de diretórios

```
agitare_django/
├── config/               # settings, urls raiz, wsgi
├── core/
│   ├── models.py         # Service, CaseStudy, BlogPost, Lead, ContactSubmission
│   ├── views.py          # views de página + endpoints HTMX
│   ├── urls.py           # todas as rotas
│   └── forms.py          # ContactForm
├── templates/
│   ├── base.html         # layout global (favicon: agitare-favicon.svg)
│   ├── pages/            # home, services, products, portfolio, blog, contact
│   └── partials/         # _header, _footer, _blog_grid, _demo_map/chat/kanban
└── static/
    ├── css/              # um arquivo por página + index/header/footer
    ├── js/               # neural-bg.js, gsap-hero.js (scroll-scrub do vídeo)
    └── media/
        ├── agitare_imagem-video_flow.mp4   # vídeo da hero
        ├── agitare-favicon.svg             # favicon com gradiente da marca
        └── cases-logo/                     # logos dos cases (SVG)
            ├── cases-logo-tenisbrasil.svg
            ├── cases-logo-mtb.svg
            └── ...
```

## Identidade visual

```css
--brand-blue:    #21317A
--brand-pink:    #F02D62
--gradient-brand: linear-gradient(135deg, #21317A 0%, #F02D62 100%)
--bg-primary:    #0A192F
--font-sans:     Inter
--font-heading:  Outfit
```

O CSS é global (sem CSS Modules). Cada página carrega seu próprio arquivo via `{% block extra_css %}`.

**Regra editorial:** não expor linguagens/frameworks no conteúdo do site (sem mencionar Python, Django, HTMX etc. para o usuário final).

## Padrões HTMX

- CSRF automático: handler global em `base.html` lê o cookie `csrftoken` e injeta `X-CSRFToken` em todos os POSTs — não adicionar `{% csrf_token %}` em botões fora de `<form>`.
- Ícones Lucide em conteúdo swappado: chamar `lucide.createIcons()` no evento `htmx:afterSettle`.
- Estado entre requests: passar via `hx-vals` (GET) ou body do POST — sem sessão para demos.
- Auto-ciclo: `hx-trigger="every Ns"` + `hx-swap="outerHTML"` + `hx-vals` com o próximo estado embutido no próprio elemento retornado.

## Vídeo da hero (scroll-scrub)

A hero da home tem um vídeo de fundo que avança/retrocede conforme o scroll (não toca sozinho). Controlado por `static/js/gsap-hero.js`.

- **`<video>` nativo**, não iframe/Vimeo — seek nativo (`currentTime`) é síncrono e fluido nos dois sentidos.
- **Carregado via Blob**: o JS faz `fetch` do MP4 e usa `URL.createObjectURL`. Necessário porque o `runserver` do Django **não suporta HTTP Range requests** — sem isso o vídeo não é "seekable" e o scrub congela. Em produção (nginx/WhiteNoise há suporte a Range), o Blob continua funcionando igual.
- **Scrub**: `gsap.ticker` faz lerp de `smoothTime` → `targetTime` (setado no `onUpdate` do ScrollTrigger) e aplica em `video.currentTime`.
- **O MP4 precisa de keyframe denso** para o scrub não travar. Reencodar sempre que trocar o vídeo:
  ```
  ffmpeg -i entrada.mp4 -an -c:v libx264 -crf 23 -g 1 -keyint_min 1 -movflags +faststart -pix_fmt yuv420p saida.mp4
  ```
  `-g 1 -keyint_min 1` = um keyframe em cada frame (todo ponto é seekable). ffmpeg disponível via `imageio-ffmpeg` (já instalado): `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`.

## Rotas HTMX existentes

| URL | Método | View |
|-----|--------|------|
| `/htmx/products/map/` | GET | `htmx_products_map` |
| `/htmx/products/map/search/` | POST | `htmx_products_map_search` |
| `/htmx/products/chat/` | GET | `htmx_products_chat` |
| `/htmx/products/chat/advance/` | POST | `htmx_products_chat_advance` |
| `/htmx/products/chat/reset/` | POST | `htmx_products_chat_reset` |
| `/htmx/products/kanban/` | GET | `htmx_products_kanban` |

## Modelos

### CaseStudy
Exibido em `/portfolio/` (página completa) e `/` (cards de destaque na home).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `order` | int | Ordem de exibição |
| `title` | str | Nome do case |
| `subtitle` | str | Subtítulo (ex: "Arquitetura de Escala para Portal de Mídia") |
| `tag` | str | Badge da categoria |
| `description` | text | Descrição curta (usada no card da home) |
| `context` | text | Seção "Contexto Geral" no portfolio |
| `problem` | text | Seção "Problema & Desafio" no portfolio |
| `solution` | text | Seção "Solução Técnica" no portfolio |
| `techs` | JSON | Lista de strings com tecnologias: `["React", "AWS EC2"]` |
| `diagram_svg` | text | Elementos SVG internos do diagrama técnico (sem tag `<svg>`) |
| `metrics` | JSON | Lista de métricas ROI: `[{"label": "...", "value": "..."}]` |
| `result` | str | Resultado resumido (exibido no card da home) |
| `logo` | str | Caminho relativo em `static/`, ex: `media/cases-logo/cases-logo-tenisbrasil.svg` |
| `card_bg` | str | CSS de background do card home, ex: `linear-gradient(135deg, #030f12 0%, #051518 100%)` |

**Cases cadastrados:** TenisBrasil (UOL), Memorial Tênis Brasileiro, Beach Mania, Imobiliária Litoral RS.

### Outros modelos
- **Service** — serviços exibidos em `/servicos/`, gerenciados pelo admin
- **BlogPost** — posts em `/blog/`, filtráveis por categoria via HTMX
- **Lead** — capturado pelo AIChatBot (Fase 5, ainda não implementado)
- **ContactSubmission** — formulário multi-step em `/contato/`

## Cards de case na home (`home.html`)

- Imagem do card: `.caseImagePlaceholder` com altura fixa de **240px**
- Logo exibido via `<img class="caseLogo">` quando `case.logo` está preenchido
- Tamanho ideal de imagem/logo: **800 × 320px** (proporção 5:2), `object-fit: contain`
- Fundo customizável por case via campo `card_bg` no admin
- Fallback quando sem logo: exibe o título em texto (`.caseLogoOverlay`)

## Favicon

`static/media/agitare-favicon.svg` — SVG com gradiente da marca aplicado via `linearGradient` + máscara SVG. O gradiente segue `--gradient-brand` (#21317A → #F02D62, diagonal 135°).

## Fases de migração (React → Django)

- [x] Fase 1 — Setup + páginas estáticas (Services, Portfolio)
- [x] Fase 2 — Home + Blog (GSAP hero, filtro HTMX)
- [x] Fase 3 — Contact multi-step form + ContactSubmission
- [x] Fase 4 — Products (demos interativos MAP/CHAT/KANBAN via HTMX + Alpine)
- [x] Fase 4.5 — Portfolio dinâmico (CaseStudy totalmente gerenciável via admin)
- [ ] Fase 5 — AIChatBot widget (state machine em sessão, salva Lead no banco)

## React source (referência)

`c:\Users\Leonardo\Documents\agitare` — repositório original React/Vite. Consultar para replicar lógica ou visual de qualquer página.
