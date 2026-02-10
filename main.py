import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Optional
from datetime import datetime
class RecipeNotFoundError(Exception):
    def __init__(self, recipe_name: str):
        self.recipe_name = recipe_name
        super().__init__(f"Рецепт '{recipe_name}' не найден")
class IngredientNotFoundError(Exception):
    def __init__(self, ingredient_name: str):
        self.ingredient_name = ingredient_name
        super().__init__(f"Ингредиент '{ingredient_name}' не найден")
class InvalidRecipeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Некорректный рецепт: {message}")
class FileFormatError(Exception):
    def __init__(self, format: str, filename: str):
        self.format = format
        self.filename = filename
        super().__init__(f"Формат '{format}' не поддерживается для файла '{filename}'")
class Ingredient:
    VALID_UNITS = ['g', 'kg', 'ml', 'l', 'tsp', 'tbsp', 'cup', 'item']
    def __init__(self, name: str, quantity: float, unit: str, notes: str = ""):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.notes = notes
        self._validate()
    def _validate(self):
        if not self.name.strip():
            raise ValueError("Название ингредиента не может быть пустым")
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным числом")
        if self.unit not in self.VALID_UNITS:
            raise ValueError(f"Недопустимая единица измерения. Допустимые: {', '.join(self.VALID_UNITS)}")

    def convert_to(self, new_unit: str) -> bool:
        if new_unit not in self.VALID_UNITS:
            return False
        conversions = {
            ('g', 'kg'): lambda x: x / 1000,
            ('kg', 'g'): lambda x: x * 1000,
            ('ml', 'l'): lambda x: x / 1000,
            ('l', 'ml'): lambda x: x * 1000,
            ('tsp', 'tbsp'): lambda x: x / 3,
            ('tbsp', 'tsp'): lambda x: x * 3,
        }
        key = (self.unit, new_unit)
        if key in conversions:
            self.quantity = conversions[key](self.quantity)
            self.unit = new_unit
            return True
        return False
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes
        }
    @classmethod
    def from_dict(cls, data: Dict) -> 'Ingredient':
        return cls(
            name=data['name'],
            quantity=data['quantity'],
            unit=data['unit'],
            notes=data.get('notes', '')
        )
    def __str__(self) -> str:
        return f"{self.quantity} {self.unit} {self.name}" + (f" ({self.notes})" if self.notes else "")
