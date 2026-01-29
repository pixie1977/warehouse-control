

#TODO:: По-хорошему надо тоже вынести в БД, но пока так
_available_tables = [
    {"id": "T1", "capacity": 4},
    {"id": "T2", "capacity": 1},
    {"id": "T3", "capacity": 8},
    {"id": "T4", "capacity": 6},
    {"id": "T5", "capacity": 4},
]

def get_available_tables():
    """
    Простая защита от дурака
    Исходный список не должен меняться
    """
    return _available_tables.copy()