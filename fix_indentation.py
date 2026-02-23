import re

with open('habits/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Исправляем отступы в views.py...")

# 1. Удаляем лишние пробелы в начале строк
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Удаляем пробелы в начале, но сохраняем табы/пробелы для отступов
    if line.strip():  # если строка не пустая
        # Находим первый не-пробельный символ
        stripped = line.lstrip(' ')
        # Сохраняем отступы (табы или 4 пробела)
        indent_match = re.match(r'^(\s*)', line)
        if indent_match:
            indent = indent_match.group(1)
            # Заменяем пробелы на стандартные отступы (4 пробела)
            indent_level = len(indent) // 4
            new_indent = '    ' * indent_level
            fixed_lines.append(new_indent + stripped)
        else:
            fixed_lines.append(stripped)
    else:
        fixed_lines.append('')

fixed_content = '\n'.join(fixed_lines)

# 2. Убедимся, что классы и методы правильно выровнены
# Исправим конкретно get_queryset
fixed_content = re.sub(r'^\s{4}def get_queryset', '    def get_queryset', fixed_content, flags=re.MULTILINE)
fixed_content = re.sub(r'^\s{8}def', '        def', fixed_content, flags=re.MULTILINE)

with open('habits/views.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Отступы исправлены!")
