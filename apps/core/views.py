from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Image Processing Application'
        return context


class AboutView(TemplateView):
    """About page view"""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'About'
        return context
