# Создайте категории (если их нет)
python manage.py load_goods --create-categories

# Загрузка с созданием категорий и товаров
python manage.py load_goods --create-products --create-categories

# Обновление существующих товаров
python manage.py load_goods --update --create-categories

# Полная перезагрузка
python manage.py load_goods --clear --create-products --create-categories

# Загрузка с указанием файла
python manage.py load_goods --file fixtures/inventory_data.json --create-products

# Базовый экспорт (простой формат)
python manage.py export_product_residue

# Экспорт с указанием имени файла
python manage.py export_product_residue --file my_export.json

# Детальный формат
python manage.py export_product_residue --format detailed

# Полный формат
python manage.py export_product_residue --format full

# Экспорт с фильтрами
python manage.py export_product_residue --category "Ткани" --min_quantity 50

# Экспорт с использованием стандартного сериализатора Django
python manage.py export_product_residue --format django

# Отчет по остаткам
python manage.py inventory_report

# Отчет по категории
python manage.py inventory_report --category "Ткани"

# Отчет с экспортом в файл
python manage.py inventory_report --export report.txt