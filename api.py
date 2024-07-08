from openai import OpenAI, AsyncOpenAI

from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_assistant_response(question: str) -> str:
    """Получает ответ от OpenAI Assistant API на заданный вопрос."""
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Или другая подходящая модель Assistant API
                                              messages=[
                                                  {"role": "user", "content": question}
                                              ],
                                              temperature=0.7,
                                              # Уровень креативности (0 - минимальный, 1 - максимальный)
                                              max_tokens=1000)
    return response.choices[0].message.content
