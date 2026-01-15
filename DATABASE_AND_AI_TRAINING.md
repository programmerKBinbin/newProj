# База данных и стратегия дообучения ИИ-клонов

## Полная структура базы данных

### Схема базы данных (PostgreSQL)

#### 1. Таблица `users` - Пользователи

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER,
    city VARCHAR(255),
    timezone VARCHAR(50),
    language_code VARCHAR(10) DEFAULT 'ru',
    is_premium BOOLEAN DEFAULT FALSE,
    premium_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_city ON users(city);
CREATE INDEX idx_users_premium ON users(is_premium, premium_until);
```

**Назначение:** Хранит базовую информацию о пользователях Telegram

---

#### 2. Таблица `clones` - ИИ-клоны пользователей

```sql
CREATE TABLE clones (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Основной профиль клона (структурированные данные)
    personality_profile JSONB NOT NULL DEFAULT '{}',
    /*
    Структура personality_profile:
    {
        "values": ["семья", "карьера", "саморазвитие"],
        "interests": ["программирование", "музыка", "путешествия"],
        "communication_style": "прямой, с юмором",
        "emotional_patterns": {
            "morning": "энергичный",
            "evening": "спокойный"
        },
        "thinking_patterns": ["аналитический", "креативный"],
        "goals": ["найти работу", "изучить Python"],
        "fears": ["неудача", "одиночество"],
        "strengths": ["коммуникабельность", "упорство"],
        "weaknesses": ["перфекционизм"]
    }
    */
    
    -- Векторное представление личности (для поиска совместимостей)
    personality_embedding VECTOR(1536), -- OpenAI embedding размерность
    
    -- Статистика и метрики
    accuracy_score DECIMAL(5,2) DEFAULT 0.00, -- 0-100%
    diaries_count INTEGER DEFAULT 0,
    last_diary_at TIMESTAMP,
    total_words_analyzed INTEGER DEFAULT 0,
    
    -- Состояние клона
    status VARCHAR(50) DEFAULT 'creating', -- creating, active, paused, deleted
    training_stage VARCHAR(50) DEFAULT 'initial', -- initial, learning, mature
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_trained_at TIMESTAMP
);

CREATE INDEX idx_clones_user_id ON clones(user_id);
CREATE INDEX idx_clones_status ON clones(status);
CREATE INDEX idx_clones_accuracy ON clones(accuracy_score DESC);
CREATE INDEX idx_clones_personality_embedding ON clones USING ivfflat (personality_embedding vector_cosine_ops);
```

**Назначение:** Хранит профиль ИИ-клона, его характеристики и векторное представление для поиска

---

#### 3. Таблица `diaries` - Дневники пользователей

```sql
CREATE TABLE diaries (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    clone_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    
    -- Контент дневника
    content_text TEXT NOT NULL, -- Транскрибированный текст
    audio_file_path VARCHAR(500), -- Путь к аудио файлу в хранилище
    audio_duration_seconds INTEGER, -- Длительность аудио
    word_count INTEGER,
    
    -- Анализ дневника
    analysis_result JSONB, -- Результат анализа ИИ
    /*
    Структура analysis_result:
    {
        "emotions": ["радость", "тревога"],
        "topics": ["работа", "отношения"],
        "sentiment": "positive",
        "key_phrases": ["важное решение", "новый проект"],
        "needs_detected": ["нужен чайник", "ищу работу"],
        "offers_detected": ["продаю велосипед"],
        "insights": ["пользователь ценит независимость"]
    }
    */
    
    -- Векторное представление для семантического поиска
    content_embedding VECTOR(1536),
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    analyzed_at TIMESTAMP,
    analysis_version VARCHAR(50) -- Версия модели анализа
);

