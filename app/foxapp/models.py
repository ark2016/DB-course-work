from django.db import models


class Survey(models.Model):
    """Модель исследования лисиц"""
    survey_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="Название")
    season = models.CharField(max_length=50, null=True, blank=True, verbose_name="Сезон")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    images = models.ManyToManyField('Image', through='SurveyImageInt', verbose_name="Изображения", related_name='surveys')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Исследование"
        verbose_name_plural = "Исследования"


class ContactPerson(models.Model):
    """Модель контактного лица"""
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Отчество")
    team = models.CharField(max_length=100, null=True, blank=True, verbose_name="Команда")
    contacts = models.TextField(verbose_name="Контактная информация")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Контактное лицо"
        verbose_name_plural = "Контактные лица"


class Location(models.Model):
    """Модель местоположения"""
    name_of_location = models.CharField(max_length=255, primary_key=True, verbose_name="Название местности")
    longitude = models.FloatField(verbose_name="Долгота")
    latitude = models.FloatField(verbose_name="Широта")
    height = models.FloatField(null=True, blank=True, verbose_name="Высота")

    def __str__(self):
        return self.name_of_location

    class Meta:
        verbose_name = "Местоположение"
        verbose_name_plural = "Местоположения"


class Camera(models.Model):
    """Модель фотоловушки"""
    camera_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100, verbose_name="Модель")
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Серийный номер")
    comments = models.TextField(null=True, blank=True, verbose_name="Комментарии")
    location = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True, verbose_name="Местоположение")
    contact_person = models.ForeignKey(ContactPerson, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Контактное лицо")

    def __str__(self):
        return f"{self.model} (ID: {self.camera_id})"

    class Meta:
        verbose_name = "Фотоловушка"
        verbose_name_plural = "Фотоловушки"


class Image(models.Model):
    """Модель изображения"""
    image_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255, verbose_name="Имя файла")
    capture_date_time = models.DateTimeField(verbose_name="Дата и время съемки")
    size = models.IntegerField(null=True, blank=True, verbose_name="Размер файла")
    has_fox = models.BooleanField(default=False, verbose_name="Наличие лисицы")
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True, related_name='images', verbose_name="Фотоловушка")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Местоположение")
    image_file = models.ImageField(upload_to='fox_images/', null=True, blank=True, verbose_name="Файл изображения")

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class Fox(models.Model):
    """Модель лисицы"""
    SEX_CHOICES = [
        ('M', 'Самец'),
        ('F', 'Самка'),
        ('U', 'Неизвестно'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('CUB', 'Детеныш'),
        ('JUVENILE', 'Молодая особь'),
        ('ADULT', 'Взрослая особь'),
        ('SENIOR', 'Старая особь'),
        ('UNKNOWN', 'Неизвестно'),
    ]
    
    fox_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Имя/Идентификатор")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Пол")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, verbose_name="Возрастная группа")
    group = models.CharField(max_length=100, null=True, blank=True, verbose_name="Группа")
    notes = models.TextField(null=True, blank=True, verbose_name="Примечания")
    images = models.ManyToManyField(Image, through='FoxImageInt', verbose_name="Изображения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Лисица"
        verbose_name_plural = "Лисицы"


class SurveyImageInt(models.Model):
    """Промежуточная модель для связи между исследованиями и изображениями"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name="Исследование")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name="Изображение") 

    class Meta:
        verbose_name = "Связь исследование-изображение"
        verbose_name_plural = "Связи исследование-изображение"
        unique_together = ('survey', 'image')


class FoxImageInt(models.Model):
    """Промежуточная модель для связи между лисицами и изображениями"""
    fox = models.ForeignKey(Fox, on_delete=models.CASCADE, verbose_name="Лисица")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name="Изображение")

    class Meta:
        verbose_name = "Связь лисица-изображение"
        verbose_name_plural = "Связи лисица-изображение"
        unique_together = ('fox', 'image') 