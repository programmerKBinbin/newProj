import hmac
import hashlib
from urllib.parse import parse_qsl
from app.core.config import settings

def validate_telegram_init_data(init_data: str) -> bool:
    """
    Валидация initData от Telegram Web App
    """
    try:
        # Парсим данные
        parsed_data = dict(parse_qsl(init_data))
        
        # Извлекаем hash и остальные данные
        received_hash = parsed_data.pop('hash', '')
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Создаем строку для проверки
        data_check_string = '\n'.join(
            f"{key}={value}" 
            for key, value in sorted(parsed_data.items())
        )
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем
        return hmac.compare_digest(calculated_hash, received_hash)
    except Exception:
        return False

def extract_telegram_user_id(init_data: str) -> Optional[int]:
    """
    Извлекает telegram_id пользователя из initData
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
        user_data = parsed_data.get('user', '')
        if user_data:
            import json
            user = json.loads(user_data)
            return user.get('id')
    except Exception:
        pass
    return None