CREATE INDEX idx_diaries_user_id ON diaries(user_id);
CREATE INDEX idx_diaries_clone_id ON diaries(clone_id);
CREATE INDEX idx_diaries_created_at ON diaries(created_at DESC);
CREATE INDEX idx_diaries_content_embedding ON diaries USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_diaries_analyzed ON diaries(analyzed_at) WHERE analyzed_at IS NOT NULL;
```

**Назначение:** Хранит все дневники пользователей, их анализ и векторные представления для поиска

---

#### 4. Таблица `clone_memories` - Память клона

```sql
CREATE TABLE clone_memories (
    id BIGSERIAL PRIMARY KEY,
    clone_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    source_diary_id BIGINT REFERENCES diaries(id) ON DELETE SET NULL,
    
    -- Тип памяти
    memory_type VARCHAR(50) NOT NULL, -- fact, preference, experience, relationship, goal, fear
    
    -- Содержимое памяти
    memory_content TEXT NOT NULL, -- Что клон "помнит"
    memory_context TEXT, -- Контекст, когда это было упомянуто
    
    -- Важность и релевантность
    importance_score DECIMAL(3,2) DEFAULT 0.5, -- 0-1, насколько важно
    confidence_score DECIMAL(3,2) DEFAULT 0.5, -- 0-1, насколько уверен клон
    
    -- Вектор для семантического поиска
    memory_embedding VECTOR(1536),
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP, -- Когда последний раз использовалась в контексте
    usage_count INTEGER DEFAULT 0 -- Сколько раз использовалась
);

