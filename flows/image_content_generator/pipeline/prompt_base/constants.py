# flake8: noqa: E501

# ====================================================================================
# JSON SCHEMAS
# ====================================================================================


CHUNK_INSTRUCTIONS: str = """
---
## 🎬 INSTRUCCIONES DE CONTINUIDAD (MÓDULO DE ESCENAS)
Actualmente estás generando una sección del guion completo.

**RANGO DE ESCENAS:** DEBES generar exactamente las escenas de la **{start_scene} a la {end_scene}**.

**CONTEXTO NARRATIVO ANTERIOR:**
{context}

**REGLA DE HILACIÓN:** Asegúrate de que la transición entre la última escena conocida y la nueva escena ({start_scene}) sea fluida, lógica y mantenga la misma atmósfera cinematográfica. No repitas escenas, solo continúa la historia. Mantén la numeración secuencial.
---
"""

# ====================================================================================
# CORE PROMPTS (IMAGE, AUDIO)
# ====================================================================================

IMAGE_PROMPT: str = """{image_idea}"""

AUDIO_PROMPT: str = """Narra el siguiente guion religioso de forma pausada, solemne y compasiva. Lee todo el texto tal cual aparece, sin omitir ninguna frase:

{audio_text}"""

ALIGNMENT_PROMPT: str = """# 🧠 PROMPT MAESTRO — ALINEAMIENTO DE AUDIO Y TEXTO

Eres un experto en el alineamiento de audio y texto. Tu tarea es identificar los tiempos exactos de inicio y fin para cada escena del guion basándote en los datos de Whisper.

---

## 🔹 DATOS DE WHISPER (Con timestamps)
{whisper_data}

---

## 📝 GUION ORIGINAL (Escenas)
{scenes_data}

---

## 📋 INSTRUCCIONES (CRÍTICAS)
1. Debes devolver exactamente {expected_count} escenas en el JSON.
2. Para cada escena, identifica el tiempo de inicio (`start_time`) y fin (`end_time`) en el audio.
3. El inicio de la escena 1 suele ser 0.000s.
4. El fin de una escena debe coincidir con el inicio de la siguiente.
4. Sé preciso. Ignora pequeñas diferencias de palabras entre el guion y el audio.
5. Responde exclusivamente en formato JSON.

## 📦 FORMATO DE SALIDA (JSON)
Responde exclusivamente con el siguiente esquema JSON:
```json
{{
  "alignments": [
    {{
      "scene_number": 1,
      "start_time": 0.000,
      "end_time": 5.452
    }},
    ...
  ]
}}
```
"""
