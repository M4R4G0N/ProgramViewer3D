#!/usr/bin/env python3
"""
Script de exemplo: Simulação de trem passando por nuvem de pontos
Demonstra como usar o TrainSimulator e TrainRenderer
"""

import sys
from core.application import Viewer3DApplication
from train_viewer import TrainViewer


def run_train_simulation(data_file=None):
    """
    Executa simulação de trem
    
    Args:
        data_file: Arquivo de dados para nuvem de pontos (opcional)
    """
    
    print("\n" + "=" * 60)
    print("🚂 SIMULADOR DE TREM 3D")
    print("=" * 60)
    print()
    
    # Configuração do trem
    train_config = {
        'mode': 'advanced',  # 'basic' ou 'advanced' (com fumaça)
        'num_wagons': 6,
        'wagon_length': 20.0,
        'wagon_width': 8.0,
        'wagon_height': 5.0,
        'points_per_wagon': 800,
        'gap_between_wagons': 3.0,
    }
    
    # Cria aplicação base
    print("📱 Inicializando aplicação 3D...")
    app = Viewer3DApplication()
    
    # Integra trem
    print("🚂 Integrando simulador de trem...")
    train_app = TrainViewer(app, train_config=train_config, data_file=data_file)
    
    # Printa controles
    print("\n" + "=" * 60)
    print("⌨️  CONTROLES")
    print("=" * 60)
    print("K              - Toggle visibilidade do trem")
    print("L              - Toggle visibilidade da nuvem de pontos")
    print("G              - Toggle grade 3D")
    print("+/-            - Aumenta/diminui velocidade do trem")
    print("SPACE          - Pausa/retoma trem")
    print("R              - Reseta posição do trem")
    print()
    print("Mouse LEFT     - Rotaciona câmera")
    print("Mouse RIGHT    - Pam/zoom da câmera")
    print("Scroll         - Zoom")
    print()
    print("ESC            - Sair")
    print("=" * 60)
    print()
    
    # Printa configuração
    print("⚙️  CONFIGURAÇÃO DO TREM")
    print("=" * 60)
    print(f"Modo: {train_config['mode']}")
    print(f"Vagões: {train_config['num_wagons']}")
    print(f"Dimensões: {train_config['wagon_width']:.1f}m x {train_config['wagon_height']:.1f}m x {train_config['wagon_length']:.1f}m")
    print(f"Pontos por vagão: {train_config['points_per_wagon']:,}")
    print("=" * 60)
    print()
    
    # Patch do loop principal para incluir controles do trem
    original_key_callback = app._key_callback
    
    def patched_key_callback(window, key, scancode, action, mods):
        # Trata primeiro com callback original
        original_key_callback(window, key, scancode, action, mods)
        
        # Se não está em modo editor, trata trem
        if action == glfw.PRESS and not app.font_editor.active:
            train_app.handle_train_key_input(key)
    
    # Substitui callback
    import glfw
    glfw.set_key_callback(app.window, patched_key_callback)
    
    # Patch do render para incluir trem
    original_render_frame = app._render_frame
    
    def patched_render_frame():
        # Atualiza trem
        train_app.update(dt=1.0)
        
        # Renderiza normalmente
        original_render_frame()
        
        # Renderiza trem
        train_app.render()
    
    # Substitui render
    app._render_frame = patched_render_frame
    
    # Executa aplicação
    print("🎬 Iniciando simulação...")
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n⏹️  Simulação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante simulação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n✅ Simulação finalizada")


def main():
    """Função principal"""
    
    # Verifica argumentos
    data_file = None
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        print(f"📂 Será carregado arquivo: {data_file}")
    else:
        print("💡 Dica: forneça um arquivo de dados como argumento")
        print("   Exemplos:")
        print("   python train_simulation.py data.pts")
        print("   python train_simulation.py clouds/test_helix.pts")
        print()
    
    # Executa simulação
    run_train_simulation(data_file)


if __name__ == "__main__":
    main()