CREATE INDEX idx_memories_clone_id ON clone_memories(clone_id);
CREATE INDEX idx_memories_type ON clone_memories(memory_type);
CREATE INDEX idx_memories_importance ON clone_memories(importance_score DESC);
CREATE INDEX idx_memories_embedding ON clone_memories USING ivfflat (memory_embedding vector_cosine_ops);
CREATE INDEX idx_memories_last_used ON clone_memories(last_used_at DESC);
```

**Назначение:** Хранит конкретные факты, предпочтения и опыт, которые клон "помнит" о пользователе

**Примеры записей:**
- `memory_type: "preference"`, `memory_content: "Любит утренний кофе, не пьет после 18:00"`
- `memory_type: "fact"`, `memory_content: "Работает программистом в компании X"`
- `memory_type: "experience"`, `memory_content: "В детстве боялся собак, но преодолел страх"`
- `memory_type: "goal"`, `memory_content: "Хочет выучить Python к концу года"`

---

#### 5. Таблица `clone_conversations` - Общение между клонами

```sql
CREATE TABLE clone_conversations (
    id BIGSERIAL PRIMARY KEY,
    clone1_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    clone2_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    
    -- Диалог
    messages JSONB NOT NULL,
    /*
    Структура messages:
    [
        {
            "role": "clone1",
            "content": "Привет! Как дела?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "clone2",
            "content": "Отлично! Только что закончил проект.",
            "timestamp": "2024-01-15T10:00:15Z"
        }
    ]
    */
    
    -- Контекст разговора
    conversation_context JSONB,
    /*
    {
        "topic": "работа",
        "mood": "positive",
        "topics_discussed": ["карьера", "хобби"]
    }
    */
    
    -- Результаты анализа
    compatibility_analysis JSONB,
    /*
    {
        "overall_score": 0.87,
        "values_match": 0.9,
        "communication_match": 0.85,
        "interests_match": 0.88,
        "insights": ["Оба ценят семью", "Похожий юмор"]
    }
    */
    
    -- Статус
    status VARCHAR(50) DEFAULT 'active', -- active, completed, archived
    conversation_length INTEGER, -- Количество сообщений
    
    -- Метаданные
    started_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_clone1 ON clone_conversations(clone1_id);
CREATE INDEX idx_conversations_clone2 ON clone_conversations(clone2_id);
CREATE INDEX idx_conversations_status ON clone_conversations(status);
CREATE INDEX idx_conversations_started_at ON clone_conversations(started_at DESC);
```

**Назначение:** Хранит все диалоги между клонами для анализа совместимости

---

#### 6. Таблица `compatibilities` - Найденные совместимости

```sql
CREATE TABLE compatibilities (
    id BIGSERIAL PRIMARY KEY,
    clone1_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    clone2_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    user1_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Оценки совместимости
    overall_score DECIMAL(5,2) NOT NULL, -- 0-100%
    scores_by_level JSONB NOT NULL,
    /*
    {
        "values": 0.85,
        "emotional": 0.90,
        "communication": 0.82,
        "lifestyle": 0.88,
        "conflict_resolution": 0.80
    }
    */
    
    -- Детали совместимости
    conversation_summary TEXT, -- Краткое описание, что обсуждали клоны
    key_matches JSONB, -- Ключевые совпадения
    /*
    [
        "Оба ценят семью",
        "Похожий чувство юмора",
        "Оба любят путешествия"
    ]
    */
    
    -- Предсказания
    predictions JSONB,
    /*
    {
        "relationship_potential": "high",
        "predicted_issues": ["разные графики работы"],
        "solutions_found": ["компромисс по времени"]
    }
    */
    
    -- Статус
    status VARCHAR(50) DEFAULT 'pending', -- pending, shown, accepted, rejected, expired
    shown_to_user1_at TIMESTAMP,
    shown_to_user2_at TIMESTAMP,
    user1_response VARCHAR(50), -- accepted, rejected, pending
    user2_response VARCHAR(50),
    
    -- Связь с разговором
    conversation_id BIGINT REFERENCES clone_conversations(id),
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_compatibilities_clone1 ON compatibilities(clone1_id);
CREATE INDEX idx_compatibilities_clone2 ON compatibilities(clone2_id);
CREATE INDEX idx_compatibilities_users ON compatibilities(user1_id, user2_id);
CREATE INDEX idx_compatibilities_score ON compatibilities(overall_score DESC);
CREATE INDEX idx_compatibilities_status ON compatibilities(status);
```

**Назначение:** Хранит найденные совместимости между пользователями

---

#### 7. Таблица `needs` - Потребности и предложения пользователей

```sql
CREATE TABLE needs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    clone_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    source_diary_id BIGINT REFERENCES diaries(id) ON DELETE SET NULL,
    
    -- Тип потребности
    need_type VARCHAR(50) NOT NULL, -- thing, job, service
    direction VARCHAR(50) NOT NULL, -- need, offer
    
    -- Детали
    title VARCHAR(255) NOT NULL,
    description TEXT,
    details JSONB,
    /*
    Для thing:
    {
        "item": "чайник",
        "condition": "новый",
        "price_range": "500-1000",
        "location": "Москва, центр"
    }
    
    Для job:
    {
        "position": "помощник программиста",
        "skills_required": ["Python", "Git"],
        "schedule": "удаленно, частичная занятость",
        "salary_range": "30000-50000"
    }
    
    Для service:
    {
        "service_type": "ремонт",
        "skill": "сантехник",
        "location": "Москва",
        "price_range": "2000-5000"
    }
    */
    
    -- Локация
    city VARCHAR(255),
    district VARCHAR(255),
    
    -- Вектор для поиска совпадений
    need_embedding VECTOR(1536),
    
    -- Статус
    status VARCHAR(50) DEFAULT 'active', -- active, matched, fulfilled, expired, cancelled
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_needs_user_id ON needs(user_id);
CREATE INDEX idx_needs_type ON needs(need_type, direction);
CREATE INDEX idx_needs_status ON needs(status);
CREATE INDEX idx_needs_city ON needs(city);
CREATE INDEX idx_needs_embedding ON needs USING ivfflat (need_embedding vector_cosine_ops);
```

**Назначение:** Хранит потребности и предложения пользователей для поиска совпадений

---

#### 8. Таблица `matches` - Найденные совпадения потребностей

```sql
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    user1_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    need1_id BIGINT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    need2_id BIGINT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    
    -- Тип совпадения
    match_type VARCHAR(50) NOT NULL, -- thing, job, service
    
    -- Переговоры клонов
    clone_negotiations JSONB,
    /*
    {
        "conversation": [
            {"role": "clone1", "content": "Мой пользователь ищет чайник"},
            {"role": "clone2", "content": "У моего пользователя есть лишний чайник"}
        ],
        "agreed_terms": {
            "price": 700,
            "location": "Москва, центр",
            "meeting_time": "выходные"
        }
    }
    */
    
    -- Детали совпадения
    match_score DECIMAL(5,2), -- Насколько хорошо совпадают потребности
    details JSONB,
    
    -- Статус
    status VARCHAR(50) DEFAULT 'pending', -- pending, shown, accepted, rejected, completed, cancelled
    
    -- Ответы пользователей
    user1_response VARCHAR(50),
    user2_response VARCHAR(50),
    shown_to_user1_at TIMESTAMP,
    shown_to_user2_at TIMESTAMP,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_matches_users ON matches(user1_id, user2_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_type ON matches(match_type);
```

**Назначение:** Хранит найденные совпадения потребностей между пользователями

---

#### 9. Таблица `clone_training_logs` - Логи обучения клонов

```sql
CREATE TABLE clone_training_logs (
    id BIGSERIAL PRIMARY KEY,
    clone_id BIGINT NOT NULL REFERENCES clones(id) ON DELETE CASCADE,
    
    -- Тип обучения
    training_type VARCHAR(50) NOT NULL, -- initial_creation, daily_update, fine_tune, memory_update
    
    -- Данные обучения
    training_data JSONB, -- Какие данные использовались
    training_prompt TEXT, -- Промпт, который использовался
    training_response TEXT, -- Ответ модели
    
    -- Результаты
    accuracy_before DECIMAL(5,2),
    accuracy_after DECIMAL(5,2),
    improvements JSONB, -- Что улучшилось
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    processing_time_ms INTEGER
);

CREATE INDEX idx_training_logs_clone_id ON clone_training_logs(clone_id);
CREATE INDEX idx_training_logs_type ON clone_training_logs(training_type);
CREATE INDEX idx_training_logs_created_at ON clone_training_logs(created_at DESC);
```

**Назначение:** Логирует все процессы обучения клонов для отладки и анализа

---

#### 10. Таблица `notifications` - Уведомления

```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Тип уведомления
    type VARCHAR(50) NOT NULL, -- compatibility_found, match_found, clone_updated, daily_reminder
    
    -- Содержимое
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    data JSONB, -- Дополнительные данные (ID совместимости, совпадения и т.д.)
    
    -- Статус
    read BOOLEAN DEFAULT FALSE,
    sent_to_telegram BOOLEAN DEFAULT FALSE,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read, created_at DESC);
CREATE INDEX idx_notifications_type ON notifications(type);
```

**Назначение:** Хранит уведомления для пользователей

---

## Стратегия "дообучения" и персонализации клонов

### Подход: RAG (Retrieval Augmented Generation) + Системные промпты

**Почему не Fine-tuning для каждого пользователя:**
- Fine-tuning стоит $8-80 за модель (зависит от размера)
- Нужна отдельная модель для каждого пользователя = нереально дорого
- Медленное обновление (нужно переобучать модель)
- Сложно откатить изменения

**Почему RAG + промпты:**
- Дешево (только API вызовы)
- Быстрое обновление (просто добавляем данные в БД)
- Гибкость (можно легко менять информацию)
- Масштабируемо (один подход для всех пользователей)

---

### Как клон "запоминает" информацию

#### Этап 1: Извлечение информации из дневника

Когда пользователь отправляет дневник:

1. **Транскрипция** (если голос) → текст
2. **Анализ через GPT-4** с промптом:
```
Проанализируй дневник пользователя и извлеки:
1. Факты о человеке (работа, семья, хобби)
2. Предпочтения (что любит, что не любит)
3. Эмоции и чувства
4. Цели и мечты
5. Страхи и проблемы
6. Потребности (нужен/предлагает что-то)
7. Стиль общения (как говорит, какие слова использует)

Верни структурированный JSON.
```

3. **Сохранение в БД:**
   - Текст дневника → `diaries`
   - Извлеченные факты → `clone_memories`
   - Потребности → `needs`
   - Обновление профиля → `clones.personality_profile`

#### Этап 2: Создание векторных представлений

Для каждого важного элемента создаем embedding:

```python
# Псевдокод
diary_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=diary_text
)

memory_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=memory_content
)

