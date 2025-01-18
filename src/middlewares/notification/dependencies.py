from fastapi import Request


def get_unread_notifications_count_user(request: Request) -> int:
    return getattr(request.state, 'notifications_count_user', 0)
