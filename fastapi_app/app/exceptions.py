
class NutritionAPIException(Exception):
    """Base exception for the application."""
    status_code: int = 500
    detail: str = "An internal error occurred."

    def __init__(self, detail: str = None, status_code: int = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code

class EntityNotFoundException(NutritionAPIException):
    """Exception raised when an entity is not found."""
    status_code = 404
    detail = "Entity not found."

class RecipeNotFoundException(EntityNotFoundException):
    """Exception raised when a recipe is not found."""
    detail = "Recipe not found."

class BadRequestException(NutritionAPIException):
    """Exception raised for bad requests."""
    status_code = 400
    detail = "Bad request."

class DatabaseException(NutritionAPIException):
    """Exception raised for database errors."""
    status_code = 500
    detail = "Database error."