# Сохраняем в БД
diary.content_embedding = diary_embedding
memory.memory_embedding = memory_embedding
```

**Зачем:** Для семантического поиска - находим релевантную информацию по смыслу, а не по ключевым словам

---

### Как клон общается как человек

#### Подход 1: Системный промпт с контекстом

Когда клону нужно ответить или общаться:

1. **Собираем релевантный контекст из БД:**
   - Последние 10 дневников пользователя
   - Важные воспоминания (memories с высокой важностью)
   - Профиль личности (personality_profile)
   - Недавние события

2. **Формируем системный промпт:**

```
Ты - ИИ-клон пользователя. Твоя задача - общаться и думать как этот человек.

ПРОФИЛЬ ЛИЧНОСТИ:
{personality_profile}

ВАЖНЫЕ ФАКТЫ О ПОЛЬЗОВАТЕЛЕ:
{relevant_memories}

НЕДАВНИЕ СОБЫТИЯ:
{recent_diaries}

СТИЛЬ ОБЩЕНИЯ:
- Используй слова и фразы, которые использует пользователь
- Отражай его эмоциональные паттерны
- Думай как он думает
- Реагируй как он реагирует

ПОМНИ:
- Ты не просто имитируешь, ты понимаешь его ценности и мотивации
- Используй конкретные факты из его жизни
- Будь последовательным в характере
```

3. **Отправляем запрос в GPT-4** с этим промптом

#### Подход 2: RAG для поиска релевантной информации

Когда клону нужно ответить на вопрос или общаться:

1. **Семантический поиск в памяти:**
```python
# Псевдокод
question_embedding = get_embedding(user_question)

