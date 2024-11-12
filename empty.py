import itertools
from datetime import datetime


def generate_combinations(dates):
    # Сортируем даты по возрастанию
    sorted_dates = sorted(dates, key=lambda date: datetime.strptime(date, "%Y-%m-%d"))

    # Генерируем все возможные комбинации из 20 дней
    total_combinations = itertools.combinations(sorted_dates, 20)
    total_count = 0

    # Подсчитываем общее количество комбинаций
    for _ in itertools.combinations(sorted_dates, 20):
        total_count += 1

    # Перебираем комбинации и обрабатываем их по мере генерации
    for i, combination in enumerate(total_combinations, 1):
        # Здесь можно обработать комбинацию, например, записать в файл
        # print(list(combination)) # Для демонстрации, но это может быть заменено на запись в файл

        # Выводим процент выполнения
        if i % 1000 == 0 or i == total_count:
            print(f"Progress: {i / total_count * 100:.2f}%")


# Пример использования
dates = [
    "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
    "2024-01-06", "2024-01-07", "2024-01-08", "2024-01-09", "2024-01-10",
    "2024-01-11", "2024-01-12", "2024-01-13", "2024-01-14", "2024-01-15",
    "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19", "2024-01-20",
    "2024-01-21", "2024-01-22", "2024-01-23", "2024-01-24", "2024-01-25",
    "2024-01-26", "2024-01-27", "2024-01-28", "2024-01-29", "2024-01-30"
]

generate_combinations(dates)

