import datetime
from typing import NamedTuple, List, Tuple, Any

from db_queries import IncomeExpensesQueries


class Expense(NamedTuple):
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
    amount, subcategorie, categorie = zip(*query)
    return amount, subcategorie, categorie