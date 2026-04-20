from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.finances import (
    constants as finance_constants,
)


class MindsetFinanceIdea(BaseIdea):
    """
    Idea model for financial mindset transformation stories.
    """
    IDEA_PROMPT = finance_constants.IDEA_PROMPT_MINDSET
    financial_problem: str
    mindset_shift: str
    key_principle: str


class StrategyFinanceIdea(BaseIdea):
    """
    Idea model for practical financial strategy videos.
    """
    IDEA_PROMPT = finance_constants.IDEA_PROMPT_ESTRATEGIA
    strategy_name: str
    common_mistake: str
    actionable_tip: str


class FinancesHandler(CategoryHandler):
    """
    Specialized handler for Finance-themed short videos.
    Encapsulates Mindset and Strategy finance variants.
    """

    SCRIPT_PROMPT = finance_constants.SCRIPT_PROMPT
    idea_variants = [
        MindsetFinanceIdea,
        StrategyFinanceIdea,
    ]
