
from typing import ClassVar
from pydantic import Field
from flows.image_content_generator.pipeline.prompt_base.models import BaseIdea, CategoryHandler
from flows.image_content_generator.pipeline.prompt_shorts.eco_colapso import (
    constants as eco_constants,
)

class FragilityCollapseIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["FragilityCollapse"]
    system_at_risk: str = Field(description="El sistema específico que falla")
    collapse_trigger: str = Field(description="El evento pequeño que dispara el colapso")

class NormalityBiasIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["NormalityBias"]
    current_comfort: str = Field(description="El lujo cotidiano que damos por sentado")
    hidden_reality: str = Field(description="La verdad brutal bajo la superficie")

class ResourceScarcityIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["ResourceScarcity"]
    scarce_resource: str = Field(description="El recurso básico que desaparece")
    new_price: str = Field(description="El nuevo y oscuro precio de conseguirlo")

class UrbanDecayIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["UrbanDecay"]
    urban_element: str = Field(description="Elemento de la ciudad en ruinas")
    sensory_decay: str = Field(description="Detalle sensorial (olor, sonido) de la decadencia")

class TechCollapseIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["TechCollapse"]
    invisible_dependency: str = Field(description="La tecnología de la que dependemos sin saberlo")
    digital_darkness: str = Field(description="Cómo se ve el mundo sin esa conexión")

class EliteEscapeIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["EliteEscape"]
    elite_shelter: str = Field(description="El refugio exclusivo de los poderosos")
    commoner_view: str = Field(description="Cómo lo ven los que se quedaron fuera")

class SlowCollapseIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["SlowCollapse"]
    subtle_loss: str = Field(description="La pequeña pérdida que nadie notó")
    cumulative_effect: str = Field(description="En qué se convirtió esa pérdida después de un tiempo")

class GovernmentSecrecyIdea(BaseIdea):
    IDEA_PROMPT: ClassVar[str] = eco_constants.IDEA_PROMPTS["GovernmentSecrecy"]
    hidden_document_or_place: str = Field(description="El archivo, ley o búnker secreto")
    secret_agenda: str = Field(description="La verdadera intención oculta del gobierno")

class EcoColapsoHandler(CategoryHandler):
    """
    Specialized handler for "Eco del Colapso" themed short videos.
    V2.0 - 7 thematic variants.
    """
    SCRIPT_PROMPT: ClassVar[str] = eco_constants.SCRIPT_PROMPT
    idea_variants = [
        FragilityCollapseIdea,
        NormalityBiasIdea,
        ResourceScarcityIdea,
        UrbanDecayIdea,
        TechCollapseIdea,
        EliteEscapeIdea,
        SlowCollapseIdea,
        GovernmentSecrecyIdea,
    ]
    @classmethod
    def get_full_script_prompt(cls, selected_idea_data: BaseIdea) -> str:
        # Get base prompt from parent
        base_prompt = super().get_full_script_prompt(selected_idea_data)
        # Replace the style placeholder
        return base_prompt.replace("{estilo_base}", eco_constants.IMAGE_STYLE_GUIDE)
