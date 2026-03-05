"""
AI-powered transaction categorizer.

Uses OpenAI to guess the best category for a transaction
based on its description. Falls back gracefully if API key
is missing or the call fails.
"""


from openai import AsyncOpenAI

from app.config import settings
from app.domain.interfaces.repositories import IAICategorizerService
from app.shared.logger import logger


class OpenAICategorizerService(IAICategorizerService):
    def __init__(self) -> None:
        self.client = (
            AsyncOpenAI(api_key=settings.openai_api_key)
            if settings.openai_api_key else None
        )

    async def categorize(
        self, description: str, available_categories: list[dict[str, str]]
    ) -> str | None:
        if not self.client:
            return None

        categories_text = "\n".join(
            f"- {cat['id']}: {cat['name']} ({cat['type']})" for cat in available_categories
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial assistant. Given a transaction description, "
                            "pick the most appropriate category from the list. "
                            "Respond with ONLY the category ID.\n\n"
                            f"Categories:\n{categories_text}"
                        ),
                    },
                    {"role": "user", "content": description},
                ],
                max_tokens=50,
                temperature=0.1,
            )

            category_id = response.choices[0].message.content.strip()
            valid_ids = {cat["id"] for cat in available_categories}
            return category_id if category_id in valid_ids else None

        except Exception as e:
            logger.error("ai_categorization_failed", error=str(e))
            return None

    async def generate_insights(self, transactions: list[dict[str, object]]) -> str:
        if not self.client:
            return "Insights indisponíveis: chave da OpenAI não configurada."

        # Keep context window reasonable
        summary = "\n".join(
            f"- {t.get('description')}: R$ {t.get('amount')} ({t.get('type')}, {t.get('category')})"
            for t in transactions[:50]
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um consultor financeiro pessoal. Analise as transações "
                            "e dê 3-5 dicas práticas e específicas em português. "
                            "Mencione valores e categorias concretas."
                        ),
                    },
                    {"role": "user", "content": f"Minhas transações recentes:\n{summary}"},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error("ai_insights_failed", error=str(e))
            return "Não foi possível gerar insights no momento."
