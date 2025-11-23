#!/usr/bin/env python3
"""
Novo visualizador 3D com sistema de gabaritos de túnel
Permite:
1. Selecionar gabarito (define zonas de alerta/invasão)
2. Carregar arquivo UPL e classificar pontos
3. Animar trem passando através da nuvem de pontos
4. Controlar velocidade e posição Y do trem
"""

import sys
import glfw
import numpy as np
from OpenGL.GL import *

from core.application import Viewer3DApplication
from loaders.data_loader import UPLLoader
from utils.tunnel_templates import TemplateRegistry, FerroviaTunel
from ui.gabarit_selector_menu import GabaritSelectorMenu
from ui.train_model_selector_menu import TrainModelSelectorMenu
from ui.train_control_panel import TrainControlPanel
from utils.ore_train_simulator import OreTrainSimulator
from renderers.train_renderer import TrainRenderer


class GabaritVisualizerApp(Viewer3DApplication):
    """Aplicação com sistema de gabaritos e simulação de trem"""
    
    def __init__(self):
        """Inicializa a aplicação"""
        super().__init__()
        
        # Estado do gabarito
        self.current_gabarit = None  # Será selecionado no menu
        self.current_gabarit_key = 'ferrovia'
        self.upl_data_loaded = False
        
        # Estado do trem
        self.ore_train = None
        self.train_renderer = None
        self.show_train = True
        self.show_cloud = True
        self.train_paused = False
        self.current_velocity = 1.0
        self.original_velocity = 1.0
        
        # Menus
        self.gabarit_menu = GabaritSelectorMenu(self.width, self.height, self.font)
        self.gabarit_menu.on_gabarit_selected = self._on_gabarit_selected
        
        self.train_menu = TrainModelSelectorMenu(self.width, self.height, self.font)
        self.train_menu.on_train_selected = self._on_train_selected
        
        # Painel de controle
        self.control_panel = TrainControlPanel(self.width, self.height, self.font)
        self.control_panel.on_speed_change = self._on_speed_change
        self.control_panel.on_y_position_change = self._on_y_position_change
        self.control_panel.on_menu_toggle = self._toggle_train_menu
        self.control_panel.on_pause_toggle = self._toggle_pause
        self.control_panel.on_reset = self._reset_train
        
        # Estado de animação
        self.start_time = 0
        self.paused_time = 0
        
        # Carrega gabarito padrão
        self._load_default_gabarit()
        
        print("\n" + "="*70)
        print("🔧 Visualizador com Sistema de Gabaritos de Túnel")
        print("="*70)
        print("\nInstruções:")
        print("  1. Pressione 'G' para selecionar o GABARITO")
        print("  2. Carregue um arquivo UPL (File → Open)")
        print("  3. Pressione 'T' para selecionar e animar o TREM")
        print("  4. Use os controles do painel para ajustar a simulação")
        print("="*70 + "\n")
    
    def _load_default_gabarit(self):
        """Carrega gabarito padrão (ferrovia)"""
        self.current_gabarit = TemplateRegistry.get('ferrovia')
        self.current_gabarit_key = 'ferrovia'
        print(f"📋 Gabarito padrão carregado: {self.current_gabarit.name}")
    
    def _on_gabarit_selected(self, gabarit_key):
        """Callback quando gabarito é selecionado"""
        self.current_gabarit = TemplateRegistry.get(gabarit_key)
        self.current_gabarit_key = gabarit_key
        print(f"✅ Gabarito selecionado: {self.current_gabarit.name}")
        
        # Recarrega arquivo UPL com novo gabarito se já estava carregado
        if self.upl_data_loaded and self.current_file:
            self._reload_upl_with_gabarit()
    
    def _reload_upl_with_gabarit(self):
        """Recarrega o arquivo UPL com o gabarito atual"""
        if not self.current_file:
            return
        
        print(f"🔄 Recarregando {self.current_file} com gabarito '{self.current_gabarit.name}'...")
        
        try:
            # Carrega com novo gabarito
            loader = UPLLoader(template=self.current_gabarit)
            vertices, colors = loader.load(self.current_file)
            
            # Atualiza dados
            self.vertices = vertices
            self.colors = colors
            self.n_vertices = len(vertices)
            
            # Cria/atualiza VBO
            self._setup_vbo()
            print(f"✅ Arquivo recarregado com novas cores")
        except Exception as e:
            print(f"❌ Erro ao recarregar: {e}")
    
    def _on_train_selected(self, model_name, vagons):
        """Callback quando modelo de trem é selecionado"""
        print(f"🚂 Criando trem: {model_name} com {vagons} vagões...")
        
        self.ore_train = OreTrainSimulator(model_name, vagons)
        self.train_renderer = TrainRenderer()
        
        self.show_train = True
        self.train_paused = False
        self.start_time = glfw.get_time()
        
        # Inicializa display do painel
        self.control_panel.set_y_position_display(self.ore_train.position_y)
        
        print(f"✅ Trem criado com sucesso!")
    
    def _on_speed_change(self, speed):
        """Callback quando velocidade muda"""
        self.current_velocity = speed
        if self.ore_train:
            self.ore_train.velocity = speed
    
    def _on_y_position_change(self, y_position):
        """Callback quando posição Y muda"""
        if self.ore_train:
            self.ore_train.position_y = y_position
            self.control_panel.set_y_position_display(y_position)
    
    def _toggle_train_menu(self):
        """Abre/fecha menu de seleção de trem"""
        self.train_menu.toggle()
    
    def _toggle_pause(self):
        """Pausa/resume a animação"""
        self.train_paused = not self.train_paused
        if self.train_paused:
            self.paused_time = glfw.get_time()
        else:
            self.start_time += glfw.get_time() - self.paused_time
    
    def _reset_train(self):
        """Reseta posição do trem"""
        if self.ore_train:
            self.ore_train.reset()
            print("🔄 Trem resetado para posição inicial")
    
    def on_key(self, window, key, scancode, action, mods):
        """Processa eventos de teclado"""
        if action == glfw.PRESS:
            # G: Selecionar gabarito
            if key == glfw.KEY_G:
                self.gabarit_menu.toggle()
                return
            
            # T: Selecionar trem
            elif key == glfw.KEY_T:
                self.train_menu.toggle()
                return
            
            # K: Mostrar/esconder trem
            elif key == glfw.KEY_K:
                self.show_train = not self.show_train
                status = "visível" if self.show_train else "oculto"
                print(f"🚂 Trem {status}")
                return
            
            # L: Mostrar/esconder nuvem
            elif key == glfw.KEY_L:
                self.show_cloud = not self.show_cloud
                status = "visível" if self.show_cloud else "oculta"
                print(f"☁️  Nuvem de pontos {status}")
                return
            
            # SPACE: Pausa/resume
            elif key == glfw.KEY_SPACE:
                self._toggle_pause()
                return
            
            # R: Reset trem
            elif key == glfw.KEY_R:
                self._reset_train()
                return
        
        # Passa para menus
        if self.gabarit_menu.handle_key(key, scancode, action, mods):
            return
        
        if self.train_menu.handle_key(key, scancode, action, mods):
            return
        
        if self.control_panel.handle_key(key, scancode, action, mods):
            return
        
        # Passa para aplicação base
        super().on_key(window, key, scancode, action, mods)
    
    def on_mouse_button(self, window, button, action, mods):
        """Processa cliques do mouse"""
        if action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            
            # Menus têm prioridade
            if self.gabarit_menu.handle_click(x, y):
                return
            
            if self.train_menu.handle_click(x, y):
                return
            
            if self.control_panel.handle_click(x, y):
                return
        
        # Passa para aplicação base
        super().on_mouse_button(window, button, action, mods)
    
    def load_file(self, filepath):
        """Carrega arquivo com gabarito atual"""
        print(f"\n📂 Carregando arquivo: {filepath}")
        print(f"   Com gabarito: {self.current_gabarit.name}")
        
        try:
            loader = UPLLoader(template=self.current_gabarit)
            vertices, colors = loader.load(filepath)
            
            self.vertices = vertices
            self.colors = colors
            self.n_vertices = len(vertices)
            self.current_file = filepath
            self.upl_data_loaded = True
            
            self._setup_vbo()
            
            # Ajusta câmera
            if len(vertices) > 0:
                center = vertices.mean(axis=0)
                extent = (vertices.max(axis=0) - vertices.min(axis=0)).max()
                self.camera.look_at(
                    eye=center + np.array([extent, extent*0.5, extent]),
                    target=center,
                    up=np.array([0, 1, 0])
                )
            
            print(f"✅ Arquivo carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
    
    def _setup_vbo(self):
        """Cria VBO para renderização eficiente"""
        # ... implementação similar ao aplicativo anterior ...
        pass
    
    def render(self):
        """Renderiza a cena"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Renderiza nuvem de pontos
        if self.show_cloud and self.n_vertices > 0:
            glPointSize(2.0)
            glBegin(GL_POINTS)
            for i in range(min(self.n_vertices, 100000)):  # Limita por performance
                color = self.colors[i] if i < len(self.colors) else [1, 1, 1]
                vertex = self.vertices[i] if i < len(self.vertices) else [0, 0, 0]
                glColor3f(*color)
                glVertex3f(*vertex)
            glEnd()
        
        # Renderiza trem
        if self.show_train and self.ore_train:
            current_time = glfw.get_time() if not self.train_paused else self.paused_time
            elapsed = current_time - self.start_time
            
            # Atualiza posição do trem
            self.ore_train.update(elapsed / 1000.0)  # Converte para segundos
            
            # Renderiza
            if self.train_renderer:
                points, colors = self.ore_train.get_points()
                self.train_renderer.render(points, colors)
        
        # Renderiza menus e painel
        self.gabarit_menu.render()
        self.train_menu.render()
        self.control_panel.render()
        
        # Status na tela
        self._render_status()
    
    def _render_status(self):
        """Renderiza informações de status"""
        y = self.height - 30
        
        status_text = f"Gabarito: {self.current_gabarit.name}"
        if self.ore_train:
            status_text += f" | Trem: {self.ore_train.model_name} | Vel: {self.current_velocity:.1f}"
        
        self.font.draw_text(10, y, status_text, color=(1, 1, 1), font_size=0.8)
    
    def run(self):
        """Inicia o loop principal"""
        # Patch de callbacks
        self.original_key_callback = self.on_key
        self.original_mouse_callback = self.on_mouse_button
        
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        
        # Loop principal
        while not glfw.window_should_close(self.window):
            self.render()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        glfw.terminate()


def main():
    """Função principal"""
    app = GabaritVisualizerApp()
    
    # Carrega arquivo se fornecido
    if len(sys.argv) > 1:
        app.load_file(sys.argv[1])
    
    app.run()


if __name__ == "__main__":
    main()
