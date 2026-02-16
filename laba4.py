import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from bs4 import BeautifulSoup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser_laba4 import Parser

BOT_TOKEN = "7153114500:AAHi-mmNRffmt74dz6JAvqg31FYUboSJcaQ"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

current_articles = []

def get_topics_keyboard(articles_list, show_more=True):
    """
    articles_list - список, где каждый элемент это [ссылка, автор, название]
    """
    buttons = []

    # Создаем кнопки для каждой статьи
    for i, article in enumerate(articles_list[:10]):  # максимум 10 кнопок
        if len(article) >= 3:  # проверяем, что есть все данные
            link, author, title = article[0], article[1], article[2]

            # Обрезаем длинные названия
            short_title = title[:30] + "..." if len(title) > 30 else title

            # Создаем callback с индексом статьи
            buttons.append([
                InlineKeyboardButton(
                    text=f"📄 {short_title}",
                    callback_data=f"article_{i}"
                )
            ])

    # Кнопка "Найти больше тем" в конце
    if show_more and articles_list:
        buttons.append([
            InlineKeyboardButton(text="🔍 Найти больше тем", callback_data="show_more")
        ])

    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


current_articles = []
category_url = ""


# Обработка нажатия на статью
@dp.callback_query(F.data.startswith("article_"))
async def show_article_details(callback: types.CallbackQuery):
    global current_articles

    try:
        article_index = int(callback.data.split("_")[1])

        # Проверяем, что есть статьи
        if not current_articles or article_index >= len(current_articles):
            await callback.answer("Статья не найдена ❌")
            return

        article = current_articles[article_index]

        if len(article) >= 3:
            link, author, title = article[0], article[1], article[2]

            # Формируем сообщение
            message_text = f"""
📚 *{title}*

👤 *Автор:* {author}
🔗 *Ссылка:* `{link}`

*Что дальше?*
1. Нажми кнопку ниже чтобы перейти к статье
2. Или выбери другую статью
            """

            # Клавиатура с действиями
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Читать статью", url=link)],
                [
                    InlineKeyboardButton(text="📄 Другая статья", callback_data="back_to_list"),
                    InlineKeyboardButton(text="◀️ Назад к поиску", callback_data="back_to_main")
                ]
            ])

            await callback.message.edit_text(
                message_text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

    except Exception as e:
        print(f"Ошибка: {e}")
        await callback.answer("Произошла ошибка ❌")

    await callback.answer()


# Кнопка "Найти больше тем"
@dp.callback_query(F.data == "show_more")
async def show_more_articles(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"🔍 *Найти больше тем можно тут:*\n\n"
        f"{category_url}",
        parse_mode="Markdown",
        reply_markup=get_inline_keyboard()
    )
    await callback.answer()


# Кнопка "Назад к списку"
@dp.callback_query(F.data == "back_to_list")
async def back_to_list(callback: types.CallbackQuery):
    global current_articles

    if current_articles:
        response = f"📚 *Найдено статей:* {len(current_articles)}\n\n"
        response += "*Выберите статью из списка:*"

        await callback.message.edit_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_topics_keyboard(current_articles)
        )
    else:
        await callback.message.edit_text(
            "Список статей пуст. Попробуйте новый поиск.",
            reply_markup=get_inline_keyboard()
        )

    await callback.answer()


# Кнопка "Назад в главное меню"
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await start(callback.message)
    await callback.answer()

# Клавиатура с inline-кнопками
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Выбор темы", callback_data="choose_topic")],
        [InlineKeyboardButton(text="📖 Помощь", callback_data="help")]
    ])
    return keyboard


# Парсер
async def search_cyberleninka(query):
    global category_url
    a = await Parser().parse_tem()
    category_url = [value for key, value in a.items() if query.lower() in key.lower()]
    if not category_url:
        return
    list_site = await Parser().parse_site(category_url[0])
    return list_site


# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🔬 *Поиск научных статей на КиберЛенинке*\n\n"
        "Используй кнопки ниже для поиска:",
        parse_mode="Markdown",
        reply_markup=get_inline_keyboard()
    )


# Обработка кнопки "Выбор темы"
@dp.callback_query(F.data == "choose_topic")
async def choose_topic(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 *Введите тему для поиска:*\n\n"
        "Примеры:\n"
        "• Искусственный интеллект\n"
        "• Машинное обучение\n"
        "• Экономика\n"
        "• Медицина\n"
        "• Физика",
        parse_mode="Markdown"
    )
    await callback.answer()


# Обработка кнопки "Помощь"
@dp.callback_query(F.data == "help")
async def help_command(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📚 *Помощь по использованию бота:*\n\n"
        "1. Нажмите *'🔍 Выбор темы'*\n"
        "2. Введите тему для поиска\n"
        "3. Получите список статей\n\n"
        "Бот ищет статьи на сайте *cyberleninka.ru*\n"
        "Все статьи на русском языке",
        parse_mode="Markdown",
        reply_markup=get_inline_keyboard()
    )
    await callback.answer()


# Обработка поисковых запросов
@dp.message()
async def search(message: types.Message):
    global current_articles
    query = message.text.strip()

    if len(query) < 2:
        await message.answer(
            "Введите минимум 2 символа",
            reply_markup=get_inline_keyboard()
        )
        return

    await message.answer(f"🔍 *Ищу:* {query}...", parse_mode="Markdown")

    current_articles = await search_cyberleninka(query)

    if current_articles:
        await message.answer(
            "✅ *Тема найдена*",
            parse_mode="Markdown",
            reply_markup=get_topics_keyboard(current_articles, show_more=True)
        )
    else:
        await message.answer(
            "❌ *Тема не найдена*\n\n"
            "Попробуйте другой запрос",
            parse_mode="Markdown",
            reply_markup=get_inline_keyboard()
        )


# Запуск
async def main():
    print("🤖 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())