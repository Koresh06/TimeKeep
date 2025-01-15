from fastapi import Request


def get_unread_notifications_count(request: Request) -> int:
    return getattr(request.state, 'notifications_count', 0)
