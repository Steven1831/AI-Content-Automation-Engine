
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from flows.image_content_generator.pipeline.pipeline import Pipeline
from flows.image_content_generator.pipeline.schemas import VideoOrientation

RESOURCE_BASE = Path("flows/image_content_generator/resource")
SHORT_OUT_BASE = Path("flows/image_content_generator/out_short")

pipeline = Pipeline(
    out_base=SHORT_OUT_BASE,
    resource_base=RESOURCE_BASE,
    orientation=VideoOrientation.SHORT
)

print('=== ANALISIS DE FILTRO: ECO DEL COLAPSO (SQLITE) ===\n')

def print_group(title, state_list):
    # Use the new store
    all_ideas = pipeline.store.get_all()
    group = [i for i in all_ideas if i.state.value in state_list]
    
    print(f'{title} ({len(group)}):')
    for row in group:
        print(f'   - ID {row.id}: {row.title}')
    print('')

print_group('[X] TOTALMENTE LISTOS (Drive + YouTube)', ['COMPLETED'])
print_group('[A] ARCHIVADOS (Espacio Liberado)', ['ARCHIVED'])
print_group('[D] SOLO EN DRIVE (Pendiente YouTube)', ['UPLOADED_TO_DRIVE'])
print_group('[Y] SOLO PROGRAMADOS (Pendiente Renombrar)', ['PUBLISHED_TO_YOUTUBE'])
print_group('[P] EN LA FÁBRICA (Producción)', ['METADATA_GENERATED', 'VIDEO_MUSIC_GENERATED', 'VIDEO_SUBTITLED', 'VIDEO_GENERATED', 'AUDIO_GENERATED', 'VIDEOS_GENERATED', 'IMAGES_GENERATED', 'SCRIPT_GENERATED'])
print_group('[N] NUEVAS IDEAS', ['NEW'])
