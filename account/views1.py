"""
Django Views for Dynamic Landing Page
Place this in your Django app's views.py
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from .models1 import CarouselSlide, CoreValue, SectionContent, SiteSettings


def home(request):
    """
    View for the home/landing page with dynamic content
    All content is fetched from the database instead of being hardcoded
    """
    
    # Fetch all active carousel slides, ordered by position
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    
    # Fetch all active core values, ordered by position
    values = CoreValue.objects.filter(is_active=True).order_by('order')
    
    # Fetch specific section content
    try:
        mission = SectionContent.objects.get(section_type='mission')
    except SectionContent.DoesNotExist:
        mission = None
    
    try:
        vision = SectionContent.objects.get(section_type='vision')
    except SectionContent.DoesNotExist:
        vision = None
    
    try:
        hero = SectionContent.objects.get(section_type='hero_about')
    except SectionContent.DoesNotExist:
        hero = None
    
    # Fetch site settings
    try:
        settings = SiteSettings.get_settings()
    except:
        settings = None
    
    context = {
        'slides': slides,
        'values': values,
        'mission': mission,
        'vision': vision,
        'hero': hero,
        'settings': settings,
        'slide_count': slides.count(),  # For JavaScript
    }
    
    return render(request, 'account/home.html', context)


class HomePageView(TemplateView):
    """
    Class-based view alternative (if you prefer)
    """
    template_name = 'account/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['slides'] = CarouselSlide.objects.filter(
            is_active=True
        ).order_by('order')
        
        context['values'] = CoreValue.objects.filter(
            is_active=True
        ).order_by('order')
        
        context['mission'] = SectionContent.objects.filter(
            section_type='mission'
        ).first()
        
        context['vision'] = SectionContent.objects.filter(
            section_type='vision'
        ).first()
        
        context['hero'] = SectionContent.objects.filter(
            section_type='hero_about'
        ).first()
        
        context['settings'] = SiteSettings.get_settings()
        context['slide_count'] = context['slides'].count()
        
        return context


# Optional: API views for AJAX/REST requests
from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response


class CarouselSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselSlide
        fields = [
            'id', 'title', 'subtitle', 'description',
            'background_image', 'cta_primary_text', 'cta_primary_url',
            'cta_secondary_text', 'cta_secondary_url', 'order'
        ]


class CoreValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreValue
        fields = ['id', 'icon_class', 'title', 'description', 'order']


class SectionContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionContent
        fields = ['section_type', 'title', 'content']


@api_view(['GET'])
def api_carousel_slides(request):
    """API endpoint to fetch carousel slides as JSON"""
    slides = CarouselSlide.objects.filter(is_active=True).order_by('order')
    serializer = CarouselSlideSerializer(slides, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_core_values(request):
    """API endpoint to fetch core values as JSON"""
    values = CoreValue.objects.filter(is_active=True).order_by('order')
    serializer = CoreValueSerializer(values, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_section_content(request, section_type):
    """API endpoint to fetch specific section content"""
    try:
        content = SectionContent.objects.get(section_type=section_type)
        serializer = SectionContentSerializer(content)
        return Response(serializer.data)
    except SectionContent.DoesNotExist:
        return Response({'error': 'Section not found'}, status=404)


@api_view(['GET'])
def api_site_settings(request):
    """API endpoint to fetch site settings"""
    settings = SiteSettings.get_settings()
    return Response({
        'company_name': settings.company_name,
        'tagline': settings.tagline,
        'primary_color': settings.primary_color,
        'secondary_color': settings.secondary_color,
        'contact_email': settings.contact_email,
        'phone_number': settings.phone_number,
    })