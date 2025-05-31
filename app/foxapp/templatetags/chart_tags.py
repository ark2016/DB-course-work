from django import template
import math

register = template.Library()

@register.filter
def div(value, arg):
    """Деление двух чисел"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Умножение двух чисел"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def sub(value, arg):
    """Вычитание двух чисел"""
    try:
        return float(value) - float(arg)
    except ValueError:
        return 0

@register.filter
def add(value, arg):
    """Сложение двух чисел"""
    try:
        return float(value) + float(arg)
    except ValueError:
        return 0

@register.filter
def min_value(value, arg):
    """Возвращает минимальное из двух чисел"""
    try:
        return min(float(value), float(arg))
    except ValueError:
        return 0

@register.filter
def to_svg_endpoint(angle, params):
    """Вычисляет конечную точку дуги для SVG path
    params должен быть строкой вида "cx,cy,r", например "50,50,40"
    """
    try:
        # Разбиваем параметры на компоненты
        cx, cy, r = map(float, params.split(','))
        
        # Преобразуем угол из градусов в радианы
        rad = math.radians(float(angle))
        
        # Вычисляем координаты точки на окружности
        x = cx + r * math.sin(rad)
        y = cy - r * math.cos(rad)
        
        return f"{x},{y}"
    except (ValueError, AttributeError):
        return "50,50"  # Возвращаем значение по умолчанию в случае ошибки 