import json
from pathlib import Path
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.schemas import State

db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
ideas_dir = Path("flows/image_content_generator/out_short/ideas")
store = SqliteStore(db_path)

urgent_videos = [
    {
        "title": "El barco que nadie quiere",
        "category": "UrbanDecayIdea",
        "hook": "Zarpó como un viaje de lujo al fin del mundo. Hoy es una prisión en medio del océano.",
        "narrations": [
            "Zarpó como un viaje de lujo al fin del mundo. Hoy es una prisión en medio del océano.",
            "El MV Hondius no tiene a dónde ir.",
            "Tres pasajeros muertos. Camarotes sellados.",
            "El causante no es un patógeno común...",
            "Es la cepa Andes, la única en el planeta con capacidad documentada para saltar de humano a humano.",
            "Mientras el barco errante pide auxilio, los puertos le cierran sus puertas.",
            "La OMS dice que el riesgo es bajo, pero el silencio en cubierta cuenta otra historia.",
            "Nos acostumbramos a mirar las tragedias a través de una pantalla, creyendo que el océano nos protege.",
            "Pero el aislamiento no es la cura.",
            "Es solo la sala de espera."
        ],
        "prompt": {
            "environment": "Un crucero inmenso, oscuro y fantasmal flotando en un océano negro bajo la luna fría.",
            "lighting": "Luz amarilla de emergencia parpadeando rítmicamente.",
            "composition": "Acercamiento lento a una ventana empañada de un camarote.",
            "style": "90s dark retro anime style, Satoshi Kon style, eerie, isolation, high contrast noir lighting, VHS textures. No text."
        }
    },
    {
        "title": "El mapa de contactos",
        "category": "UrbanDecayIdea",
        "hook": "El problema ya no es el barco. El problema son los que lograron bajarse.",
        "narrations": [
            "El problema ya no es el barco. El problema son los que lograron bajarse.",
            "Antes de que sonaran las alarmas, decenas de pasajeros aparentemente sanos desembarcaron en la remota isla de Santa Elena.",
            "Caminaron por aeropuertos.",
            "Tomaron vuelos internacionales cruzando hacia Johannesburgo y Ámsterdam.",
            "El virus Andes es paciente; puede incubar en absoluto silencio en tu cuerpo hasta por seis semanas.",
            "Imagina la fragilidad de nuestro tablero moderno...",
            "Un solo viajero, un solo pasaporte, un aeropuerto lleno.",
            "La normalidad es un cristal tan fino...",
            "Que basta una sola tos en una sala de espera para quebrarlo.",
            "El verdadero contagio empieza cuando nadie sabe a dónde fuiste."
        ],
        "prompt": {
            "environment": "El largo pasillo de un aeropuerto internacional bañado en luz fluorescente verdosa y enfermiza.",
            "lighting": "Luz fluorescente verdosa, enfermiza, oscureciendo los rincones.",
            "composition": "Cámara baja, mostrando una maleta abandonada en el centro. Al fondo, silueta borrosa.",
            "style": "90s dark retro anime style, Akira style, urban decay, dystopian realistic, high contrast noir lighting. No text."
        }
    },
    {
        "title": "El escape de Santa Elena",
        "category": "GovernmentSecrecyIdea",
        "hook": "Te piden que mantengas la calma. Pero lo que el comunicado no dijo, es lo que debería aterrarte.",
        "narrations": [
            "Te piden que mantengas la calma. Pero lo que el comunicado no dijo, es lo que debería aterrarte.",
            "Oficialmente, las cifras son pequeñas y el riesgo es bajo.",
            "Pero los operativos en tierra parecen de zona de guerra.",
            "Hospitales preparándose para evacuaciones con aislamiento biológico extremo.",
            "Lo que todavía no se sabe es cómo este crucero zarpó de Ushuaia con controles portuarios anulados.",
            "Cómo decenas desembarcaron tranquilamente en Santa Elena cuando ya llevaban un cadáver a bordo.",
            "No hacen falta conspiraciones.",
            "La simple incompetencia burocrática y los protocolos ciegos son suficientes para apagar una ciudad.",
            "Cuando los mensajes oficiales son de hielo...",
            "El silencio es quien hace las preguntas."
        ],
        "prompt": {
            "environment": "Un puesto de aduanas fronterizo sumido en las sombras. Televisor viejo de tubo (CRT) mostrando estática.",
            "lighting": "Oscuridad total rota solo por el brillo azul y estático del televisor CRT.",
            "composition": "Paneo muy lento hacia un funcionario sin rostro hablando detrás de un escritorio.",
            "style": "90s dark retro anime style, Ghost in the Shell style, cyberpunk documentary realism, muted palette. No text."
        }
    }
]

for video in urgent_videos:
    # 1. Add to SQLite
    idea_obj = store.add_new_idea(video["title"], video["category"])
    
    folder = ideas_dir / f"idea_{idea_obj.id:06d}"
    folder.mkdir(parents=True, exist_ok=True)
    
    # 2. Write idea.json
    idea_data = {
        "title": video["title"],
        "hook": video["hook"]
    }
    with open(folder / "idea.json", "w", encoding="utf-8") as f:
        json.dump(idea_data, f, indent=2, ensure_ascii=False)
        
    # 3. Create script.json bypassing LLM
    scenes = []
    for i, narration in enumerate(video["narrations"]):
        # Add slight variations to composition per scene to keep Veo dynamic
        comps = ["Plano general", "Primer plano", "Plano detalle", "Ángulo holandés", "Plano medio"]
        comp = video["prompt"]["composition"] + f" ({comps[i % len(comps)]})"
        
        scene = {
            "scene_number": i + 1,
            "narration": narration,
            "image_prompt": {
                "subjects": [
                    {
                        "description": "Una figura misteriosa o elemento central de la toma.",
                        "action": "Esperando en el silencio tenso de la escena."
                    }
                ],
                "environment": video["prompt"]["environment"],
                "lighting": video["prompt"]["lighting"],
                "composition": comp,
                "style": video["prompt"]["style"]
            }
        }
        scenes.append(scene)
        
    script_data = {"scenes": scenes}
    with open(folder / "script.json", "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
        
    # 4. Update State to SCRIPT_VALIDATED so it goes straight to Veo image generation
    idea_obj.state = State.SCRIPT_VALIDATED
    store.save(idea_obj)
    
    print(f"URGENT VIDEO INJECTED: ID {idea_obj.id} - {idea_obj.title} (State: SCRIPT_VALIDATED)")
