
from pydantic import BaseModel, Field
from typing import List

class SeoMetadata(BaseModel):
    youtube_title: str = Field(description="Título de máximo 60 caracteres con objeto cotidiano")
    youtube_description: str = Field(description="Descripción con resumen, pregunta y hashtags")
    hashtags: List[str] = Field(description="Lista de exactamente 5 hashtags")
    comentario_fijado: str = Field(description="Pregunta de debate con 2 opciones")
    # Mantener compatibilidad con el resto del pipeline aunque el prompt pida menos
    tiktok_caption: str = ""
    instagram_caption: str = ""
    facebook_caption: str = ""

class SeoPromptManager:
    @staticmethod
    def get_seo_prompt(story_title: str, story_narration: str) -> str:
        return f"""Eres el estratega de contenido de "Eco del Colapso", especializado en YouTube Shorts sobre colapso civilizatorio.

GUION GENERADO:
Título Base: {story_title}
Narración Completa: {story_narration}

Tu tarea es generar los metadatos completos optimizados para YouTube.

REGLAS PARA EL TÍTULO:
1. Máximo 60 caracteres.
2. Debe contener un objeto cotidiano concreto O una situación específica reconocible.
3. Usa alguna de estas estructuras probadas:
   - "El último/a [objeto cotidiano]"
   - "El día que [acción cotidiana] desapareció"
   - "Cuando [cosa normal] se convirtió en [consecuencia distópica]"
   - "[Número] horas antes del [evento de colapso]"
   - "La ciudad que [verbo dramático] en silencio"
4. NUNCA uses títulos abstractos. El título debe funcionar como minihistoria.

REGLAS PARA LA DESCRIPCIÓN:
- Primeras 2 líneas (150 caracteres): resumen del video con palabras clave naturales.
- Línea 3: invitación a comentar con una pregunta específica.
- Línea 4: hashtags.
- Palabras clave: colapso civilizatorio, distopía, supervivencia, anime retro, postapocalíptico, crisis.

REGLAS PARA HASHTAGS:
- Exactamente 5 hashtags.
- Incluir: #EcoDelColapso #DarkAnime y otros 3 rotados.

REGLAS PARA EL COMENTARIO FIJADO:
- Una pregunta que genere debate sobre el tema del video.
- Máximo 2 opciones de respuesta.

Devuelve EXACTAMENTE un JSON con este formato:
{{
  "youtube_title": "texto",
  "youtube_description": "texto",
  "hashtags": ["#tag1", "..."],
  "comentario_fijado": "texto"
}}
"""