class Recipe:
    VALID_DIFFICULTIES = ['Easy', 'Medium', 'Hard']
    def __init__(self, name: str, description: str = "", category: str = ""):
        self.name = name
        self.description = description
        self.prep_time = 0  # время подготовки в минутах
        self.cook_time = 0  # время готовки в минутах
        self.difficulty = 'Medium'
        self.servings = 1
        self.category = category
        self.ingredients: List[Ingredient] = []
        self.instructions: List[str] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients.append(ingredient)
        self.updated_at = datetime.now().isoformat()
    def remove_ingredient(self, name: str):
        for i, ingredient in enumerate(self.ingredients):
            if ingredient.name.lower() == name.lower():
                del self.ingredients[i]
                self.updated_at = datetime.now().isoformat()
                return
        raise IngredientNotFoundError(name)
    def add_instruction(self, instruction: str, step: Optional[int] = None):
        if step is None:
            self.instructions.append(instruction)
        else:
            self.instructions.insert(max(0, step - 1), instruction)
        self.updated_at = datetime.now().isoformat()
    def calculate_total_time(self) -> int:
        return self.prep_time + self.cook_time
    def validate(self) -> bool:
        if not self.name.strip():
            raise InvalidRecipeError("Название рецепта не может быть пустым")
        if self.prep_time < 0 or self.cook_time < 0:
            raise InvalidRecipeError("Время не может быть отрицательным")
        if self.difficulty not in self.VALID_DIFFICULTIES:
            raise InvalidRecipeError(f"Сложность должна быть одна из: {', '.join(self.VALID_DIFFICULTIES)}")
        if not self.ingredients:
            raise InvalidRecipeError("Рецепт должен содержать хотя бы один ингредиент")
        if not self.instructions:
            raise InvalidRecipeError("Рецепт должен содержать инструкции по приготовлению")
        return True
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'difficulty': self.difficulty,
            'servings': self.servings,
            'category': self.category,
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'instructions': self.instructions,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'total_time': self.calculate_total_time()
        }
    @classmethod
    def from_dict(cls, data: Dict) -> 'Recipe':
        recipe = cls(
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', '')
        )
        recipe.prep_time = data.get('prep_time', 0)
        recipe.cook_time = data.get('cook_time', 0)
        recipe.difficulty = data.get('difficulty', 'Medium')
        recipe.servings = data.get('servings', 1)
        recipe.instructions = data.get('instructions', [])
        recipe.created_at = data.get('created_at', datetime.now().isoformat())
        recipe.updated_at = data.get('updated_at', datetime.now().isoformat())
        ingredients_data = data.get('ingredients', [])
        for ing_data in ingredients_data:
            recipe.add_ingredient(Ingredient.from_dict(ing_data))
        return recipe
    def __str__(self) -> str:
        ingredients_list = "\n".join([f"  - {ing}" for ing in self.ingredients])
        instructions_list = "\n".join([f"  {i + 1}. {step}" for i, step in enumerate(self.instructions)])
        return f"""
{'=' * 60}
{self.name.upper()}
{'=' * 60}
Категория: {self.category}
Сложность: {self.difficulty}
Время: Подготовка {self.prep_time} мин, Готовка {self.cook_time} мин
Порций: {self.servings}
ОПИСАНИЕ:
{self.description}
ИНГРЕДИЕНТЫ:
{ingredients_list}
ИНСТРУКЦИЯ:
{instructions_list}
"""
class Cookbook:
    def __init__(self, name: str = "Моя кулинарная книга"):
        self.name = name
        self.recipes: List[Recipe] = []
    def add_recipe(self, recipe: Recipe):
        try:
            recipe.validate()
            self.recipes.append(recipe)
            print(f"Рецепт '{recipe.name}' успешно добавлен!")
        except (InvalidRecipeError, ValueError) as e:
            print(f"Ошибка при добавлении рецепта: {e}")
    def remove_recipe(self, recipe_name: str):
        for i, recipe in enumerate(self.recipes):
            if recipe.name.lower() == recipe_name.lower():
                del self.recipes[i]
                print(f"Рецепт '{recipe_name}' удален.")
                return
        raise RecipeNotFoundError(recipe_name)
    def find_recipe_by_name(self, name: str) -> Recipe:
        for recipe in self.recipes:
            if recipe.name.lower() == name.lower():
                return recipe
        raise RecipeNotFoundError(name)
    def find_recipes_by_ingredient(self, ingredient_name: str) -> List[Recipe]:
        result = []
        ingredient_name_lower = ingredient_name.lower()
        for recipe in self.recipes:
            for ingredient in recipe.ingredients:
                if ingredient_name_lower in ingredient.name.lower():
                    result.append(recipe)
                    break
        return result
    def find_recipes_by_category(self, category: str) -> List[Recipe]:
        category_lower = category.lower()
        return [r for r in self.recipes if category_lower in r.category.lower()]
    def get_statistics(self) -> Dict:
        if not self.recipes:
            return {}
        total_recipes = len(self.recipes)
        total_ingredients = sum(len(r.ingredients) for r in self.recipes)
        avg_ingredients = total_ingredients / total_recipes
        categories = {}
        for recipe in self.recipes:
            categories[recipe.category] = categories.get(recipe.category, 0) + 1
        return {
            'total_recipes': total_recipes,
            'total_ingredients': total_ingredients,
            'avg_ingredients_per_recipe': round(avg_ingredients, 2),
            'categories': categories
        }
    def save_to_file(self, filename: str, format: str = 'json'):
        try:
            if format.lower() == 'json':
                self._save_to_json(filename)
            elif format.lower() == 'xml':
                self._save_to_xml(filename)
            else:
                raise FileFormatError(format, filename)

            print(f"Кулинарная книга сохранена в файл: {filename}")

        except (IOError, PermissionError) as e:
            print(f"Ошибка при записи файла: {e}")
        except FileFormatError as e:
            print(f"Ошибка формата: {e}")

    def _save_to_json(self, filename: str):
        data = {
            'cookbook_name': self.name,
            'recipes': [recipe.to_dict() for recipe in self.recipes],
            'statistics': self.get_statistics(),
            'export_date': datetime.now().isoformat()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    def _save_to_xml(self, filename: str):
        root = ET.Element('cookbook')
        ET.SubElement(root, 'name').text = self.name
        ET.SubElement(root, 'export_date').text = datetime.now().isoformat()
        recipes_elem = ET.SubElement(root, 'recipes')
        for recipe in self.recipes:
            recipe_elem = ET.SubElement(recipes_elem, 'recipe')
            ET.SubElement(recipe_elem, 'name').text = recipe.name
            ET.SubElement(recipe_elem, 'description').text = recipe.description
            ET.SubElement(recipe_elem, 'category').text = recipe.category
            ET.SubElement(recipe_elem, 'prep_time').text = str(recipe.prep_time)
            ET.SubElement(recipe_elem, 'cook_time').text = str(recipe.cook_time)
            ET.SubElement(recipe_elem, 'difficulty').text = recipe.difficulty
            ET.SubElement(recipe_elem, 'servings').text = str(recipe.servings)
            ingredients_elem = ET.SubElement(recipe_elem, 'ingredients')
            for ingredient in recipe.ingredients:
                ing_elem = ET.SubElement(ingredients_elem, 'ingredient')
                ET.SubElement(ing_elem, 'name').text = ingredient.name
                ET.SubElement(ing_elem, 'quantity').text = str(ingredient.quantity)
                ET.SubElement(ing_elem, 'unit').text = ingredient.unit
                if ingredient.notes:
                    ET.SubElement(ing_elem, 'notes').text = ingredient.notes
            instructions_elem = ET.SubElement(recipe_elem, 'instructions')
            for i, instruction in enumerate(recipe.instructions, 1):
                ET.SubElement(instructions_elem, 'step', number=str(i)).text = instruction
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
    def load_from_file(self, filename: str, format: str = 'json'):
        try:
            if format.lower() == 'json':
                self._load_from_json(filename)
            elif format.lower() == 'xml':
                self._load_from_xml(filename)
            else:
                raise FileFormatError(format, filename)
            print(f"Кулинарная книга загружена из файла: {filename}")
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден.")
        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении JSON файла: {e}")
        except (ET.ParseError, KeyError) as e:
            print(f"Ошибка при чтении XML файла: {e}")
        except FileFormatError as e:
            print(f"Ошибка формата: {e}")
    def _load_from_json(self, filename: str):
        """Загружает из JSON формата"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.name = data.get('cookbook_name', self.name)
        self.recipes = []
        recipes_data = data.get('recipes', [])
        for recipe_data in recipes_data:
            try:
                recipe = Recipe.from_dict(recipe_data)
                self.recipes.append(recipe)
            except (KeyError, ValueError) as e:
                print(f"Ошибка при загрузке рецепта: {e}")
    def _load_from_xml(self, filename: str):
        tree = ET.parse(filename)
        root = tree.getroot()
        self.name = root.find('name').text if root.find('name') is not None else self.name
        self.recipes = []
        recipes_elem = root.find('recipes')
        if recipes_elem is not None:
            for recipe_elem in recipes_elem.findall('recipe'):
                try:
                    name = recipe_elem.find('name').text
                    description = recipe_elem.find('description').text if recipe_elem.find(
                        'description') is not None else ""
                    category = recipe_elem.find('category').text if recipe_elem.find('category') is not None else ""
                    recipe = Recipe(name, description, category)
                    prep_time = recipe_elem.find('prep_time')
                    if prep_time is not None and prep_time.text:
                        recipe.prep_time = int(prep_time.text)
                    cook_time = recipe_elem.find('cook_time')
                    if cook_time is not None and cook_time.text:
                        recipe.cook_time = int(cook_time.text)
                    difficulty = recipe_elem.find('difficulty')
                    if difficulty is not None and difficulty.text:
                        recipe.difficulty = difficulty.text
                    servings = recipe_elem.find('servings')
                    if servings is not None and servings.text:
                        recipe.servings = int(servings.text)
                    ingredients_elem = recipe_elem.find('ingredients')
                    if ingredients_elem is not None:
                        for ing_elem in ingredients_elem.findall('ingredient'):
                            ing_name = ing_elem.find('name').text
                            ing_quantity = float(ing_elem.find('quantity').text)
                            ing_unit = ing_elem.find('unit').text
                            ing_notes = ing_elem.find('notes').text if ing_elem.find('notes') is not None else ""
                            ingredient = Ingredient(ing_name, ing_quantity, ing_unit, ing_notes)
                            recipe.add_ingredient(ingredient)
                    instructions_elem = recipe_elem.find('instructions')
                    if instructions_elem is not None:
                        for step_elem in instructions_elem.findall('step'):
                            recipe.add_instruction(step_elem.text)
                    self.recipes.append(recipe)
                except (AttributeError, ValueError) as e:
                    print(f"Ошибка при загрузке рецепта из XML: {e}")
    def __str__(self) -> str:
        recipes_list = "\n".join([f"  - {recipe.name} ({recipe.category})" for recipe in self.recipes])
        stats = self.get_statistics()
        stats_text = ""
        if stats:
            stats_text = f"""
СТАТИСТИКА:
  Всего рецептов: {stats['total_recipes']}
  Всего ингредиентов: {stats['total_ingredients']}
  Среднее ингредиентов на рецепт: {stats['avg_ingredients_per_recipe']}
  Категории: {', '.join([f'{k} ({v})' for k, v in stats['categories'].items()])}
"""

        return f"""
╔══════════════════════════════════════════════════════╗
║                  {self.name.upper():^40}           ║
╚══════════════════════════════════════════════════════╝

СОДЕРЖАНИЕ:
{recipes_list if recipes_list else "  (пусто)"}
{stats_text}
"""

def main():
    print("=" * 60)
    print("СИСТЕМА УПРАВЛЕНИЯ КУЛИНАРНЫМИ РЕЦЕПТАМИ")
    print("=" * 60)
    my_cookbook = Cookbook("Семейные рецепты")
    spaghetti_carbonara = Recipe(
        name="Спагетти Карбонара",
        description="Классическое итальянское блюдо с беконом и сыром",
        category="Паста"
    )
    spaghetti_carbonara.prep_time = 15
    spaghetti_carbonara.cook_time = 20
    spaghetti_carbonara.difficulty = "Medium"
    spaghetti_carbonara.servings = 4
    try:
        spaghetti_carbonara.add_ingredient(Ingredient("Спагетти", 400, "g"))
        spaghetti_carbonara.add_ingredient(Ingredient("Бекон", 200, "g", "нарезанный кубиками"))
        spaghetti_carbonara.add_ingredient(Ingredient("Яйца", 3, "item"))
        spaghetti_carbonara.add_ingredient(Ingredient("Пармезан", 100, "g", "тертый"))
        spaghetti_carbonara.add_ingredient(Ingredient("Черный перец", 1, "tsp", "молотый"))
        spaghetti_carbonara.add_ingredient(Ingredient("Соль", 1, "tsp"))
    except ValueError as e:
        print(f"Ошибка при добавлении ингредиента: {e}")
    spaghetti_carbonara.add_instruction("Сварите спагетти в подсоленной воде до состояния аль денте.")
    spaghetti_carbonara.add_instruction("Обжарьте бекон до хрустящей корочки.")
    spaghetti_carbonara.add_instruction("Взбейте яйца с тертым пармезаном и черным перцем.")
    spaghetti_carbonara.add_instruction("Смешайте горячие спагетти с беконом, затем добавьте яичную смесь.")
    spaghetti_carbonara.add_instruction("Быстро перемешайте до образования кремообразного соуса.")
    my_cookbook.add_recipe(spaghetti_carbonara)
    salad = Recipe(
        name="Греческий салат",
        description="Освежающий овощной салат с фетой",
        category="Салаты"
    )
    salad.prep_time = 20
    salad.cook_time = 0
    salad.difficulty = "Easy"
    salad.servings = 2
    try:
        salad.add_ingredient(Ingredient("Помидоры", 3, "item", "нарезанные дольками"))
        salad.add_ingredient(Ingredient("Огурцы", 2, "item", "нарезанные кубиками"))
        salad.add_ingredient(Ingredient("Красный лук", 0.5, "item", "тонко нарезанный"))
        salad.add_ingredient(Ingredient("Фета", 150, "g", "кубиками"))
        salad.add_ingredient(Ingredient("Оливки", 100, "g", "без косточек"))
        salad.add_ingredient(Ingredient("Оливковое масло", 3, "tbsp"))
    except ValueError as e:
        print(f"Ошибка при добавлении ингредиента: {e}")
    salad.add_instruction("Нарежьте все овощи и сложите в большую миску.")
    salad.add_instruction("Добавьте кубики феты и оливки.")
    salad.add_instruction("Полейте оливковым маслом и аккуратно перемешайте.")
    salad.add_instruction("Подавайте сразу или охладите 30 минут перед подачей.")
    my_cookbook.add_recipe(salad)
    print(my_cookbook)
    print("\nПоиск рецептов, содержащих 'бекон':")
    try:
        bacon_recipes = my_cookbook.find_recipes_by_ingredient("бекон")
        for recipe in bacon_recipes:
            print(f"  - {recipe.name}")
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
    print("\nИнформация о рецепте 'Спагетти Карбонара':")
    try:
        recipe = my_cookbook.find_recipe_by_name("Спагетти Карбонара")
        print(recipe)
    except RecipeNotFoundError as e:
        print(f"Ошибка: {e}")
    print("\nСохранение кулинарной книги...")
    my_cookbook.save_to_file("cookbook.json", "json")
    my_cookbook.save_to_file("cookbook.xml", "xml")
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ОБРАБОТКИ ИСКЛЮЧЕНИЙ")
    print("=" * 60)
    try:
        missing_recipe = my_cookbook.find_recipe_by_name("Несуществующий рецепт")
    except RecipeNotFoundError as e:
        print(f"✓ Корректно обработано исключение: {e}")
    try:
        invalid_ingredient = Ingredient("", -5, "invalid_unit")
    except ValueError as e:
        print(f"✓ Корректно обработано исключение: {e}")
    print("\nПопытка загрузки несуществующего файла:")
    my_cookbook.load_from_file("nonexistent.json", "json")
    print("\n" + "=" * 60)
    print("СОЗДАНИЕ НОВОЙ КНИГИ И ЗАГРУЗКА ИЗ ФАЙЛА")
    print("=" * 60)
    new_cookbook = Cookbook("Загруженная кулинарная книга")
    new_cookbook.load_from_file("cookbook.json", "json")
    print(new_cookbook)
if __name__ == "__main__":
    main()