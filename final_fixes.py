import os

print("=== Исправление оставшихся проблем ===")

# 1. Исправляем test_habit_model_fields в тестах
test_file = 'habits/tests_api.py'
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'self.assertEqual(self.habit.time, "20:00:00")' in content:
    content = content.replace(
        'self.assertEqual(self.habit.time, "20:00:00")',
        'self.assertEqual(str(self.habit.time), "20:00:00")'
    )
    print("✓ Исправлено сравнение времени в тесте")

with open(test_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Исправляем views.py для правильной работы с чужими привычками
views_file = 'habits/views.py'
with open(views_file, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Найдем метод get_queryset и исправим его
import re

# Заменяем get_queryset на версию, которая показывает все привычки для проверки прав
new_get_queryset = '''    def get_queryset(self):
        """
        Возвращаем привычки:
        - Для обычных запросов: ВСЕ привычки (права проверяются в permissions)
        - Для публичного эндпоинта: только публичные привычки
        """
        if self.action == "public":
            # Для публичного эндпоинта показываем только публичные привычки
            return Habit.objects.filter(is_public=True)
        
        # Для обычных запросов показываем ВСЕ привычки
        # Права доступа проверяются через permission_classes
        return Habit.objects.all()'''

# Находим и заменяем старый get_queryset
pattern = r'def get_queryset\(self\):.*?(?=\n    def|\n\n)'
views_content = re.sub(pattern, new_get_queryset, views_content, flags=re.DOTALL)

# Также добавим метод для проверки существования объекта
new_retrieve_method = '''    def retrieve(self, request, *args, **kwargs):
        """Переопределяем retrieve для корректной обработки ошибок"""
        try:
            instance = self.get_object()
            
            # Проверяем права доступа через permission класс
            self.check_object_permissions(request, instance)
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            
        except Habit.DoesNotExist:
            return Response(
                {"detail": "Привычка не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )'''

# Находим и заменяем старый retrieve
retrieve_pattern = r'def retrieve\(self.*?(?=\n    def|\n\n|\Z)'
views_content = re.sub(retrieve_pattern, new_retrieve_method, views_content, flags=re.DOTALL)

with open(views_file, 'w', encoding='utf-8') as f:
    f.write(views_content)

print("✓ Исправлен get_queryset в views.py")
print("✓ Исправлен retrieve метод в views.py")

# 3. Проверим urls.py
print("\n=== Проверка маршрутов ===")
urls_file = 'config/urls.py'
if os.path.exists(urls_file):
    with open(urls_file, 'r') as f:
        urls_content = f.read()
    if 'path("api/habits/", include("habits.urls"))' in urls_content:
        print("✓ Маршруты настроены правильно")
    else:
        print("⚠ Проверьте маршруты в config/urls.py")

print("\n=== Все исправления применены ===")
print("Запустите тесты: python manage.py test habits.tests_api")
