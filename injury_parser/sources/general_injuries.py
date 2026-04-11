"""
Общий парсер для извлечения информации о травмах из новостных статей и клубных сайтов.
Использует комбинацию regex паттернов и NLP подходов для извлечения структурированных данных.
"""

import re
import asyncio
import aiohttp
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

from .base import BaseInjuryParser

logger = logging.getLogger(__name__)

class GeneralInjuriesParser(BaseInjuryParser):
    """
    Общий парсер для извлечения информации о травмах с различных спортивных сайтов.
    Работает с HTML контентом и извлекает структурированные данные о травмах игроков.
    """
    
    def __init__(self, source_name: str, base_url: str, team_mapping: Dict[str, str] = None):
        super().__init__(source_name, base_url)
        self.team_mapping = team_mapping or {}
        
        # Паттерны для извлечения информации о травмах
        self.injury_patterns = [
            # Паттерн 1: "Игрок [Имя] травмирован [тип травмы] и пропустит [период]"
            re.compile(
                r'(\w+(?:\s+\w+)*?)\s+(?:травмирован|получил травму|повредил)\s+'
                r'(.+?)\s+(?:и\s+)?(?:пропустит|будет отсутствовать|выбыл на)\s+'
                r'(.+?)(?:\.|,|\n)',
                re.IGNORECASE
            ),
            
            # Паттерн 2: "[Игрок] out with [травма] for [период]"
            re.compile(
                r'(\w+(?:\s+\w+)*?)\s+out\s+with\s+(.+?)\s+for\s+(.+?)(?:\.|,|\n)',
                re.IGNORECASE
            ),
            
            # Паттерн 3: "[Игрок] сомневается в участии из-за [травма]"
            re.compile(
                r'(\w+(?:\s+\w+)*?)\s+(?:сомневается|не уверен|под вопросом)\s+'
                r'в\s+участии\s+(?:из-?за|из-за)\s+(.+?)(?:\.|,|\n)',
                re.IGNORECASE
            ),
            
            # Паттерн 4: "Клуб подтверждает: [Игрок] получит [травма]"
            re.compile(
                r'(?:Клуб\s+)?(?:подтверждает|сообщает|заявил)\s*:?\s*'
                r'(\w+(?:\s+\w+)*?)\s+(?:получит|травмирован|повредил)\s+(.+?)(?:\.|,|\n)',
                re.IGNORECASE
            ),
            
            # Паттерн 5: "[Игрок] - [травма] - [период отсутствия]"
            re.compile(
                r'(\w+(?:\s+\w+)*?)\s*[-–]\s*(.+?)\s*[-–]\s*(.+?)(?:\.|,|\n|\||)',
                re.IGNORECASE
            )
        ]
        
        # Словарь для нормализации названий травм
        self.injury_normalization = {
            # Коленные травмы
            r'ACR|передняя крестообразная связка|ACL tear': 'ACL tear',
            r'ПКР|задняя крестообразная связка|PCL tear': 'PCL tear', 
            r'Мениск|meniscus tear': 'Meniscus tear',
            r'Связка колена|knee ligament': 'Knee ligament',
            r'Хрящ|cartilage damage': 'Cartilage damage',
            
            # Голеностоп
            r'Голеностоп|ankle sprain|растяжение голеностопа': 'Ankle sprain',
            r'Ахиллес|Achilles tendon': 'Achilles tendon',
            
            # Бедро и пах
            r'Бедро|hamstring|растяжение бедра': 'Hamstring strain',
            r'Четырёхглавая|quadriceps': 'Quadriceps strain',
            r'Пах|groin|аддуктор': 'Groin strain',
            
            # Спина и шея
            r'Спина|back pain|спина': 'Back injury',
            r'Шея|neck|шейный отдел': 'Neck injury',
            
            # Голова и сотрясение
            r'Сотрясение|concussion| сотрясение мозга': 'Concussion',
            r'Череп|skull fracture': 'Skull fracture',
            
            # Кости
            r'Перелом|fracture|ломаная кость': 'Fracture',
            r'Трещина|crack|stress fracture': 'Stress fracture',
            
            # Общие
            r'Ушиб|bruise|contusion': 'Bruise',
            r'Растяжение|strain|растяжение': 'Muscle strain',
            r'Воспаление|inflammation|tendinitis': 'Tendonitis',
            r'Мышечная усталость|fatigue|усталость мышц': 'Muscle fatigue'
        }
        
        # Паттерны для определения продолжительности отсутствия
        self.duration_patterns = [
            # Недели
            (r'(\d+)\s*(?:неделе|недели|недель|week|weeks)', lambda x: int(x) * 7),
            # Дни
            (r'(\d+)\s*(?:день|дня|дней|day|days)', lambda x: int(x)),
            # Месяцы
            (r'(\d+)\s*(?:месяце|месяца|месяцев|month|months)', lambda x: int(x) * 30),
            # Сезон
            (r'весь\s+сезон|whole\s+season|southeast|сезон', lambda x: 180),  # Примерно полгода
            # Неопределенно
            (r'неопределенно|indefinite|точный\s+срок\s+неизвестен', lambda x: 999)  # Большое число
        ]
    
    async def parse_injuries(self, html_content: str, team_name: str = None) -> List[Dict]:
        """
        Извлекает информацию о травмах из HTML контента.
        
        Args:
            html_content: HTML содержимое страницы с новостями о травмах
            team_name: Название команды (для контекста и фильтрации)
            
        Returns:
            Список словарей с информацией о травмах:
            [
                {
                    'player_name': str,
                    'injury_type': str,
                    'injury_severity': str,
                    'expected_return': str,  # Например: "2-3 недели"
                    'return_date': datetime,  # Если можно определить дату
                    'games_missed': int,      # Ожидаемое количество пропущенных матчей
                    'team': str,
                    'source': str,
                    'confidence': float,      # Уверенность в извлеченных данных (0-1)
                    'raw_text': str,          # Исходный текст для отладки
                    'extracted_at': datetime  # Когда было извлечено
                }
            ]
        """
        if not html_content or not html_content.strip():
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Удаляем скрипты и стили для чистого текста
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            # Разбиваем на предложения для лучшего анализа
            sentences = re.split(r'[.!?]+', text)
            injuries = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:  # Слишком короткое предложение
                    continue
                    
                injury_data = self._extract_injury_from_sentence(sentence, team_name)
                if injury_data:
                    injuries.append(injury_data)
            
            # Дeduплицируем похожие травмы (одна и та же травма может быть упомянута несколько раз)
            unique_injuries = self._deduplicate_injuries(injuries)
            
            logger.info(f"Извлечено {len(unique_injuries)} травм из {self.source_name}")
            return unique_injuries
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге травм из {self.source_name}: {e}")
            return []
    
    def _extract_injury_from_sentence(self, sentence: str, team_name: str = None) -> Optional[Dict]:
        """Извлекает информацию о травме из одного предложения"""
        for pattern in self.injury_patterns:
            match = pattern.search(sentence)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) >= 3:
                        player_name = groups[0].strip()
                        injury_description = groups[1].strip()
                        absence_info = groups[2].strip()
                        
                        # Нормализуем название игрока
                        player_name = self._normalize_player_name(player_name)
                        
                        # Проверяем, относится ли эта травма к интересующей нас команде
                        if team_name and not self._is_relevant_team(player_name, injury_description, team_name):
                            continue
                        
                        # Извлекаем информацию о травме
                        injury_info = self._parse_injury_details(injury_description)
                        
                        # Извлекаем информацию об отсутствии
                        absence_info = self._parse_absence_info(absence_info)
                        
                        # Вычисляем уверенность в извлеченных данных
                        confidence = self._calculate_confidence(sentence, player_name, injury_description)
                        
                        # Порог уверенности - не возвращаем слишком неопределенные результаты
                        if confidence < 0.3:
                            continue
                        
                        return {
                            'player_name': player_name,
                            'injury_type': injury_info['type'],
                            'injury_severity': injury_info['severity'],
                            'expected_return': absence_info['description'],
                            'return_date': absence_info.get('date'),
                            'games_missed': absence_info.get('games', 0),
                            'team': team_name or self._extract_team_from_context(sentence),
                            'source': self.source_name,
                            'confidence': confidence,
                            'raw_text': sentence,
                            'extracted_at': datetime.now()
                        }
                except Exception as e:
                    logger.debug(f"Ошибка при обработке совпадения '{match.group()}': {e}")
                    continue
        
        return None
    
    def _normalize_player_name(self, name: str) -> str:
        """Нормализует имя игрока для единообразного сравнения"""
        # Удаляем лишние пробелы
        name = ' '.join(name.split())
        
        # Убираем известные префиксы/суффиксы, если они не часть имени
        prefixes_to_remove = ['mr.', 'mrs.', 'dr.', 'prof.']
        suffixes_to_remove = ['jr.', 'sr.', 'ii', 'iii', 'iv']
        
        name_parts = name.lower().split()
        if name_parts and name_parts[0] in prefixes_to_remove:
            name_parts = name_parts[1:]
        if name_parts and name_parts[-1] in suffixes_to_remove:
            name_parts = name_parts[:-1]
        
        return ' '.join(name_parts).title()
    
    def _is_relevant_team(self, player_name: str, injury_description: str, team_name: str) -> bool:
        """Проверяет, относится ли информация о травме к интересующей нас команде"""
        if not team_name:
            return True
            
        # Проверяем прямое упоминание команды в описании травмы
        team_lower = team_name.lower()
        desc_lower = injury_description.lower()
        
        if team_lower in desc_lower:
            return True
            
        # Проверяем через отображение команд (если задано)
        if self.team_mapping:
            for canonical_name, aliases in self.team_mapping.items():
                if team_name.lower() == canonical_name.lower():
                    for alias in aliases:
                        if alias.lower() in desc_lower:
                            return True
                    break
        
        # Если не нашли явного упоминания команды, предполагаем, что это может быть релевантно
        # (травма может быть упомянута без прямого указания команды в предложении)
        return True
    
    def _parse_injury_details(self, description: str) -> Dict[str, str]:
        """Извлекает детали травмы из описания"""
        description_lower = description.lower().strip()
        
        # Нормализуем описание травмы
        normalized_injury = description_lower
        for pattern, replacement in self.injury_normalization.items():
            normalized_injury = re.sub(pattern, replacement, normalized_injury, flags=re.IGNORECASE)
        
        # Определяем степень тяжести на основе ключевых слов
        severity_keywords = {
            'легкая': ['легкая', 'minor', 'slight', 'minimal'],
            'умеренная': ['умеренная', 'moderate', 'medium'],
            'тяжелая': ['тяжелая', 'severe', 'serious', 'significant', 'major'],
            'критическая': ['критическая', 'critical', 'life-threatening', 'карьерa']
        }
        
        severity = 'неизвестно'
        for sev, keywords in severity_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                severity = sev
                break
        
        return {
            'type': normalized_injury.title(),
            'severity': severity
        }
    
    def _parse_absence_info(self, absence_text: str) -> Dict[str, any]:
        """Извлекает информацию об ожидаемом времени отсутствия"""
        absence_text = absence_text.strip().lower()
        
        # Ищем продолжительность отсутствия
        days = None
        return_date = None
        
        for pattern, converter in self.duration_patterns:
            match = re.search(pattern, absence_text)
            if match:
                try:
                    days = converter(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue
        
        # Если не нашли конкретную продолжительность, пытаемся извлечь дату возврата
        if days is None:
            # Ищем упоминания конкретных дат
            date_patterns = [
                r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})',  # DD.MM.YYYY или MM/DD/YYYY
                r'(\d{1,2})\s+(январ|феврал|март|апрел|ма|июн|июл|авг|сент|окт|нояб|декабр)[а-я]*\s+(\d{2,4})',
                r'(январ|феврал|март|апрел|ма|июн|июл|авг|сент|окт|нояб|декабр)[а-я]*\s+(\d{1,2}),?\s+(\d{2,4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, absence_text, re.IGNORECASE)
                if match:
                    try:
                        # Попытка преобразовать в дату (упрощенно)
                        # В реальной реализации нужно было бы обрабатывать разные форматы
                        return_date = datetime.now() + timedelta(days=30)  # Placeholder
                        break
                    except ValueError:
                        continue
        
        # Если все еще нет данных, пытаемся оценить по ключевым словам
        if days is None:
            if any(word in absence_text for word in ['неделе', 'недели', 'недель', 'week', 'weeks']):
                days = 14  # Предполагаем 2 недели как среднее
            elif any(word in absence_text for word in ['день', 'дня', 'дней', 'day', 'days']):
                days = 7   # Предполагаем 1 неделю как среднее
            elif any(word in absence_text for word in ['месяце', 'месяца', 'месяцев', 'month', 'months']):
                days = 60  # Предполагаем 2 месяца как среднее
            elif any(word in absence_text for word in ['сезон', 'season', 'карьерa']):
                days = 180 # Предполагаем полсезона как среднее
            else:
                days = 14  # Значение по умолчанию
        
        # Вычисляем ожидаемое количество пропущенных матчей
        # Предполагаем среднюю частоту матчей - 2 матча в неделю для большинства видов спорта
        games_missed = max(1, int((days / 7) * 2)) if days else 0
        
        return {
            'description': absence_text.capitalize(),
            'date': return_date,
            'games': games_missed
        }
    
    def _calculate_confidence(self, sentence: str, player_name: str, injury_description: str) -> float:
        """Вычисляет уверенность в извлеченных данных"""
        confidence = 0.5  # Базовая уверенность
        
        # Повышаем уверенность если есть четкие маркеры травмы
        injury_indicators = ['травмирован', 'повредил', 'получил травму', 'out with', 'injured']
        if any(indicator in sentence.lower() for indicator in injury_indicators):
            confidence += 0.2
        
        # Повышаем уверенность если есть информация об отсутствии
        absence_indicators = ['пропустит', 'отсутствует', 'выбыл', 'out', 'из-?за']
        if any(indicator in sentence.lower() for indicator in absence_indicators):
            confidence += 0.2
        
        # Повышаем уверенность если имя игрока выглядит правдоподобно
        if len(player_name.split()) >= 2 and all(part.isalpha() for part in player_name.split()):
            confidence += 0.1
        
        # Повышаем уверенность если есть числовая информация
        if re.search(r'\d+', sentence):
            confidence += 0.1
        
        # Понижаем уверенность если есть слова неопределенности
        uncertainty_words = ['возможно', 'может быть', 'предположительно', 'maybe', 'possibly']
        if any(word in sentence.lower() for word in uncertainty_words):
            confidence -= 0.1
        
        # Ограничиваем уверенность диапазоном [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def _deduplicate_injuries(self, injuries: List[Dict]) -> List[Dict]:
        """Удаляет дублирующиеся записи о травмах"""
        if not injuries:
            return injuries
        
        unique_injuries = []
        seen = set()
        
        for injury in injuries:
            # Создаем ключ для deduplication на основе ключевых полей
            key = (
                injury.get('player_name', '').lower().strip(),
                injury.get('injury_type', '').lower().strip(),
                injury.get('team', '').lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                unique_injuries.append(injury)
        
        return unique_injuries
    
    def _extract_team_from_context(self, sentence: str) -> str:
        """Пытается извлечь название команды из контекста предложения"""
        # Простая эвристика: ищем известные названия команд рядом с упоминанием травмы
        # В реальной реализации нужно было бы иметь базу данных команд
        common_team_indicators = [
            'футбольный клуб', 'футбольная команда', 'фк', 
            'баскетбольный клуб', 'баскетбольная команда', 'бк',
            'хоккейный клуб', 'хоккейная команда', 'хк',
            'волейбольный клуб', 'волейбольная команда', 'вк'
        ]
        
        words = sentence.lower().split()
        for i, word in enumerate(words):
            if any(indicator in word for indicator in common_team_indicators):
                # Ищем название команды рядом
                context_words = words[max(0, i-3):min(len(words), i+4)]
                # Здесь была бы логика извлечения названия команды из контекста
                # Для простоты возвращаем неизвестную команду
                return "Неизвестная команда"
        
        return "Неизвестная команда"

# Специализированные парсеры для конкретных источников
# Каждый парсер наследует общий класс и переопределяет методы при необходимости

class FootballInjuriesParser(GeneralInjuriesParser):
    """Парсер для новостей о футбольных травмах"""
    
    def __init__(self, team_mapping: Dict[str, str] = None):
        super().__init__("Football Injuries", "https://www.example.com/football-injuries", team_mapping)
        
        # Можно добавить специфические паттерны для футбола
        self.sport_specific_patterns = [
            # Паттерны специфичные для футбола
            re.compile(
                r'(\w+(?:\s+\w+)*?)\s+(?:получил|повредил)\s+(?:разрыв|растяжение)\s+(?:задней|передней)\s+'
                r'(?:бедра|мышцы)\s+(?:бедра|мышцы)\s+(?:и\s+)?(?:пропустит|будет отсутствовать)',
                re.IGNORECASE
            )
        ]

class TransfermarktInjuriesParser(GeneralInjuriesParser):
    """Парсер для Transfermarkt (специализируется на трансферах и травмах)"""
    
    def __init__(self, team_mapping: Dict[str, str] = None):
        super().__init__("Transfermarkt Injuries", "https://www.transfermarkt.com/team/INJURIES/team/", team_mapping)
        
        # Transfermarkt имеет специфическую структуру данных
        # Можно добавить парсинг их таблиц травм

class EspnInjuriesParser(GeneralInjuriesParser):
    """Парсер для ESPN травм"""
    
    def __init__(self, team_mapping: Dict[str, str] = None):
        super().__init__("ESPN Injuries", "https://www.espn.com/sports/injuries/_/", team_mapping)

class BbcSportInjuriesParser(GeneralInjuriesParser):
    """Парсер для BBC Sport травм"""
    
    def __init__(self, team_mapping: Dict[str, str] = None):
        super().__init__("BBC Sport Injuries", "https://www.bbc.com/sport/football/injuries", team_mapping)

# Фабрика для создания парсеров
def create_injury_parser(source_type: str, team_mapping: Dict[str, str] = None) -> BaseInjuryParser:
    """
    Фабричный метод для создания парсеров травм
    
    Args:
        source_type: Тип парсера ('general', 'football', 'transfermarkt', 'espn', 'bbc_sport')
        team_mapping: Словарь сопоставления названий команд (опционально)
        
    Returns:
        Экземпляр соответствующего парсера
    """
    parsers = {
        'general': GeneralInjuriesParser,
        'football': FootballInjuriesParser,
        'transfermarkt': TransfermarktInjuriesParser,
        'espn': EspnInjuriesParser,
        'bbc_sport': BbcSportInjuriesParser
    }
    
    parser_class = parsers.get(source_type.lower(), GeneralInjuriesParser)
    return parser_class(team_mapping)

# Для обратной совместимости
InjuryParser = GeneralInjuriesParser
