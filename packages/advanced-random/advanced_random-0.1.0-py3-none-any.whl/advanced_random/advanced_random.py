# advanced_random.py
import random
import string
from typing import List, Any, Dict, Union


class AdvancedRandom:
    """
    Улучшенный рандом с дополнительными функциями.
    """

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.seed = seed

    def choice_weighted(self, items: List[Any], weights: List[float]) -> Any:
        """
        Случайный выбор с весами.
        """
        if len(items) != len(weights):
            raise ValueError("Длины items и weights должны совпадать.")
        total = sum(weights)
        rand = random.uniform(0, total)
        current = 0
        for item, weight in zip(items, weights):
            current += weight
            if rand <= current:
                return item
        return items[-1]  # fallback

    def sample_unique(self, population: List[Any], k: int) -> List[Any]:
        """
        Возвращает k уникальных элементов из списка.
        Если k больше длины списка — возвращает перемешанный список.
        """
        if k >= len(population):
            return random.sample(population, len(population))
        return random.sample(population, k)

    def choice_without(self, items: List[Any], exclude: List[Any]) -> Any:
        """
        Случайно выбирает элемент, исключая указанные.
        """
        available = [item for item in items if item not in exclude]
        if not available:
            raise ValueError("Нет доступных элементов после исключения.")
        return random.choice(available)

    def random_string(self, length: int = 8, charset: str = None) -> str:
        """
        Генерирует случайную строку заданной длины.
        charset — набор символов. По умолчанию: буквы + цифры.
        """
        if charset is None:
            charset = string.ascii_letters + string.digits
        return ''.join(random.choice(charset) for _ in range(length))

    def random_password(self, length: int = 12) -> str:
        """
        Генерирует надёжный пароль: минимум одна заглавная, строчная, цифра.
        """
        if length < 4:
            raise ValueError("Длина пароля должна быть не менее 4.")
        
        lower = random.choice(string.ascii_lowercase)
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        others = ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%") 
                         for _ in range(length - 3))
        
        pwd = list(lower + upper + digit + others)
        random.shuffle(pwd)
        return ''.join(pwd)

    def normal_int(self, mu: float = 0, sigma: float = 1, min_val: int = None, max_val: int = None) -> int:
        """
        Целое число из нормального распределения с ограничением.
        """
        value = random.normalvariate(mu, sigma)
        if min_val is not None:
            value = max(value, min_val)
        if max_val is not None:
            value = min(value, max_val)
        return int(value)

    def random_dict_key(self, d: Dict[Any, Any], weight_key: str = None) -> Any:
        """
        Выбор случайного ключа из словаря.
        Если weight_key указана и значения — словари, использует веса.
        Пример: d = {'a': {'weight': 2}, 'b': {'weight': 1}}
        """
        if not d:
            raise ValueError("Словарь пуст.")
        
        if weight_key and all(isinstance(v, dict) for v in d.values()):
            weights = [v.get(weight_key, 1) for v in d.values()]
            return self.choice_weighted(list(d.keys()), weights)
        else:
            return random.choice(list(d.keys()))


# Удобный глобальный экземпляр
adv_random = AdvancedRandom()
