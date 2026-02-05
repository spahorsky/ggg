import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List


# Базовые исключения
class RecipeError(Exception): pass


class RecipeNotFoundError(RecipeError): pass


class ValidationError(RecipeError): pass


class Ingredient:
    def __init__(self, name: str, quantity: float, unit: str):
        self.validate(name, quantity, unit)
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def validate(self, name: str, quantity: float, unit: str):
        if not name:
            raise ValidationError("Ингредиент не содержит название")
        if quantity <= 0:
            raise ValidationError("Количество должно быть положительным")

    @classmethod
    def from_dict(cls, data: dict) -> 'Ingredient':
        return cls(
            data['name'],
            float(data['quantity']),
            data['unit']
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit
        }

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"


class Recipe:
    def __init__(self, recipe_id: int, title: str, category: str,
                 prep_time: int, cook_time: int):
        self.validate(title, category, prep_time, cook_time)

        self.recipe_id = recipe_id
        self.title = title
        self.category = category
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.created_at = datetime.now()
        self.ingredients: List[Ingredient] = []
        self.instructions: List[str] = []

    def validate(self, title: str, category: str, prep_time: int, cook_time: int):
        if not title:
            raise ValidationError("Рецепт не содержит название")
        if prep_time < 0 or cook_time < 0:
            raise ValidationError("Время не может быть отрицательным")

    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients.append(ingredient)

    def add_instruction(self, instruction: str):
        self.instructions.append(instruction)

    @classmethod
    def from_dict(cls, data: dict) -> 'Recipe':
        recipe = cls(
            data['recipe_id'],
            data['title'],
            data['category'],
            data['prep_time'],
            data['cook_time']
        )
        recipe.created_at = datetime.fromisoformat(data['created_at'])

        # Восстанавливаем ингредиенты
        for ing_data in data.get('ingredients', []):
            ingredient = Ingredient.from_dict(ing_data)
            recipe.add_ingredient(ingredient)

        # Восстанавливаем инструкции
        recipe.instructions = data.get('instructions', [])

        return recipe

    def to_dict(self) -> dict:
        return {
            'recipe_id': self.recipe_id,
            'title': self.title,
            'category': self.category,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'created_at': self.created_at.isoformat(),
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'instructions': self.instructions
        }

    def __str__(self):
        total_time = self.prep_time + self.cook_time
        return f"Рецепт({self.recipe_id}): {self.title} ({total_time} мин)"


class RecipeBook:
    def __init__(self):
        self.recipes: dict[int, Recipe] = {}
        self.categories: List[str] = []

    def add_recipe(self, recipe: Recipe):
        self.recipes[recipe.recipe_id] = recipe
        if recipe.category not in self.categories:
            self.categories.append(recipe.category)

    def remove_recipe(self, recipe_id: int):
        if recipe_id not in self.recipes:
            raise RecipeNotFoundError(f"Рецепт с ID {recipe_id} не найден")
        del self.recipes[recipe_id]

    def get_recipe(self, recipe_id: int) -> Recipe:
        if recipe_id not in self.recipes:
            raise RecipeNotFoundError(f"Рецепт с ID {recipe_id} не найден")
        return self.recipes[recipe_id]

    @classmethod
    def from_dict(cls, data: dict) -> 'RecipeBook':
        rb = cls()

        # Восстанавливаем рецепты
        for recipe_data in data.get('recipes', {}).values():
            recipe = Recipe.from_dict(recipe_data)
            rb.add_recipe(recipe)

        # Восстанавливаем категории
        rb.categories = data.get('categories', [])

        return rb

    def to_dict(self) -> dict:
        return {
            'recipes': {rid: recipe.to_dict() for rid, recipe in self.recipes.items()},
            'categories': self.categories
        }

