"""
Script para exportar todos os caracteres do VectorFont para char.json
"""

import json
from ui.vector_font import VectorFont

def export_all_chars():
    """Exporta todos os caracteres para char.json"""
    font = VectorFont()
    
    char_data = {}
    
    for char_key, raw_strokes in font.strokes.items():
        segments = []
        
        # Converte strokes para formato simples
        if isinstance(raw_strokes, list):
            # Lista simples de segmentos
            for stroke in raw_strokes:
                if len(stroke) == 4:
                    x1, y1, x2, y2 = stroke
                    segments.append([x1, y1, x2, y2])
        elif isinstance(raw_strokes, tuple):
            # Tupla que pode conter listas aninhadas
            for item in raw_strokes:
                if isinstance(item, tuple) and len(item) == 4:
                    x1, y1, x2, y2 = item
                    segments.append([x1, y1, x2, y2])
        
        char_data[char_key] = segments
    
    # Salva JSON
    with open('char.json', 'w', encoding='utf-8') as f:
        json.dump(char_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportados {len(char_data)} caracteres para char.json")
    
    # Mostra estatísticas
    total_segments = sum(len(segs) for segs in char_data.values())
    print(f"📊 Total de segmentos: {total_segments}")
    print(f"📝 Caracteres: {', '.join(sorted(char_data.keys()))}")

if __name__ == "__main__":
    export_all_chars()
