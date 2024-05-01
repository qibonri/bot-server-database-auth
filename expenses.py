import datetime
from typing import NamedTuple, List, Tuple, Any

from db_queries import IncomeExpensesQueries


class Expense(NamedTuple):
    """Объект, описывающий расход.
        :param id: Уникальный идентификатор расхода.
        :type id: int
        :param category: Категория расхода.
        :type category: str
        :param subcategory: Подкатегория расхода.
        :type subcategory: str
        :param time: Время совершения расхода.
        :type time: str
        :param amount: Сумма расхода.
        :type amount: int
        :param description: Описание расхода.
        :type description: str"""
    id: int
    category: str
    subcategory: str
    time: str
    amount: int
    description: str

    def __str__(self):
        return (
            f'Добавлен расход: {self.amount}\n'
            f'Время: {self.time}\n'
            f'Категория: {self.subcategory}:{self.category}'
            )


def add_expense(
    category: str,
    subcategory: str,
    amount: str,
) -> Expense:
    """Добавление нового расхода в базу данных.
        :param category: Категория расхода.
        :type category: str
        :param subcategory: Подкатегория расхода.
        :type subcategory: str
        :param amount: Сумма расхода.
        :type amount: str
        :returns: Объект расхода.
        :rtype: Expense
        """
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = IncomeExpensesQueries().get_expenses_description(subcategory)
    IncomeExpensesQueries().insert(
        'expenses', {
            'categorie': category,
            'subcategorie': subcategory,
            'time': time,
            'amount': int(amount),
            'description': description
            }
        )
    return Expense(
        id=None,
        category=category,
        subcategory=subcategory,
        time=time,
        amount=int(amount),
        description=description
    )


def parse_stats_query(query: List[Tuple[str]]) -> Tuple[Any, Any, Any]:
    """Парсинг результата запроса, возвращающего статистику расходов.
    :param query: Результат запроса.
    :type query: List[Tuple[str]]
    :returns: Кортеж, содержащий суммы, подкатегории и категории расходов.
    :rtype: Tuple[Any, Any, Any]
    """
    amount, subcategorie, categorie = zip(*query)
    return amount, subcategorie, categorie
