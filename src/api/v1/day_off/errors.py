from fastapi import HTTPException, status


class DayOffNotFoundError(Exception):
    pass

class DepartmentPermissionError(HTTPException):
    def __init__(self, detail: str = "You can only perform this action for users in your department."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class InsufficientOvertimeHours(HTTPException):
    def __init__(self):
        self.detail = f"Недостаточно часов для отгула!"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=self.detail)
