"""
Componentes de UI genéricos para OpenGL
Botões, sliders, toggles e outros widgets reutilizáveis
"""

from OpenGL.GL import *
import math


class UIComponent:
    """Classe base para todos os componentes de UI"""
    
    def __init__(self, x, y, width, height):
        """
        Inicializa componente
        
        Args:
            x, y: Posição (canto inferior esquerdo)
            width, height: Dimensões
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
    
    def contains_point(self, px, py):
        """
        Verifica se ponto está dentro do componente
        
        Args:
            px, py: Coordenadas do ponto
            
        Returns:
            True se ponto está dentro
        """
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)
    
    def draw(self):
        """Renderiza o componente (sobrescrever em subclasses)"""
        pass
    
    def on_click(self, x, y):
        """Callback de clique (sobrescrever em subclasses)"""
        pass


class ColorButton(UIComponent):
    """Botão quadrado colorido para seleção de cores"""
    
    def __init__(self, x, y, size, color, selected=False):
        """
        Args:
            x, y: Posição
            size: Tamanho do quadrado
            color: Tupla RGBA (0-1)
            selected: Se está selecionado
        """
        super().__init__(x, y, size, size)
        self.color = color
        self.selected = selected
        self.on_select_callback = None
    
    def draw(self):
        """Renderiza o botão de cor"""
        if not self.visible:
            return
        
        # Quadrado com a cor
        glColor4f(*self.color)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Borda (mais grossa se selecionado)
        border_color = [1, 1, 0, 1] if self.selected else [0.5, 0.5, 0.5, 1]
        border_width = 4.0 if self.selected else 2.0
        
        glColor4f(*border_color)
        glLineWidth(border_width)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        glLineWidth(1.0)
    
    def on_click(self, x, y):
        """Dispara callback ao clicar"""
        if self.on_select_callback:
            self.on_select_callback(self)


class ToggleButton(UIComponent):
    """Botão toggle ON/OFF com animação deslizante"""
    
    def __init__(self, x, y, width, height, enabled=False, label=""):
        """
        Args:
            x, y: Posição
            width, height: Dimensões
            enabled: Estado inicial (True/False)
            label: Texto do botão
        """
        super().__init__(x, y, width, height)
        self.enabled_state = enabled
        self.label = label
        self.on_toggle_callback = None
    
    def draw(self):
        """Renderiza o toggle button"""
        if not self.visible:
            return
        
        # Fundo do botão
        bg_color = [0.3, 0.5, 0.3, 0.8] if self.enabled_state else [0.5, 0.3, 0.3, 0.8]
        glColor4f(*bg_color)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Borda
        glColor4f(0.7, 0.7, 0.7, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Indicador deslizante (círculo)
        slider_radius = self.height * 0.4
        slider_x = self.x + self.width - slider_radius - 5 if self.enabled_state else self.x + slider_radius + 5
        slider_y = self.y + self.height / 2
        
        self._draw_circle(slider_x, slider_y, slider_radius, [1, 1, 1, 1])
        
        glLineWidth(1.0)
    
    def _draw_circle(self, cx, cy, radius, color):
        """Desenha círculo preenchido"""
        glColor4f(*color)
        segments = 32
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    def on_click(self, x, y):
        """Alterna estado ao clicar"""
        self.enabled_state = not self.enabled_state
        if self.on_toggle_callback:
            self.on_toggle_callback(self, self.enabled_state)


class Slider(UIComponent):
    """Slider horizontal para seleção de valores numéricos"""
    
    def __init__(self, x, y, width, height, min_value=0.0, max_value=100.0, value=50.0):
        """
        Args:
            x, y: Posição
            width, height: Dimensões
            min_value, max_value: Range de valores
            value: Valor inicial
        """
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change_callback = None
    
    def draw(self):
        """Renderiza o slider"""
        if not self.visible:
            return
        
        # Fundo da barra
        glColor4f(0.3, 0.3, 0.3, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Borda
        glColor4f(0.6, 0.6, 0.6, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Barra de progresso
        progress = (self.value - self.min_value) / (self.max_value - self.min_value)
        progress_width = self.width * progress
        
        glColor4f(0.4, 0.6, 0.8, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + progress_width, self.y)
        glVertex2f(self.x + progress_width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Indicador de posição (círculos concêntricos)
        handle_x = self.x + progress_width
        handle_y = self.y + self.height / 2
        
        self._draw_circle(handle_x, handle_y, self.height * 0.6, [1, 1, 1, 1])
        self._draw_circle(handle_x, handle_y, self.height * 0.4, [0.8, 0.8, 0.8, 1])
        
        glLineWidth(1.0)
    
    def _draw_circle(self, cx, cy, radius, color):
        """Desenha círculo preenchido"""
        glColor4f(*color)
        segments = 32
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    def on_click(self, x, y):
        """Atualiza valor baseado na posição do clique"""
        # Calcula valor baseado na posição X do clique
        progress = (x - self.x) / self.width
        progress = max(0.0, min(1.0, progress))
        
        self.value = self.min_value + progress * (self.max_value - self.min_value)
        
        if self.on_change_callback:
            self.on_change_callback(self, self.value)


class Button(UIComponent):
    """Botão retangular genérico com texto"""
    
    def __init__(self, x, y, width, height, label="", color=(0.3, 0.3, 0.3, 0.9)):
        """
        Args:
            x, y: Posição
            width, height: Dimensões
            label: Texto do botão
            color: Cor de fundo RGBA
        """
        super().__init__(x, y, width, height)
        self.label = label
        self.color = color
        self.hover = False
        self.on_click_callback = None
    
    def draw(self):
        """Renderiza o botão"""
        if not self.visible:
            return
        
        # Fundo do botão
        color = list(self.color)
        if self.hover:
            color = [c * 1.2 for c in color[:3]] + [color[3]]  # Clareia ao passar mouse
        
        glColor4f(*color)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Borda
        glColor4f(0.7, 0.7, 0.7, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        glLineWidth(1.0)
    
    def on_click(self, x, y):
        """Dispara callback ao clicar"""
        if self.on_click_callback:
            self.on_click_callback(self)


class Panel(UIComponent):
    """Painel retangular para agrupar outros componentes"""
    
    def __init__(self, x, y, width, height, bg_color=(0.15, 0.15, 0.15, 0.95)):
        """
        Args:
            x, y: Posição
            width, height: Dimensões
            bg_color: Cor de fundo RGBA
        """
        super().__init__(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = (0.5, 0.5, 0.5, 1.0)
        self.components = []
    
    def add_component(self, component):
        """Adiciona componente ao painel"""
        self.components.append(component)
    
    def draw(self):
        """Renderiza o painel e seus componentes"""
        if not self.visible:
            return
        
        # Sombra
        shadow_offset = 5
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(self.x + shadow_offset, self.y - shadow_offset)
        glVertex2f(self.x + self.width + shadow_offset, self.y - shadow_offset)
        glVertex2f(self.x + self.width + shadow_offset, self.y + self.height - shadow_offset)
        glVertex2f(self.x + shadow_offset, self.y + self.height - shadow_offset)
        glEnd()
        
        # Fundo
        glColor4f(*self.bg_color)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        
        # Borda
        glColor4f(*self.border_color)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        glLineWidth(1.0)
        
        # Renderiza componentes filhos
        for component in self.components:
            component.draw()
    
    def on_click(self, x, y):
        """Propaga clique para componentes filhos"""
        for component in self.components:
            if component.contains_point(x, y) and component.enabled:
                component.on_click(x, y)
                return True
        return False
