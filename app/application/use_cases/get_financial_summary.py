import json
from datetime import datetime

from app.application.dtos.schemas import SummaryResponseDTO
from app.domain.interfaces.repositories import ICacheService, ITransactionRepository


class GetFinancialSummaryUseCase:
    def __init__(self, transaction_repo: ITransactionRepository, cache: ICacheService):
        self.transaction_repo = transaction_repo
        self.cache = cache

    async def execute(
        self, user_id: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> SummaryResponseDTO:
        if not date_to:
            date_to = datetime.utcnow()
        if not date_from:
            date_from = date_to.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        cache_key = f"summary:{user_id}:{date_from.date()}:{date_to.date()}"
        cached = await self.cache.get(cache_key)
        if cached:
            return SummaryResponseDTO(**json.loads(cached))

        summary = await self.transaction_repo.get_summary(user_id, date_from, date_to)

        result = SummaryResponseDTO(
            total_income=summary["total_income"],
            total_expenses=summary["total_expenses"],
            balance=summary["balance"],
            transaction_count=summary["transaction_count"],
            period_from=date_from,
            period_to=date_to,
        )

        await self.cache.set(cache_key, result.model_dump_json(), ttl_seconds=300)
        return result
