import json

import sys

def print_steps(json_data, indent=0, prefix='', file=None):
    """Рекурсивно печатает шаги из вложенного JSON-объекта.

    Аргументы:
    json_data -- словарь с шагами и подшагами
    indent -- текущий уровень отступа
    prefix -- текущий префикс для вертикальных линий
    file -- файловый объект для записи вывода
    """
    keys = list(json_data.keys())
    for i, key in enumerate(keys):
        value = json_data[key]
        is_last = i == len(keys) - 1

        new_prefix = prefix + ('└── ' if is_last else '├── ')

        print(prefix + new_prefix + value["step"], file=file)

        if value.get("need_futher_breakdown"):
            next_prefix = prefix + ('    ' if is_last else '│   ')
            print_steps(value["SubSteps"], indent=indent + 4, prefix=next_prefix, file=file)

if __name__ == "__main__":
    data = {
        # ... ваш JSON
    }

    with open("output.txt", "w", encoding="utf-8") as f:
        original_stdout = sys.stdout  # сохраняем оригинальный stdout
        sys.stdout = f  # редиректим stdout в файл
        print_steps(data)
        sys.stdout = original_stdout  # возвращаем stdout обратно

# Пример использования
if __name__ == "__main__":
    with open("/Volumes/Windows/questions_brakedown/result_1697222887.623343.json", "r") as data_file:
        data = json.load(data_file)
        with open("output.txt", "w", encoding="utf-8") as f:
            sys.stdout = f  # редиректим stdout в файл
            print_steps(data)
            sys.stdout = original_stdout  # возвращаем stdout обратно
        #print_steps(data)
