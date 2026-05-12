from typing import Any, Type, TypeVar

from pydantic import BaseModel

from tools.common.gemini_base import GeminiBase

T = TypeVar("T", bound=BaseModel)


class GeminiTextGenerator(GeminiBase):
    text_model: str = "gemini-3.1-flash-lite-preview"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def generate_text(self, prompt: str, schema: Type[T]) -> T:
        """
        Generates content with Gemini and parses it into a Pydantic model.
        Forces removal of 'additionalProperties' for API compatibility.
        """
        def clean_schema(s: dict):
            if not isinstance(s, dict):
                return
            s.pop("additionalProperties", None)
            s.pop("additional_properties", None) # Some SDK versions use this
            for v in s.values():
                if isinstance(v, dict):
                    clean_schema(v)
                elif isinstance(v, list):
                    for item in v:
                        clean_schema(item)

        # Generate schema and clean it
        raw_schema = schema.model_json_schema()
        clean_schema(raw_schema)

        response = self.client.models.generate_content(
            model=self.text_model,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': raw_schema,
            }
        )
        self._extract_usage(response, self.text_model)

        if not response.text:
            raise RuntimeError("❌ No hay respuesta de Gemini")

        return schema.model_validate_json(response.text)
