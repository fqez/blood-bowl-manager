"""Services for rules catalog endpoints."""

from models.base.expensive_mistake import ExpensiveMistakesRules


class RulesService:
    """Rules catalog service."""

    @staticmethod
    async def get_expensive_mistakes_rules() -> ExpensiveMistakesRules | None:
        """Return the expensive mistakes rules document."""
        return await ExpensiveMistakesRules.get("expensive_mistakes")
