from setuptools import setup

with open('requirements.txt', 'r') as file:
    requirements = [line.strip() for line in file]

setup(
    name='telegram-bot',
    version='1.0',
    description='Telegram-бот "Финансовый ассистент"',
    author='Слемзина Виктория, Чукавина Дарья',
    url='https://github.com/qibonri/bot-server-database-auth, https://github.com/Darya-Ch05/bot-frontend-and-functions',
    install_requires=requirements, #pipreqs
    packages=["db", "graphs"],
    entry_points={
        'console_scripts': [
            'telegram-bot=telegram_bot.main:main',
        ],
    },
)
