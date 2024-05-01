import datetime
from typing import NamedTuple

from db_queries import IncomeExpensesQueries


class Income(NamedTuple):
    id: int
    amount: int
    time: str
    categorie: str
    description: str

    def __str__(self):
        return (
            f'Добавлено {self.amount}  рублей\n'
            f'Время: {self.time}\n'
            f'В категорию {self.categorie}:'
            f'{self.description}'
        )


def add_income(amount: int, categorie: str):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    description = IncomeExpensesQueries().get_income_description(categorie)
    IncomeExpensesQueries().insert(
        'income', {
            'amount': amount,
            'time': time,
            'categorie': categorie,
            'description': description
        }
    )
    return Income(
        id=None,
        amount=int(amount),
        time=time,
        categorie=categorie,
        description=description
    )