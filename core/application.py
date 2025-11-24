"""
Aplicação principal de visualização 3D
Integra todos os componentes: câmera, renderizadores, UI, carregadores
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

from core.camera import Camera3D
from core.configuration import Configuration
from renderers.point_cloud import PointCloudRenderer, AxesRenderer, AxisIndicator
from loaders.data_loader import DataLoaderFactory
from ui.vector_font import VectorFont
from ui.components import Panel, ColorButton, ToggleButton, Slider, Button
from ui.font_editor import FontEditor
from ui.menu_bar import MenuBar
from ui.train_control_panel import TrainControlPanel
from ui.train_selector_menu import TrainSelectorMenu


class Viewer3DApplication:
    """
    Aplicação principal de visualização 3D
    Orquestra todos os componentes do sistema
    """
    
    def __init__(self, config_file="config.json"):
        """
        Inicializa a aplicação
        
        Args:
            config_file: Arquivo de configuração
        """
        # Configuração
        self.config = Configuration(config_file)
        
        # Inicializa GLFW
        if not glfw.init():
            raise RuntimeError("Falha ao inicializar GLFW")
        
        # Cria janela
        window_params = self.config.get_window_params()
        self.width = window_params["width"]
        self.height = window_params["height"]
        self.title = window_params["title"]
        
        glfw.window_hint(glfw.SAMPLES, 4 if self.config.get("enable_antialiasing") else 0)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Falha ao criar janela GLFW")
        
        glfw.make_context_current(self.window)
        
        # Habilita VSync para melhor experiência visual
        glfw.swap_interval(1)
        
        # Componentes principais
        cam_params = self.config.get_camera_params()
        self.camera = Camera3D(
            distance=cam_params["distance"],
            pitch=cam_params["pitch"],
            yaw=cam_params["yaw"]
        )
        
        self.point_renderer = PointCloudRenderer()
        self.axes_renderer = AxesRenderer()
        self.axis_indicator = AxisIndicator(self.width, self.height)
        self.font = VectorFont()
        self.data_loader = DataLoaderFactory()
        
        # Estado da UI
        self.show_config_menu = False
        self.config_panel = None
        self.ui_components = []
        
        # Font Editor
        self.font_editor = FontEditor(self.width, self.height)
        
        # Menu Bar
        self.menu_bar = MenuBar(self.width, self.height)
        
        # Inicializa lista de arquivos recentes no menu
        self.menu_bar.update_recent_files(self.config.get_recent_files())
        
        # Train Control Panel
        self.control_panel = TrainControlPanel(self.width, self.height, self.font)
        self.control_panel.visible = False  # Inicialmente oculto
        
        # Callbacks do painel de controle
        self.control_panel.on_menu = lambda: self.train_selector.open()
        self.control_panel.on_toggle_train = lambda: print("🚂 Toggle Trem")
        self.control_panel.on_toggle_cloud = lambda: print("☁️  Toggle Nuvem")
        self.control_panel.on_pause = lambda: print("⏸️  Pause")
        self.control_panel.on_reset = lambda: print("🔄 Reset")
        self.control_panel.on_velocity_change = lambda v, is_absolute=False: print(f"⚡ Velocidade: {v}")
        self.control_panel.on_y_position_change = lambda y: print(f"↕️  Posição Y: {y}")
        
        # Train Selector Menu
        self.train_selector = TrainSelectorMenu(self.width, self.height, self.font)
        self.train_selector.on_confirm_callback = self._on_train_selected
        self.train_selector.on_cancel_callback = self._on_train_selector_cancel
        
        # Auto-rotation (runtime only, not salvo)
        self.auto_rotate_x = False
        self._auto_rotate_angle_x = 0.0  # graus
        self._rotation_speed_deg = 30.0  # deg/s padrão
        self._last_frame_time = glfw.get_time()
        self._auto_rotate_center = None  # Cache do centro para auto-rotação
        # Show all points (toggle LOD)
        self.show_all_points = False
        
        # FPS counter
        self._fps_counter = 0
        self._fps_last_time = glfw.get_time()
        self._current_fps = 0
        
        # Estado do mouse
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.left_mouse_x = 0
        self.left_mouse_y = 0
        self.left_drag = False
        self.right_drag = False
        self.ctrl_pressed = False
        
        # Arquivo carregado
        self.current_file = None
        
        # Registra callbacks
        self._register_callbacks()
        
        # Inicializa OpenGL
        self._init_opengl()
        
        # Cria UI
        self._create_config_menu()
        
        print("✅ Aplicação inicializada com sucesso!")
    
    def _init_opengl(self):
        """Configura estado inicial do OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        
        # Otimizações de desempenho
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_FASTEST)
        glDisable(GL_LIGHTING)  # Não usa iluminação, economiza processamento
        glDisable(GL_TEXTURE_2D)  # Sem texturas
        glShadeModel(GL_FLAT)  # Shading plano é mais rápido
        
        bg_color = self.config.get_background_color()
        glClearColor(*bg_color)
        
        point_size = self.config.get_point_size()
        self.point_renderer.set_point_size(point_size)
        
        # Configura projeção
        self._resize_viewport(self.width, self.height)
    
    def _resize_viewport(self, width, height):
        """Configura viewport e projeção"""
        if height == 0:
            height = 1
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)
    
    def _create_config_menu(self):
        """Cria menu de configuração"""
        menu_width = 500
        menu_height = 450
        menu_x = self.width / 2 - menu_width / 2
        menu_y = self.height / 2 - menu_height / 2
        
        # Painel principal
        self.config_panel = Panel(menu_x, menu_y, menu_width, menu_height)
        
        # Botões de cor
        presets = self.config.get_background_presets()
        color_y = menu_y + menu_height - 170
        
        for i, preset in enumerate(presets):
            btn = ColorButton(
                menu_x + 20 + i * 80,
                color_y,
                60,
                preset["color"],
                selected=(i == 1)
            )
            btn.on_select_callback = lambda b, idx=i: self._on_color_preset_selected(idx)
            self.config_panel.add_component(btn)
            self.ui_components.append(btn)
        
        # Toggle de eixos
        toggle = ToggleButton(
            menu_x + 200,
            menu_y + menu_height - 290,
            100,
            40,
            enabled=self.config.get_show_axes()
        )
        toggle.on_toggle_callback = lambda b, state: self._on_axes_toggle(state)
        self.config_panel.add_component(toggle)
        self.ui_components.append(toggle)
        
        # Slider de tamanho de pontos
        slider = Slider(
            menu_x + 50,
            menu_y + menu_height - 390,
            400,
            30,
            min_value=1.0,
            max_value=10.0,
            value=self.config.get_point_size()
        )
        slider.on_change_callback = lambda s, value: self._on_point_size_change(value)
        self.config_panel.add_component(slider)
        self.ui_components.append(slider)
        
        # Botão fechar
        close_btn = Button(
            menu_x + menu_width / 2 - 75,
            menu_y + 20,
            150,
            40,
            label="FECHAR",
            color=(0.5, 0.2, 0.2, 0.9)
        )
        close_btn.on_click_callback = lambda b: self._close_config_menu()
        self.config_panel.add_component(close_btn)
        self.ui_components.append(close_btn)
    
    def _on_color_preset_selected(self, index):
        """Callback de seleção de cor"""
        presets = self.config.get_background_presets()
        color = presets[index]["color"]
        self.config.set_background_color(color)
        glClearColor(*color)
        print(f"🎨 Cor de fundo: {presets[index]['name']}")
    
    def _on_axes_toggle(self, state):
        """Callback de toggle de eixos"""
        self.config.set_show_axes(state)
        self.axes_renderer.visible = state
        print(f"📐 Eixos: {'Ativados' if state else 'Desativados'}")
    
    def _on_point_size_change(self, value):
        """Callback de mudança de tamanho"""
        self.config.set_point_size(value)
        self.point_renderer.set_point_size(value)
    
    def _close_config_menu(self):
        """Fecha menu de configuração"""
        self.show_config_menu = False
        print("⚙️  Menu fechado")
    
    def _register_callbacks(self):
        """Registra callbacks de input"""
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_window_size_callback(self.window, self._window_size_callback)
    
    def _key_callback(self, window, key, scancode, action, mods):
        """Callback de teclado"""
        # Train Selector Menu tem prioridade máxima
        if self.train_selector.handle_key(key, action):
            return
        
        # Detecta Ctrl
        if key in [glfw.KEY_LEFT_CONTROL, glfw.KEY_RIGHT_CONTROL]:
            self.ctrl_pressed = (action == glfw.PRESS)
        
        if action == glfw.PRESS or action == glfw.REPEAT:
            # ESC: Sair ou fechar editor
            if key == glfw.KEY_ESCAPE:
                if self.font_editor.active:
                    self.font_editor.deactivate()
                else:
                    glfw.set_window_should_close(window, True)
            
            # Font Editor ativo - controles específicos
            if self.font_editor.active:
                # Comandos especiais primeiro (prioridade sobre mudança de caractere)
                if key == glfw.KEY_TAB:
                    self.font_editor.toggle_mode()
                elif key == glfw.KEY_ENTER:
                    self.font_editor.finalize_shape()
                elif key == glfw.KEY_DELETE:
                    self.font_editor.delete_selected()
                elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
                    self.font_editor.adjust_smoothness(1)
                elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
                    self.font_editor.adjust_smoothness(-1)
                # Comandos com Shift (mudar caractere)
                elif mods & glfw.MOD_SHIFT and glfw.KEY_A <= key <= glfw.KEY_Z:
                    char = chr(key)
                    self.font_editor.set_current_char(char)
                # Comandos de letras (sem Shift)
                elif key == glfw.KEY_S and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.toggle_snap()
                elif key == glfw.KEY_E and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.export_code()
                elif key == glfw.KEY_C and not self.ctrl_pressed and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.clear_all()
                elif key == glfw.KEY_D and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.toggle_edit_mode()
                elif key == glfw.KEY_J and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.save_json()
                elif key == glfw.KEY_L and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.load_json()
                elif key == glfw.KEY_I and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.load_from_vector_font()
                elif key == glfw.KEY_R and not (mods & glfw.MOD_SHIFT):
                    self.font_editor.reverse_selected_arc()
                # Números e símbolos (com/sem Shift)
                elif glfw.KEY_0 <= key <= glfw.KEY_9:
                    if mods & glfw.MOD_SHIFT:
                        # Shift + número = símbolo
                        shift_symbols = {
                            glfw.KEY_1: '!',
                            glfw.KEY_2: '@',
                            glfw.KEY_3: '#',
                            glfw.KEY_4: '$',
                            glfw.KEY_5: '%',
                            glfw.KEY_6: '^',
                            glfw.KEY_7: '&',
                            glfw.KEY_8: '*',
                            glfw.KEY_9: '(',
                            glfw.KEY_0: ')'
                        }
                        char = shift_symbols.get(key, chr(key))
                    else:
                        # Sem Shift = número
                        char = chr(key)
                    self.font_editor.set_current_char(char)
                # Outros símbolos especiais
                elif key == glfw.KEY_GRAVE_ACCENT:  # Tecla ~
                    if mods & glfw.MOD_SHIFT:
                        self.font_editor.set_current_char('~')
                    else:
                        self.font_editor.set_current_char('`')
                return  # Não processa outros comandos
            
            # F: Abrir Font Editor
            if key == glfw.KEY_F:
                self.font_editor.activate()
                return
            
            # P: Toggle Painel de Controle
            elif key == glfw.KEY_P:
                self._process_menu_action('toggle_control_panel')
            
            # C: Menu de configuração
            elif key == glfw.KEY_C:
                self._process_menu_action('show_config')
            
            # R: Reset câmera
            elif key == glfw.KEY_R:
                self.camera.reset()
                print("🔄 Câmera resetada")
            
            # U: Recarregar arquivo
            elif key == glfw.KEY_U and self.current_file:
                self.load_file(self.current_file)
            
            # O: Abrir arquivo
            elif key == glfw.KEY_O:
                self._open_file_dialog()
            
            # T: Tabela de pontos / Shift+T: Seletor de Trem
            elif key == glfw.KEY_T:
                if mods & glfw.MOD_SHIFT:
                    self._process_menu_action('open_train_selector')
                else:
                    self._open_points_table()
            
            # V: Toggle auto-rotação X
            elif key == glfw.KEY_V:
                self.auto_rotate_x = not self.auto_rotate_x
                checked_str = "✓" if self.auto_rotate_x else " "
                print(f"🔄 Auto-rotação X: {'ativada' if self.auto_rotate_x else 'desativada'}")
                # Atualiza estado no menu
                for item in self.menu_bar.menus[1]['items']:
                    if item.get('action') == 'toggle_auto_rotate_x':
                        item['checked'] = self.auto_rotate_x
            
            # X/Y/Z: Vistas perpendiculares
            elif key == glfw.KEY_X:
                pitch, yaw = self.camera.get_rotation_matrix()
                # Normaliza yaw para 0-360
                yaw_normalized = yaw % 360
                if yaw_normalized < 0:
                    yaw_normalized += 360
                
                if abs(pitch) < 5 and abs(yaw_normalized - 90) < 5:
                    self.camera.set_view(0, 270)
                elif abs(pitch) < 5 and abs(yaw_normalized - 270) < 5:
                    self.camera.set_view(0, 90)
                else:
                    self.camera.set_view(0, 90)
            
            elif key == glfw.KEY_Y:
                pitch, yaw = self.camera.get_rotation_matrix()
                if abs(pitch - 90) < 5:
                    self.camera.set_view(-90, yaw)
                elif abs(pitch + 90) < 5:
                    self.camera.set_view(90, yaw)
                else:
                    self.camera.set_view(90, yaw)
            
            elif key == glfw.KEY_Z:
                pitch, yaw = self.camera.get_rotation_matrix()
                # Normaliza yaw para 0-360
                yaw_normalized = yaw % 360
                if yaw_normalized < 0:
                    yaw_normalized += 360
                
                if abs(pitch) < 5 and abs(yaw_normalized) < 5:
                    self.camera.set_view(0, 180)
                elif abs(pitch) < 5 and abs(yaw_normalized - 180) < 5:
                    self.camera.set_view(0, 0)
                else:
                    self.camera.set_view(0, 0)
            
            # Movimento com setas (se menu fechado)
            elif not self.show_config_menu:
                rotation_speed = 2.0  # graus por tecla
                move_speed = self.config.get("camera_move_speed", 5.0)
                
                # Com SHIFT: move a câmera relativo à direção que está apontando
                if mods & glfw.MOD_SHIFT:
                    if key == glfw.KEY_UP:
                        # Move para frente na direção da câmera
                        self.camera.move_camera_relative(forward=move_speed)
                    elif key == glfw.KEY_DOWN:
                        # Move para trás na direção da câmera
                        self.camera.move_camera_relative(forward=-move_speed)
                    elif key == glfw.KEY_LEFT:
                        # Move para esquerda da câmera
                        self.camera.move_camera_relative(right=-move_speed)
                    elif key == glfw.KEY_RIGHT:
                        # Move para direita da câmera
                        self.camera.move_camera_relative(right=move_speed)
                    elif key == glfw.KEY_J:
                        # Move para baixo relativo à câmera
                        self.camera.move_camera_relative(up=-move_speed)
                    elif key == glfw.KEY_K:
                        # Move para cima relativo à câmera
                        self.camera.move_camera_relative(up=move_speed)
                else:
                    # Sem SHIFT: rotaciona a câmera (muda direção de visão)
                    if key == glfw.KEY_UP:
                        # Rotaciona para cima (aumenta pitch)
                        self.camera.rotate(0, rotation_speed)
                    elif key == glfw.KEY_DOWN:
                        # Rotaciona para baixo (diminui pitch)
                        self.camera.rotate(0, -rotation_speed)
                    elif key == glfw.KEY_LEFT:
                        # Rotaciona para esquerda (diminui yaw)
                        self.camera.rotate(-rotation_speed, 0)
                    elif key == glfw.KEY_RIGHT:
                        # Rotaciona para direita (aumenta yaw)
                        self.camera.rotate(rotation_speed, 0)
                    elif key == glfw.KEY_J:
                        # Move target para baixo (eixo Y global)
                        self.camera.move_target(0, -move_speed, 0)
                    elif key == glfw.KEY_K:
                        # Move target para cima (eixo Y global)
                        self.camera.move_target(0, move_speed, 0)
    
    def _mouse_button_callback(self, window, button, action, mods):
        """Callback de botão do mouse"""
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                mx, my = glfw.get_cursor_pos(window)
                my_inverted = self.height - my  # Inverte Y para sistema OpenGL
                
                # Train Selector Menu tem prioridade máxima
                if self.train_selector.handle_click(mx, my_inverted):
                    return
                
                # Verifica clique na barra de menu ou dropdown (usa coordenadas OpenGL - Y crescendo para cima)
                # Sempre processa clique se menu está ativo (dropdown aberto) OU se está sobre a barra
                if self.menu_bar.active_menu is not None or self.menu_bar.is_over_menu(mx, my_inverted):
                    menu_action = self.menu_bar.handle_click(mx, my_inverted)
                    if menu_action and menu_action != 'none':
                        self._process_menu_action(menu_action)
                    return
                
                # Verifica clique no Font Editor
                if self.font_editor.active:
                    if self.font_editor.on_click(mx, my_inverted):
                        # Font editor processou o clique
                        # Mas ainda precisamos setar left_drag para o drag funcionar
                        self.left_drag = True
                        self.last_mouse_x, self.last_mouse_y = glfw.get_cursor_pos(window)
                        return
                
                # Verifica clique no Control Panel
                if self.control_panel.visible:
                    if self.control_panel.handle_click(mx, my_inverted):
                        return
                
                # Verifica clique na UI
                if self.show_config_menu:
                    if self.config_panel.on_click(mx, my_inverted):
                        return
                
                self.left_drag = True
                self.last_mouse_x, self.last_mouse_y = glfw.get_cursor_pos(window)
            else:
                # Release
                if self.font_editor.active:
                    self.font_editor.on_release()
                self.left_drag = False
        
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.right_drag = True
                self.last_mouse_x, self.last_mouse_y = glfw.get_cursor_pos(window)
            else:
                self.right_drag = False
    
    def _cursor_pos_callback(self, window, xpos, ypos):
        """Callback de movimento do mouse"""
        # Calcula deltas antes de tudo
        dx = xpos - self.last_mouse_x
        dy = ypos - self.last_mouse_y
        
        # Se não há movimento, ignora
        if dx == 0 and dy == 0:
            return
        
        # Atualiza hover do editor
        if self.font_editor.active:
            ypos_inverted = self.height - ypos
            self.font_editor.update_hover(xpos, ypos_inverted)
            
            # Se estiver arrastando, chama on_drag
            if self.left_drag:
                if self.font_editor.dragging:
                    self.font_editor.on_drag(xpos, ypos_inverted)
                    self.last_mouse_x = xpos
                    self.last_mouse_y = ypos
                    return  # Não processa drag da câmera
                elif self.font_editor.edit_mode:
                    # Debug: em modo edição mas não arrastando
                    pass
        
        # Atualiza hover do menu apenas se não está arrastando (economiza processamento)
        if not self.left_drag and not self.right_drag:
            try:
                self.menu_bar.handle_hover(xpos, self.height - ypos)
            except Exception:
                pass
            
            # Atualiza hover do control panel
            if self.control_panel.visible:
                try:
                    self.control_panel.update_hover(xpos, self.height - ypos)
                except Exception:
                    pass
        
        # Processa drag da câmera
        if self.left_drag:
            if self.ctrl_pressed:
                # Pan
                self.camera.pan(dx, dy)
            else:
                # Rotação
                self.camera.rotate(dx * 0.5, dy * 0.5)
        
        elif self.right_drag and self.ctrl_pressed:
            # Movimento frontal
            self.camera.move_forward(dy)
        
        self.last_mouse_x = xpos
        self.last_mouse_y = ypos
    
    def _scroll_callback(self, window, xoffset, yoffset):
        """Callback de scroll (zoom)"""
        self.camera.zoom(-yoffset * 20.0)
    
    def _window_size_callback(self, window, width, height):
        """Callback de redimensionamento"""
        self.width = width
        self.height = height
        self._resize_viewport(width, height)
        self.axis_indicator.update_screen_size(width, height)
        self.config.set_window_params(width, height)
        # Atualiza tamanho da barra de menu
        try:
            self.menu_bar.update_size(width, height)
        except Exception:
            pass
        # Atualiza tamanho do control panel
        try:
            self.control_panel.update_size(width, height)
        except Exception:
            pass
    
    def load_file(self, filepath):
        """
        Carrega arquivo de dados
        
        Args:
            filepath: Caminho do arquivo
        """
        try:
            print(f"\n📂 Carregando arquivo: {filepath}")
            vertices, colors = self.data_loader.load(filepath)
            self.point_renderer.set_data(vertices, colors)
            self.current_file = filepath
            
            # Adiciona ao histórico de arquivos recentes
            self.config.add_recent_file(filepath)
            self.config.save()
            
            # Atualiza menu com arquivos recentes
            self.menu_bar.update_recent_files(self.config.get_recent_files())
            
            # Ajusta câmera para centralizar e cacheia centro para auto-rotação
            center = self.point_renderer.get_center()
            self.camera.set_target(*center)
            self._auto_rotate_center = center  # Cacheia para auto-rotação
            
            print(f"✅ Arquivo carregado com sucesso!\n")
        except Exception as e:
            print(f"❌ Erro ao carregar arquivo: {e}")
    
    def _open_file_dialog(self):
        """Abre diálogo para selecionar arquivo"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Cria janela temporária (escondida)
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # Abre diálogo
            filepath = filedialog.askopenfilename(
                title="Selecione um arquivo de nuvem de pontos",
                filetypes=[
                    ("Todos os arquivos", "*.*"),
                    ("Arquivos UPL", "*.upl"),
                    ("Arquivos PTS", "*.pts"),
                    ("Arquivos CSV", "*.csv"),
                    ("Arquivos LAS", "*.las"),
                    ("Arquivos PCD", "*.pcd")
                ]
            )
            
            # Destroi janela temporária
            root.destroy()
            
            # Carrega arquivo se selecionado
            if filepath:
                self.load_file(filepath)
        except Exception as e:
            print(f"❌ Erro ao abrir diálogo: {e}")
    
    def _open_points_table(self):
        """Abre janela com tabela de pontos"""
        if not hasattr(self.point_renderer, 'vertices') or self.point_renderer.vertices is None:
            print("⚠️  Nenhum dado carregado!")
            return
        
        # Importa módulo de tabela
        from ui.points_table import PointsTableWindow
        
        # Cria janela de tabela (passa self para poder mover câmera)
        vertices = self.point_renderer.vertices
        colors = self.point_renderer.colors if hasattr(self.point_renderer, 'colors') else None
        
        table_window = PointsTableWindow(vertices, colors, self.current_file, app=self)
        table_window.run()
    
    def _on_train_selected(self, model, vagons, y_offset):
        """Callback quando trem é selecionado"""
        print(f"🚂 Trem selecionado:")
        print(f"   Modelo: {model}")
        print(f"   Vagões: {vagons}")
        print(f"   Posição Y: {y_offset}")
        # Aqui você pode adicionar lógica para carregar o arquivo do trem
        # Por exemplo: self.load_file(f"trains/{model}.upl")
    
    def _on_train_selector_cancel(self):
        """Callback quando seletor de trem é cancelado"""
        print("❌ Seleção de trem cancelada")

    def _process_menu_action(self, action):
        """Processa ações vindas da MenuBar"""
        if action == 'open_file':
            self._open_file_dialog()
        elif action == 'reload_file':
            if self.current_file:
                self.load_file(self.current_file)
        elif action.startswith('open_recent_'):
            # Abre arquivo recente pelo índice
            idx = int(action.split('_')[-1])
            recent_files = self.config.get_recent_files()
            if 0 <= idx < len(recent_files):
                filepath = recent_files[idx]
                import os
                if os.path.exists(filepath):
                    self.load_file(filepath)
                else:
                    print(f"⚠️  Arquivo não encontrado: {filepath}")
        elif action == 'cache_stats':
            self.data_loader.print_cache_stats()
        elif action == 'clear_cache':
            print("🗑️  Limpando cache...")
            self.data_loader.clear_cache()
            print("✅ Cache limpo com sucesso!")
        elif action == 'exit':
            glfw.set_window_should_close(self.window, True)
        elif action == 'show_table':
            self._open_points_table()
        elif action == 'show_config':
            self.show_config_menu = not self.show_config_menu
        elif action == 'view_x':
            self.camera.set_view(0, 90)
        elif action == 'view_y':
            # Mantém yaw atual
            pitch, yaw = self.camera.get_rotation_matrix()
            self.camera.set_view(90, yaw)
        elif action == 'view_z':
            self.camera.set_view(0, 0)
        elif action == 'reset_camera':
            self.camera.reset()
        elif action == 'font_editor':
            self.font_editor.activate()
        elif action == 'toggle_control_panel':
            self.control_panel.visible = not self.control_panel.visible
            # Atualiza checkbox no menu
            for item in self.menu_bar.menus[2]['items']:  # Menu Ferramentas
                if item.get('action') == 'toggle_control_panel':
                    item['checked'] = self.control_panel.visible
            print(f"🎛️  Painel de Controle: {'Ativado' if self.control_panel.visible else 'Desativado'}")
        elif action == 'open_train_selector':
            self.train_selector.open()
            print("🚂 Abrindo seletor de trem...")
        elif action == 'toggle_auto_rotate_x':
            self.auto_rotate_x = not self.auto_rotate_x
            print(f"🔁 Auto-rotacionar X: {'Ativado' if self.auto_rotate_x else 'Desativado'}")
        elif action == 'toggle_show_all_points':
            # Alterna entre renderizar todos os pontos ou usar LOD
            self.show_all_points = not getattr(self, 'show_all_points', False)
            if self.show_all_points:
                # Desativa LOD para renderizar todos os pontos
                self.point_renderer.set_lod_enabled(False)
                # Atualiza checkbox no menu
                for item in self.menu_bar.menus[1]['items']:
                    if item.get('action') == 'toggle_show_all_points':
                        item['checked'] = True
                print(f"⚡ Mostrar todos os pontos: ATIVADO (renderizando {self.point_renderer.n_vertices:,} pontos)")
            else:
                # Reativa LOD com padrão
                self.point_renderer.set_lod_enabled(True)
                for item in self.menu_bar.menus[1]['items']:
                    if item.get('action') == 'toggle_show_all_points':
                        item['checked'] = False
                print("⚡ Mostrar todos os pontos: DESATIVADO (LOD ativado)")
        else:
            print(f"⚠️  Ação de menu desconhecida: {action}")
    
    def render(self):
        """Renderiza um frame"""
        # Limpa tela
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Aplica câmera
        self.camera.apply()
        
        # Renderiza cena 3D
        if self.config.get_show_axes():
            self.axes_renderer.render()
        
        # Se auto-rotacionar ativo, aplica transformação ao redor do centro da nuvem
        if self.auto_rotate_x and hasattr(self.point_renderer, 'vertices') and self.point_renderer.n_vertices > 0:
            try:
                # Usa centro em cache (calculado apenas quando carrega arquivo)
                if self._auto_rotate_center is None:
                    self._auto_rotate_center = self.point_renderer.get_center()
                
                center = self._auto_rotate_center
                glPushMatrix()
                glTranslatef(center[0], center[1], center[2])
                glRotatef(self._auto_rotate_angle_x, 1.0, 0.0, 0.0)
                glTranslatef(-center[0], -center[1], -center[2])
                self.point_renderer.render()
                glPopMatrix()
            except Exception:
                # Fallback: renderiza sem transformação
                self.point_renderer.render()
        else:
            self.point_renderer.render()
        
        # Renderiza indicador de eixos
        pitch, yaw = self.camera.get_rotation_matrix()
        self.axis_indicator.render(pitch, yaw)
        
        # Modo 2D para UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Renderiza UI (se menu aberto)
        if self.show_config_menu:
            self._render_config_menu_content()
        
        # Renderiza Control Panel (se visível)
        if self.control_panel.visible:
            self.control_panel.render()
        
        # Renderiza Train Selector Menu (se ativo)
        self.train_selector.render()
        
        # Renderiza Font Editor (tem prioridade)
        if self.font_editor.active:
            self.font_editor.render()

        # Renderiza barra de menu sempre por cima
        try:
            self.menu_bar.render()
        except Exception:
            pass
        
        # Restaura modo 3D
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def _render_config_menu_content(self):
        """Renderiza conteúdo do menu de configuração"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Renderiza painel
        self.config_panel.draw()
        
        # Renderiza textos
        menu_x = self.config_panel.x
        menu_y = self.config_panel.y
        menu_height = self.config_panel.height
        
        # Título
        self.font.draw_text(menu_x + 150, menu_y + menu_height - 30, 
                           "CONFIGURACOES", color=(1, 1, 1), font_size=1.2)
        
        # Labels
        self.font.draw_text(menu_x + 20, menu_y + menu_height - 105,
                           "Cor de Fundo", color=(0.9, 0.9, 0.9), font_size=0.9)
        
        self.font.draw_text(menu_x + 200, menu_y + menu_height - 235,
                           "Mostrar Eixos", color=(0.9, 0.9, 0.9), font_size=0.9)
        
        self.font.draw_text(menu_x + 50, menu_y + menu_height - 345,
                           "Tamanho", color=(0.9, 0.9, 0.9), font_size=0.9)
        
        # Valor do slider
        value_text = f"{self.point_renderer.get_point_size():.1f}px"
        self.font.draw_text(menu_x + 400, menu_y + menu_height - 345,
                           value_text, color=(1, 1, 0), font_size=0.8)
        
        # Instruções
        self.font.draw_text(menu_x + 60, menu_y + menu_height - 80,
                           "Clique nos elementos ou use C para fechar",
                           color=(0.7, 0.7, 0.7), font_size=0.7)
        
        glDisable(GL_BLEND)
    
    def run(self):
        """Loop principal da aplicação"""
        self._print_controls()
        
        while not glfw.window_should_close(self.window):
            # Atualiza tempo e ângulo de rotação automática
            current_time = glfw.get_time()
            dt = current_time - self._last_frame_time
            
            # Limita dt para evitar pulos grandes (ex: quando pausa debugger)
            dt = min(dt, 0.1)  # Máximo 100ms entre frames
            
            if self.auto_rotate_x:
                # Atualiza ângulo baseado no tempo decorrido
                self._auto_rotate_angle_x = (self._auto_rotate_angle_x + self._rotation_speed_deg * dt) % 360.0
            
            self._last_frame_time = current_time
            
            # FPS counter
            self._fps_counter += 1
            if current_time - self._fps_last_time >= 1.0:
                self._current_fps = self._fps_counter
                
                # Monta título com FPS e stats de renderização
                title = f"{self.title} | FPS: {self._current_fps}"
                
                # Adiciona info de LOD se ativo
                if hasattr(self.point_renderer, 'get_render_stats'):
                    stats = self.point_renderer.get_render_stats()
                    if stats['lod_active']:
                        title += f" | Pontos: {stats['rendered_points']:,}/{stats['total_points']:,} ({stats['percentage']:.0f}%)"
                    elif stats['total_points'] > 0:
                        title += f" | Pontos: {stats['total_points']:,}"
                
                glfw.set_window_title(self.window, title)
                self._fps_counter = 0
                self._fps_last_time = current_time

            # Renderiza
            self.render()
            
            # Swap buffers
            glfw.swap_buffers(self.window)
            
            # Processa eventos sem bloquear
            # poll_events é rápido, mas processar cada evento de mouse tem custo
            glfw.poll_events()
        
        # Salva configurações ao sair
        cam_params = self.camera.get_rotation_matrix()
        self.config.set_camera_params(self.camera.distance, cam_params[0], cam_params[1])
        self.config.save()
        
        glfw.terminate()
    
    def _print_controls(self):
        """Imprime controles no console"""
        print("\n" + "="*60)
        print("🎮 CONTROLES")
        print("="*60)
        print("\n[Mouse]")
        print("  Arrastar Esq:         Rotacionar câmera")
        print("  Ctrl + Arrastar Esq:  Pan (mover lateral)")
        print("  Ctrl + Arrastar Dir:  Mover frente/trás")
        print("  Scroll:               Zoom in/out")
        print("\n[Teclado - Rotacionar Campo de Visão (sem Shift)]")
        print("  ↑↓←→:                 Rotacionar direção da câmera")
        print("  J/K:                  Mover target cima/baixo (eixo Y)")
        print("\n[Teclado - Mover Câmera Relativo (com Shift)]")
        print("  Shift + ↑:            Mover para FRENTE (direção da câmera)")
        print("  Shift + ↓:            Mover para TRÁS (direção da câmera)")
        print("  Shift + ←:            Mover para ESQUERDA (relativo à câmera)")
        print("  Shift + →:            Mover para DIREITA (relativo à câmera)")
        print("  Shift + J:            Mover para BAIXO (relativo à câmera)")
        print("  Shift + K:            Mover para CIMA (relativo à câmera)")
        print("\n[Outras Teclas]")
        print("  X/Y/Z:                Vistas perpendiculares")
        print("  R:                    Reset câmera")
        print("  C:                    Menu configuração")
        print("  F:                    ✏️  Editor de Fontes")
        print("  P:                    🎛️  Painel de Controle")
        if self.current_file:
            print("  U:                    Recarregar arquivo")
        print("  ESC:                  Sair")
        print("="*60)
        print("="*60 + "\n")
