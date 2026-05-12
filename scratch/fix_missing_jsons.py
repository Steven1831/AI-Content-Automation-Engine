import json
from pathlib import Path
from flows.image_content_generator.pipeline.storage_sqlite import SqliteStore
from flows.image_content_generator.pipeline.prompt_shorts.eco_colapso.models import (
    GovernmentSecrecyIdea, EliteEscapeIdea
)

db_path = Path("flows/image_content_generator/out_short/ideas_tracking.db")
ideas_dir = Path("flows/image_content_generator/out_short/ideas")
store = SqliteStore(db_path)

# Models map
models = {
    "GovernmentSecrecyIdea": GovernmentSecrecyIdea,
    "EliteEscapeIdea": EliteEscapeIdea
}

# Fix IDs 25 to 36
for i in range(25, 37):
    idea_obj = store.get_by_id(i)
    if not idea_obj:
        continue
    
    folder = ideas_dir / f"idea_{i:06d}"
    folder.mkdir(parents=True, exist_ok=True)
    
    model_cls = models.get(idea_obj.category, GovernmentSecrecyIdea)
    
    # Create a basic idea.json that matches the model
    # We use the title as the hook for now, or a generic one
    data = {
        "title": idea_obj.title,
        "hook": f"¡Atención! {idea_obj.title}. Lo que no quieren que sepas."
    }
    
    # Add specific fields based on category
    if idea_obj.category == "GovernmentSecrecyIdea":
        data["hidden_document_or_place"] = "Archivos clasificados nivel 5"
        data["secret_agenda"] = "Control total de la población"
    else:
        data["elite_shelter"] = "Búnker autosuficiente en zona remota"
        data["commoner_view"] = "Desesperación y abandono"

    with open(folder / "idea.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Creado idea.json para ID {i}")
