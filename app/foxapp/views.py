from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from .models import Survey, Image, Fox, Camera, SurveyImageInt, FoxImageInt


def home(request):
    """Домашняя страница с основной статистикой"""
    surveys_count = Survey.objects.count()
    images_count = Image.objects.count()
    fox_count = Fox.objects.count()
    camera_count = Camera.objects.count()
    
    # Изображения с лисицами
    images_with_fox = Image.objects.filter(has_fox=True).count()
    images_without_fox = Image.objects.filter(has_fox=False).count()
    
    # Количество связей между исследованиями и изображениями
    survey_image_count = SurveyImageInt.objects.count()
    
    # Количество связей между лисицами и изображениями
    fox_image_count = FoxImageInt.objects.count()
    
    # Статистика по возрастным группам лисиц
    fox_by_age_group = Fox.objects.values('age_group').annotate(count=Count('fox_id'))
    
    context = {
        'surveys_count': surveys_count,
        'images_count': images_count,
        'fox_count': fox_count,
        'camera_count': camera_count,
        'images_with_fox': images_with_fox,
        'images_without_fox': images_without_fox,
        'survey_image_count': survey_image_count,
        'fox_image_count': fox_image_count,
        'fox_by_age_group': fox_by_age_group,
    }
    return render(request, 'foxapp/home.html', context)


def stats_api(request):
    """API для получения статистики в JSON формате"""
    stats = {
        'surveys': Survey.objects.count(),
        'images': Image.objects.count(),
        'foxes': Fox.objects.count(),
        'cameras': Camera.objects.count(),
        'images_with_fox': Image.objects.filter(has_fox=True).count(),
        'survey_image_relations': SurveyImageInt.objects.count(),
        'fox_image_relations': FoxImageInt.objects.count(),
        'fox_by_sex': {
            'male': Fox.objects.filter(sex='M').count(),
            'female': Fox.objects.filter(sex='F').count(),
            'unknown': Fox.objects.filter(sex='U').count(),
        }
    }
    return JsonResponse(stats) 