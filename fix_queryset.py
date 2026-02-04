import re

with open('habits/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Вернем get_queryset который показывает все привычки для проверки прав
new_get_queryset = '''    def get_queryset(self):
        """
        Возвращаем привычки:
        - Для обычных запросов: ВСЕ привычки (права проверяются отдельно)
        - Для публичного эндпоинта: только публичные привычки
        """
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        
        # Показываем все привычки, доступ будет контролироваться permissions
        return Habit.objects.all()'''

# Находим и заменяем
pattern = r'def get_queryset\(self\):.*?(?=\n    def \w+|\n\n|\Z)'
content = re.sub(pattern, new_get_queryset, content, flags=re.DOTALL)

with open('habits/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("get_queryset исправлен")