# Ищем похожие воспоминания
similar_memories = vector_search(
    query_embedding=question_embedding,
    table=clone_memories,
    limit=5,
    similarity_threshold=0.7
)

# Ищем похожие дневники
similar_diaries = vector_search(
    query_embedding=question_embedding,
    table=diaries,
    limit=3,
    similarity_threshold=0.7
)
```

2. **Формируем контекст из найденного:**
```
КОНТЕКСТ ДЛЯ ОТВЕТА:
- Пользователь ранее говорил: "{similar_memory_1}"
- В дневнике от {date}: "{diary_excerpt}"
- Пользователь ценит: "{value_from_profile}"
```

3. **Отправляем в GPT-4** с контекстом

---

### Процесс обновления клона

#### Ежедневное обновление (после каждого дневника)

1. **Анализ нового дневника:**
   - Извлечение новых фактов
   - Обновление профиля личности
   - Добавление новых воспоминаний

2. **Пересчет точности клона:**
```python
# Псевдокод
accuracy = calculate_accuracy(
    diaries_count=clone.diaries_count,
    consistency_score=check_consistency(), # Насколько последовательны данные
    detail_score=check_detail_level(), # Насколько детален профиль
    memory_count=clone.memories.count()
)
```

3. **Обновление векторного представления:**
   - Пересчитываем `personality_embedding` на основе обновленного профиля
   - Это нужно для поиска совместимостей

#### Еженедельное углубленное обучение

Раз в неделю для каждого активного клона:

1. **Анализ всех дневников за неделю:**
   - Поиск паттернов
   - Выявление изменений в личности
   - Обновление важных воспоминаний

2. **Оптимизация памяти:**
   - Удаление устаревших/неважных воспоминаний
   - Повышение важности часто используемых
   - Консолидация похожих воспоминаний

3. **Обновление системного промпта:**
   - Добавление новых ключевых характеристик
   - Уточнение стиля общения

---

### Как клон общается с другим клоном

#### Процесс генерации диалога

1. **Подготовка контекста для обоих клонов:**
```python
# Для клона 1
context1 = {
    "profile": clone1.personality_profile,
    "recent_memories": get_recent_memories(clone1, limit=10),
    "communication_style": clone1.communication_style
}

# Для клона 2
context2 = {
    "profile": clone2.personality_profile,
    "recent_memories": get_recent_memories(clone2, limit=10),
    "communication_style": clone2.communication_style
}
```

2. **Генерация диалога через GPT-4:**
```
Создай диалог между двумя людьми на основе их профилей:

ЧЕЛОВЕК 1:
{context1}

ЧЕЛОВЕК 2:
{context2}

ТЕМА РАЗГОВОРА: {topic} (например, "работа", "хобби", "отношения")

ТРЕБОВАНИЯ:
- Каждый говорит в своем стиле
- Используй факты из их профилей
- Диалог должен быть естественным
- 10-15 реплик всего
```

3. **Анализ диалога на совместимость:**
```
Проанализируй диалог между двумя людьми:
{generated_dialogue}

Оцени совместимость по уровням:
1. Ценности (0-1)
2. Эмоциональная (0-1)
3. Коммуникационная (0-1)
4. Образ жизни (0-1)
5. Решение конфликтов (0-1)

Найди ключевые совпадения и потенциальные проблемы.
```

4. **Сохранение результатов:**
   - Диалог → `clone_conversations`
   - Анализ → `compatibilities` (если совместимость высокая)

---

### Оптимизация и улучшение клонов

#### Метрики качества клона

1. **Точность (accuracy_score):**
   - Насколько хорошо клон предсказывает решения пользователя
   - Тестируется на вопросах, где известен ответ пользователя

2. **Последовательность:**
   - Насколько последовательны ответы клона
   - Не противоречит ли сам себе

3. **Детализация:**
   - Насколько детален профиль
   - Использует ли конкретные факты

4. **Релевантность:**
   - Насколько релевантны ответы контексту
   - Использует ли правильные воспоминания

#### Процесс улучшения

1. **Сбор обратной связи:**
   - Пользователь оценивает ответы клона
   - Отмечает несоответствия

2. **Корректировка:**
   - Если клон ошибся → обновляем соответствующие воспоминания
   - Если не использовал важный факт → повышаем важность памяти
   - Если противоречил → проверяем и исправляем профиль

3. **A/B тестирование:**
   - Тестируем разные промпты
   - Выбираем лучшие варианты

---

### Пример: Как клон отвечает на вопрос

**Вопрос пользователя:** "Что бы я сделал, если бы мне предложили работу в другом городе?"

**Процесс:**

1. **Поиск релевантной информации:**
```python
# Семантический поиск
memories = vector_search("работа в другом городе", clone.memories)
# Находит: "Пользователь ценит семью и не хочет переезжать"
# Находит: "Пользователь говорил, что карьера важна, но семья важнее"

