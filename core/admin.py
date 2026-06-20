from django.contrib import admin
from .models import Service, CaseStudy, BlogPost, Lead, ContactSubmission


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'roi_label', 'roi_value')
    list_display_links = ('title',)
    list_editable = ('order',)
    ordering = ('order',)


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'tag', 'result')
    list_display_links = ('title',)
    list_editable = ('order',)
    fieldsets = (
        ('Identificação', {
            'fields': ('order', 'tag', 'title', 'subtitle', 'url', 'description', 'result')
        }),
        ('Textos do Portfolio', {
            'fields': ('context', 'problem', 'solution')
        }),
        ('Stack & Métricas', {
            'fields': ('techs', 'metrics')
        }),
        ('Visual', {
            'fields': ('logo', 'card_bg', 'diagram_svg')
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'read_time', 'published_at')
    list_filter = ('category',)
    date_hierarchy = 'published_at'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('email', 'goal', 'business_type', 'revenue', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'service', 'created_at')
    readonly_fields = ('created_at',)
