#!/usr/bin/env python3
"""
Simulador de Trem de Minério com Arquivo UPL
Carrega pontos do arquivo .upl e simula trem de minério passando por eles
"""

import sys
import os
from core.application import Viewer3DApplication
from utils.ore_train_models import list_available_models, create_train_model
from utils.ore_train_simulator import OreTrainSimulator
from renderers.train_renderer import TrainRenderer
import glfw


def list_models():
    """Mostra modelos disponíveis"""
    print("\n" + "="*60)
    print("[MODELOS] TRENS DE MINÉRIO DISPONÍVEIS")
    print("="*60 + "\n")
    
    models = list_available_models()
    for i, model in enumerate(models, 1):
        train = create_train_model(model, 30)
        print(f"{i:2d}. {model:15} - {train.max_speed:3.0f} km/h | "
              f"{train.power_hp:4d} HP | {train.tractive_effort_ton:3.0f}t esforço")
    
    print("\n")
    return models


def select_train_model(models):
    """Permite ao usuário selecionar modelo"""
    while True:
        try:
            choice = input("[ENTRADA] Escolha um modelo (número ou nome): ").strip()
            
            # Tenta por número
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
            
            # Tenta por nome
            if choice in models:
                return choice
            
            # Tenta case-insensitive
            for model in models:
                if model.lower() == choice.lower():
                    return model
            
            print("[ERRO] Modelo não encontrado. Tente novamente.")
        
        except KeyboardInterrupt:
            print("\n[CANCELADO] Cancelado pelo usuário")
            return None
        except Exception as e:
            print(f"[ERRO] {e}")


def get_ore_car_count():
    """Permite ao usuário selecionar número de vagões"""
    print("\n" + "="*60)
    print("[CONFIGURAÇÃO] NÚMERO DE VAGÕES DE MINÉRIO")
    print("="*60)
    print("\nOpções rápidas:")
    print("  1. Leve (15 vagões)")
    print("  2. Médio (30 vagões) - PADRÃO")
    print("  3. Pesado (60 vagões)")
    print("  4. Ultra Pesado (100 vagões)")
    print("  5. Customizado")
    
    while True:
        try:
            choice = input("\n[ENTRADA] Escolha uma opção (1-5) ou quantidade: ").strip()
            
            if choice == '1':
                return 15
            elif choice == '2':
                return 30
            elif choice == '3':
                return 60
            elif choice == '4':
                return 100
            elif choice == '5':
                num = int(input("[ENTRADA] Digite a quantidade de vagões (1-200): "))
                if 1 <= num <= 200:
                    return num
                else:
                    print("[ERRO] Quantidade deve estar entre 1 e 200")
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= 200:
                    return num
                else:
                    print("[ERRO] Quantidade deve estar entre 1 e 200")
            else:
                print("[ERRO] Entrada inválida")
        
        except KeyboardInterrupt:
            print("\n[CANCELADO]")
            return 30  # Padrão
        except Exception as e:
            print(f"[ERRO] {e}")


