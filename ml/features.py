"""
Вычисление признаков для ML-модели из сырых данных матча и контекста.
"""

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta


def calculate_form(points_list: List[int]) -> int:
    """
    Вычисляет форму команды: сумма очков за последние N матчей.
    W = 3, D = 1, L = 0
    """
    return sum(points_list[-5:]) if points_list else 0


def calculate_h2h_advantage(h2h_matches: List[Dict], home_team_id: int, away_team_id: int) -> float:
    """
    Вычисляет % побед домашней команды в личных встречах.
    h2h_matches: список матчей с полями: home_team_id, away_team_id, winner
    winner: 0 - ничья, 1 - победа хозяев, 2 - победа гостей
    """
    if not h2h_matches:
        return 0.5  # нейтрально, если нет данных

    home_wins = 0
    total = 0
    for match in h2h_matches:
        if match['home_team_id'] == home_team_id and match['away_team_id'] == away_team_id:
            total += 1
            if match['winner'] == 1:  # хозяева выиграли
                home_wins += 1
        elif match['home_team_id'] == away_team_id and match['away_team_id'] == home_team_id:
            total += 1
            if match['winner'] == 2:  # гости выиграли (но это выезд для original home)
                home_wins += 1  # потому что если оригинальные хозяева были гостями и выиграли — это их победа в H2H

    return home_wins / total if total > 0 else 0.5


def extract_features_from_match(
    match_data: Dict,
    home_team_recent_form: List[int],
    away_team_recent_form: List[int],
    h2h_matches: List[Dict],
    weather_data: Optional[Dict] = None,
    fatigue_data: Optional[Dict] = None
) -> np.ndarray:
    """
    Извлекает вектор признаков для одного матча.
    Возвращает np.ndarray kształта (1, n_features) для передачи в модель.
    """
    # xG (expected goals)
    home_xg = match_data.get('home_xg', 0.0)
    away_xg = match_data.get('away_xg', 0.0)

    # Форма
    home_form = calculate_form(home_team_recent_form)
    away_form = calculate_form(away_team_recent_form)

    # H2H
    home_team_id = match_data.get('home_team_id')
    away_team_id = match_data.get('away_team_id')
    h2h_home_win = calculate_h2h_advantage(h2h_matches, home_team_id, away_team_id)

    # Травмы
    injuries_home = match_data.get('injuries_home', 0)
    injuries_away = match_data.get('injuries_away', 0)

    # Погода
    weather_temp = weather_data.get('temperature', 15.0) if weather_data else 15.0
    weather_precip = weather_data.get('precipitation', 0.0) if weather_data else 0.0

    # Усталость (дни с последнего матча)
    fatigue_home = fatigue_data.get('home', 3) if fatigue_data else 3
    fatigue_away = fatigue_data.get('away', 3) if fatigue_data else 3

    # Формируем вектор признаков
    features = np.array([[
        home_xg, away_xg,
        home_form, away_form,
        h2h_home_win,
        injuries_home, injuries_away,
        weather_temp, weather_precip,
        fatigue_home, fatigue_away
    ]])

    return features


def get_feature_names() -> List[str]:
    """Возвращает имена признаков в порядке следования."""
    return [
        'home_xg', 'away_xg',
        'home_form', 'away_form',
        'h2h_home_win',
        'injuries_home', 'injuries_away',
        'weather_temp', 'weather_precip',
        'fatigue_home', 'fatigue_away'
    ]