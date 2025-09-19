import json

def transform_fixture(input_file, output_file):
    # Открытие исходного JSON файла
    with open(input_file, 'r', encoding='utf-8') as file:
        ingredients_data = json.load(file)
    
    # Преобразование данных в формат Django фикстуры
    transformed_data = [
        {
            "model": "recipes.ingredient",  # Укажите название вашего приложения и модели
            "pk": idx + 1,  # Генерация уникальных PK для каждой записи
            "fields": {
                "name": ingredient["name"],
                "measurement_unit": ingredient["measurement_unit"]
            }
        }
        for idx, ingredient in enumerate(ingredients_data)
    ]
    
    # Сохранение преобразованных данных в новый файл
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(transformed_data, file, ensure_ascii=False, indent=2)
    
    print(f"Фикстура сохранена в {output_file}")

# Укажите путь к вашему исходному файлу и желаемый путь для результата
input_file = 'ingredients.json'  # Путь к вашему исходному JSON файлу
output_file = 'ingredients_transformed.json'  # Путь для сохранённого изменённого JSON

# Вызов функции для преобразования
transform_fixture(input_file, output_file)