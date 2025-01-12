import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import asyncio
from getpass import getpass
from src.core.session import async_session_maker
from src.api.v1.user.service import UserService
from src.api.v1.user.schemas import UserCreate
from src.models.user import Role, WorkSchedule


async def create_superuser() -> None:
    async with async_session_maker() as session:  
        print("Создание суперпользователя")
        
        # Проверка пароля
        while True:
            password = getpass("Введите пароль (минимум 8 символов): ")
            if len(password) < 8:
                print("Пароль слишком короткий. Пожалуйста, введите минимум 8 символов.")
            else:
                break

        username = input("Введите username суперпользователя: ")
        full_name = "Superuser"
        position = "superuser"
        role = Role.SUPERUSER.value
        work_schedule = WorkSchedule.DAILY.value

        # Проверяем, существует ли пользователь
        super_user = await UserService(session).create_superuser(
            UserCreate(
                username=username,
                full_name=full_name,
                position=position,
                role=role,
                work_schedule=work_schedule,
                password=password,
            )
        )
        print(f'Superuser created successfully.\nUsername: {super_user.username}\nPassword: {password}')

if __name__ == '__main__':
    try:
        asyncio.run(create_superuser())
    except KeyboardInterrupt:
        pass