# Сериализация и десериализация
class RecipeSerializer:
    @staticmethod
    def save_to_json(recipe_book: RecipeBook, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recipe_book.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✅ Рецепты сохранены в {filename}")

    @staticmethod
    def load_from_json(filename: str) -> RecipeBook:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Рецепты загружены из {filename}")
        return RecipeBook.from_dict(data)

    @staticmethod
    def save_to_xml(recipe_book: RecipeBook, filename: str):
        root = ET.Element("recipe_book")

        # Категории
        categories_elem = ET.SubElement(root, "categories")
        for category in recipe_book.categories:
            ET.SubElement(categories_elem, "category").text = category

        # Рецепты
        recipes_elem = ET.SubElement(root, "recipes")
        for recipe in recipe_book.recipes.values():
            recipe_elem = ET.SubElement(recipes_elem, "recipe")
            recipe_elem.set("id", str(recipe.recipe_id))

            ET.SubElement(recipe_elem, "title").text = recipe.title
            ET.SubElement(recipe_elem, "category").text = recipe.category
            ET.SubElement(recipe_elem, "prep_time").text = str(recipe.prep_time)
            ET.SubElement(recipe_elem, "cook_time").text = str(recipe.cook_time)
            ET.SubElement(recipe_elem, "created_at").text = recipe.created_at.isoformat()

            # Ингредиенты
            ingredients_elem = ET.SubElement(recipe_elem, "ingredients")
            for ingredient in recipe.ingredients:
                ing_elem = ET.SubElement(ingredients_elem, "ingredient")
                ET.SubElement(ing_elem, "name").text = ingredient.name
                ET.SubElement(ing_elem, "quantity").text = str(ingredient.quantity)
                ET.SubElement(ing_elem, "unit").text = ingredient.unit

            # Инструкции
            instructions_elem = ET.SubElement(recipe_elem, "instructions")
            for instruction in recipe.instructions:
                ET.SubElement(instructions_elem, "step").text = instruction

        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"✅ Рецепты сохранены в {filename}")

    @staticmethod
    def load_from_xml(filename: str) -> RecipeBook:
        tree = ET.parse(filename)
        root = tree.getroot()

        recipe_book = RecipeBook()

        # Загружаем категории
        categories_elem = root.find('categories')
        if categories_elem is not None:
            for category_elem in categories_elem.findall('category'):
                recipe_book.categories.append(category_elem.text)

        # Загружаем рецепты
        recipes_elem = root.find('recipes')
        if recipes_elem is not None:
            for recipe_elem in recipes_elem.findall('recipe'):
                recipe_id = int(recipe_elem.get('id'))

                recipe = Recipe(
                    recipe_id=recipe_id,
                    title=recipe_elem.find('title').text,
                    category=recipe_elem.find('category').text,
                    prep_time=int(recipe_elem.find('prep_time').text),
                    cook_time=int(recipe_elem.find('cook_time').text)
                )

                # Устанавливаем дату создания
                recipe.created_at = datetime.fromisoformat(
                    recipe_elem.find('created_at').text
                )

                # Загружаем ингредиенты
                ingredients_elem = recipe_elem.find('ingredients')
                if ingredients_elem is not None:
                    for ing_elem in ingredients_elem.findall('ingredient'):
                        ingredient = Ingredient(
                            name=ing_elem.find('name').text,
                            quantity=float(ing_elem.find('quantity').text),
                            unit=ing_elem.find('unit').text
                        )
                        recipe.add_ingredient(ingredient)

                # Загружаем инструкции
                instructions_elem = recipe_elem.find('instructions')
                if instructions_elem is not None:
                    for step_elem in instructions_elem.findall('step'):
                        recipe.add_instruction(step_elem.text)

                recipe_book.add_recipe(recipe)

        print(f"✅ Рецепты загружены из {filename}")
        return recipe_book


def main():
    """Демонстрация работы"""
    try:
        print("=== СОЗДАНИЕ КУЛИНАРНОЙ КНИГИ ===")

        # Создаем книгу рецептов
        book = RecipeBook()

        # Создаем первый рецепт
        recipe1 = Recipe(1, "Омлет с сыром", "завтрак", 5, 10)
        recipe1.add_ingredient(Ingredient("Яйца", 3, "шт"))
        recipe1.add_ingredient(Ingredient("Молоко", 50, "мл"))
        recipe1.add_ingredient(Ingredient("Сыр", 50, "г"))
        recipe1.add_instruction("Взбить яйца с молоком")
        recipe1.add_instruction("Вылить на сковороду")
        recipe1.add_instruction("Добавить сыр и жарить 10 минут")

        # Создаем второй рецепт
        recipe2 = Recipe(2, "Салат Цезарь", "обед", 15, 0)
        recipe2.add_ingredient(Ingredient("Куриная грудка", 200, "г"))
        recipe2.add_ingredient(Ingredient("Салат Айсберг", 100, "г"))
        recipe2.add_ingredient(Ingredient("Сухарики", 50, "г"))
        recipe2.add_instruction("Обжарить куриную грудку")
        recipe2.add_instruction("Нарезать салат")
        recipe2.add_instruction("Смешать все ингредиенты")

        # Добавляем рецепты в книгу
        book.add_recipe(recipe1)
        book.add_recipe(recipe2)

        print(f"Создано: {len(book.recipes)} рецепта")
        print(f"Категории: {', '.join(book.categories)}")

        print("\n=== СОХРАНЕНИЕ И ЗАГРУЗКА ===")

        # Сохраняем в JSON
        RecipeSerializer.save_to_json(book, "recipes.json")

        # Сохраняем в XML
        RecipeSerializer.save_to_xml(book, "recipes.xml")

        # Загружаем из XML
        book_loaded = RecipeSerializer.load_from_xml("recipes.xml")

        print(f"Загружено: {len(book_loaded.recipes)} рецептов")

        # Проверяем данные
        loaded_recipe = book_loaded.get_recipe(1)
        print(f"\nПроверка загруженного рецепта:")
        print(f"Название: {loaded_recipe.title}")
        print(f"Ингредиентов: {len(loaded_recipe.ingredients)}")
        print(f"Шагов приготовления: {len(loaded_recipe.instructions)}")

        print("\n✅ Все работает корректно!")

    except ValidationError as e:
        print(f"❌ Ошибка валидации: {e}")
    except RecipeNotFoundError as e:
        print(f"❌ Рецепт не найден: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()