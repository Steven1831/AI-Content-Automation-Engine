from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_longs.finances import (
    constants as finance_long_constants,
)


class MindsetFinanceIdeaLong(BaseIdea):
    """
    Deep idea model for long-form financial mindset transformation stories.
    """
    IDEA_PROMPT = finance_long_constants.IDEA_PROMPT_MINDSET
    financial_problem: str
    mindset_shift: str
    key_principle: str


class StrategyFinanceIdeaLong(BaseIdea):
    """
    Deep idea model for long-form practical financial strategy videos.
    """
    IDEA_PROMPT = finance_long_constants.IDEA_PROMPT_ESTRATEGIA
    strategy_name: str
    common_mistake: str
    actionable_tip: str


class FinancesHandlerLong(CategoryHandler):
    """
    Specialized handler for Long Finance-themed videos.
    Encapsulates Mindset and Strategy finance variants for 10-minute content.
    """

    SCRIPT_PROMPT = finance_long_constants.SCRIPT_PROMPT
    idea_variants = [
        MindsetFinanceIdeaLong,
        StrategyFinanceIdeaLong,
    ]