diaries = vector_search("переезд работа", clone.diaries)
# Находит дневник: "Думал о переезде, но не хочу оставлять родителей"
```

2. **Формирование ответа:**
```
Системный промпт: Ты - клон пользователя. Используй эти факты:
- Пользователь ценит семью больше карьеры
- Говорил, что не хочет переезжать из-за родителей
- Но карьера тоже важна

Вопрос: "Что бы я сделал, если бы мне предложили работу в другом городе?"

Ответь как пользователь, используя его ценности и факты.
```

3. **Ответ клона (через GPT-4):**
"Сложный вопрос. С одной стороны, карьерная возможность - это важно. Но я очень ценю близость с семьей, особенно с родителями. Скорее всего, я бы попросил удаленную работу или попробовал договориться о гибком графике с возможностью приезжать домой. Полный переезд был бы для меня слишком тяжелым решением."

4. **Обновление статистики:**
   - Увеличиваем `usage_count` для использованных воспоминаний
   - Обновляем `last_used_at`

---

## Техническая реализация

### Библиотеки и инструменты

**Для работы с векторами:**
- `pgvector` - расширение PostgreSQL для векторного поиска
- `openai` - для создания embeddings

**Для работы с ИИ:**
- `openai` - GPT-4 API
- `langchain` (опционально) - для упрощения работы с RAG

**Для работы с БД:**
- `SQLAlchemy` - ORM
- `alembic` - миграции
- `asyncpg` - асинхронный драйвер PostgreSQL

### Пример кода: Получение ответа от клона

```python
async def get_clone_response(clone_id: int, question: str) -> str:
    # 1. Получаем клон и его профиль
    clone = await get_clone(clone_id)
    
    # 2. Создаем embedding вопроса
    question_embedding = await create_embedding(question)
    
    # 3. Ищем релевантные воспоминания
    memories = await vector_search_memories(
        clone_id=clone_id,
        query_embedding=question_embedding,
        limit=5
    )
    
    # 4. Ищем релевантные дневники
    diaries = await vector_search_diaries(
        clone_id=clone_id,
        query_embedding=question_embedding,
        limit=3
    )
    
    # 5. Формируем системный промпт
    system_prompt = build_system_prompt(
        personality_profile=clone.personality_profile,
        memories=memories,
        recent_diaries=diaries
    )
    
    # 6. Отправляем в GPT-4
    response = await openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.7  # Для более естественных ответов
    )
    
    # 7. Обновляем статистику использованных воспоминаний
    await update_memory_usage([m.id for m in memories])
    
    return response.choices[0].message.content
```

---

## Масштабирование подхода

### Этап 1: MVP (RAG + промпты)
- Используем GPT-4 с системными промптами
- Векторный поиск в памяти
- Быстро и дешево

### Этап 2: Оптимизация
- Fine-tuning базовой модели на общих данных проекта
- RAG для персонализации каждого клона
- Комбинация подходов

### Этап 3: Продвинутое обучение
- Fine-tuning отдельных моделей для разных типов клонов
- Использование более мощных моделей для анализа
- Автоматическая оптимизация промптов

---

## Итоговая архитектура обучения

```
ПОЛЬЗОВАТЕЛЬ → Дневник → Анализ GPT-4 → Извлечение фактов
                                                    ↓
                                    Сохранение в БД (memories, profile)
                                                    ↓
                                    Создание embeddings → Векторный поиск
                                                    ↓
ВОПРОС/ОБЩЕНИЕ → Поиск релевантного контекста → Формирование промпта
                                                    ↓
                                    GPT-4 с контекстом → Ответ клона
                                                    ↓
                                    Обратная связь → Улучшение памяти
```

Этот подход позволяет клонам "запоминать" информацию, общаться как человек и постоянно улучшаться без дорогого fine-tuning для каждого пользователя.
