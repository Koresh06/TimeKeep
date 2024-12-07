# from sqlalchemy.ext.asyncio import AsyncSession
# from src.api.v1.user.service import UserService
# from src.api.v1.user.schemas import UserCreate


# async def test_create_superuser(async_db_session: AsyncSession):
#     password = "password123"
#     username = "superuser"
#     full_name = "Super User"
#     position = "superuser"
#     role = "moderator"

#     super_user = await UserService(async_db_session).create_superuser(
#         UserCreate(
#             username=username,
#             full_name=full_name,
#             position=position,
#             role=role,
#             password=password,
#             is_superuser=True,
#         )
#     )

#     assert super_user.username == username
#     assert super_user.full_name == full_name