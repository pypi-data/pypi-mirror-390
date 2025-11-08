import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain.messages import AIMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class LangChainOpenAIClient:
    """Клиент для работы с OpenAI API через LangChain v1.0"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5",
        max_tokens: int = 1500,
        temperature: float = 0.7,
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Инициализируем LangChain модель
        self.chat_model = ChatOpenAI(
            model=model,
            api_key=api_key,
            max_tokens=max_tokens if not self._is_gpt5() else None,
            temperature=temperature if not self._is_gpt5() else None,
            reasoning_effort="minimal" if self._is_gpt5() else None,
            max_retries=3
        )

        # Получаем лимиты для модели
        self.model_limits = self._get_model_limits()

        # Для диагностики пустых ответов
        self.last_completion_tokens = 0

        logger.info(
            f"LangChain OpenAI клиент инициализирован с моделью {model} (GPT-5: {self._is_gpt5()}, лимит: {self.model_limits['total_context']} токенов)"
        )
        
    @property
    def is_gpt5(self) -> bool:
        """Определяет, является ли модель GPT-5"""
        return self._is_gpt5()
        
    def _is_gpt5(self) -> bool:
        """Определяет, является ли модель GPT-5"""
        return "gpt-5" in self.model.lower()

    def _get_model_limits(self) -> Dict[str, int]:
        """Возвращает лимиты для конкретной модели"""
        model_limits = {
            # GPT-3.5
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16385,
            # GPT-4
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            # GPT-5
            "gpt-5-mini": 128000,
            "gpt-5": 200000,
        }

        # Получаем лимит для текущей модели или используем консервативное значение
        total_limit = model_limits.get(self.model, 8192)

        # Резервируем место для ответа и буфера
        completion_reserve = min(
            self.max_tokens * 2, total_limit // 4
        )  # Резервируем место для ответа
        buffer_reserve = 500  # Буфер для безопасности

        return {
            "total_context": total_limit,
            "max_input_tokens": total_limit - completion_reserve - buffer_reserve,
            "completion_reserve": completion_reserve,
        }

    def _convert_messages_to_langchain(
        self, messages: List[Dict[str, str]]
    ) -> List[Any]:
        """Конвертирует сообщения из формата dict в LangChain messages"""
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                # По умолчанию считаем user
                langchain_messages.append(HumanMessage(content=content))

        return langchain_messages

    def _convert_langchain_to_dict(self, message: AIMessage) -> Dict[str, Any]:
        """Конвертирует LangChain сообщение обратно в dict для логирования"""
        return {
            "content": message.content if hasattr(message, "content") else str(message),
            "role": "assistant",
        }

    def _get_completion_params(
        self, max_tokens: Optional[int] = None, temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Получает параметры для запроса в зависимости от модели"""
        params = {}

        if self.is_gpt5:
            # Для GPT-5 используем специальные параметры
            if max_tokens:
                params["max_completion_tokens"] = max_tokens
            params["reasoning_effort"] = "minimal"
        else:
            # Для обычных моделей
            if max_tokens:
                params["max_tokens"] = max_tokens
            elif self.max_tokens:
                params["max_tokens"] = self.max_tokens

            if temperature is not None:
                params["temperature"] = temperature
            elif self.temperature is not None:
                params["temperature"] = self.temperature

        return params

    async def get_completion(
        self,
        messages: List
    ) -> str:
        response = await self.chat_model.ainvoke(messages)
        return response.content if hasattr(response, 'content') else str(response)
        
    
    
    async def _prepare_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Подготавливает сообщения для отправки в API
        Обрезает контекст если он слишком большой
        """

        # Более точная оценка токенов для русского текста
        def estimate_message_tokens(msg):
            content = msg.get("content", "")
            # Для русского текста: примерно 2.5-3 символа на токен
            return len(content) // 2.5

        total_estimated_tokens = sum(estimate_message_tokens(msg) for msg in messages)
        max_input_tokens = self.model_limits["max_input_tokens"]

        if total_estimated_tokens <= max_input_tokens:
            return messages

        logger.info(
            f"Контекст слишком большой ({int(total_estimated_tokens)} токенов), обрезаем до {max_input_tokens}"
        )

        # Сохраняем системные сообщения
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        other_messages = [msg for msg in messages if msg.get("role") != "system"]

        # Рассчитываем токены системных сообщений
        system_tokens = sum(estimate_message_tokens(msg) for msg in system_messages)
        available_tokens = max_input_tokens - system_tokens

        if available_tokens <= 0:
            logger.warning("Системные сообщения занимают весь доступный контекст")
            return system_messages

        # Берем последние сообщения, помещающиеся в доступные токены
        current_tokens = 0
        trimmed_messages = []

        for msg in reversed(other_messages):
            msg_tokens = estimate_message_tokens(msg)
            if current_tokens + msg_tokens > available_tokens:
                break
            trimmed_messages.insert(0, msg)
            current_tokens += msg_tokens

        result_messages = system_messages + trimmed_messages
        logger.info(
            f"Контекст обрезан до {len(result_messages)} сообщений (~{int(current_tokens + system_tokens)} токенов)"
        )

        return result_messages

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Анализирует настроение и намерения сообщения

        Args:
            text: Текст для анализа

        Returns:
            Словарь с результатами анализа
        """
        analysis_prompt = f"""
        Проанализируй следующее сообщение пользователя и определи:
        1. Настроение (позитивное/нейтральное/негативное)
        2. Уровень заинтересованности (1-10)
        3. Готовность к покупке (1-10)
        4. Основные возражения или вопросы
        5. Рекомендуемая стратегия ответа
        
        Сообщение: "{text}"
        
        Ответь в формате JSON:
        {{
            "sentiment": "positive/neutral/negative",
            "interest_level": 1-10,
            "purchase_readiness": 1-10,
            "objections": ["список возражений"],
            "key_questions": ["ключевые вопросы"],
            "response_strategy": "рекомендуемая стратегия"
        }}
        """

        try:
            # Для анализа настроения используем более низкую температуру если поддерживается
            temp = 0.3 if not self.is_gpt5 else None

            response = await self.get_completion(
                [
                    {
                        "role": "system",
                        "content": "Ты эксперт по анализу намерений клиентов в продажах.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=temp,
            )

            # Пытаемся распарсить JSON
            return json.loads(response)

        except Exception as e:
            logger.error(f"Ошибка при анализе настроения: {e}")
            # Возвращаем дефолтные значения
            return {
                "sentiment": "neutral",
                "interest_level": 5,
                "purchase_readiness": 5,
                "objections": [],
                "key_questions": [],
                "response_strategy": "continue_conversation",
            }

    async def generate_follow_up(
        self, conversation_history: List[Dict[str, str]], analysis: Dict[str, Any]
    ) -> str:
        """
        Генерирует персонализированное продолжение разговора

        Args:
            conversation_history: История разговора
            analysis: Результат анализа последнего сообщения

        Returns:
            Персонализированный ответ
        """
        strategy_prompt = f"""
        На основе анализа сообщения клиента:
        - Настроение: {analysis['sentiment']}
        - Уровень заинтересованности: {analysis['interest_level']}/10
        - Готовность к покупке: {analysis['purchase_readiness']}/10
        - Возражения: {analysis['objections']}
        - Стратегия: {analysis['response_strategy']}
        
        Сгенерируй персонализированный ответ, который:
        1. Учитывает текущее настроение клиента
        2. Отвечает на его ключевые вопросы и возражения
        3. Мягко направляет к следующему этапу воронки продаж
        4. Сохраняет доверительный тон общения
        """

        messages = conversation_history + [
            {"role": "system", "content": strategy_prompt}
        ]

        # Для творческих задач используем более высокую температуру если поддерживается
        temp = 0.8 if not self.is_gpt5 else None

        return await self.get_completion(messages, temperature=temp)

    async def check_api_health(self) -> bool:
        """Проверяет доступность OpenAI API"""
        try:
            test_messages = [{"role": "user", "content": "Привет"}]
            await self.get_completion(test_messages, max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"OpenAI API недоступен: {e}")
            return False

    def estimate_tokens(self, text: str) -> int:
        """Более точная оценка количества токенов в тексте"""
        # Для русского текста: примерно 2.5-3 символа на токен
        return int(len(text) / 2.5)

    async def get_available_models(self) -> List[str]:
        """Получает список доступных моделей"""
        # LangChain не предоставляет прямой доступ к списку моделей
        # Возвращаем стандартный список моделей OpenAI
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-5-mini",
            "gpt-5",
        ]

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Распознает голосовое сообщение через Whisper API
        
        Примечание: LangChain не предоставляет прямой доступ к Whisper API.
        Для транскрибации рекомендуется использовать прямой OpenAI клиент.

        Args:
            audio_file_path: Путь к аудио файлу

        Returns:
            Распознанный текст
        """
        logger.warning(
            "❌ Транскрибация аудио не поддерживается через LangChain. Используйте прямой OpenAI клиент."
        )
        return ""
