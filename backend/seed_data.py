# backend/seed_data.py
"""
Скрипт для заполнения базы данных демонстрационными данными канцелярского магазина «Канцелярия №1».
Создает категории и товары канцелярских принадлежностей для демонстрации работы приложения.
Использует placeholder изображения с unsplash.com.
"""

from app.database import SessionLocal, init_db
from app.models.category import Category
from app.models.product import Product


def create_categories(db):
    """
    Создает категории товаров.

    Args:
        db: Сессия SQLAlchemy

    Returns:
        dict: Словарь созданных категорий {slug: Category}
    """
    categories_data = [
        {"name": "Письменные принадлежности", "slug": "pismennye"},
        {"name": "Тетради и бумага", "slug": "bumaga"},
        {"name": "Школьные товары", "slug": "shkolnye"},
        {"name": "Офисные принадлежности", "slug": "ofisnye"},
        {"name": "Рисование и творчество", "slug": "tvorchestvo"},
    ]

    categories = {}
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories[cat_data["slug"]] = category

    db.commit()

    # Обновляем объекты после commit для получения ID
    for category in categories.values():
        db.refresh(category)

    return categories


def create_products(db, categories):
    """
    Создает товары в различных категориях.

    Args:
        db: Сессия SQLAlchemy
        categories: Словарь категорий
    """
    products_data = [
        # Письменные принадлежности
        {"name": "Ручка гелевая Pilot G-2", "description": "Гелевая ручка 0.7 мм, синие чернила. Плавное письмо, удобный грип.", "price": 89, "brand": "Pilot", "sku": "PIL-G2-BL", "unit": "шт", "pack_qty": 1, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400"},
        {"name": "Карандаш чернографитный HB", "description": "Классический карандаш твёрдости HB, заточенный. Набор 12 шт.", "price": 145, "brand": "Koh-i-Noor", "sku": "KIN-HB-12", "unit": "упаковка", "pack_qty": 12, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1587145820266-a5951ee6f620?w=400"},
        {"name": "Маркер текстовый набор 4 цв.", "description": "Флуоресцентные текстовыделители, скошенный наконечник. 4 цвета.", "price": 210, "brand": "Stabilo", "sku": "STB-BOSS-4", "unit": "упаковка", "pack_qty": 4, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400"},
        {"name": "Ручка шариковая синяя", "description": "Шариковая ручка 0.5 мм, экономичный расход. Упаковка 50 шт.", "price": 390, "brand": "ErichKrause", "sku": "EK-R301-50", "unit": "упаковка", "pack_qty": 50, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1625480860249-be231d1e1d0f?w=400"},

        # Тетради и бумага
        {"name": "Тетрадь 48 л. в клетку", "description": "Тетрадь на скрепке, обложка картон, клетка. Плотная бумага.", "price": 65, "brand": "ErichKrause", "sku": "EK-48-KL", "unit": "шт", "pack_qty": 1, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400"},
        {"name": "Бумага А4 «SvetoCopy» 500 л.", "description": "Офисная бумага для печати, белизна 146% CIE, плотность 80 г/м².", "price": 540, "brand": "SvetoCopy", "sku": "SC-A4-500", "unit": "упаковка", "pack_qty": 500, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1568871391541-1d62a0d54c89?w=400"},
        {"name": "Блокнот на пружине А5", "description": "Блокнот 80 листов, твёрдая обложка, перфорация. Клетка.", "price": 230, "brand": "Hatber", "sku": "HAT-A5-80", "unit": "шт", "pack_qty": 1, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=400"},
        {"name": "Стикеры клейкие 76×76 мм", "description": "Самоклеящиеся листки, неоновые цвета, 100 листов в блоке.", "price": 120, "brand": "Global Notes", "sku": "GN-76-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=400"},

        # Школьные товары
        {"name": "Пенал школьный", "description": "Пенал на молнии, два отделения, прочный текстиль.", "price": 340, "brand": "Brauberg", "sku": "BRG-PEN-01", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1546548970-71785318a17b?w=400"},
        {"name": "Рюкзак школьный", "description": "Ортопедическая спинка, светоотражатели, два больших отделения.", "price": 2490, "brand": "Brauberg", "sku": "BRG-BAG-22", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
        {"name": "Дневник школьный", "description": "Дневник в твёрдой обложке, 48 листов, справочный материал.", "price": 180, "brand": "Hatber", "sku": "HAT-DN-48", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400"},
        {"name": "Обложки для тетрадей 20 шт.", "description": "Универсальные плотные обложки ПВХ, набор 20 штук.", "price": 95, "brand": "ErichKrause", "sku": "EK-OBL-20", "unit": "упаковка", "pack_qty": 20, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400"},

        # Офисные принадлежности
        {"name": "Степлер №24/6", "description": "Металлический степлер до 20 листов, скобы 24/6.", "price": 410, "brand": "KW-trio", "sku": "KW-24-6", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1612599316791-451087c7ff00?w=400"},
        {"name": "Папка-регистратор 75 мм", "description": "Архивная папка с арочным механизмом, ламинированный картон.", "price": 320, "brand": "Brauberg", "sku": "BRG-REG-75", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1568667256549-094345857637?w=400"},
        {"name": "Скрепки канцелярские 28 мм", "description": "Металлические скрепки, никелированные, 100 шт. в упаковке.", "price": 55, "brand": "ErichKrause", "sku": "EK-SKR-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1456735190827-d1262f71b8a3?w=400"},
        {"name": "Лоток для бумаг горизонтальный", "description": "Пластиковый лоток-сетка для документов, штабелируемый.", "price": 260, "brand": "Brauberg", "sku": "BRG-LOT-H", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400"},
        {"name": "Файлы-вкладыши А4 100 шт.", "description": "Перфорированные прозрачные файлы, плотность 35 мкм.", "price": 240, "brand": "ErichKrause", "sku": "EK-FL-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1583521214690-73421a1829a9?w=400"},

        # Рисование и творчество
        {"name": "Краски акварельные 24 цв.", "description": "Медовая акварель 24 цвета с кистью, яркие пигменты.", "price": 210, "brand": "Гамма", "sku": "GAM-AQ-24", "unit": "шт", "pack_qty": 1, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400"},
        {"name": "Пластилин 12 цветов", "description": "Мягкий пластилин, не липнет к рукам, стек в комплекте.", "price": 150, "brand": "Луч", "sku": "LUCH-PL-12", "unit": "упаковка", "pack_qty": 12, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1499744937866-d7e566a20a61?w=400"},
        {"name": "Цветная бумага А4 16 цв.", "description": "Двусторонняя цветная бумага, 16 листов, для аппликаций.", "price": 110, "brand": "Hatber", "sku": "HAT-CB-16", "unit": "упаковка", "pack_qty": 16, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1502691876148-a84978e59af8?w=400"},
        {"name": "Кисти художественные набор 5 шт.", "description": "Синтетические кисти разных размеров для красок.", "price": 175, "brand": "Гамма", "sku": "GAM-KS-5", "unit": "упаковка", "pack_qty": 5, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400"},
    ]

    for product_data in products_data:
        product = Product(stock=100, **product_data)
        db.add(product)

    db.commit()
    print(f"✅ Created {len(products_data)} products")


def seed_database():
    """
    Главная функция для заполнения базы данных.
    Создает таблицы, категории и товары.
    """
    print("🚀 Starting database seeding...")

    # Инициализируем БД (создаем таблицы)
    init_db()
    print("✅ Database tables created")

    # Создаем сессию
    db = SessionLocal()

    try:
        # Проверяем, не заполнена ли уже БД
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            print("⚠️  Database already contains data. Skipping seed.")
            return

        # Создаем категории
        print("📁 Creating categories...")
        categories = create_categories(db)
        print(f"✅ Created {len(categories)} categories")

        # Создаем товары
        print("📦 Creating products...")
        create_products(db, categories)

        print("🎉 Database seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()