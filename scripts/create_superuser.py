import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from getpass import getpass
from src.core.database.infrastructure import db_helper
from src.api.v1.user.service import UserService
from src.api.v1.user.schemas import UserCreate
from src.models.user import Role, WorkSchedule



async def create_superuser() -> None:
    async with db_helper.sessionmaker() as session:  
        print("Создание суперпользователя")
        
        while True:
            password = getpass("Введите пароль (минимум 8 символов): ")
            if len(password) < 8:
                print("Пароль слишком короткий. Пожалуйста, введите минимум 8 символов.")
            else:
                break

        username = input("Введите username суперпользователя: ")
        full_name = "Superuser"
        position = "superuser"
        rank = "superuser"
        role = Role.SUPERUSER
        work_schedule = WorkSchedule.DAILY

        super_user = await UserService(session).create_superuser(
            UserCreate(
                username=username,
                full_name=full_name,
                position=position,
                rank=rank,
                role=role,
                work_schedule=work_schedule,
                password=password,
                is_active=True,
            )
        )
        print(f'Superuser created successfully.\nUsername: {super_user.username}')

if __name__ == '__main__':
    try:
        asyncio.run(create_superuser())
    except KeyboardInterrupt:
        pass