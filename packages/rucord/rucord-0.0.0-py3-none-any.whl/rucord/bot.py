import asyncio

from command import Table_For_Commands
from .interaction import Interaction


class Bot:
    def __init__(self):
        self.commands = Table_For_Commands

    async def process_command(self, name: str, interaction: Interaction):
        """Обрабатывает команду по имени"""
        cmd = self.commands.get(name)
        if not cmd:
            print(f"❌ Команда '{name}' не найдена.")
            return
        await cmd.invoke(interaction)

    def run(self):
        """Имитация запуска — просто ждёт ввод команд"""
        print("🤖 aiocord бот запущен! Введите команду:")

        async def loop():
            while True:
                name = input("> ")
                inter = Interaction(user="Элиас", channel="#general")
                await self.process_command(name, inter)

        asyncio.run(loop())
