import csv
import os
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init()

def check_progress():
    csv_path = 'flows/image_content_generator/out_short/ideas_tracking.csv'
    base_dir = Path('flows/image_content_generator/out_short/ideas')
    if not os.path.exists(csv_path):
        print("No se encontro el archivo de seguimiento.")
        return

    print(f"\n{'='*60}")
    print(f"MONITOR DE PRODUCCION - ECO DEL COLAPSO")
    print(f"{'='*60}\n")
    
    states_colors = {
        'COMPLETED': Fore.GREEN,
        'UPLOADED_TO_DRIVE': Fore.GREEN,
        'METADATA_GENERATED': Fore.BLUE,
        'VIDEO_MUSIC_GENERATED': Fore.BLUE,
        'VIDEO_SUBTITLED': Fore.YELLOW,
        'VIDEO_GENERATED': Fore.YELLOW,
        'AUDIO_GENERATED': Fore.YELLOW,
        'VIDEOS_GENERATED': Fore.MAGENTA,
        'IMAGES_GENERATED': Fore.MAGENTA,
        'SCRIPT_GENERATED': Fore.CYAN,
        'NEW': Fore.WHITE,
    }

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ideas = list(reader)

        # Totales
        total = len(ideas)
        completed_ideas = [i for i in ideas if i['state'] in ['COMPLETED', 'UPLOADED_TO_DRIVE']]
        completed = len(completed_ideas)
        in_progress_ideas = [i for i in ideas if i['state'] not in ['COMPLETED', 'UPLOADED_TO_DRIVE', 'NEW']]
        in_progress = len(in_progress_ideas)
        pending = len([i for i in ideas if i['state'] == 'NEW'])

        print(f"Resumen: {Fore.GREEN}{completed} Listos{Style.RESET_ALL} | {Fore.YELLOW}{in_progress} En proceso{Style.RESET_ALL} | {Fore.WHITE}{pending} Pendientes{Style.RESET_ALL}\n")

        print(f"{'ID':<4} | {'ESTADO':<25} | {'PROGRESO':<10} | {'TITULO'}")
        print("-" * 75)

        for idea in ideas:
            state = idea['state']
            color = states_colors.get(state, Fore.WHITE)
            
            # Calcular porcentaje para los que están en proceso
            progress_str = "---"
            if state == 'COMPLETED' or state == 'UPLOADED_TO_DRIVE':
                progress_str = "100%"
            elif state == 'NEW':
                progress_str = "0%"
            else:
                # Contar archivos para estimar %
                idea_id = int(idea['id'])
                folder = base_dir / f"idea_{idea_id:06d}"
                
                img_count = len(list((folder / "images").glob("*.png"))) if (folder / "images").exists() else 0
                vid_count = len(list((folder / "videos").glob("*.mp4"))) if (folder / "videos").exists() else 0
                
                # Cada video tiene 12 escenas. 
                # El proceso es: Script(10%) -> Imagenes(40%) -> Videos(40%) -> Edicion(10%)
                total_pct = 0
                if state == 'SCRIPT_GENERATED': total_pct = 10 + (img_count / 12 * 30)
                elif state == 'IMAGES_GENERATED': total_pct = 40 + (vid_count / 12 * 40)
                elif state in ['VIDEOS_GENERATED', 'AUDIO_GENERATED', 'VIDEO_SUBTITLED', 'VIDEO_MUSIC_GENERATED', 'METADATA_GENERATED']:
                    total_pct = 80 + 15 # Casi listo
                
                progress_str = f"{min(99, int(total_pct))}%"

            # Solo mostrar si no está completado o si es uno de los recientes
            if state != 'COMPLETED' or int(idea['id']) > total - 5:
                print(f"{idea['id']:<4} | {color}{state:<25}{Style.RESET_ALL} | {progress_str:<10} | {idea['title']}")

    except Exception as e:
        print(f"Error leyendo el progreso: {e}")

    print(f"\n{Fore.BLACK}{Style.BRIGHT}Actualizado: {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

if __name__ == "__main__":
    check_progress()
