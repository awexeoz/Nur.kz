import asyncio
import logging
import requests
import re
import json
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from config import TOKEN

import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")  # Подключение к MongoDB
db = client["Nurkz"]  # Выбор базы данных
collection = db["users"]  # Выбор коллекции

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_article_id(url):
    match = re.search(r'/(\d+)-', url)
    if match:
        return match.group(1)
    return None

async def add_user(user_id, username):
    user_data = {"user_id": user_id, "username": username, "last_interaction_time": None}
    collection.insert_one(user_data)

async def get_user(user_id):
    query = {"user_id": user_id}
    return collection.find_one(query)

async def update_last_interaction_time(user_id, interaction_time):
    query = {"user_id": user_id}
    new_values = {"$set": {"last_interaction_time": interaction_time}}
    collection.update_one(query, new_values)

async def fetch_news():
    headers = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"
    }

    url = "https://www.nur.kz/latest/"
    r = requests.get(url=url, headers=headers)
    r.encoding = 'utf-8'

    soup = BeautifulSoup(r.text, "lxml")
    articles_cards = soup.find_all("a", class_= "article-preview-category__content")

    new_news_dict = {}

    # Загрузка существующих новостей из файла, если они там есть
    try:
        with open('news_dict.json', 'r', encoding='utf-8') as file:
            existing_news = json.load(file)
    except FileNotFoundError:
        existing_news = {}

    for article in articles_cards:
        article_category = article.find("span", class_="article-preview-category__text").text.strip()
        article_title = article.find("h2", class_="article-preview-category__subhead").text.strip()
        article_url = f'{article.get("href")}'

        article_date_time = article.find("time").get("datetime")

        article_id = get_article_id(article_url)

        # Проверка, есть ли уже такая новость в базе
        if article_id in existing_news:
            continue  # Если такая новость уже есть, пропустить

        # Добавление новой новости в словарь
        new_news_dict[article_id] = {
            "Date" : article_date_time,
            "Category" : article_category,
            "Title" : article_title,
            "Url" : article_url
        }

        # Отправка уведомления о новой новости каждому пользователю
        users = collection.find()  # Получаем список всех пользователей
        for user in users:
            user_id = user["user_id"]
            await bot.send_message(user_id, f"📰 Новая новость!\nКатегория: {article_category}\nЗаголовок: {article_title}\nДата: {article_date_time}\n{article_url}")

    # Добавление новых новостей к существующим и сохранение обновленного списка в файл
    existing_news.update(new_news_dict)
    with open('news_dict.json', 'w', encoding='utf-8') as file:
        json.dump(existing_news, file, indent=4, ensure_ascii=False)


async def fetch_news_periodically(interval_seconds):
    while True:
        await fetch_news()  # Выполнение обновления новостей
        await asyncio.sleep(60)  # Ожидание перед следующим обновлением

async def main():
    # Запуск асинхронной задачи обновления новостей
    news_update_task = asyncio.create_task(fetch_news_periodically(60))  # Обновление каждую минуту
    # Запуск бота
    await dp.start_polling(bot)

def paginate_news(news_list, page_number, items_per_page):
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    return news_list[start_index:end_index], end_index


async def get_news(message: types.Message, page_number: int = 1):
    with open('news_dict.json', 'r', encoding='utf-8') as file:
        news = json.load(file)

    # Получаем отсортированный список ключей (article_id) по дате
    sorted_article_ids = sorted(news.keys(), key=lambda x: news[x]['Date'])

    items_per_page = 1  # Устанавливаем количество новостей на одной странице
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_news = sorted_article_ids[start_index:end_index]

    for article_id in paginated_news:
        article = news[article_id]
        category = article['Category']
        title = article['Title']
        date = article['Date']
        url = article['Url']

        # Преобразование формата даты
        formatted_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M')

        links = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Смотреть на сайте', url=url)]
        ])

        # Формирование сообщения
        news_message = f"📰 {category}\n💡 {title}\n🕒 {formatted_date}"

        await message.answer(news_message, reply_markup=links)

    # Добавляем кнопки пагинации
    total_pages = len(sorted_article_ids) // items_per_page + (1 if len(sorted_article_ids) % items_per_page > 0 else 0)
    pagination_buttons = []
    if page_number > 1:
        pagination_buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f"page_{page_number - 1}"))
    if page_number < total_pages:
        pagination_buttons.append(InlineKeyboardButton(text='➡️', callback_data=f"page_{page_number + 1}"))

    pagination_keyboard = InlineKeyboardMarkup(inline_keyboard=[pagination_buttons])

    await message.answer("Выберите страницу:", reply_markup=pagination_keyboard)





@dp.message(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Я бот новостей. Я могу предоставить тебе последние новости с сайта Nur.kz.Чтобы начать, просто нажми кнопку News в меню ниже.",
                         reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)  # Чтобы дать боту немного времени на удаление клавиатуры
    await message.answer("Выберите пункт меню:", reply_markup=get_main_keyboard())
    await add_user(message.from_user.id, message.from_user.username)

def get_main_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='News')]
    ],
                                     resize_keyboard=True,
                                     input_field_placeholder='Выберите пункт меню')

@dp.message(lambda message: message.text == 'News')
async def cmd_news(message: types.Message):
    # Обновление времени последнего взаимодействия пользователя
    await update_last_interaction_time(message.from_user.id, datetime.datetime.now().isoformat())
    await get_news(message)

@dp.message(lambda message: message.text == 'News')
async def cmd_news(message: types.Message):
    # Обновление времени последнего взаимодействия пользователя
    await update_last_interaction_time(message.from_user.id, datetime.datetime.now().isoformat())
    await get_news(message)


@dp.callback_query(lambda callback_query: callback_query.data.startswith('page_'))
async def process_page_selection(callback_query: types.CallbackQuery):
    page_number = int(callback_query.data.split('_')[1])
    await get_news(callback_query.message, page_number)
    await bot.answer_callback_query(callback_query.id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())