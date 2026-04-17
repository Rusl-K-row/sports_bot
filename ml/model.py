import joblib
import logging
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from config import MODEL_PATH

# Путь к файлу модели
MODEL_DIR = Path(MODEL_PATH).parent
MODEL_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class MatchOutcomeModel:
    """
    Модель логистической регрессии для прогнозирования исхода матча:
    0 - победа хозяев (Home Win)
    1 - ничья (Draw)
    2 - победа гостей (Away Win)
    """

    def __init__(self):
        self.model = LogisticRegression(
            multi_class='multinomial',
            solver='lbfgs',
            max_iter=1000,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = [
            'home_xg', 'away_xg',
            'home_form', 'away_form',
            'h2h_home_win',
            'injuries_home', 'injuries_away',
            'weather_temp', 'weather_precip',
            'fatigue_home', 'fatigue_away'
        ]

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Обучает модель на размеченных данных."""
        if X.shape[1] != len(self.feature_names):
            raise ValueError(f"Expected {len(self.feature_names)} features, got {X.shape[1]}")

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Возвращает вероятности для каждого класса: [P(home_win), P(draw), P(away_win)]
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted. Call fit() first or load a pre-trained model.")

        if X.shape[1] != len(self.feature_names):
            raise ValueError(f"Expected {len(self.feature_names)} features, got {X.shape[1]}")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Возвращает предсказанный класс (0, 1, 2)."""
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

    def save(self, path: str = None):
        """Сохраняет модель и скейлер на диск."""
        path = path or MODEL_PATH
        data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted
        }
        joblib.dump(data, path)
        return path

    def load(self, path: str = None):
        """Загружает модель и скейлер с диска."""
        path = path or MODEL_PATH
        try:
            data = joblib.load(path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.is_fitted = data['is_fitted']
            return self
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found: {path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")


# Удобная функция для быстрого доступа
def get_model() -> MatchOutcomeModel:
    """Возвращает загруженную модель (или новую, если файл не найден)."""
    model = MatchOutcomeModel()
    try:
        model.load()
    except FileNotFoundError:
        logger.warning("Pre-trained model not found. Returning untrained model.")
    return model