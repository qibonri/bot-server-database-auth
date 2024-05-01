import os
import logging
import re
import aiogram.utils.markdown as md
from time import sleep
from typing import AnyStr
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from income import add_income
from tables import GraphStatistic
from expenses import add_expense, parse_stats_query
from db_queries import DeleteQueries, StatsQueries
from middelwares import AccessMiddleware
from keyboards import (MainMenu, ExpensesCategories, IncomeCategories, expenses_keyboards_dict, TextStats, TextGraph,
                       GraphStats, DeleteChoices)

BOT_API_TOKEN: AnyStr = os.getenv('7049229917:AAG7o_muXfApHrdiaMwI8-qMCeHHkfooZs')
logging.basicConfig(level=logging.INFO)
bot = Bot(token='7049229917:AAG7o_muXfApHrdiaMwI8-qMCeHHkfooZs')
dp = Dispatcher(bot, storage=MemoryStorage())
#ACCESS_ID: AnyStr = os.getenv('MY_TELEGRAM_ID') # заглушка доступа
#dp.middleware.setup(AccessMiddleware(ACCESS_ID)) # заглушка доступа
MAIN_MENU = MainMenu().create_keyboard()


@dp.message_handler(commands=['start'])
async def main_menu(message: types.Message):
    """Открыть главное меню"""
    await message.reply('Добро пожаловать в телеграмм-бот "Финансовый ассистент" - ваш личный помощник в '
                        'планировании и контроле финансов! Здесь вы сможете создать свой личный финансовый план на '
                        'нужный период, отслеживать доходы, расходы и их соответствие заданному плану, '
                        'а также анализировать рациональность вашего бюджета и финансового плана с помощью '
                        'удобной визуализации. Давайте вместе сделаем управление финансами легким и эффективным! \nВыберите, что вы хотите сделать:', reply_markup=MAIN_MENU)


@dp.message_handler(commands=['Помощь'])
async def help_message(message: types.Message):
    """Показать справочное сообщение"""
    await message.reply(
        'Бот для финансового мониторинга\n\n'
        '- Вы можете добавить расходы по категориям\n'
        '- Добавить и удалить доходы/расходы\n'
        '- Посмотреть статистику за день, неделю, месяц или за все время',
        reply_markup=MAIN_MENU
    )


@dp.message_handler(state='*', commands='stop')
@dp.message_handler(Text(equals='stop', ignore_case=True), state='*')
async def stop_handler(message: types.Message, state: FSMContext):
    """Разрешить пользователю останавливать любые действия"""
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Остановлено:', current_state)
    await state.finish()
    await message.reply('Остановка предыдущего действия.', reply_markup=MAIN_MENU)


class IncomeForm(StatesGroup):
    categorie = State()
    amount = State()


class ExpenseForm(StatesGroup):
    categorie = State()
    subcategorie = State()
    amount = State()


class DeleteForm(StatesGroup):
    table_name = State()
    operation = State()


@dp.message_handler(commands='Доходы')
async def income(message: types.Message):
    """Отобразить меню подкатегорий доходов"""
    await IncomeForm.categorie.set()
    await message.reply(
        'Выберите категорию',
        reply_markup=IncomeCategories().create_keyboard()
    )


@dp.message_handler(state=IncomeForm.categorie)
async def process_income_categorie(message: types.Message, state: FSMContext):
    """Получения дохода по категориям"""
    async with state.proxy() as data:
        data['categorie'] = message.text.split('/')[1]

    await IncomeForm.next()
    await message.reply('Введите сумму дохода')


@dp.message_handler(
    lambda message: not message.text.isdigit(),
    state=IncomeForm.amount
)

async def invalid_income_amount(message: types.Message):
    await message.reply('Сумма должна быть числом\nВведите сумму дохода')


@dp.message_handler(
    lambda message: message.text.isdigit(),
    state=IncomeForm.amount
)
async def process_income_amount(message: types.Message, state: FSMContext):
    """Получить сумму дохода, если сообщение верное (цифра)"""
    async with state.proxy() as data:
        data['amount'] = int(message.text)
        await message.reply(f'Новый доход {message.text}₽ добавлен')
    add_income(
        amount=data['amount'],
        categorie=data['categorie']
    )
    await state.finish()
    await message.reply(
        'Выберите следующую команду',
        reply_markup=MAIN_MENU
    )


@dp.message_handler(commands='Расходы')
async def income(message: types.Message):
    """Отобразить меню категорий расходов"""
    await ExpenseForm.categorie.set()
    await message.reply(
        'Выберите категорию',
        reply_markup=ExpensesCategories().create_keyboard()
    )


@dp.message_handler(state=ExpenseForm.categorie)
async def process_expense_categorie(message: types.Message, state: FSMContext):
    """Расходы по категориям"""
    categorie = message.text.split('/')[1]
    async with state.proxy() as data:
        data['categorie'] = categorie

    await ExpenseForm.next()
    await message.reply(
        'Выберите подкатегорию',
        reply_markup=expenses_keyboards_dict[categorie]
    )


