import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from foxapp.models import (
    Survey, ContactPerson, Location, Camera,
    Image, Fox, FoxImageInt, SurveyImageInt
)


class Command(BaseCommand):
    help = 'Генерирует тестовые данные для базы данных лисиц'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем генерацию тестовых данных...')
        
        # Очистка базы данных (опционально)
        self.clear_data()
        
        # Создание тестовых данных
        self.create_contact_persons()
        self.create_surveys()
        self.create_locations()
        self.create_cameras()
        self.create_foxes()
        self.create_images()
        self.create_survey_image_relations()
        self.create_fox_image_relations()
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
    
    def clear_data(self):
        """Очистка данных в базе"""
        self.stdout.write('Очистка существующих данных...')
        FoxImageInt.objects.all().delete()
        SurveyImageInt.objects.all().delete()
        Fox.objects.all().delete()
        Image.objects.all().delete()
        Camera.objects.all().delete()
        Location.objects.all().delete()
        Survey.objects.all().delete()
        ContactPerson.objects.all().delete()
    
    def create_contact_persons(self):
        """Создание контактных лиц"""
        self.stdout.write('Создание контактных лиц...')
        names = [
            ('Иван', 'Иванов', 'Иванович'),
            ('Петр', 'Петров', 'Петрович'),
            ('Анна', 'Сидорова', 'Алексеевна'),
            ('Мария', 'Кузнецова', 'Владимировна'),
            ('Алексей', 'Смирнов', 'Николаевич'),
        ]
        teams = ['Полевая группа А', 'Полевая группа Б', 'Аналитики', 'Фотографы']
        
        for name in names:
            ContactPerson.objects.create(
                first_name=name[0],
                last_name=name[1],
                middle_name=name[2],
                team=random.choice(teams),
                contacts=f"email: {name[0].lower()}.{name[1].lower()}@example.com, тел: +7-9{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            )
    
    def create_surveys(self):
        """Создание исследований"""
        self.stdout.write('Создание исследований...')
        surveys = [
            ('Исследование мигрирующих лисиц в Подмосковье', 'Весна', '2023-03-01', '2023-05-31', 'Изучение миграционных паттернов лисиц в период весны 2023 года'),
            ('Летний учет популяции лисиц', 'Лето', '2023-06-01', '2023-08-31', 'Количественный учет и оценка распределения лисиц в летний период'),
            ('Исследование социального поведения лисиц', 'Осень', '2023-09-01', '2023-11-30', 'Наблюдение за социальными взаимодействиями в группах лисиц'),
            ('Зимнее выживание лисиц', 'Зима', '2023-12-01', '2024-02-28', 'Исследование стратегий выживания лисиц в зимний период'),
        ]
        
        for name, season, start, end, desc in surveys:
            Survey.objects.create(
                name=name,
                season=season,
                start_date=start,
                end_date=end,
                description=desc
            )
    
    def create_locations(self):
        """Создание местоположений"""
        self.stdout.write('Создание местоположений...')
        locations = [
            ('Лесной участок А', 37.4125, 55.7520, 150),
            ('Овраг у реки', 37.3980, 55.7610, 120),
            ('Окраина поля', 37.4320, 55.7430, 160),
            ('Холм с деревьями', 37.4050, 55.7680, 180),
            ('Заброшенный сад', 37.4220, 55.7550, 155),
            ('Лесополоса у дороги', 37.3920, 55.7500, 140),
            ('Заросли кустарника', 37.4180, 55.7600, 145),
            ('Берег пруда', 37.4010, 55.7480, 130),
        ]
        
        for name, lon, lat, height in locations:
            Location.objects.create(
                name_of_location=name,
                longitude=lon,
                latitude=lat,
                height=height
            )
    
    def create_cameras(self):
        """Создание фотоловушек"""
        self.stdout.write('Создание фотоловушек...')
        camera_models = ['WildCam Pro X2', 'NatureSpy 4K', 'ForestEye 2000', 'TrailMaster HD']
        
        locations = list(Location.objects.all())
        contacts = list(ContactPerson.objects.all())
        
        for i, location in enumerate(locations):
            Camera.objects.create(
                model=random.choice(camera_models),
                serial_number=f"SN{random.randint(1000, 9999)}",
                comments=f"Установлена {random.choice(['на дереве', 'на столбе', 'на специальной опоре'])} на высоте {random.randint(1, 3)} м",
                location=location,
                contact_person=random.choice(contacts)
            )
    
    def create_foxes(self):
        """Создание лисиц"""
        self.stdout.write('Создание лисиц...')
        fox_names = ['Рыжик', 'Огонёк', 'Хвостик', 'Плут', 'Умница', 'Быстрая', 'Хитрый', 'Ловкач', 'Пушистик', 'Звёздочка']
        sex_choices = ['M', 'F']
        age_group_choices = ['CUB', 'JUVENILE', 'ADULT', 'SENIOR', 'UNKNOWN']
        groups = ['Северная группа', 'Южная группа', 'Западная группа', 'Восточная группа', None]
        
        for i in range(15):
            sex = random.choice(sex_choices)
            age_group = random.choice(age_group_choices)
            
            if age_group == 'CUB':
                age = random.randint(1, 11)
            elif age_group == 'JUVENILE':
                age = random.randint(12, 24)
            elif age_group == 'ADULT':
                age = random.randint(25, 60)
            elif age_group == 'SENIOR':
                age = random.randint(61, 120)
            else:
                age = None
            
            Fox.objects.create(
                name=f"{fox_names[i % len(fox_names)]}-{random.randint(1, 999)}",
                sex=sex,
                age=age,
                age_group=age_group,
                group=random.choice(groups),
                notes=f"Обнаружен в {random.choice(['марте', 'апреле', 'мае', 'июне', 'июле', 'августе', 'сентябре', 'октябре'])} 2023"
            )
    
    def create_images(self):
        """Создание изображений"""
        self.stdout.write('Создание изображений...')
        cameras = list(Camera.objects.all())
        
        # Создаем по несколько изображений для каждой камеры
        for camera in cameras:
            # Получаем случайную дату для изображений
            year = 2023
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            base_date = datetime(year, month, day)
            
            for i in range(random.randint(5, 15)):
                # Случайное смещение времени
                random_time = timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                
                capture_datetime = base_date + random_time
                has_fox = random.choice([True, False, True, True])  # Повышаем вероятность True
                
                Image.objects.create(
                    file_name=f"IMG_{camera.camera_id}_{random.randint(1000, 9999)}.jpg",
                    capture_date_time=capture_datetime,
                    size=random.randint(1000000, 8000000),  # размер в байтах
                    has_fox=has_fox,
                    camera=camera,
                    location=camera.location
                )
    
    def create_survey_image_relations(self):
        """Создание связей между исследованиями и изображениями"""
        self.stdout.write('Создание связей между исследованиями и изображениями...')
        surveys = list(Survey.objects.all())
        images = list(Image.objects.all())
        
        for image in images:
            # Находим подходящее исследование по датам
            suitable_surveys = []
            for survey in surveys:
                start_date = datetime.combine(survey.start_date, datetime.min.time())
                end_date = datetime.combine(survey.end_date, datetime.max.time())
                if start_date <= image.capture_date_time <= end_date:
                    suitable_surveys.append(survey)
            
            # Если есть подходящие исследования, выбираем одно из них
            if suitable_surveys:
                survey = random.choice(suitable_surveys)
            else:
                # Если нет подходящего по датам, просто выбираем случайное
                survey = random.choice(surveys)
            
            SurveyImageInt.objects.create(
                survey=survey,
                image=image
            )
    
    def create_fox_image_relations(self):
        """Создание связей между лисицами и изображениями"""
        self.stdout.write('Создание связей между лисицами и изображениями...')
        foxes = list(Fox.objects.all())
        images_with_fox = list(Image.objects.filter(has_fox=True))
        
        # Для каждого изображения с лисицами добавляем от 1 до 3 лисиц
        for image in images_with_fox:
            num_foxes = random.randint(1, min(3, len(foxes)))
            selected_foxes = random.sample(foxes, num_foxes)
            
            for fox in selected_foxes:
                FoxImageInt.objects.create(
                    fox=fox,
                    image=image
                ) 