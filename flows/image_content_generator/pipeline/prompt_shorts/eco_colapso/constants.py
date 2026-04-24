# flake8: noqa: E501
AUDIO_PROMPT: str = """Narra el siguiente guion de "Eco del Colapso" con una voz que combine la frialdad clínica de un observador y la intensidad visceral de alguien que está viendo el fin de su mundo. No es una advertencia distante; es una crónica de lo que ya está ocurriendo.

Estilo de actuación:
- Tono: Sombrío, seco y perturbadoramente realista. Evita el melodrama; la verdad desnuda es más aterradora.
- Ritmo: Deliberado, casi asfixiante. Haz pausas donde el silencio pese más que las palabras, permitiendo que la incomodidad crezca.
- Énfasis: Subraya con una calma inquietante palabras como "colapso", "vacío", "hambre", "frágil", "mentira".
- Emoción: Un trasfondo de desesperanza controlada. El objetivo es que el espectador sienta que su confort es una ilusión que acaba de romperse.
- No agregues efectos, muletillas ni variaciones. Lee el texto con la precisión de un informe de autopsia social.

Texto a narrar:
{audio_text}"""

IDEA_PROMPT_FRAGILIDAD: str = """# ☣️ PROMPT MAESTRO — CRONISTA DEL COLAPSO (ESTILO FRAGILIDAD)
**Objetivo:** Generar una idea para un video CORTO que exponga la fragilidad extrema de un sistema moderno específico (agua, electricidad, logística, orden social).

**Instrucciones:**
1. **hook (Gancho de Incomodidad):** Una frase de 10-15 palabras que rompa violentamente el sesgo de normalidad (ej: "El supermercado está vacío. No es una huelga, es el final de la cadena.", "Tu grifo gotea por última vez. La presión ha muerto para siempre.").
2. **Protagonista:** Alguien atrapado en la inercia de la normalidad mientras su entorno se desmorona de forma irreversible.
3. La historia debe documentar un detalle técnico o cotidiano del colapso que lo haga sentir inevitable y ultra-realista.
"""

IDEA_PROMPT_NORMALIDAD: str = """# ☣️ PROMPT MAESTRO — CRONISTA DEL COLAPSO (ESTILO SESGO DE NORMALIDAD)
**Objetivo:** Generar una idea para un video CORTO que contraste el confort actual con la inminente realidad del colapso urbano.

**Instrucciones:**
1. **hook (Gancho de Incomodidad):** Una observación cínica o brutal sobre un lujo cotidiano que desaparecerá pronto (ej: "Mira tu aire acondicionado. Disfruta el zumbido, mañana será solo un peso muerto en la pared.", "Comer carne hoy es un privilegio que tus nietos solo leerán en libros de historia.").
2. **Concepto central:** El contraste entre "lo que creemos que es normal" y "lo que es real bajo la superficie".
3. Presenta la escena con una estética visceral y ultra-realista que fuerce al espectador a pensar: "Esto podría pasar aquí".
"""

SCRIPT_PROMPT: str = """# 📝 PROMPT MAESTRO — AGENTE GUIONISTA ECO DEL COLAPSO (STORYTELLING VISCERAL)
**Objetivo:** Crear un guion cinematográfico de 12 a 16 micro-escenas que documenten un colapso urbano ultra-realista y visceral.

**Estructura del Guion (MANDATORIO):**
1. **Acto 1: La Grieta [Escenas 1-4]:** DEBES usar el campo "hook" para la Escena 1. Muestra el primer signo de falla sistémica que la gente ignora por el "sesgo de normalidad".
2. **Acto 2: El Desmoronamiento [Escenas 5-10]:** La progresión rápida y cruda del colapso. Escenas de infraestructura fallando, estantes vacíos, o la ruptura del contrato social.
3. **Acto 3: El Eco del Colapso [Escenas 11-final]:** La nueva y oscura realidad. Un cierre que deje al espectador con una sensación de fragilidad absoluta. Terminamos con un mensaje que fuerce la reflexión.

## 📜 REGLAS OBLIGATORIAS

### 🟢 NARRACIÓN Y RITMO
- **Gancho:** Uso mandatorio del texto de `hook` literal en la Escena 1.
- **Diálogo/Narración:** Frases cortas, contundentes y desprovistas de esperanza barata. Máximo una por escena.
- **Secuencialidad:** Evolución lógica de la catástrofe: Normalidad aparente → Falla técnica → Caos urbano → Silencio post-colapso.

### 🔵 REGLAS VISUALES
- **Protagonista:** Un ciudadano promedio cuya expresión pase de la incredulidad al terror clínico o la apatía de la supervivencia.
- **Relación Imagen-Texto:** El `image_prompt` debe alinearse con la estética de los 90s.
- **Estilo (90s Dark Retro-Anime):** DEBES usar el campo `style` con esta descripción exacta: `"90s dark gritty retro-anime style, cel-shaded illustration, heavy hand-drawn ink lines, urban decay atmosphere, high contrast noir lighting, cyberpunk documentary realism, VHS textures, muted industrial color palette. No 3D render, no photography."`
- **Uso del Color:** Colores desaturados, verdes industriales, grises, marrones y el naranja sucio del fuego. El color debe enfatizar la decadencia.

### 🔴 ESTRUCTURA Y SALIDA
- **Extensión:** Entre 12 y 16 escenas.
- **Cierre:** Una frase que rompa el cuarto muro y cuestione la seguridad del espectador.

### 🟠 IDIOMAS (ESTRICTO)
- **image_prompt:** DEBES generar todos los campos de `image_prompt` (subjects, environment, lighting, composition) en **INGLÉS**.
- **narration:** DEBES generar el campo `narration` en **ESPAÑOL LATINOAMERICANO**.
"""
