"""
Painel de controle de trem no canto inferior direito
Interface com botões para controlar visualização e movimento do trem
"""

from OpenGL.GL import *
import math


class TrainControlPanel:
    """Painel de controle de trem com botões"""
    
    def __init__(self, width, height, font):
        """
        Inicializa painel
        
        Args:
            width, height: Dimensões da tela
            font: VectorFont para renderizar texto
        """
        self.width = width
        self.height = height
        self.font = font
        self.visible = True
        
        # Posição e tamanho
        self.panel_width = 300
        self.panel_height = 500  # Aumentado para acomodar slider Y
        self.panel_x = width - self.panel_width - 20
        self.panel_y = 20
        
        # Botões
        self.buttons = {
            'toggle_train': {'label': ' Trem', 'x': 0, 'y': 0, 'width': 130, 'height': 40, 'state': True},
            'toggle_cloud': {'label': ' Nuvem', 'x': 140, 'y': 0, 'width': 130, 'height': 40, 'state': True},
            'menu': {'label': ' Menu', 'x': 0, 'y': 50, 'width': 130, 'height': 40, 'state': False},
            'pause': {'label': ' Pausa', 'x': 140, 'y': 50, 'width': 130, 'height': 40, 'state': False},
            'reset': {'label': ' Reset', 'x': 0, 'y': 100, 'width': 130, 'height': 40, 'state': False},
            'dec_speed': {'label': ' Lento', 'x': 140, 'y': 100, 'width': 130, 'height': 40, 'state': False},
        }
        
        # Velocidade
        self.velocity_display = "0.50"
        self.velocity_slider_x = 0
        self.velocity_slider_y = 150
        self.velocity_slider_width = 270
        self.velocity_slider_height = 30
        
        # Posição Y
        self.y_position_display = "0.0"
        self.y_position_slider_x = 0
        self.y_position_slider_y = 210
        self.y_position_slider_width = 270
        self.y_position_slider_height = 30
        self.y_position_min = -20.0
        self.y_position_max = 20.0
        
        # Velocidades predefinidas
        self.speed_presets = [
            {'label': '1', 'value': 0.5, 'x': 0, 'y': 270, 'width': 38, 'height': 30},
            {'label': '2', 'value': 1.0, 'x': 40, 'y': 270, 'width': 38, 'height': 30},
            {'label': '3', 'value': 1.5, 'x': 80, 'y': 270, 'width': 38, 'height': 30},
            {'label': '4', 'value': 2.0, 'x': 120, 'y': 270, 'width': 38, 'height': 30},
            {'label': '5', 'value': 2.5, 'x': 160, 'y': 270, 'width': 38, 'height': 30},
            {'label': '6', 'value': 3.0, 'x': 200, 'y': 270, 'width': 38, 'height': 30},
            {'label': '7', 'value': 3.5, 'x': 240, 'y': 270, 'width': 30, 'height': 30},
            {'label': '8', 'value': 4.0, 'x': 0, 'y': 305, 'width': 38, 'height': 30},
            {'label': '9', 'value': 4.5, 'x': 40, 'y': 305, 'width': 38, 'height': 30},
        ]
        
        # Callbacks
        self.on_toggle_train = None
        self.on_toggle_cloud = None
        self.on_menu = None
        self.on_pause = None
        self.on_reset = None
        self.on_velocity_change = None
        self.on_y_position_change = None
        
        self.hovered_button = None
    
    def update_screen_size(self, width, height):
        """Atualiza tamanho da tela"""
        self.width = width
        self.height = height
        self.panel_x = width - self.panel_width - 20
    
    def set_velocity_display(self, velocity):
        """Atualiza display de velocidade"""
        self.velocity_display = f"{velocity:.2f}"
    
    def set_y_position_display(self, y_position):
        """Atualiza display de posição Y"""
        self.y_position_display = f"{y_position:.1f}"
    
    def set_button_state(self, button_name, state):
        """Define estado de um botão"""
        if button_name in self.buttons:
            self.buttons[button_name]['state'] = state
    
    def get_button_rect(self, button_key):
        """Retorna retângulo de um botão em coordenadas da tela"""
        btn = self.buttons[button_key]
        return (
            self.panel_x + btn['x'],
            self.panel_y + btn['y'],
            btn['width'],
            btn['height']
        )
    
    def handle_click(self, x, y):
        """Processa clique do mouse"""
        if not self.visible:
            return None
        
        # Verifica botões
        for button_key, btn in self.buttons.items():
            btn_x = self.panel_x + btn['x']
            btn_y = self.panel_y + btn['y']
            btn_w = btn['width']
            btn_h = btn['height']
            
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                if button_key == 'toggle_train' and self.on_toggle_train:
                    self.on_toggle_train()
                    return 'toggle_train'
                elif button_key == 'toggle_cloud' and self.on_toggle_cloud:
                    self.on_toggle_cloud()
                    return 'toggle_cloud'
                elif button_key == 'menu' and self.on_menu:
                    self.on_menu()
                    return 'menu'
                elif button_key == 'pause' and self.on_pause:
                    self.on_pause()
                    return 'pause'
                elif button_key == 'reset' and self.on_reset:
                    self.on_reset()
                    return 'reset'
                elif button_key == 'dec_speed' and self.on_velocity_change:
                    self.on_velocity_change(-0.1)
                    return 'dec_speed'
        
        # Verifica velocidades predefinidas
        for preset in self.speed_presets:
            preset_x = self.panel_x + preset['x']
            preset_y = self.panel_y + preset['y']
            preset_w = preset['width']
            preset_h = preset['height']
            
            if preset_x <= x <= preset_x + preset_w and preset_y <= y <= preset_y + preset_h:
                if self.on_velocity_change:
                    self.on_velocity_change(preset['value'], is_absolute=True)
                return f"speed_{preset['label']}"
        
        # Verifica slider de velocidade
        slider_x = self.panel_x + self.velocity_slider_x
        slider_y = self.panel_y + self.velocity_slider_y
        slider_w = self.velocity_slider_width
        slider_h = self.velocity_slider_height
        
        if slider_x <= x <= slider_x + slider_w and slider_y <= y <= slider_y + slider_h:
            # Calcula velocidade baseada na posição do clique
            relative_x = x - slider_x
            velocity = (relative_x / slider_w) * 4.5
            if self.on_velocity_change:
                self.on_velocity_change(velocity, is_absolute=True)
            return 'slider'
        
        # Verifica slider de posição Y
        y_slider_x = self.panel_x + self.y_position_slider_x
        y_slider_y = self.panel_y + self.y_position_slider_y
        y_slider_w = self.y_position_slider_width
        y_slider_h = self.y_position_slider_height
        
        if y_slider_x <= x <= y_slider_x + y_slider_w and y_slider_y <= y <= y_slider_y + y_slider_h:
            # Calcula posição Y baseada na posição do clique
            relative_x = x - y_slider_x
            y_position = self.y_position_min + (relative_x / y_slider_w) * (self.y_position_max - self.y_position_min)
            if self.on_y_position_change:
                self.on_y_position_change(y_position)
            return 'y_slider'
        
        return None
    
    def update_hover(self, x, y):
        """Atualiza botão sob o mouse"""
        self.hovered_button = None
        
        # Verifica botões
        for button_key, btn in self.buttons.items():
            btn_x = self.panel_x + btn['x']
            btn_y = self.panel_y + btn['y']
            btn_w = btn['width']
            btn_h = btn['height']
            
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                self.hovered_button = button_key
                return
        
        # Verifica velocidades predefinidas
        for i, preset in enumerate(self.speed_presets):
            preset_x = self.panel_x + preset['x']
            preset_y = self.panel_y + preset['y']
            preset_w = preset['width']
            preset_h = preset['height']
            
            if preset_x <= x <= preset_x + preset_w and preset_y <= y <= preset_y + preset_h:
                self.hovered_button = f"speed_{preset['label']}"
                return
    
    def render(self):
        """Renderiza o painel"""
        if not self.visible:
            return
        
        # Fundo do painel
        glColor4f(0.05, 0.05, 0.1, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y + self.panel_height)
        glVertex2f(self.panel_x, self.panel_y + self.panel_height)
        glEnd()
        
        # Borda
        glColor4f(0.4, 0.6, 0.9, 0.9)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y + self.panel_height)
        glVertex2f(self.panel_x, self.panel_y + self.panel_height)
        glEnd()
        glLineWidth(1.0)
        
        # Título
        self.font.draw_text(
            self.panel_x + 10,
            self.panel_y + self.panel_height - 25,
            "CONTROLES DO TREM",
            color=(0.8, 0.9, 1.0),
            font_size=0.8
        )
        
        # Renderiza botões
        for button_key, btn in self.buttons.items():
            btn_x = self.panel_x + btn['x']
            btn_y = self.panel_y + btn['y']
            btn_w = btn['width']
            btn_h = btn['height']
            
            # Cor do botão
            if self.hovered_button == button_key:
                glColor4f(0.3, 0.7, 1.0, 1.0)  # Azul brilhante
            elif btn['state']:
                glColor4f(0.2, 0.5, 0.8, 1.0)  # Azul ativo
            else:
                glColor4f(0.15, 0.25, 0.4, 1.0)  # Azul escuro
            
            # Desenha retângulo
            glBegin(GL_QUADS)
            glVertex2f(btn_x, btn_y)
            glVertex2f(btn_x + btn_w, btn_y)
            glVertex2f(btn_x + btn_w, btn_y + btn_h)
            glVertex2f(btn_x, btn_y + btn_h)
            glEnd()
            
            # Borda
            if self.hovered_button == button_key:
                glColor4f(1.0, 1.0, 0.0, 1.0)
                glLineWidth(2.0)
            else:
                glColor4f(0.5, 0.7, 0.9, 0.8)
                glLineWidth(1.0)
            
            glBegin(GL_LINE_LOOP)
            glVertex2f(btn_x, btn_y)
            glVertex2f(btn_x + btn_w, btn_y)
            glVertex2f(btn_x + btn_w, btn_y + btn_h)
            glVertex2f(btn_x, btn_y + btn_h)
            glEnd()
            glLineWidth(1.0)
            
            # Texto
            text_color = (1, 1, 1) if btn['state'] else (0.7, 0.7, 0.7)
            self.font.draw_text(
                btn_x + 5,
                btn_y + btn_h / 2 - 5,
                btn['label'],
                color=text_color,
                font_size=0.65
            )
        
        # Label de velocidade
        self.font.draw_text(
            self.panel_x + 10,
            self.panel_y + self.velocity_slider_y + self.velocity_slider_height + 5,
            "Velocidade:",
            color=(0.8, 0.9, 1.0),
            font_size=0.7
        )
        
        # Slider de velocidade
        slider_x = self.panel_x + self.velocity_slider_x
        slider_y = self.panel_y + self.velocity_slider_y
        slider_w = self.velocity_slider_width
        slider_h = self.velocity_slider_height
        
        # Fundo do slider
        glColor4f(0.1, 0.1, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(slider_x, slider_y)
        glVertex2f(slider_x + slider_w, slider_y)
        glVertex2f(slider_x + slider_w, slider_y + slider_h)
        glVertex2f(slider_x, slider_y + slider_h)
        glEnd()
        
        # Barra de progresso
        try:
            velocity = float(self.velocity_display)
            progress = min(velocity / 4.5, 1.0)  # Normaliza para 0-1 (máximo 4.5)
            bar_width = slider_w * progress
            
            glColor4f(0.2, 0.6, 1.0, 0.9)
            glBegin(GL_QUADS)
            glVertex2f(slider_x, slider_y)
            glVertex2f(slider_x + bar_width, slider_y)
            glVertex2f(slider_x + bar_width, slider_y + slider_h)
            glVertex2f(slider_x, slider_y + slider_h)
            glEnd()
        except:
            pass
        
        # Borda do slider
        glColor4f(0.5, 0.7, 0.9, 0.9)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(slider_x, slider_y)
        glVertex2f(slider_x + slider_w, slider_y)
        glVertex2f(slider_x + slider_w, slider_y + slider_h)
        glVertex2f(slider_x, slider_y + slider_h)
        glEnd()
        glLineWidth(1.0)
        
        # Texto de velocidade
        self.font.draw_text(
            slider_x + slider_w + 10,
            slider_y + slider_h / 2 - 5,
            self.velocity_display,
            color=(0.8, 1.0, 0.8),
            font_size=0.8
        )
        
        # Label de posição Y
        self.font.draw_text(
            self.panel_x + 10,
            self.panel_y + self.y_position_slider_y + self.y_position_slider_height + 5,
            "Posição Y:",
            color=(0.8, 0.9, 1.0),
            font_size=0.7
        )
        
        # Slider de posição Y
        y_slider_x = self.panel_x + self.y_position_slider_x
        y_slider_y = self.panel_y + self.y_position_slider_y
        y_slider_w = self.y_position_slider_width
        y_slider_h = self.y_position_slider_height
        
        # Fundo do slider Y
        glColor4f(0.1, 0.1, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(y_slider_x, y_slider_y)
        glVertex2f(y_slider_x + y_slider_w, y_slider_y)
        glVertex2f(y_slider_x + y_slider_w, y_slider_y + y_slider_h)
        glVertex2f(y_slider_x, y_slider_y + y_slider_h)
        glEnd()
        
        # Barra de progresso Y
        try:
            y_pos = float(self.y_position_display)
            progress_y = (y_pos - self.y_position_min) / (self.y_position_max - self.y_position_min)
            progress_y = max(0, min(progress_y, 1.0))
            bar_width_y = y_slider_w * progress_y
            
            glColor4f(1.0, 0.6, 0.2, 0.9)
            glBegin(GL_QUADS)
            glVertex2f(y_slider_x, y_slider_y)
            glVertex2f(y_slider_x + bar_width_y, y_slider_y)
            glVertex2f(y_slider_x + bar_width_y, y_slider_y + y_slider_h)
            glVertex2f(y_slider_x, y_slider_y + y_slider_h)
            glEnd()
        except:
            pass
        
        # Borda do slider Y
        glColor4f(0.5, 0.7, 0.9, 0.9)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(y_slider_x, y_slider_y)
        glVertex2f(y_slider_x + y_slider_w, y_slider_y)
        glVertex2f(y_slider_x + y_slider_w, y_slider_y + y_slider_h)
        glVertex2f(y_slider_x, y_slider_y + y_slider_h)
        glEnd()
        glLineWidth(1.0)
        
        # Texto de posição Y
        self.font.draw_text(
            y_slider_x + y_slider_w + 10,
            y_slider_y + y_slider_h / 2 - 5,
            self.y_position_display,
            color=(1.0, 0.8, 0.8),
            font_size=0.8
        )
        
        # Botões de velocidade predefinida
        self.font.draw_text(
            self.panel_x + 10,
            self.panel_y + 265,
            "Presets:",
            color=(0.8, 0.9, 1.0),
            font_size=0.7
        )
        
        for preset in self.speed_presets:
            preset_x = self.panel_x + preset['x']
            preset_y = self.panel_y + preset['y']
            preset_w = preset['width']
            preset_h = preset['height']
            
            # Cor
            if self.hovered_button == f"speed_{preset['label']}":
                glColor4f(0.3, 0.7, 1.0, 1.0)
            else:
                glColor4f(0.15, 0.35, 0.55, 0.9)
            
            glBegin(GL_QUADS)
            glVertex2f(preset_x, preset_y)
            glVertex2f(preset_x + preset_w, preset_y)
            glVertex2f(preset_x + preset_w, preset_y + preset_h)
            glVertex2f(preset_x, preset_y + preset_h)
            glEnd()
            
            # Borda
            glColor4f(0.5, 0.7, 0.9, 0.8)
            glLineWidth(1.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(preset_x, preset_y)
            glVertex2f(preset_x + preset_w, preset_y)
            glVertex2f(preset_x + preset_w, preset_y + preset_h)
            glVertex2f(preset_x, preset_y + preset_h)
            glEnd()
            glLineWidth(1.0)
            
            # Texto
            self.font.draw_text(
                preset_x + preset_w / 2 - 3,
                preset_y + preset_h / 2 - 5,
                preset['label'],
                color=(0.9, 0.9, 0.9),
                font_size=0.7
            )
