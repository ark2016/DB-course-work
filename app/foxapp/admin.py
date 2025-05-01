from django.contrib import admin
from .models import (
    Survey, ContactPerson, Location, Camera,
    Image, Fox, FoxImageInt, SurveyImageInt
)


class SurveyImageInline(admin.TabularInline):
    model = SurveyImageInt
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('survey_id', 'name', 'season', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    list_filter = ('season',)
    inlines = [SurveyImageInline]


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'middle_name', 'team')
    search_fields = ('last_name', 'first_name', 'team')
    list_filter = ('team',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name_of_location', 'longitude', 'latitude', 'height')
    search_fields = ('name_of_location',)


class FoxImageInline(admin.TabularInline):
    model = FoxImageInt
    extra = 1


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('camera_id', 'model', 'serial_number', 'location')
    search_fields = ('model', 'serial_number')
    list_filter = ('model',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'file_name', 'capture_date_time', 'has_fox')
    search_fields = ('file_name',)
    list_filter = ('has_fox',)
    inlines = [FoxImageInline, SurveyImageInline]


@admin.register(Fox)
class FoxAdmin(admin.ModelAdmin):
    list_display = ('fox_id', 'name', 'sex', 'age', 'age_group', 'group')
    search_fields = ('name',)
    list_filter = ('sex', 'age_group', 'group')
    inlines = [FoxImageInline]


@admin.register(FoxImageInt)
class FoxImageIntAdmin(admin.ModelAdmin):
    list_display = ('fox', 'image')
    list_filter = ('fox', 'image')


@admin.register(SurveyImageInt)
class SurveyImageIntAdmin(admin.ModelAdmin):
    list_display = ('survey', 'image')
    list_filter = ('survey', 'image') 