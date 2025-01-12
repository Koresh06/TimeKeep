from fastapi_admin.resources import Model

from models import User

class UserResource(Model):
    label = "Users"
    model = User
    fields = ["username", "full_name", "role", "is_active", "create_at"]  # Поля для отображения
