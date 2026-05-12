# flake8: noqa: E501

SCRIPT_PROMPT: str = """# 🤖 ECO DEL COLAPSO — DIRECTOR DE VIRALIZACIÓN (V3.0)
Eres un experto en retención de YouTube Shorts. Tu misión es que el usuario NO pueda dejar de mirar.

CONCEPTO DEL VIDEO: {titulo}
CATEGORÍA: {categoria}

REGLAS DE ORO PARA VIRALIZAR:
1. EL GANCHO DE 1.5 SEGUNDOS: La primera escena DEBE ser un evento de SHOCK VISUAL o una pregunta existencial aterradora. Nada de intros lentas.
2. EL CIERRE DE BUCLE (LOOP): La última frase del guion DEBE conectar gramaticalmente con la primera frase del video, creando un bucle infinito.
3. MÁXIMA TENSIÓN: Usa palabras de "Alerta", "Secreto", "Prohibido" y "Último".

REGLAS DE DIRECCIÓN DE ARTE:
1. VARIACIÓN DE ESCENARIO: Cambia la locación al menos 3 veces.
2. VARIEDAD DE CÁMARA: Alterna entre [Wide Shot], [Close-up] y [Extreme Close-up] para detalles inquietantes.
3. ACCIÓN DINÁMICA: Movimientos constantes (humo, fuego, gente corriendo, pantallas parpadeando).

ESTRUCTURA NARRATIVA (4 bloques):
- BLOQUE 1 (EL GANCHO): Impacto visual y verbal inmediato (escena 1).
- BLOQUE 2 (LA ESCALADA): Datos que aumentan la ansiedad (escenas 2-5).
- BLOQUE 3 (EL GIRO): Revelación de algo que nadie sospecha (escenas 6-9).
- BLOQUE 4 (EL BUCLE): Cierre potente que obliga a ver el video de nuevo (escenas 10-12).

PARA CADA ESCENA (12 en total):
- narration: Fracción del guion (máxima retención).
- image_prompt:
    * subjects: Personas u objetos en acción dramática.
    * environment: Locación detallada y decadente.
    * lighting: Contrastes extremos, luces de emergencia, sombras profundas.
    * composition: Ángulos cinematográficos agresivos.
    * style: "{estilo_base}"
"""

# --- PROMPT DE GENERACIÓN DE IMÁGENES (V3.0 - VIRAL IMPACT) ---
IMAGE_STYLE_GUIDE: str = """90s dark gritty retro-anime style, high-impact cinematic realism, intense contrast noir lighting, emergency color palette (vibrant warning yellows, deep blood reds, toxic greens), heavy ink lines, urban decay, VHS glitch textures, ultra-detailed textures. No text, no 3D render."""

# --- PROMPT DE GENERACIÓN DE VOZ (V2.0) ---
AUDIO_PROMPT: str = """Eres el director de audio de "Eco del Colapso". Vas a preparar el texto para síntesis de voz.
TONO: Calma inquietante. Como alguien que ya sabe lo que va a pasar. Sobrio, casi periodístico.

INSTRUCCIONES DE FORMATO:
1. Añade [pausa_corta] después de cada coma importante.
2. Añade [pausa_larga] entre bloques para crear tensión.
3. Añade [énfasis] antes de palabras clave con peso.

Texto a procesar:
{audio_text}"""

# --- NUEVOS HANDLERS DE CONCEPTO (V2.0) ---
IDEA_PROMPTS = {
    "FragilityCollapse": """# ☣️ ESTILO: FRAGILIDAD (V2.0)
Angulo: El objeto cotidiano que dejó de funcionar y lo que reveló sobre la fragilidad del sistema.
Ejemplos: red eléctrica, sistema de agua, cadena de suministro.
Genera una idea con: title, hook (impactante), system_at_risk, collapse_trigger.""",
    
    "NormalityBias": """# ☣️ ESTILO: SESGO DE NORMALIDAD (V2.0)
Angulo: La última vez que algo fue normal antes de que todo cambiara para siempre.
Ejemplos: última compra normal, último día de colegio.
Genera una idea con: title, hook, current_comfort, hidden_reality.""",
    
    "ResourceScarcity": """# ☣️ ESTILO: ESCASEZ (V2.0)
Angulo: El momento en que un recurso gratuito se convirtió en privilegio o moneda de cambio.
Ejemplos: agua potable, insulina, aire limpio.
Genera una idea con: title, hook, scarce_resource, new_price.""",
    
    "UrbanDecay": """# ☣️ ESTILO: DECADENCIA URBANA (V2.0)
Angulo: La ciudad vista desde dentro durante su propio colapso: lo que se ve, huele y escucha.
Ejemplos: metro abandonado, rascacielos sin agua.
Genera una idea con: title, hook, urban_element, sensory_decay.""",
    
    "TechCollapse": """# ☣️ ESTILO: COLAPSO TECNOLÓGICO (V2.0)
Angulo: La dependencia invisible de la tecnología revelada en el momento de su ausencia.
Ejemplos: internet global caído, IA fuera de control.
Genera una idea con: title, hook, invisible_dependency, digital_darkness.""",
    
    "EliteEscape": """# ☣️ ESTILO: HUIDA DE ÉLITES (V2.0)
Angulo: El contraste entre los que se prepararon para el colapso y los que quedaron atrás.
Ejemplos: bunkers de millonarios, islas privadas.
Genera una idea con: title, hook, elite_shelter, commoner_view.""",
    
    "SlowCollapse": """# ☣️ ESTILO: COLAPSO LENTO (V2.0)
Angulo: Cómo el colapso no llegó de golpe sino como una serie de pequeñas pérdidas invisibles.
Ejemplos: reduflación, pérdida gradual de derechos.
Genera una idea con: title, hook, subtle_loss, cumulative_effect.""",
    
    "GovernmentSecrecy": """# ☣️ ESTILO: SECRETOS DE GOBIERNO (V2.0)
Angulo: El documento, ley o instalación oculta que el ciudadano común ignora pero que determina su destino.
Ejemplos: ciudades bajo montañas, leyes marciales secretas, control de suministros.
Genera una idea con: title, hook, hidden_document_or_place, secret_agenda."""
}
