"""
Menu de Seleção de Gabarito de Túnel
Permite escolher qual gabarito usar para classificar pontos como alerta/invasão
"""

import glfw
import numpy as np
from utils.tunnel_templates import TemplateRegistry


class GabaritSelectorMenu:
    """Menu para seleção do gabarito de túnel"""
    
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
        self.selected_index = 0
        
        # Carrega lista de gabaritos
        self.gabarits = TemplateRegistry.list_all()
        self.gabarits_names = TemplateRegistry.get_names()
        
        # Dimensões dos botões
        self.button_width = 300
        self.button_height = 50
        self.button_spacing = 10
        
        # Callback quando gabarito é selecionado
        self.on_gabarit_selected = None
    
    def toggle(self):
        """Abre/fecha o menu"""
        self.visible = not self.visible
        if self.visible:
            self.selected_index = 0
    
    def handle_key(self, key, scancode, action, mods):
        """
        Processa entrada de teclado
        
        Args:
            key, scancode, action, mods: Parâmetros do callback GLFW
        """
        if not self.visible:
            return False
        
        if action not in (glfw.PRESS, glfw.REPEAT):
            return False
        
        # Navegação com setas verticais
        if key == glfw.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self.gabarits)
            return True
        elif key == glfw.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.gabarits)
            return True
        
        # ENTER para confirmar
        elif key == glfw.KEY_ENTER:
            self._confirm_selection()
            return True
        
        # ESC para fechar
        elif key == glfw.KEY_ESCAPE:
            self.visible = False
            return True
        
        return False
    
    def handle_click(self, x, y):
        """
        Processa clique do mouse
        
        Args:
            x, y: Coordenadas do clique em pixels
        """
        if not self.visible:
            return False
        
        # Calcula posição dos botões
        start_y = (self.height - len(self.gabarits) * (self.button_height + self.button_spacing)) // 2
        start_x = (self.width - self.button_width) // 2
        
        # Verifica qual botão foi clicado
        for i, gabarit_key in enumerate(self.gabarits):
            button_y = start_y + i * (self.button_height + self.button_spacing)
            
            if (start_x <= x <= start_x + self.button_width and
                button_y <= y <= button_y + self.button_height):
                self.selected_index = i
                self._confirm_selection()
                return True
        
        return False
    
    def _confirm_selection(self):
        """Confirma a seleção do gabarito"""
        selected_key = self.gabarits[self.selected_index]
        
        if self.on_gabarit_selected:
            self.on_gabarit_selected(selected_key)
        
        self.visible = False
    
    def render(self):
        """Renderiza o menu na tela"""
        if not self.visible:
            return
        
        # Fundo semi-transparente
        self._render_background()
        
        # Título
        title_y = self.height - 100
        self.font.draw_text(
            self.width // 2 - 150,
            title_y,
            "SELECIONE O GABARITO",
            color=(1.0, 1.0, 1.0),
            font_size=1.2
        )
        
        # Descrição
        self.font.draw_text(
            self.width // 2 - 200,
            title_y - 40,
            "Escolha o tipo de túnel para classificar os pontos",
            color=(0.8, 0.8, 0.8),
            font_size=0.8
        )
        
        # Botões dos gabaritos
        start_y = (self.height - len(self.gabarits) * (self.button_height + self.button_spacing)) // 2
        start_x = (self.width - self.button_width) // 2
        
        for i, gabarit_key in enumerate(self.gabarits):
            button_y = start_y + i * (self.button_height + self.button_spacing)
            is_selected = (i == self.selected_index)
            
            self._render_button(
                start_x,
                button_y,
                self.button_width,
                self.button_height,
                self.gabarits_names[gabarit_key],
                is_selected
            )
        
        # Instruções
        instr_y = start_y - 60
        self.font.draw_text(
            self.width // 2 - 150,
            instr_y,
            "↑/↓ Navegar | ENTER Confirmar | ESC Cancelar",
            color=(0.7, 0.9, 1.0),
            font_size=0.7
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
    
    def _render_button(self, x, y, width, height, text, selected):
        """
        Renderiza um botão
        
        Args:
            x, y, width, height: Posição e dimensões
            text: Texto do botão
            selected: Se está selecionado
        """
        from OpenGL.GL import glColor3f, glBegin, glVertex2f, glEnd, GL_QUADS, GL_LINE_LOOP
        
        # Cor de fundo
        if selected:
            glColor3f(0.0, 0.6, 1.0)  # Azul claro para selecionado
        else:
            glColor3f(0.2, 0.2, 0.3)  # Cinza escuro
        
        # Desenha fundo
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Desenha borda
        if selected:
            glColor3f(1.0, 1.0, 0.0)  # Amarelo para selecionado
        else:
            glColor3f(0.5, 0.5, 0.5)  # Cinza
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Renderiza texto
        text_color = (1.0, 1.0, 0.0) if selected else (1.0, 1.0, 1.0)
        text_x = x + (width - len(text) * 7) // 2  # Centraliza aproximadamente
        text_y = y + (height - 15) // 2
        
        self.font.draw_text(text_x, text_y, text, color=text_color, font_size=1.0)


if __name__ == '__main__':
    # Teste do menu
    print("🔧 Menu de Seleção de Gabarito")
    print("="*60)
    
    registry = TemplateRegistry()
    print("\nGabaritos disponíveis:")
    for key, name in registry.get_names().items():
        print(f"  • {key:15} → {name}")
