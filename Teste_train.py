#!/usr/bin/env python3
"""
Visualizador 3D com Simulador de Trem de Minério
Carrega arquivo UPL + simula trem passando pelos pontos
Menu visual para seleção de trem dentro da aplicação
"""

import os
import glfw
from OpenGL.GL import *
from core.application import Viewer3DApplication
from utils.ore_train_simulator import OreTrainSimulator
from renderers.train_renderer import TrainRenderer
from ui.train_selector_menu import TrainSelectorMenu
from ui.train_control_panel import TrainControlPanel


def main():
    """Função principal - Inicializa visualizador com trem"""
    
    # Arquivo UPL padrão
    upl_file = "RLT_NE__20250227_00 1.upl"
    
    print("\n" + "="*70)
    print("[INICIAR] VISUALIZADOR 3D COM SIMULADOR DE TREM DE MINÉRIO")
    print("="*70)
    print(f"\n[INFO] Arquivo UPL: {upl_file}")
    
    # Valores iniciais
    train_model = 'ES43'
    num_vagons = 30
    
    # Cria aplicação
    print("\n[APP] Inicializando visualizador 3D...")
    app = Viewer3DApplication()
    
    # Cria menu de seleção de trem
    train_menu = TrainSelectorMenu(app.width, app.height, app.font)
    
    # Cria painel de controle
    control_panel = TrainControlPanel(app.width, app.height, app.font)
    
    # Carrega arquivo UPL
    if os.path.exists(upl_file):
        print(f"[LOAD] Carregando arquivo UPL...")
        app.load_file(upl_file)
        print(f"[OK] Arquivo carregado!")
    else:
        print(f"[AVISO] Arquivo {upl_file} não encontrado")
        print(f"[INFO] Continuando com visualizador vazio")
    
    # Cria simulador de trem com modelo selecionado
    print(f"\n[TREM] Criando simulador de trem...")
    ore_train = OreTrainSimulator(train_model_name=train_model, num_ore_cars=num_vagons)
    ore_train_renderer = TrainRenderer(ore_train)
    ore_train_renderer._update_vbo_data()
    
    # Estado
    show_train = True
    show_cloud = True
    train_paused = False
    original_velocity = ore_train.get_velocity()
    current_model = train_model
    current_vagons = num_vagons
    
    print(f"\n[CONTROLES]")
    print(f"  Clique nos botões no canto inferior direito para controlar o trem")
    print(f"  ESC            - Sair")
    
    # Callbacks do painel de controle
    def on_toggle_train():
        nonlocal show_train
        show_train = not show_train
        control_panel.set_button_state('toggle_train', show_train)
        print(f"[TREM] {'Visível' if show_train else 'Oculto'}")
    
    def on_toggle_cloud():
        nonlocal show_cloud
        show_cloud = not show_cloud
        control_panel.set_button_state('toggle_cloud', show_cloud)
        print(f"[NUVEM] {'Visível' if show_cloud else 'Oculto'}")
    
    def on_menu():
        train_menu.open()
    
    def on_pause():
        nonlocal train_paused, original_velocity
        train_paused = not train_paused
        control_panel.set_button_state('pause', train_paused)
        if train_paused:
            original_velocity = ore_train.get_velocity()
            ore_train.set_velocity(0)
            print(f"[PAUSA] Trem pausado")
        else:
            ore_train.set_velocity(original_velocity)
            print(f"[RETOMA] Trem retomado")
    
    def on_reset():
        nonlocal train_paused, original_velocity
        ore_train.reset()
        train_paused = False
        control_panel.set_button_state('pause', False)
        ore_train.set_velocity(original_velocity)
        print(f"[RESET] Posição reposicionada")
    
    def on_velocity_change(delta, is_absolute=False):
        nonlocal original_velocity
        if is_absolute:
            ore_train.set_velocity(delta)
            control_panel.set_velocity_display(delta)
            if not train_paused:
                original_velocity = delta
        else:
            new_vel = ore_train.get_velocity() + delta
            new_vel = max(0.01, min(new_vel, 4.5))  # Máximo 4.5
            ore_train.set_velocity(new_vel)
            control_panel.set_velocity_display(new_vel)
            if not train_paused:
                original_velocity = new_vel
        print(f"[VELOCIDADE] {ore_train.get_velocity():.2f}")
    
    def on_y_position_change(y_position):
        ore_train.position_y = y_position
        control_panel.set_y_position_display(y_position)
        print(f"[POSIÇÃO Y] {y_position:.1f}m")
    
    # Configura callbacks do painel
    control_panel.on_toggle_train = on_toggle_train
    control_panel.on_toggle_cloud = on_toggle_cloud
    control_panel.on_menu = on_menu
    control_panel.on_pause = on_pause
    control_panel.on_reset = on_reset
    control_panel.on_velocity_change = on_velocity_change
    control_panel.on_y_position_change = on_y_position_change
    
    # Inicializa display do painel
    control_panel.set_velocity_display(ore_train.get_velocity())
    control_panel.set_y_position_display(ore_train.position_y)
    
    # Callback para quando o menu confirma
    def on_train_selected(model, vagons, y_offset=0.0):
        nonlocal ore_train, ore_train_renderer, current_model, current_vagons
        nonlocal original_velocity, train_paused
        
        print(f"\n[TREM] Trocando para {model} com {vagons} vagões...")
        ore_train = OreTrainSimulator(train_model_name=model, num_ore_cars=vagons)
        
        # Aplica offset Y se fornecido
        if y_offset != 0.0:
            ore_train.position_y = y_offset
            print(f"[POSIÇÃO] Offset Y: {y_offset:.1f}m")
        
        ore_train_renderer = TrainRenderer(ore_train)
        ore_train_renderer._update_vbo_data()
        current_model = model
        current_vagons = vagons
        original_velocity = ore_train.get_velocity()
        train_paused = False
        
        stats = ore_train.get_stats()
        print(f"[OK] Modelo carregado!")
        print(f"  Modelo: {stats['model']}")
        print(f"  Vagões: {stats['ore_cars']}")
        print(f"  Comprimento: {stats['total_length_m']:.1f}m")
        print(f"  Peso: {stats['total_weight_ton']:.0f} ton")
        print(f"  Pontos: {stats['total_points']:,}")
    
    train_menu.on_confirm_callback = on_train_selected
    
    # Abre o menu de seleção no início
    train_menu.open()
    
    # Patch de callback de teclado
    original_key_callback = app._key_callback
    
    def patched_key_callback(window, key, scancode, action, mods):
        # Se menu está ativo, deixa ele processar a entrada
        if train_menu.active:
            if train_menu.handle_key(key, action):
                return
        
        # Passa para o callback original (que trata ESC e outros controles)
        original_key_callback(window, key, scancode, action, mods)
    
    # Patch de renderização
    original_render = app.render
    
    def patched_render():
        nonlocal show_train, show_cloud
        
        # Atualiza e renderiza trem
        ore_train.update(dt=1.0 / 60.0)  # 60 FPS
        ore_train_renderer._update_vbo_data()
        
        # Renderiza cena (com nuvem se ativada)
        from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glPushMatrix, glPopMatrix
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Aplica câmera
        app.camera.apply()
        
        # Renderiza nuvem (se visível)
        if show_cloud and app.config.get_show_axes():
            app.axes_renderer.render()
        
        if show_cloud:
            # Se auto-rotacionar ativo
            if app.auto_rotate_x and hasattr(app.point_renderer, 'vertices') and app.point_renderer.n_vertices > 0:
                try:
                    if app._auto_rotate_center is None:
                        app._auto_rotate_center = app.point_renderer.get_center()
                    center = app._auto_rotate_center
                    glPushMatrix()
                    from OpenGL.GL import glTranslatef, glRotatef
                    glTranslatef(center[0], center[1], center[2])
                    glRotatef(app._auto_rotate_angle_x, 1.0, 0.0, 0.0)
                    glTranslatef(-center[0], -center[1], -center[2])
                    app.point_renderer.render()
                    glPopMatrix()
                except Exception:
                    app.point_renderer.render()
            else:
                app.point_renderer.render()
        
        # Renderiza indicador de eixos
        pitch, yaw = app.camera.get_rotation_matrix()
        app.axis_indicator.render(pitch, yaw)
        
        # Renderiza trem (se visível)
        if show_train:
            ore_train_renderer.render()
        
        # Renderiza UI (se menu aberto)
        if app.show_config_menu:
            app._render_config_menu()
        
        # Renderiza Font Editor
        if app.font_editor.active:
            app.font_editor.render()
        
        # Renderiza menu bar
        try:
            app.menu_bar.render()
        except Exception:
            pass
        
        # Renderiza menu de seleção de trem (tem prioridade)
        if train_menu.active:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, app.width, 0, app.height, -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            train_menu.render()
            
            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
        
        # Renderiza painel de controle (sempre visível quando não há menu)
        if not train_menu.active:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, app.width, 0, app.height, -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            control_panel.render()
            
            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
    
    # Aplica patches
    glfw.set_key_callback(app.window, patched_key_callback)
    app.render = patched_render
    
    # Patch de mouse para o menu
    original_mouse_button_callback = app._mouse_button_callback
    
    def patched_mouse_button_callback(window, button, action, mods):
        if train_menu.active:
            mx, my = glfw.get_cursor_pos(window)
            my_inverted = app.height - my
            train_menu.handle_click(mx, my_inverted)
            return
        
        # Se painel está visível, tenta clicar nele
        if not train_menu.active and button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            mx, my = glfw.get_cursor_pos(window)
            my_inverted = app.height - my
            result = control_panel.handle_click(mx, my_inverted)
            if result:  # Se clicou no painel, não processa mais
                return
        
        original_mouse_button_callback(window, button, action, mods)
    
    # Patch de movimento do mouse para o painel
    original_cursor_pos_callback = app._cursor_pos_callback
    
    def patched_cursor_pos_callback(window, xpos, ypos):
        if not train_menu.active:
            my_inverted = app.height - ypos
            control_panel.update_hover(xpos, my_inverted)
        original_cursor_pos_callback(window, xpos, ypos)
    
    glfw.set_mouse_button_callback(app.window, patched_mouse_button_callback)
    glfw.set_cursor_pos_callback(app.window, patched_cursor_pos_callback)
    
    # Mostra estatísticas
    stats = ore_train.get_stats()
    print(f"\n[ESTATÍSTICAS DO TREM]")
    print(f"  Modelo: {stats['model']}")
    print(f"  Vagões: {stats['ore_cars']}")
    print(f"  Comprimento: {stats['total_length_m']:.1f}m")
    print(f"  Peso: {stats['total_weight_ton']:.0f} ton")
    print(f"  Pontos: {stats['total_points']:,}")
    
    print(f"\n[EXECUTAR] Clique na janela para começar...")
    print("="*70 + "\n")
    
    # Executa aplicação
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[CANCELADO] Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[FINALIZADO] Obrigado por usar o visualizador!")


if __name__ == "__main__":
    main()