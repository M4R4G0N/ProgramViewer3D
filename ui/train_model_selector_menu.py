"""
Menu Simplificado de Seleção de Modelo de Trem
Seleção apenas do modelo e número de vagões (sem Y-offset)
"""

import glfw
import numpy as np
from utils.ore_train_models import create_train_model


class TrainModelSelectorMenu:
    """Menu para seleção do modelo de trem"""
    
    # Modelos de trem disponíveis
    TRAIN_MODELS = [
        'ES43', 'DASH BB', 'SD 40', 'GT', 'G22', 'UB', 'U20', 'AC 44i', 'DASH 9', 'ES44', 'C30'
    ]
    
    def __init__(self, width, height, font):
        """
        Args:
            width, height: Dimensões da janela
            font: Instância de VectorFont para renderizar texto
        """
        self.width = width
        self.height = height
        self.font = font
        
        # Estado do menu
        self.visible = False
        self.confirming_stage = 0  # 0 = modelo, 1 = vagões
        
        # Seleção
        self.selected_model_index = 0
        self.vagons_input = "30"
        self.selected_vagons = 30
        
        # Input field status
        self.vagons_field_active = False
        self.vagons_cursor_pos = len(self.vagons_input)
        
        # Dimensões
        self.button_width = 150
        self.button_height = 40
        
        # Callback quando trem é selecionado
        self.on_train_selected = None
    
    def toggle(self):
        """Abre/fecha o menu"""
        self.visible = not self.visible
        if self.visible:
            self.confirming_stage = 0
            self.selected_model_index = 0
            self.vagons_input = "30"
            self.vagons_field_active = False
    
    def handle_key(self, key, scancode, action, mods):
        """Processa entrada de teclado"""
        if not self.visible:
            return False
        
        if action not in (glfw.PRESS, glfw.REPEAT):
            return False
        
        # STAGE 0: Seleção de modelo
        if self.confirming_stage == 0:
            if key == glfw.KEY_LEFT:
                self.selected_model_index = (self.selected_model_index - 1) % len(self.TRAIN_MODELS)
                return True
            elif key == glfw.KEY_RIGHT:
                self.selected_model_index = (self.selected_model_index + 1) % len(self.TRAIN_MODELS)
                return True
            elif key == glfw.KEY_TAB or key == glfw.KEY_DOWN:
                self.confirming_stage = 1
                self.vagons_field_active = True
                return True
            elif key == glfw.KEY_ENTER:
                self.confirming_stage = 1
                self.vagons_field_active = True
                return True
        
        # STAGE 1: Input de vagões
        elif self.confirming_stage == 1 and self.vagons_field_active:
            if key == glfw.KEY_ENTER:
                self._confirm_train()
                return True
            elif key == glfw.KEY_ESCAPE:
                self.confirming_stage = 0
                self.vagons_field_active = False
                return True
            elif key == glfw.KEY_BACKSPACE:
                if len(self.vagons_input) > 0:
                    self.vagons_input = self.vagons_input[:-1]
                return True
            # Entrada numérica
            elif glfw.KEY_0 <= key <= glfw.KEY_9:
                if len(self.vagons_input) < 3:
                    self.vagons_input += chr(key)
                return True
        
        return False
    
    def handle_click(self, x, y):
        """Processa clique do mouse"""
        if not self.visible:
            return False
        
        # Clique nos botões de modelo
        model_start_y = self.height // 2 - 100
        for i in range(len(self.TRAIN_MODELS)):
            col = i % 4
            row = i // 4
            button_x = self.width // 2 - 350 + col * (self.button_width + 20)
            button_y = model_start_y + row * (self.button_height + 15)
            
            if (button_x <= x <= button_x + self.button_width and
                button_y <= y <= button_y + self.button_height):
                self.selected_model_index = i
                self.confirming_stage = 1
                self.vagons_field_active = True
                return True
        
        # Clique no campo de vagões
        vagons_x = self.width // 2 - 100
        vagons_y = self.height // 2 + 80
        if vagons_x <= x <= vagons_x + 200 and vagons_y <= y <= vagons_y + 40:
            self.vagons_field_active = True
            self.confirming_stage = 1
            return True
        
        return False
    
    def _confirm_train(self):
        """Confirma a seleção do trem"""
        try:
            self.selected_vagons = int(self.vagons_input)
            if self.selected_vagons < 1 or self.selected_vagons > 200:
                self.selected_vagons = 30
                self.vagons_input = "30"
                return
        except ValueError:
            self.selected_vagons = 30
            self.vagons_input = "30"
            return
        
        model_name = self.TRAIN_MODELS[self.selected_model_index]
        
        if self.on_train_selected:
            self.on_train_selected(model_name, self.selected_vagons)
        
        self.visible = False
    
    def render(self):
        """Renderiza o menu na tela"""
        if not self.visible:
            return
        
        # Fundo
        self._render_background()
        
        # Título
        self.font.draw_text(
            self.width // 2 - 200,
            self.height - 100,
            "SELECIONE O TREM",
            color=(1.0, 1.0, 1.0),
            font_size=1.2
        )
        
        # STAGE 0: Seleção de modelo
        if self.confirming_stage == 0:
            self._render_model_selection()
        # STAGE 1: Input de vagões
        elif self.confirming_stage == 1:
            self._render_vagons_input()
    
    def _render_model_selection(self):
        """Renderiza seleção de modelos"""
        from OpenGL.GL import glColor3f, glBegin, glVertex2f, glEnd, GL_QUADS, GL_LINE_LOOP
        
        title_y = self.height // 2 - 50
        self.font.draw_text(
            self.width // 2 - 150,
            title_y,
            "Escolha o modelo (← →)",
            color=(0.9, 0.9, 0.9),
            font_size=0.9
        )
        
        # Mostra 4 modelos por linha
        model_start_y = self.height // 2 - 100
        
        for i, model in enumerate(self.TRAIN_MODELS):
            col = i % 4
            row = i // 4
            button_x = self.width // 2 - 350 + col * (self.button_width + 20)
            button_y = model_start_y + row * (self.button_height + 15)
            
            is_selected = (i == self.selected_model_index)
            
            # Desenha botão
            if is_selected:
                glColor3f(0.0, 0.7, 1.0)
            else:
                glColor3f(0.2, 0.2, 0.3)
            
            glBegin(GL_QUADS)
            glVertex2f(button_x, button_y)
            glVertex2f(button_x + self.button_width, button_y)
            glVertex2f(button_x + self.button_width, button_y + self.button_height)
            glVertex2f(button_x, button_y + self.button_height)
            glEnd()
            
            # Borda
            if is_selected:
                glColor3f(1.0, 1.0, 0.0)
            else:
                glColor3f(0.5, 0.5, 0.5)
            
            glBegin(GL_LINE_LOOP)
            glVertex2f(button_x, button_y)
            glVertex2f(button_x + self.button_width, button_y)
            glVertex2f(button_x + self.button_width, button_y + self.button_height)
            glVertex2f(button_x, button_y + self.button_height)
            glEnd()
            
            # Texto
            text_color = (1.0, 1.0, 0.0) if is_selected else (1.0, 1.0, 1.0)
            text_x = button_x + 10
            text_y = button_y + (self.button_height - 15) // 2
            self.font.draw_text(text_x, text_y, model, color=text_color, font_size=0.8)
        
        # Instruções
        instr_y = model_start_y - 40
        self.font.draw_text(
            self.width // 2 - 200,
            instr_y,
            "← → Navegar | ENTER ou TAB Continuar",
            color=(0.7, 0.9, 1.0),
            font_size=0.75
        )
    
    def _render_vagons_input(self):
        """Renderiza input de vagões"""
        from OpenGL.GL import glColor3f, glBegin, glVertex2f, glEnd, GL_QUADS, GL_LINE_LOOP
        
        model_name = self.TRAIN_MODELS[self.selected_model_index]
        
        # Mostra modelo selecionado
        self.font.draw_text(
            self.width // 2 - 150,
            self.height // 2 - 50,
            f"Modelo selecionado: {model_name}",
            color=(0.7, 1.0, 0.7),
            font_size=0.95
        )
        
        # Campo de vagões
        self.font.draw_text(
            self.width // 2 - 150,
            self.height // 2 + 50,
            "Número de vagões (1-200):",
            color=(0.9, 0.9, 0.9),
            font_size=0.85
        )
        
        # Input box
        input_x = self.width // 2 - 100
        input_y = self.height // 2 + 80
        input_width = 200
        input_height = 40
        
        if self.vagons_field_active:
            glColor3f(0.0, 0.5, 1.0)
        else:
            glColor3f(0.2, 0.2, 0.3)
        
        glBegin(GL_QUADS)
        glVertex2f(input_x, input_y)
        glVertex2f(input_x + input_width, input_y)
        glVertex2f(input_x + input_width, input_y + input_height)
        glVertex2f(input_x, input_y + input_height)
        glEnd()
        
        # Borda
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(input_x, input_y)
        glVertex2f(input_x + input_width, input_y)
        glVertex2f(input_x + input_width, input_y + input_height)
        glVertex2f(input_x, input_y + input_height)
        glEnd()
        
        # Texto input
        text_color = (1.0, 1.0, 0.0) if self.vagons_field_active else (0.7, 0.7, 0.7)
        self.font.draw_text(
            input_x + 10,
            input_y + (input_height - 15) // 2,
            self.vagons_input,
            color=text_color,
            font_size=1.0
        )
        
        # Instruções
        self.font.draw_text(
            self.width // 2 - 200,
            self.height // 2 + 150,
            "ENTER Confirmar | ESCAPE Voltar",
            color=(0.7, 0.9, 1.0),
            font_size=0.75
        )
    
    def _render_background(self):
        """Renderiza fundo semi-transparente"""
        from OpenGL.GL import glColor4f, glBegin, glVertex2f, glEnd, GL_QUADS
        
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
