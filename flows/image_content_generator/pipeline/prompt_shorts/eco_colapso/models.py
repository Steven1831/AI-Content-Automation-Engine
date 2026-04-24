from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.eco_colapso import (
    constants as eco_constants,
)


class FragilityCollapseIdea(BaseIdea):
    """
    Idea model for stories exposing the fragility of modern systems.
    """
    IDEA_PROMPT = eco_constants.IDEA_PROMPT_FRAGILIDAD
    system_at_risk: str
    collapse_trigger: str
    visceral_consequence: str


class NormalityBiasIdea(BaseIdea):
    """
    Idea model for stories contrasting current comfort with imminent collapse.
    """
    IDEA_PROMPT = eco_constants.IDEA_PROMPT_NORMALIDAD
    current_comfort: str
    hidden_reality: str
    call_to_awareness: str


class EcoColapsoHandler(CategoryHandler):
    """
    Specialized handler for "Eco del Colapso" themed short videos.
    Encapsulates Fragility and Normality Bias variants.
    """

    SCRIPT_PROMPT = eco_constants.SCRIPT_PROMPT
    idea_variants = [
        FragilityCollapseIdea,
        NormalityBiasIdea,
    ]
