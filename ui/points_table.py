"""
Janela de tabela de pontos usando GLFW/OpenGL
Exibe os pontos em formato tabular com scroll
"""

import glfw
from OpenGL.GL import *
import numpy as np
from ui.vector_font import VectorFont


class PointsTableWindow:
    """Janela separada mostrando tabela de pontos"""
    
    def __init__(self, vertices, colors=None, filename=None, app=None):
        """
        Inicializa janela de tabela
        
        Args:
            vertices: Array numpy (N, 3) ou flat (N*3,) com coordenadas XYZ
            colors: Array numpy (N, 3) ou flat (N*3,) com cores RGB (opcional)
            filename: Nome do arquivo (opcional)
            app: Referência à aplicação principal (para mover câmera ao clicar)
        """
        # Garante que vertices está em formato (N, 3)
        if vertices.ndim == 1:
            vertices = vertices.reshape(-1, 3)
        elif vertices.shape[1] != 3:
            raise ValueError(f"Vertices deve ter shape (N, 3) ou flat, mas tem {vertices.shape}")
        
        self.vertices = vertices
        
        # Garante que colors está em formato (N, 3) se fornecido
        if colors is not None:
            if colors.ndim == 1:
                colors = colors.reshape(-1, 3)
            elif colors.shape[1] != 3:
                raise ValueError(f"Colors deve ter shape (N, 3) ou flat, mas tem {colors.shape}")
        
        self.colors = colors
        
        self.filename = filename or "Dados"
        self.font = VectorFont()
        self.app = app  # Referência à aplicação principal
        
        # Estado da janela
        self.window = None
        self.width = 800
        self.height = 600
        
        # Scroll
        self.scroll_offset = 0
        self.row_height = 25
        self.visible_rows = 20  # Inicializa com valor padrão
        self.header_height = 60
        
        # Seleção
        self.selected_row = None
        
        # Número de pontos
        self.num_points = len(vertices)
        
    def run(self):
        """Executa a janela de tabela"""
        # Salva o contexto atual antes de criar nova janela
        previous_context = glfw.get_current_context()
        
        if not glfw.init():
            print("❌ Erro ao inicializar GLFW")
            return
        
        # Não força versão específica - usa compatibilidade
        # Isso permite usar glMatrixMode e glBegin/glEnd
        
        # Cria janela
        self.window = glfw.create_window(
            self.width, self.height,
            f"Tabela de Pontos - {self.filename} ({self.num_points} pontos)",
            None, None
        )
        
        if not self.window:
            print("❌ Erro ao criar janela de tabela")
            # Restaura contexto anterior
            if previous_context:
                glfw.make_context_current(previous_context)
            return
        
        glfw.make_context_current(self.window)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)
        
        # Configurações OpenGL
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Loop principal
        while not glfw.window_should_close(self.window):
            self._render()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        # Cleanup
        glfw.destroy_window(self.window)
        
        # Restaura o contexto anterior (janela principal)
        if previous_context:
            glfw.make_context_current(previous_context)
            print("✅ Contexto OpenGL restaurado")
    
    def _scroll_callback(self, window, xoffset, yoffset):
        """Callback de scroll"""
        # Atualiza offset (inverte para scroll natural)
        self.scroll_offset -= int(yoffset * 3)
        
        # Limita scroll
        max_scroll = max(0, self.num_points - self.visible_rows)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
    
    def _mouse_button_callback(self, window, button, action, mods):
        """Callback de clique do mouse"""
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            # Pega posição do mouse
            xpos, ypos = glfw.get_cursor_pos(window)
            
            # Converte para coordenadas da janela (origem no canto inferior esquerdo)
            ypos = self.height - ypos
            
            # Verifica se clicou na área de conteúdo (abaixo do header)
            if ypos < (self.height - self.header_height):
                # Calcula qual linha foi clicada
                content_y = self.height - self.header_height - ypos
                row_index = int(content_y / self.row_height)
                
                # Ajusta pelo scroll offset
                actual_row = self.scroll_offset + row_index
                
                if 0 <= actual_row < self.num_points:
                    self.selected_row = actual_row
                    print(f"🔍 Ponto {actual_row} selecionado: {self.vertices[actual_row]}")
                    
                    # Move câmera para o ponto selecionado (se app foi fornecido)
                    if self.app:
                        point = self.vertices[actual_row]
                        self.app.camera.set_target(float(point[0]), float(point[1]), float(point[2]))
                        print(f"📍 Câmera movida para: X={point[0]:.3f}, Y={point[1]:.3f}, Z={point[2]:.3f}")
    
    def _render(self):
        """Renderiza a tabela"""
        # Atualiza tamanho
        self.width, self.height = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, self.width, self.height)
        
        # Limpa tela
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Configura projeção ortográfica
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Calcula linhas visíveis
        header_height = 60
        self.visible_rows = (self.height - header_height) // self.row_height
        
        # Renderiza cabeçalho
        self._render_header(header_height)
        
        # Renderiza linhas
        self._render_rows(header_height)
        
        # Renderiza barra de scroll
        self._render_scrollbar()
        
        # Renderiza informações de rodapé
        self._render_footer()
    
    def _render_header(self, header_height):
        """Renderiza cabeçalho da tabela"""
        # Fundo do cabeçalho
        glColor4f(0.2, 0.2, 0.2, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, self.height - header_height)
        glVertex2f(self.width, self.height - header_height)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # Linhas de separação
        glColor4f(0.4, 0.4, 0.4, 1.0)
        glLineWidth(2)
        glBegin(GL_LINES)
        # Linha inferior do cabeçalho
        glVertex2f(0, self.height - header_height)
        glVertex2f(self.width, self.height - header_height)
        glEnd()
        
        # Colunas verticais
        col_widths = [80, 200, 200, 200]  # Índice, X, Y, Z
        x_pos = 0
        for width in col_widths[:-1]:
            x_pos += width
            glBegin(GL_LINES)
            glVertex2f(x_pos, self.height - header_height)
            glVertex2f(x_pos, self.height)
            glEnd()
        
        glLineWidth(1)
        
        # Texto do cabeçalho com VectorFont
        self.font.draw_text(30, self.height - 35, "#", color=(1, 1, 1), font_size=0.9)
        self.font.draw_text(140, self.height - 35, "X", color=(1, 0.5, 0.5), font_size=0.9)
        self.font.draw_text(340, self.height - 35, "Y", color=(0.5, 1, 0.5), font_size=0.9)
        self.font.draw_text(540, self.height - 35, "Z", color=(0.5, 0.5, 1), font_size=0.9)
    
    def _render_rows(self, header_height):
        """Renderiza linhas da tabela"""
        col_widths = [80, 200, 200, 200]
        
        # Área de conteúdo
        content_height = self.height - header_height
        start_row = self.scroll_offset
        end_row = min(start_row + self.visible_rows + 1, self.num_points)
        
        for i in range(start_row, end_row):
            row_index = i - start_row
            y_top = self.height - header_height - (row_index * self.row_height)
            y_bottom = y_top - self.row_height
            
            if y_bottom < 0:
                break
            
            # Cor de fundo
            if i == self.selected_row:
                # Destaque para linha selecionada
                glColor4f(0.3, 0.4, 0.5, 1.0)
            elif i % 2 == 0:
                glColor4f(0.18, 0.18, 0.18, 1.0)
            else:
                glColor4f(0.15, 0.15, 0.15, 1.0)
            
            glBegin(GL_QUADS)
            glVertex2f(0, y_bottom)
            glVertex2f(self.width, y_bottom)
            glVertex2f(self.width, y_top)
            glVertex2f(0, y_top)
            glEnd()
            
            # Linhas de grade
            glColor4f(0.25, 0.25, 0.25, 1.0)
            glBegin(GL_LINES)
            glVertex2f(0, y_bottom)
            glVertex2f(self.width, y_bottom)
            glEnd()
            
            # Dados do ponto com VectorFont
            vertex = self.vertices[i]
            y_text = y_top - self.row_height // 2 - 5
            
            # Índice
            self.font.draw_text(20, y_text, str(i), color=(0.7, 0.7, 1.0), font_size=0.7)
            
            # Coordenadas XYZ
            if self.colors is not None:
                color = self.colors[i]
            else:
                color = (0.8, 0.8, 0.8)
            
            self.font.draw_text(90, y_text, f"{vertex[0]:.3f}", color=(1, 0.7, 0.7), font_size=0.7)
            self.font.draw_text(290, y_text, f"{vertex[1]:.3f}", color=(0.7, 1, 0.7), font_size=0.7)
            self.font.draw_text(490, y_text, f"{vertex[2]:.3f}", color=(0.7, 0.7, 1), font_size=0.7)
    
    def _render_scrollbar(self):
        """Renderiza barra de scroll"""
        if self.num_points <= self.visible_rows:
            return
        
        # Barra de fundo
        scrollbar_width = 15
        scrollbar_x = self.width - scrollbar_width
        
        glColor4f(0.1, 0.1, 0.1, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(scrollbar_x, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height - self.header_height)
        glVertex2f(scrollbar_x, self.height - self.header_height)
        glEnd()
        
        # Thumb da scrollbar
        available_height = self.height - self.header_height
        max_scroll = max(1, self.num_points - self.visible_rows)
        
        # Proporção do conteúdo visível
        thumb_height = max(30, (self.visible_rows / self.num_points) * available_height)
        
        # Posição do thumb baseada no scroll offset
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            thumb_y = (available_height - thumb_height) * (1 - scroll_ratio)
        else:
            thumb_y = 0
        
        glColor4f(0.5, 0.5, 0.5, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(scrollbar_x + 2, thumb_y)
        glVertex2f(self.width - 2, thumb_y)
        glVertex2f(self.width - 2, thumb_y + thumb_height)
        glVertex2f(scrollbar_x + 2, thumb_y + thumb_height)
        glEnd()
    
    def _render_footer(self):
        """Renderiza informações de rodapé"""
        # Fundo do rodapé
        footer_height = 25
        glColor4f(0.18, 0.18, 0.18, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, footer_height)
        glVertex2f(0, footer_height)
        glEnd()
        
        # Linha superior
        glColor4f(0.3, 0.3, 0.3, 1.0)
        glBegin(GL_LINES)
        glVertex2f(0, footer_height)
        glVertex2f(self.width, footer_height)
        glEnd()
        
        # Texto com informações
        start = self.scroll_offset + 1
        end = min(self.scroll_offset + self.visible_rows, self.num_points)
        info_text = f"Mostrando {start}-{end} de {self.num_points} pontos"
        
        self.font.draw_text(10, 8, info_text, color=(0.7, 0.7, 0.7), font_size=0.7)
        
        # Se houver linha selecionada, mostra informação
        if self.selected_row is not None:
            sel_text = f"Selecionado: #{self.selected_row}"
            self.font.draw_text(self.width - 200, 8, sel_text, color=(0.5, 0.8, 1.0), font_size=0.7)
