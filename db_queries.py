import sqlite3
from typing import Dict, List

import os


class Query:
    def __init__(self):
        self.connection = sqlite3.connect(os.path.join('db', 'finances.db'))
        self.cursor = self.connection.cursor()


class IncomeExpensesQueries(Query):
    def __init__(self):
        super().__init__()

    #  Income, expense queries
    def insert(self, table: str, column_values: Dict):
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ", ".join("?" * len(column_values.keys()))
        self.cursor.executemany(
            f"INSERT INTO {table} "
            f"({columns}) "
            f"VALUES ({placeholders})",
            values)
        self.connection.commit()

    def get_categories(self, table_name: str) -> List[str]:
        self.cursor.execute(
            f'SELECT categorie FROM {table_name}')
        columns = self.cursor.fetchall()
        return [col[0] for col in columns]

    def get_subcategories(self, table_name: str, categorie_name) -> List[str]:
        self.cursor.execute(
            f'SELECT subcategorie '
            f'FROM {table_name} '
            f'WHERE categorie="{categorie_name}" '
        )
        columns = self.cursor.fetchall()
        return [col[0] for col in columns]

    def get_expenses_description(self, subcategorie_name: str) -> str:
        self.cursor.execute(
            f'SELECT description '
            f'FROM expenses_subcategories '
            f'WHERE subcategorie="{subcategorie_name}" '
        )
        return self.cursor.fetchall()[0][0]

    def get_income_description(self, categorie_name: str) -> str:
        self.cursor.execute(
            f'SELECT description '
            f'FROM income_categories '
            f'WHERE categorie="{categorie_name}"'
        )
        return self.cursor.fetchall()[0][0]


class StatsQueries(Query):
    def __init__(self):
        super().__init__()

    #  Stats queries
    def get_today_stats(self, action: str):
        query = (
            f'SELECT SUM(amount) as summary, subcategorie, categorie '
            f'FROM expenses '
            f'WHERE date(time)=CURRENT_DATE '
            f'GROUP BY subcategorie '
            f'ORDER BY summary DESC;'
        )
        if action == 'handler':
            self.cursor.execute(query)
            return self.cursor.fetchall()
        elif action == 'pandas':
            return query

    def get_weekly_stats(self, action: str):
        query = (
            f'SELECT SUM(amount) as summary, subcategorie, categorie '
            f'FROM expenses '
            f'WHERE date(current_timestamp)>=DATE("now", "weekday 0", "-7 days") '
            f'GROUP BY subcategorie '
            f'ORDER BY summary DESC '
            f'LIMIT 10;'
        )
        if action == 'handler':
            self.cursor.execute(query)
            return self.cursor.fetchall()
        elif action == 'pandas':
            return query

    def get_monthly_stats(self, action: str):
        query = (
            f'SELECT SUM(amount) as summary, subcategorie, categorie '
            f'FROM expenses '
            f'WHERE DATE(time, "start of month")=DATE("now", "start of month") '
            f'GROUP BY subcategorie '
            f'ORDER BY summary DESC '
            f'LIMIT 10'
        )
        if action == 'handler':
            self.cursor.execute(query)
            return self.cursor.fetchall()
        elif action == 'pandas':
            return query

    def get_top_ten_stats(self, action: str):
        query = (
            f'SELECT SUM(amount) as summary, subcategorie, categorie '
            f'FROM expenses '
            f'GROUP BY subcategorie '
            f'ORDER BY summary DESC '
            f'LIMIT 10;'
        )
        if action == 'handler':
            self.cursor.execute(query)
            return self.cursor.fetchall()
        elif action == 'pandas':
            return query

    def get_stats_dict(self):
        stats_dict = {
            'Сегодня': self.get_today_stats('handler'),
            'Неделя': self.get_weekly_stats('handler'),
            'Месяц': self.get_monthly_stats('handler'),
            'За_всё_время': self.get_top_ten_stats('handler')
        }
        return stats_dict


class DeleteQueries(Query):
    def __init__(self, table_name):
        self.table_name = table_name
        super().__init__()

    def show_last_five_transactions(self):
        query = (
            f'SELECT subcategorie, categorie, amount '
            f'FROM {self.table_name} '
            f'ORDER BY time DESC '
            f'LIMIT 5;'
        )

        # Проверка существования subcategorie
        try:
            self.cursor.execute(query)
        except sqlite3.OperationalError as e:
            if "no such column: subcategorie" in str(e):
                query = (
                    f'SELECT categorie, amount '
                    f'FROM {self.table_name} '
                    f'ORDER BY time DESC '
                    f'LIMIT 5;'
                )
                self.cursor.execute(query)

        return self.cursor.fetchall()

    def delete_last_transaction(self) -> str:
        query = (
            f'DELETE FROM {self.table_name} '
            f'WHERE id=(SELECT MAX(id) FROM {self.table_name})'
        )
        self.cursor.execute(query)
        self.connection.commit()
        return f'Последняя транзакция удалена'

    def delete_last_five_transactions(self) -> str:
        query = (
            f'DELETE FROM {self.table_name} '
            f'WHERE id IN '
            f'(SELECT id FROM {self.table_name} ORDER BY time DESC LIMIT 5);'
        )
        self.cursor.execute(query)
        self.connection.commit()
        return f'Последние пять транзакций удалены'

    def delete_current_month_transactions(self) -> str:
        query = (
            f'DELETE FROM {self.table_name} '
            f'WHERE DATE(time, "start of month")='
            f'DATE("now", "start of month") '
        )
        self.cursor.execute(query)
        self.connection.commit()
        return f'Удалены транзакции за текущий месяц'

    def delete_choices_dict(self):
        choices_dict = {
            'Удалить_последнее': self.delete_last_transaction,
            'Удалить_последние_пять': self.delete_last_five_transactions,
            'Удалить_за_текущий месяц': self.delete_current_month_transactions,
            'Показать_последние_пять': self.show_last_five_transactions
        }
        return choices_dict


class InitDB(Query):
    def __init__(self):
        super().__init__()

    def _init_db(self):
        """Инициализирует БД"""
        with open("db/createdb.sql", "r") as f:
            sql = f.read()
        self.cursor.executescript(sql)
        self.connection.commit()

    def check_db_exists(self):
        """Проверяет, инициализирована ли БД, если нет — инициализирует"""
        self.cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='expenses'"
        )
        table_exists = self.cursor.fetchall()
        if not table_exists:
            self._init_db()


InitDB().check_db_exists()