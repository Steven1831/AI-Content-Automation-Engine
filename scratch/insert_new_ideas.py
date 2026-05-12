from pathlib import Path
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.schemas import State

db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
store = SqliteStore(db_path)

new_ideas = [
    ("Lo que no te dijeron sobre la ciudad bajo la montaña", "GovernmentSecrecyIdea"),
    ("El documento que nadie leyó y suspende tu libertad", "GovernmentSecrecyIdea"),
    ("Mientras dormías, ellos escondieron las medicinas", "GovernmentSecrecyIdea"),
    ("El plan secreto de militarizar la lluvia y el agua", "GovernmentSecrecyIdea"),
    ("Mientras dormías, ellos blindaron sus zonas seguras", "EliteEscapeIdea"),
    ("Lo que no te dijeron sobre el gobierno en la sombra", "GovernmentSecrecyIdea"),
    ("El documento que nadie leyó sobre arrestos masivos", "GovernmentSecrecyIdea"),
    ("El plan secreto de expropiar toda el agua potable", "GovernmentSecrecyIdea"),
    ("Lo que no te dijeron sobre el control de tu comida", "GovernmentSecrecyIdea"),
    ("El plan secreto de esconder millones en un búnker", "EliteEscapeIdea"),
    ("El documento que nadie leyó para censurar tu red", "GovernmentSecrecyIdea"),
    ("Mientras dormías, ellos ocultaron el próximo virus", "GovernmentSecrecyIdea"),
]

for title, category in new_ideas:
    idea = store.add_new_idea(title, category)
    print(f"Añadida idea ID {idea.id}: {idea.title} ({category})")