def main():
    """Função principal"""
    
    print("\n" + "="*70)
    print("  [TREM DE MINÉRIO] SIMULADOR 3D COM PONTOS UPL")
    print("="*70)
    
    # Lista e seleciona modelo
    models = list_models()
    selected_model = select_train_model(models)
    
    if not selected_model:
        print("\n[ERRO] Nenhum modelo selecionado. Abortando.")
        return
    
    # Obtém número de vagões
    num_ore_cars = get_ore_car_count()
    
    # Mostra configuração final
    print(f"\n[CONFIGURAÇÃO FINAL]")
    print(f"  Modelo: {selected_model}")
    print(f"  Vagões: {num_ore_cars}")
    
    train_model = create_train_model(selected_model, num_ore_cars)
    print(f"  Comprimento: {train_model.get_total_length():.1f}m")
    print(f"  Peso: {train_model.get_total_weight():.0f} ton")
    
    # Verifica arquivo UPL
    print("\n" + "="*70)
    print("[ARQUIVO] CARREGANDO DADOS")
    print("="*70)
    
    upl_file = None
    if len(sys.argv) > 1:
        upl_file = sys.argv[1]
        print(f"\n[INFO] Arquivo fornecido: {upl_file}")
    else:
        # Procura arquivo padrão
        default_file = "RLT_NE__20250227_00 1.upl"
        if os.path.exists(default_file):
            upl_file = default_file
            print(f"\n[INFO] Usando arquivo padrão: {default_file}")
        else:
            print(f"\n[AVISO] Nenhum arquivo .upl encontrado.")
            print(f"[INFO] Use: python ore_train_with_upl.py seu_arquivo.upl")
            print(f"\n[INFO] Continuando sem arquivo (apenas trem)")
            upl_file = None
    
    # Cria aplicação
    print("\n[APP] Inicializando visualizador 3D...")
    app = Viewer3DApplication()
    
    # Carrega arquivo UPL se disponível
    if upl_file and os.path.exists(upl_file):
        try:
            print(f"\n[LOAD] Carregando arquivo: {upl_file}")
            app.load_file(upl_file)
            print(f"[OK] Arquivo carregado com sucesso!")
        except Exception as e:
            print(f"[ERRO] Erro ao carregar arquivo: {e}")
    
    # Cria simulador de trem
    print(f"\n[TREM] Criando simulador...")
    ore_train = OreTrainSimulator(train_model_name=selected_model, num_ore_cars=num_ore_cars)
    ore_train_renderer = TrainRenderer(ore_train)
    ore_train_renderer._update_vbo_data()
    
    # Mostra controles
    print("\n" + "="*70)
    print("[CONTROLES]")
    print("="*70)
    print("\nK              - Toggle trem de minério")
    print("L              - Toggle nuvem de pontos UPL")
    print("G              - Toggle grade")
    print("+/-            - Aumenta/diminui velocidade")
    print("SPACE          - Pausa/retoma trem")
    print("R              - Reseta posição")
    print("1-9            - Velocidade predefinida")
    print("ESC            - Sair")
    print("\n" + "="*70)
    
    # Estados
    show_train = True
    show_cloud = True
    show_grid = False
    train_paused = False
    original_velocity = ore_train.get_velocity()
    
    # Patch callbacks
    original_key_callback = app._key_callback
    original_render = app._render_frame
    
    def patched_key_callback(window, key, scancode, action, mods):
        nonlocal show_train, show_cloud, show_grid, train_paused, original_velocity
        
        original_key_callback(window, key, scancode, action, mods)
        
        if action == glfw.PRESS and not app.font_editor.active:
            # K: Toggle trem
            if key == glfw.KEY_K:
                show_train = not show_train
                print(f"[TREM] {'Visível' if show_train else 'Oculto'}")
            
            # L: Toggle nuvem
            elif key == glfw.KEY_L:
                show_cloud = not show_cloud
                print(f"[NUVEM] {'Visível' if show_cloud else 'Oculto'}")
            
            # G: Toggle grade
            elif key == glfw.KEY_G:
                show_grid = not show_grid
                print(f"[GRADE] {'Visível' if show_grid else 'Oculto'}")
            
            # +/-: Velocidade
            elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
                new_vel = ore_train.get_velocity() * 1.2
                ore_train.set_velocity(new_vel)
                print(f"[VELOCIDADE] {new_vel:.2f}")
            
            elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
                new_vel = max(0.01, ore_train.get_velocity() * 0.8)
                ore_train.set_velocity(new_vel)
                print(f"[VELOCIDADE] {new_vel:.2f}")
            
            # Números: Velocidade predefinida
            elif glfw.KEY_1 <= key <= glfw.KEY_9:
                vel_speed = (key - glfw.KEY_0) * 0.1
                ore_train.set_velocity(vel_speed)
                print(f"[VELOCIDADE] {vel_speed:.2f}")
            
            # SPACE: Pausa
            elif key == glfw.KEY_SPACE:
                train_paused = not train_paused
                if train_paused:
                    original_velocity = ore_train.get_velocity()
                    ore_train.set_velocity(0)
                    print(f"[PAUSA] Trem pausado")
                else:
                    ore_train.set_velocity(original_velocity)
                    print(f"[RETOMA] Trem retomado")
            
            # R: Reset
            elif key == glfw.KEY_R:
                ore_train.reset()
                train_paused = False
                ore_train.set_velocity(original_velocity)
                print(f"[RESET] Posição reposicionada")
    
    def patched_render_frame():
        nonlocal show_train, show_cloud, show_grid
        
        # Renderiza nuvem normalmente
        if show_cloud:
            app.point_renderer.render()
        
        # Atualiza e renderiza trem
        ore_train.update(dt=1.0)
        ore_train_renderer._update_vbo_data()
        if show_train:
            ore_train_renderer.render()
        
        # Grade (se implementado)
        if show_grid:
            # Implementar render de grade aqui se necessário
            pass
        
        # Renderiza outros elementos normalmente
        if app.axes_renderer.visible:
            app.axes_renderer.render()
        if app.axis_indicator.visible:
            app.axis_indicator.render(app.camera.pitch, app.camera.yaw)
    
    # Aplica patches
    glfw.set_key_callback(app.window, patched_key_callback)
    app._render_frame = patched_render_frame
    
    # Printa estatísticas
    stats = ore_train.get_stats()
    print(f"\n[ESTATÍSTICAS]")
    print(f"  Pontos do trem: {stats['total_points']:,}")
    print(f"  Comprimento: {stats['total_length_m']:.1f}m")
    print(f"  Peso: {stats['total_weight_ton']:.0f} ton")
    
    # Inicia aplicação
    print(f"\n[INICIAR] Clique na janela e use os controles acima")
    print("="*70 + "\n")
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[CANCELADO] Simulação interrompida")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[FINALIZADO] Obrigado por usar o Simulador de Trem de Minério!")


if __name__ == "__main__":
    main()
