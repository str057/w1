import re

with open('habits/tests_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Найдем и исправим URL в тесте
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'test_get_public_habits' in line:
        # Ищем строку с client.get
        for j in range(i, min(i+20, len(lines))):
            if 'self.client.get(' in lines[j] and '/public/' in lines[j]:
                print(f"Найдена строка: {lines[j]}")
                # Изменяем URL
                old_url = None
                new_url = None
                
                # Проверяем разные варианты кавычек
                if "'/api/habits/public/'" in lines[j]:
                    old_url = "'/api/habits/public/'"
                    new_url = "'/api/habits/habits/public/'"
                elif '"/api/habits/public/"' in lines[j]:
                    old_url = '"/api/habits/public/"'
                    new_url = '"/api/habits/habits/public/"'
                elif "/api/habits/public/" in lines[j]:
                    # Без кавычек в строке
                    lines[j] = lines[j].replace('/api/habits/public/', '/api/habits/habits/public/')
                    print("✓ URL изменен")
                    break
                
                if old_url and new_url:
                    lines[j] = lines[j].replace(old_url, new_url)
                    print(f"✓ Изменен {old_url} -> {new_url}")
                    break
        break

# Сохраняем изменения
with open('habits/tests_api.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Тест исправлен!")
