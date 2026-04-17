"""
Базовый класс для парсеров травм с разных источников.
Обеспечивает общий интерфейс и вспомогательные методы.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class BaseInjuryParser(ABC):
    """
    Абстрактный базовый класс для всех парсеров травм.
    Каждый конкретный парсер должен наследовать этот класс
    и реализовать метод `parse_injuries()`.
    """

    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url

    @abstractmethod
    def parse_injuries(self, html: str) -> List[Dict]:
        """
        Парсит HTML-страницу и возвращает список травм.
        Каждая травма — словарь с полями:
        - player_name: str
        - team_name: str
        - position: str (вратарь, защитник, полузащитник, нападающий)
        - injury_type: str
        - return_date: str (YYYY-MM-DD or None)
        - importance: int (1-3, где 3 = высокая важность)
        - source: str (название источника)
        """
        pass

    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних пробелов и переносов строк."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())

    def extract_position_from_text(self, text: str) -> Optional[str]:
        """
        Пытается извлечь позицию из текста.
        Поддерживает русские и английские варианты.
        """
        text_lower = text.lower()
        position_map = {
            'вратарь': 'вратарь',
            'goalkeeper': 'вратарь',
            'защитник': 'защитник',
            'defender': 'защитник',
            'center back': 'защитник',
            'central defender': 'защитник',
            'полузащитник': 'полузащитник',
            'midfielder': 'полузащитник',
            'нападающий': 'нападающий',
            'forward': 'нападающий',
            'striker': 'нападающий',
            'wing': 'нападающий'
        }
        for ru_key, en_key in position_map.items():
            if ru_key in text_lower or en_key in text_lower:
                return position_map[ru_key]
        return None

    def estimate_importance(self, position: str, player_name: str = "") -> int:
        """
        Оценивает важность травмированного игрока (1-3).
        Высокая важность: вратарь, ключевые защитники, звезды.
        """
        if not position:
            return 1
        position_lower = position.lower().strip()

        # Высокая важность
        high_importance_positions = {
            'вратарь',
            'goalkeeper',
            'защитник',
            'defender',
            'center back',
            'central defender',
            'либеро'
        }
        if any(pos in position_lower for pos in high_importance_positions):
            return 3

        # Средняя важность
        medium_importance_positions = {
            'полузащитник',
            'midfielder',
            'нападающий',
            'forward',
            'striker'
        }
        if any(pos in position_lower for pos in medium_importance_positions):
            return 2

        # Низкая важность по умолчанию
        return 1

    def parse_return_date(self, text: str) -> Optional[str]:
        """
        Пытается извлечь дату возврата из текста.
        Поддерживает форматы: 'out until April 10', 'expected back 2026-04-05', etc.
        Возвращает строку в формате YYYY-MM-DD или None.
        """
        if not text:
            return None
        text_lower = text.lower()
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }

        # Ищем паттерн вроде "until April 10" или "expected back 2026-04-05"
        out_until_pattern = r'out until\s+([a-zA-Z]+)\s+(\d{1,2})'
        expected_back_pattern = r'expected back\s+(\d{4})-(\d{2})-(\d{2})'
        date_only_pattern = r'(\d{4})-(\d{2})-(\d{2})'

        # Проверяем формат YYYY-MM-DD
        date_match = re.search(date_only_pattern, text)
        if date_match:
            y, m, d = date_match.groups()
            return f"{y}-{m}-{d.zfill(2)}"

        # Проверяем "expected back YYYY-MM-DD"
        exp_match = re.search(expected_back_pattern, text, re.IGNORECASE)
        if exp_match:
            y, m, d = exp_match.groups()
            return f"{y}-{m}-{d}"

        # Проверяем "out until Month DD"
        out_match = re.search(out_until_pattern, text, re.IGNORECASE)
        if out_match:
            month_name, day = out_match.groups()
            month = months.get(month_name.lower())
            if month:
                # Предполагаем текущий год — можно улучшить, учитывая сезон
                year = datetime.now().year
                return f"{year}-{month}-{day.zfill(2)}"

        return None