@dp.message_handler(state=ExpenseForm.subcategorie)
async def process_expense_subcategorie(
        message: types.Message, state: FSMContext
):
    subcategorie = message.text.split('/')[1]
    async with state.proxy() as data:
        data['subcategorie'] = subcategorie

    await ExpenseForm.next()
    await message.reply('Введите сумму расхода')


@dp.message_handler(
    lambda message: not message.text.isdigit(),
    state=ExpenseForm.amount
)
async def invalid_expense_amount(message: types.Message):
    await message.reply('Сумма должна быть числом\nВведите сумму расхода')


@dp.message_handler(
    lambda message: message.text.isdigit(),
    state=ExpenseForm.amount
)
async def process_expense_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['amount'] = int(message.text)
        await message.reply(f'Новый расход {message.text}₽ добавлен')
    add_expense(
        category=data['categorie'],
        subcategory=data['subcategorie'],
        amount=data['amount']
    )

    await state.finish()
    await message.reply(
        'Выберите следующую команду',
        reply_markup=MAIN_MENU
    )


@dp.message_handler(commands='Статистика')
async def stats_menu(message: types.Message):
    """Открыть меню статистики"""
    keyboard = TextGraph().create_keyboard()
    await message.reply('Выберите тип статистики', reply_markup=keyboard)


@dp.message_handler(commands=['Текстовая_статистика'])
async def text_stats(message: types.Message):
    """Выбор опции - Текстовая статистика"""
    keyboard = TextStats().create_keyboard()
    await message.reply('Выберите за какое время вывести статистику', reply_markup=keyboard)


@dp.message_handler(
    commands=['Сегодня', 'Неделя', 'Месяц', 'За_всё_время']
)
async def show_text_stats(message: types.Message):
    """Отображение статистики"""
    command = message.text.split('/')[1]
    stats_dict = StatsQueries().get_stats_dict()
    try:
        query_result = stats_dict[command]
        amount, subcategorie, categorie = parse_stats_query(
            query_result
        )
        for i in range(len(amount)):
            await bot.send_message(
                message.chat.id,
                md.text(
                    f'{amount[i]} | {subcategorie[i]} | {categorie[i]}'
                )
            )
    except ValueError:
        await message.answer('Нет расходов за указанный период')
    await message.reply(text='Продолжить', reply_markup=MAIN_MENU)


@dp.message_handler(commands=['График'])
async def graph_stats(message: types.Message):
    """Выбор опции - Графическая статистика"""
    keyboard = GraphStats().create_keyboard()
    await message.reply('Выберите за какое время вывести статистику', reply_markup=keyboard)


@dp.message_handler(
    commands=['Сегодня', 'Неделя', 'Месяц', 'За_всё_время']
)
async def send_graph_stat(message: types.Message):
    """Создание и отправка графика выбранного типа"""
    stat_type = message.text.split('/')[1]
    GraphStatistic().create_plot(query_name=stat_type)
    # need some time to create plot
    await message.answer('Вычисляю...Пожалуйста подождите')
    sleep(5)
    with open('graphs/output.png', 'rb') as f:
        graph = f.read()
    await message.reply('Продолжить', reply_markup=MAIN_MENU)
    await bot.send_photo(chat_id=message.chat.id, photo=graph)


@dp.message_handler(commands=['УдалитьРасходы', 'УдалитьДоходы'])
async def set_delete_state(message: types.Message, state: FSMContext):
    text = message.text.split('/')[1]
    if text == 'УдалитьРасходы':
        table_name = 'expenses'
    elif text == 'УдалитьДоходы':
        table_name = 'income'
    await DeleteForm.table_name.set()
    async with state.proxy() as data:
        data['table_name'] = table_name
    await DeleteForm.next()
    keyboard = DeleteChoices().create_keyboard()
    await message.reply('Выберите', reply_markup=keyboard)



@dp.message_handler(state=DeleteForm.operation)
async def process_delete_operation(message: types.Message, state: FSMContext):
    operation = message.text.split('/')[1]
    async with state.proxy() as data:
        data['operation'] = operation
        delete_func_dict = DeleteQueries(
            data['table_name']
        ).delete_choices_dict()
        result = delete_func_dict[data['operation']]()

    await state.finish()
    await message.reply(result, reply_markup=MAIN_MENU)


@dp.errors_handler()
async def handle_all_errors(update, error):
    chat_id = update.message.chat.id
    await bot.send_message(
        chat_id,
        (
            f'Бот получил неверную команду.\n'
            f'Возникшая ошибка:\n'
            f'>>> {error} <<<\n'
            f'Пользователь должен написать команду "stop", чтобы перезапустить бот'
        ),
    )
    return True


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, timeout=1, relax=0.1)
