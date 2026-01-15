import json
from openai import AsyncOpenAI
from app.core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Транскрипция аудио через Whisper"""
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"
            )
        return transcript.text
    
    async def analyze_diary(self, diary_text: str) -> dict:
        """Анализ дневника через GPT-4"""
        prompt = """Ты - эксперт по анализу личности. Проанализируй дневник человека и извлеки структурированную информацию.

ДНЕВНИК:
{diary_text}

ИЗВЛЕКИ СЛЕДУЮЩУЮ ИНФОРМАЦИЮ:

1. ЭМОЦИИ И НАСТРОЕНИЕ:
   - Основные эмоции (радость, грусть, тревога, спокойствие, злость, страх и т.д.)
   - Интенсивность эмоций (1-10)
   - Общее настроение (positive/neutral/negative)

2. ЦЕННОСТИ И ПРИОРИТЕТЫ:
   - Что важно для человека (семья, карьера, дружба, саморазвитие, деньги, здоровье и т.д.)
   - Приоритеты (что важнее всего)

3. ИНТЕРЕСЫ И ХОББИ:
   - Чем увлекается
   - Что любит делать

4. СТИЛЬ ОБЩЕНИЯ:
   - Формальность (формальный/неформальный/смешанный)
   - Использование юмора (да/нет, какой тип)
   - Длина предложений (короткие/средние/длинные)
   - Эмоциональность речи

5. ПАТТЕРНЫ МЫШЛЕНИЯ:
   - Аналитический или интуитивный
   - Оптимист или пессимист
   - Фокус на деталях или общей картине

6. ЦЕЛИ И МЕЧТЫ:
   - Краткосрочные цели
   - Долгосрочные мечты

7. СТРАХИ И ПРОБЛЕМЫ:
   - О чем беспокоится
   - Какие страхи упоминаются

8. ПОТРЕБНОСТИ И ПРЕДЛОЖЕНИЯ:
   - Что нужно (вещи, работа, услуги)
   - Что предлагает (вещи, работа, услуги)

ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON.""".format(diary_text=diary_text)
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты эксперт по анализу личности. Всегда отвечай валидным JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def guess_gender(self, name: str) -> str:
        """Предположение пола по имени"""
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Определи пол по имени. Ответь только: мужчина, женщина или неизвестно."},
                {"role": "user", "content": name}
            ],
            temperature=0.1
        )
        
        guess = response.choices[0].message.content.lower()
        if "мужчина" in guess or "male" in guess:
            return "male"
        elif "женщина" in guess or "female" in guess:
            return "female"
        return "unknown"
