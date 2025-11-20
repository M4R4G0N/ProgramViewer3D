# """
# Sistema de renderização de fontes vetoriais OpenGL
# Suporta A-Z, 0-9 e caracteres especiais sem dependências externas
# """

# from OpenGL.GL import *
# import math


# class VectorFont:
#     """
#     Renderizador de texto vetorial usando OpenGL primitives (GL_LINES)
#     Cada caractere é definido como conjunto de segmentos de linha
#     Com suporte para curvas arredondadas
#     """
    
#     def __init__(self, smoothness=8):
#         """
#         Inicializa o sistema de fontes vetoriais
        
#         Args:
#             smoothness: Número de segmentos por curva (maior = mais suave)
#         """
#         self.smoothness = smoothness
#         self.strokes = self._init_stroke_dictionary()
    
#     def _arc(self, cx, cy, radius, start_angle, end_angle, segments=None):
#         """
#         Gera segmentos de linha para um arco circular
        
#         Args:
#             cx, cy: Centro do arco
#             radius: Raio do arco
#             start_angle: Ângulo inicial em graus
#             end_angle: Ângulo final em graus
#             segments: Número de segmentos (None = usa self.smoothness)
            
#         Returns:
#             Lista de tuplas (x1, y1, x2, y2)
#         """
#         if segments is None:
#             segments = self.smoothness
        
#         lines = []
#         angle_step = (end_angle - start_angle) / segments
        
#         for i in range(segments):
#             a1 = math.radians(start_angle + i * angle_step)
#             a2 = math.radians(start_angle + (i + 1) * angle_step)
            
#             x1 = cx + radius * math.cos(a1)
#             y1 = cy + radius * math.sin(a1)
#             x2 = cx + radius * math.cos(a2)
#             y2 = cy + radius * math.sin(a2)
            
#             lines.append((x1, y1, x2, y2))
        
#         return lines
    
#     def _circle(self, cx, cy, radius, segments=None):
#         """
#         Gera segmentos de linha para um círculo completo
        
#         Args:
#             cx, cy: Centro do círculo
#             radius: Raio
#             segments: Número de segmentos
            
#         Returns:
#             Lista de tuplas (x1, y1, x2, y2)
#         """
#         return self._arc(cx, cy, radius, 0, 360, segments)
    
#     def _init_stroke_dictionary(self):
#         """
#         Dicionário de traços (strokes) para cada caractere
#         Coordenadas normalizadas de 0.0 a 1.0
#         Formato: Lista de tuplas (x1, y1, x2, y2)
#         Agora com curvas arredondadas!
#         """
#         strokes = {}
        
#         # A - com topo arredondado
#         strokes['A'] = (
#             [(0, 0, 0, 0.7)] +  # Linha esquerda
#             self._arc(0.5, 0.7, 0.5, 180, 0) +  # Topo arredondado
#             [(1, 0.7, 1, 0)] +  # Linha direita
#             [(0.2, 0.4, 0.8, 0.4)]  # Barra horizontal
#         )
        
#         # B - com curvas arredondadas
#         strokes['B'] = (
#             [(0, 0, 0, 1)] +  # Linha vertical
#             [(0, 1, 0.5, 1)] +
#             self._arc(0.5, 0.75, 0.25, 90, -90, 6) +  # Curva superior
#             [(0, 0.5, 0.5, 0.5)] +
#             self._arc(0.5, 0.25, 0.25, 90, -90, 6) +  # Curva inferior
#             [(0, 0, 0.5, 0)]
#         )
        
#         # C - arco completo
#         strokes['C'] = self._arc(0.5, 0.5, 0.5, 135, -135, 10)
        
#         # D - com curva arredondada
#         strokes['D'] = (
#             [(0, 0, 0, 1)] +  # Linha vertical
#             [(0, 1, 0.3, 1)] +
#             self._arc(0.3, 0.5, 0.5, 90, -90, 8) +  # Curva direita
#             [(0, 0, 0.3, 0)]
#         )
        
#         # E
#         strokes['E'] = [(1, 1, 0, 1), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0.5, 0.7, 0.5)]
        
#         # F
#         strokes['F'] = [(0, 0, 0, 1), (0, 1, 1, 1), (0, 0.5, 0.7, 0.5)]
        
#         # G - arco com barra
#         strokes['G'] = (
#             self._arc(0.5, 0.5, 0.5, 135, -135, 10) +
#             [(1, 0.5, 1, 0.2), (1, 0.2, 0.5, 0.2)]
#         )
        
#         # H
#         strokes['H'] = [(0, 0, 0, 1), (1, 0, 1, 1), (0, 0.5, 1, 0.5)]
        
#         # I
#         strokes['I'] = [(0.5, 0, 0.5, 1), (0.2, 0, 0.8, 0), (0.2, 1, 0.8, 1)]
        
#         # J - com curva inferior
#         strokes['J'] = (
#             [(0.7, 1, 0.7, 0.3)] +
#             self._arc(0.4, 0.3, 0.3, 0, -180, 6)
#         )
        
#         # K
#         strokes['K'] = [(0, 0, 0, 1), (0, 0.5, 1, 1), (0, 0.5, 1, 0)]
        
#         # L
#         strokes['L'] = [(0, 1, 0, 0), (0, 0, 1, 0)]
        
#         # M
#         strokes['M'] = [(0, 0, 0, 1), (0, 1, 0.5, 0.5), (0.5, 0.5, 1, 1), (1, 1, 1, 0)]
        
#         # N
#         strokes['N'] = [(0, 0, 0, 1), (0, 1, 1, 0), (1, 0, 1, 1)]
        
#         # O - círculo completo
#         strokes['O'] = self._circle(0.5, 0.5, 0.5, 12)
        
#         # P - com curva superior
#         strokes['P'] = (
#             [(0, 0, 0, 1)] +
#             [(0, 1, 0.4, 1)] +
#             self._arc(0.4, 0.75, 0.25, 90, -90, 6) +
#             [(0, 0.5, 0.4, 0.5)]
#         )
        
#         # Q - círculo com rabinho
#         strokes['Q'] = self._circle(0.5, 0.5, 0.5, 12) + [(0.7, 0.3, 1, 0)]
        
#         # R - com curva superior
#         strokes['R'] = (
#             [(0, 0, 0, 1)] +
#             [(0, 1, 0.4, 1)] +
#             self._arc(0.4, 0.75, 0.25, 90, -90, 6) +
#             [(0, 0.5, 0.4, 0.5)] +
#             [(0.4, 0.5, 1, 0)]
#         )
        
#         # S - curva dupla
#         strokes['S'] = (
#             self._arc(0.3, 0.7, 0.3, 0, 180, 5) +
#             self._arc(0.7, 0.3, 0.3, 180, 360, 5)
#         )
        
#         # T
#         strokes['T'] = [(0, 1, 1, 1), (0.5, 1, 0.5, 0)]
        
#         # U - com fundo arredondado
#         strokes['U'] = (
#             [(0, 1, 0, 0.3)] +
#             self._arc(0.5, 0.3, 0.5, 180, 0, 8) +
#             [(1, 0.3, 1, 1)]
#         )
        
#         # V
#         strokes['V'] = [(0, 1, 0.5, 0), (0.5, 0, 1, 1)]
        
#         # W
#         strokes['W'] = [(0, 1, 0.25, 0), (0.25, 0, 0.5, 0.5), (0.5, 0.5, 0.75, 0), (0.75, 0, 1, 1)]
        
#         # X
#         strokes['X'] = [(0, 1, 1, 0), (1, 1, 0, 0)]
        
#         # Y
#         strokes['Y'] = [(0, 1, 0.5, 0.5), (1, 1, 0.5, 0.5), (0.5, 0.5, 0.5, 0)]
        
#         # Z
#         strokes['Z'] = [(0, 1, 1, 1), (1, 1, 0, 0), (0, 0, 1, 0)]
        
#         # Números com curvas
#         # 0 - oval
#         strokes['0'] = self._circle(0.5, 0.5, 0.5, 12) + [(0.2, 0.2, 0.8, 0.8)]
        
#         # 1
#         strokes['1'] = [(0.5, 0, 0.5, 1), (0.5, 1, 0.2, 0.7), (0.2, 0, 0.8, 0)]
        
#         # 2 - com curva superior
#         strokes['2'] = (
#             self._arc(0.5, 0.7, 0.3, 180, -45, 6) +
#             [(0.8, 0.5, 0, 0), (0, 0, 1, 0)]
#         )
        
#         # 3 - duas curvas
#         strokes['3'] = (
#             self._arc(0.5, 0.75, 0.25, 180, -90, 5) +
#             self._arc(0.5, 0.25, 0.25, 90, -90, 5)
#         )
        
#         # 4
#         strokes['4'] = [(0.7, 0, 0.7, 1), (0.7, 1, 0, 0.3), (0, 0.3, 1, 0.3)]
        
#         # 5 - com curva inferior
#         strokes['5'] = (
#             [(1, 1, 0, 1), (0, 1, 0, 0.5), (0, 0.5, 0.5, 0.5)] +
#             self._arc(0.5, 0.25, 0.25, 90, -90, 5)
#         )
        
#         # 6 - círculo inferior + curva
#         strokes['6'] = (
#             self._arc(0.5, 0.7, 0.3, 45, 180, 4) +
#             self._circle(0.5, 0.25, 0.25, 8)
#         )
        
#         # 7
#         strokes['7'] = [(0, 1, 1, 1), (1, 1, 0.4, 0)]
        
#         # 8 - dois círculos
#         strokes['8'] = (
#             self._circle(0.5, 0.7, 0.3, 8) +
#             self._circle(0.5, 0.3, 0.3, 8)
#         )
        
#         # 9 - círculo superior + curva
#         strokes['9'] = (
#             self._circle(0.5, 0.75, 0.25, 8) +
#             self._arc(0.5, 0.3, 0.3, -45, -180, 4)
#         )
        
#         # Pontuação
#         strokes['.'] = self._circle(0.5, 0.1, 0.1, 6)
#         strokes[':'] = self._circle(0.5, 0.2, 0.1, 6) + self._circle(0.5, 0.7, 0.1, 6)
#         strokes['-'] = [(0.1, 0.5, 0.9, 0.5)]
#         strokes['_'] = [(0, 0, 1, 0)]
#         strokes['/'] = [(0, 0, 1, 1)]
#         strokes['\\'] = [(0, 1, 1, 0)]
#         strokes['('] = self._arc(0.7, 0.5, 0.5, 135, -135, 8)
#         strokes[')'] = self._arc(0.3, 0.5, 0.5, 45, -225, 8)
#         strokes['+'] = [(0.5, 0.2, 0.5, 0.8), (0.2, 0.5, 0.8, 0.5)]
#         strokes['='] = [(0.1, 0.4, 0.9, 0.4), (0.1, 0.6, 0.9, 0.6)]
#         strokes[' '] = []
        
#         return strokes
    
#     def draw_char(self, char, x, y, width, height):
#         """
#         Desenha um único caractere vetorial
        
#         Args:
#             char: Caractere a desenhar
#             x, y: Posição base (canto inferior esquerdo)
#             width, height: Dimensões do caractere
#         """
#         key = char.upper()
#         if key in self.strokes:
#             for line in self.strokes[key]:
#                 x1, y1, x2, y2 = line
#                 glVertex2f(x + x1 * width, y + y1 * height)
#                 glVertex2f(x + x2 * width, y + y2 * height)
    
#     def draw_text(self, x, y, text, color=(1, 1, 1), font_size=1.0):
#         """
#         Renderiza texto completo na tela
        
#         Args:
#             x, y: Posição inicial do texto
#             text: String a ser renderizada
#             color: Tupla RGB (0-1)
#             font_size: Multiplicador de tamanho (1.0 = padrão)
#         """
#         # Desabilita depth test para overlay
#         glDisable(GL_DEPTH_TEST)
        
#         # Configurações de renderização
#         glLineWidth(1.5 * font_size)
#         glColor4f(color[0], color[1], color[2], 1.0)
        
#         # Dimensões do caractere (escalado)
#         char_width = 8.0 * font_size
#         char_height = 12.0 * font_size
#         spacing = 12.0 * font_size  # Espaçamento entre caracteres
        
#         # Renderiza todos os caracteres
#         glBegin(GL_LINES)
#         for i, char in enumerate(text):
#             cx = x + i * spacing
#             self.draw_char(char, cx, y, char_width, char_height)
#         glEnd()
        
#         # Restaura estado
#         glLineWidth(1.0)
#         glEnable(GL_DEPTH_TEST)
    
#     def measure_text(self, text, font_size=1.0):
#         """
#         Calcula largura total de um texto
        
#         Args:
#             text: String a medir
#             font_size: Multiplicador de tamanho
            
#         Returns:
#             Largura total em pixels
#         """
#         spacing = 12.0 * font_size
#         return len(text) * spacing
    
#     def add_custom_char(self, char, strokes):
#         """
#         Adiciona caractere customizado ao dicionário
        
#         Args:
#             char: Caractere (string)
#             strokes: Lista de tuplas (x1, y1, x2, y2) normalizadas
#         """
#         self.strokes[char.upper()] = strokes
"""
Sistema de renderização de fontes vetoriais OpenGL - Estilo Arial (Sans-Serif)
Suporta A-Z, 0-9 e caracteres especiais sem dependências externas.
"""

from OpenGL.GL import *
import math

class VectorFont:
    """
    Renderizador de texto vetorial estilo Sans-Serif (Arial-like).
    Limpo, geométrico e sem serifas.
    """
    
    def __init__(self, smoothness=12):
        """
        Args:
            smoothness: Aumentado o padrão para 12 para curvas mais redondas estilo Arial
        """
        self.smoothness = smoothness
        self.strokes = self._init_stroke_dictionary()
    
    def _arc(self, cx, cy, radius, start_angle, end_angle, segments=None):
        """Gera segmentos de linha para um arco circular"""
        if segments is None:
            segments = self.smoothness
        
        lines = []
        # Garante que steps sejam inteiros se a diferença for grande, ou mínimo 1
        diff = abs(end_angle - start_angle)
        if segments < 2: segments = 2
            
        angle_step = (end_angle - start_angle) / segments
        
        for i in range(segments):
            a1 = math.radians(start_angle + i * angle_step)
            a2 = math.radians(start_angle + (i + 1) * angle_step)
            
            x1 = cx + radius * math.cos(a1)
            y1 = cy + radius * math.sin(a1)
            x2 = cx + radius * math.cos(a2)
            y2 = cy + radius * math.sin(a2)
            
            lines.append((x1, y1, x2, y2))
        
        return lines
    
    def _bezier(self, x0, y0, cx, cy, x1, y1, segments=None):
        """
        Gera segmentos de linha para uma curva Bezier quadrática
        
        Args:
            x0, y0: Ponto inicial
            cx, cy: Ponto de controle
            x1, y1: Ponto final
            segments: Número de segmentos (None = usa self.smoothness)
            
        Returns:
            Lista de tuplas (x1, y1, x2, y2)
        """
        if segments is None:
            segments = self.smoothness
        
        if segments < 2:
            segments = 2
        
        lines = []
        for i in range(segments):
            t1 = i / segments
            t2 = (i + 1) / segments
            
            # Fórmula de Bezier quadrática: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            bx1 = (1-t1)**2 * x0 + 2*(1-t1)*t1 * cx + t1**2 * x1
            by1 = (1-t1)**2 * y0 + 2*(1-t1)*t1 * cy + t1**2 * y1
            bx2 = (1-t2)**2 * x0 + 2*(1-t2)*t2 * cx + t2**2 * x1
            by2 = (1-t2)**2 * y0 + 2*(1-t2)*t2 * cy + t2**2 * y1
            
            lines.append((bx1, by1, bx2, by2))
        
        return lines
    
    def _bezier_cubic(self, x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments=None):
        """
        Gera segmentos de linha para uma curva Bezier cúbica
        
        Args:
            x0, y0: Ponto inicial
            cx1, cy1: Primeiro ponto de controle
            cx2, cy2: Segundo ponto de controle
            x1, y1: Ponto final
            segments: Número de segmentos (None = usa self.smoothness)
            
        Returns:
            Lista de tuplas (x1, y1, x2, y2)
        """
        if segments is None:
            segments = self.smoothness
        
        if segments < 2:
            segments = 2
        
        lines = []
        for i in range(segments):
            t1 = i / segments
            t2 = (i + 1) / segments
            
            # Fórmula de Bezier cúbica: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
            bx1 = (1-t1)**3 * x0 + 3*(1-t1)**2*t1 * cx1 + 3*(1-t1)*t1**2 * cx2 + t1**3 * x1
            by1 = (1-t1)**3 * y0 + 3*(1-t1)**2*t1 * cy1 + 3*(1-t1)*t1**2 * cy2 + t1**3 * y1
            bx2 = (1-t2)**3 * x0 + 3*(1-t2)**2*t2 * cx1 + 3*(1-t2)*t2**2 * cx2 + t2**3 * x1
            by2 = (1-t2)**3 * y0 + 3*(1-t2)**2*t2 * cy1 + 3*(1-t2)*t2**2 * cy2 + t2**3 * y1
            
            lines.append((bx1, by1, bx2, by2))
        
        return lines
    
    def _circle(self, cx, cy, radius, segments=None):
        """Gera círculo completo"""
        return self._arc(cx, cy, radius, 0, 360, segments)
    
    def _init_stroke_dictionary(self):
        """
        Carrega dicionário de caracteres do char.json
        Se não existir, usa valores hardcoded como fallback
        """
        import json
        import os
        
        # Tenta carregar do JSON
        json_path = os.path.join(os.path.dirname(__file__), '..', 'char.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                
                strokes = {}
                for char_key, stroke_list in char_data.items():
                    char_strokes = []
                    
                    for stroke in stroke_list:
                        if stroke['type'] == 'line':
                            # Adiciona linha como tupla
                            char_strokes.append((
                                stroke['x1'],
                                stroke['y1'],
                                stroke['x2'],
                                stroke['y2']
                            ))
                        elif stroke['type'] == 'arc':
                            # Gera segmentos do arco
                            arc_segments = self._arc(
                                stroke['cx'],
                                stroke['cy'],
                                stroke['radius'],
                                stroke['start_angle'],
                                stroke['end_angle'],
                                stroke.get('segments', 12)
                            )
                            char_strokes.extend(arc_segments)
                        elif stroke['type'] == 'bezier':
                            # Gera segmentos da curva Bezier quadrática
                            bezier_segments = self._bezier(
                                stroke['x0'],
                                stroke['y0'],
                                stroke['cx'],
                                stroke['cy'],
                                stroke['x1'],
                                stroke['y1'],
                                stroke.get('segments', 12)
                            )
                            char_strokes.extend(bezier_segments)
                        elif stroke['type'] == 'bezier_cubic':
                            # Gera segmentos da curva Bezier cúbica
                            bezier_segments = self._bezier_cubic(
                                stroke['x0'],
                                stroke['y0'],
                                stroke['cx1'],
                                stroke['cy1'],
                                stroke['cx2'],
                                stroke['cy2'],
                                stroke['x1'],
                                stroke['y1'],
                                stroke.get('segments', 12)
                            )
                            char_strokes.extend(bezier_segments)
                    
                    strokes[char_key] = char_strokes
                
                return strokes
            except Exception as e:
                print(f"⚠️  Erro ao carregar char.json: {e}")
                print("📋 Usando fonte hardcoded como fallback")
        
        # Fallback: dicionário hardcoded
        return self._init_stroke_dictionary_hardcoded()
    
    def _init_stroke_dictionary_hardcoded(self):
        """
        Dicionário estilo Arial / Helvetica (Sans-Serif).
        Coordenadas normalizadas 0.0 a 1.0.
        """
        strokes = {}
        
        # === LETRAS MAIÚSCULAS ===
        
        # A - Topo pontudo, sem serifa
        strokes['A'] = [
            (0, 0, 0.5, 1),     # Diagonal esquerda
            (0.5, 1, 1, 0),     # Diagonal direita
            (0.25, 0.4, 0.75, 0.4) # Barra horizontal (mais baixa estilo arial)
        ]
        
        # B - Duas curvas limpas à direita
        strokes['B'] = (
            [(0, 0, 0, 1)] +    # Haste vertical
            [(0, 1, 0.5, 1)] +  # Topo
            self._arc(0.5, 0.75, 0.25, 90, -90) + # Curva superior
            [(0.5, 0.5, 0, 0.5)] + # Meio
            self._arc(0.5, 0.25, 0.25, 90, -90) + # Curva inferior
            [(0.5, 0, 0, 0)]    # Base
        )
        
        # C - Aberto e geométrico
        strokes['C'] = self._arc(0.55, 0.5, 0.5, 60, 300, 12)
        
        # D - Haste e arco único
        strokes['D'] = (
            [(0, 0, 0, 1)] +
            [(0, 1, 0.4, 1)] +
            self._arc(0.4, 0.5, 0.5, 90, -90, 14) +
            [(0.4, 0, 0, 0)]
        )
        
        # E - Barras retas, sem serifa
        strokes['E'] = [
            (0, 0, 0, 1),       # Vertical
            (0, 1, 0.9, 1),     # Topo
            (0, 0.5, 0.8, 0.5), # Meio (levemente menor)
            (0, 0, 0.9, 0)      # Base
        ]
        
        # F - Igual E sem base
        strokes['F'] = [
            (0, 0, 0, 1),
            (0, 1, 0.9, 1),
            (0, 0.5, 0.8, 0.5)
        ]
        
        # G - Sem espora (spur), estilo moderno
        strokes['G'] = (
            self._arc(0.5, 0.5, 0.5, 45, 315, 14) + # Arco grande
            [(0.9, 0.35, 0.9, 0), (0.9, 0, 0.5, 0)] # Perna reta simples
             # Nota: Arial moderno às vezes não tem barra horizontal interna, 
             # mas mantivemos a perna vertical para legibilidade
        )
        strokes['G'] = (
             self._arc(0.5, 0.5, 0.5, 60, 360, 14) + # Arco C
             [(1.0, 0.5, 1.0, 0.0), (1.0, 0.0, 0.5, 0.0)] # Canto reto
        )
        # Correção para G mais estilo Arial tradicional (com traço horizontal)
        strokes['G'] = (
            self._arc(0.5, 0.5, 0.5, 45, 300, 12) + 
            [(1.0, 0.4, 0.5, 0.4), (1.0, 0.4, 1.0, 0.0)]
        )

        # H - Reto simples
        strokes['H'] = [
            (0, 0, 0, 1),
            (1, 0, 1, 1),
            (0, 0.5, 1, 0.5)
        ]
        
        # I - Apenas um traço (sem serifas topo/base)
        strokes['I'] = [(0.5, 0, 0.5, 1)]
        
        # J - Gancho simples, sem topo
        strokes['J'] = (
            [(0.7, 1, 0.7, 0.3)] +
            self._arc(0.35, 0.3, 0.35, 0, -180, 8)
        )
        
        # K - Perna superior saindo da haste, inferior saindo da perna (estilo grotesco)
        strokes['K'] = [
            (0, 0, 0, 1),
            (0, 0.4, 1, 1),
            (0.4, 0.6, 1, 0)
        ]
        
        # L - Simples
        strokes['L'] = [(0, 1, 0, 0), (0, 0, 0.8, 0)]
        
        # M - Hastes retas, meio toca a base
        strokes['M'] = [
            (0, 0, 0, 1),       # Esquerda sobe
            (0, 1, 0.5, 0),     # Meio desce
            (0.5, 0, 1, 1),     # Meio sobe
            (1, 1, 1, 0)        # Direita desce
        ]
        
        # N - Reto
        strokes['N'] = [
            (0, 0, 0, 1),
            (0, 1, 1, 0),
            (1, 0, 1, 1)
        ]
        
        # O - Oval geométrico
        strokes['O'] = self._arc(0.5, 0.5, 0.5, 0, 360, 16)
        
        # P - Fechado
        strokes['P'] = (
            [(0, 0, 0, 1)] +
            [(0, 1, 0.5, 1)] +
            self._arc(0.5, 0.75, 0.25, 90, -90, 8) +
            [(0.5, 0.5, 0, 0.5)]
        )
        
        # Q - O com traço simples cruzando
        strokes['Q'] = (
            self._arc(0.5, 0.5, 0.5, 0, 360, 16) +
            [(0.6, 0.3, 1.0, -0.1)] # Traço saindo pra fora
        )
        
        # R - Perna reta (estilo Arial)
        strokes['R'] = (
            [(0, 0, 0, 1)] +
            [(0, 1, 0.5, 1)] +
            self._arc(0.5, 0.75, 0.25, 90, -90, 8) +
            [(0.5, 0.5, 0, 0.5)] +
            [(0.5, 0.5, 1, 0)] # Perna reta diagonal
        )
        
        # S - Estilo Arial: Arco superior e inferior conectados suavemente
        # O truque é estender os arcos para além da metade para criar a diagonal curva
        strokes['S'] = (
            # Arco Superior (da direita para esquerda/baixo)
            self._arc(0.5, 0.74, 0.26, 45, 250) +
            
            # Pequena conexão central (para garantir que não haja buracos)
            [(0.41, 0.49, 0.59, 0.51)] +
            
            # Arco Inferior (da direita/cima para esquerda)
            self._arc(0.5, 0.26, 0.26, 70, -135)
        )
        # # Simplificando S para visual melhor em low-poly
        # strokes['S'] = (
        #      self._arc(0.5, 0.75, 0.25, 90, 270) +
        #      self._arc(0.5, 0.25, 0.25, -90, 90)
        # )
        
        # T - Sem serifa
        strokes['T'] = [(0, 1, 1, 1), (0.5, 1, 0.5, 0)]
        
        # U - Sem haste vertical direita descendo
        strokes['U'] = (
            [(0, 1, 0, 0.35)] +
            # self._arc(0.5, 0.5, 0.5, 0, 360, 16)
            self._arc(0.5, 0.5, 0.5, 180, 360, 10) +
            [(1, 0.35, 1, 1)]
        )
        
        # V - Bico afiado na base
        strokes['V'] = [(0, 1, 0.5, 0), (0.5, 0, 1, 1)]
        
        # W - Igual M invertido
        strokes['W'] = [
            (0, 1, 0.2, 0),
            (0.2, 0, 0.5, 0.8),
            (0.5, 0.8, 0.8, 0),
            (0.8, 0, 1, 1)
        ]
        
        # X
        strokes['X'] = [(0, 1, 1, 0), (1, 1, 0, 0)]
        
        # Y - Geométrico
        strokes['Y'] = [(0, 1, 0.5, 0.5), (1, 1, 0.5, 0.5), (0.5, 0.5, 0.5, 0)]
        
        # Z
        strokes['Z'] = [(0, 1, 1, 1), (1, 1, 0, 0), (0, 0, 1, 0)]
        
        # === NÚMEROS ===
        
        # 0 - Oval alto
        strokes['0'] = self._arc(0.5, 0.5, 0.5, 0, 360, 14) + [(0.5, 0.5, 0.5, 0.5)] # Ponto no meio removido, apenas oval
        strokes['0'] = (
            [(0, 0.3, 0, 0.7), (1, 0.3, 1, 0.7)] +
            self._arc(0.5, 0.7, 0.5, 0, 180) +
            self._arc(0.5, 0.3, 0.5, 180, 360)
        )
        
        # 1 - Estilo Arial: Bico inclinado e haste reta. SEM base.
        strokes['1'] = [(0.2, 0.7, 0.5, 1), (0.5, 1, 0.5, 0)]
        
        # 2
        strokes['2'] = (
            self._arc(0.5, 0.75, 0.25, 180, 0) +
            [(0.75, 0.75, 0, 0), (0, 0, 1, 0)]
        )
        
        # 3
        strokes['3'] = (
            [(0, 1, 1, 1), (1, 1, 0.5, 0.5)] + # Topo reto estilo '7' mas curvo no meio? Arial 3 é arredondado.
            self._arc(0.5, 0.75, 0.25, 170, -80) + # Redefinindo para 3 arredondado
            self._arc(0.5, 0.25, 0.25, 90, -180)
        )
        # Ajuste para 3 mais limpo
        strokes['3'] = (
             self._arc(0.5, 0.75, 0.25, 45, 270) +
             self._arc(0.5, 0.25, 0.25, -90, 135)
        )

        # 4 - Aberto ou Fechado? Arial é fechado.
        strokes['4'] = [(0.75, 0, 0.75, 1), (0.75, 1, 0, 0.4), (0, 0.4, 1, 0.4)]
        
        # 5
        strokes['5'] = (
            [(0.8, 1, 0, 1), (0, 1, 0, 0.6)] +
            self._arc(0.45, 0.35, 0.35, 160, -100) # Barriga
        )
        
        # 6 - Aberto em cima (estilo moderno) ou fechado? Arial é fechado.
        strokes['6'] = (
             self._arc(0.5, 0.25, 0.25, 0, 360) + # Barriga
             self._arc(0.5, 0.5, 0.5, 100, 180) + # Pescoço curvado
             [(0.05, 0.55, 0.5, 1.0)] # Reta final topo
        )
        
        # 7 - Simples
        strokes['7'] = [(0, 1, 1, 1), (1, 1, 0.3, 0)]
        
        # 8 - Boneco de neve
        strokes['8'] = (
            self._arc(0.5, 0.73, 0.27, 0, 360, 10) +
            self._arc(0.5, 0.27, 0.27, 0, 360, 10)
        )
        
        # 9 - Círculo topo, perna curva
        strokes['9'] = (
             self._arc(0.5, 0.75, 0.25, 0, 360) + # Cabeça
             self._arc(0.5, 0.5, 0.5, 0, -80) +   # Pescoço descendo
             [(1.0, 0.5, 0.5, 0.0)]
        )
        
        # Pontuação (Simplificada)
        strokes['.'] = [(0.4, 0, 0.4, 0.1), (0.4, 0.1, 0.6, 0.1), (0.6, 0.1, 0.6, 0), (0.6, 0, 0.4, 0)] # Quadrado preenchido fake
        strokes['-'] = [(0.1, 0.5, 0.9, 0.5)]
        strokes['+'] = [(0.5, 0.2, 0.5, 0.8), (0.2, 0.5, 0.8, 0.5)]
        strokes['='] = [(0.1, 0.4, 0.9, 0.4), (0.1, 0.6, 0.9, 0.6)]
        strokes[' '] = []
        
        return strokes
    
    def draw_char(self, char, x, y, width, height):
        """Desenha caractere"""
        key = char.upper()
        if key in self.strokes:
            for line in self.strokes[key]:
                x1, y1, x2, y2 = line
                glVertex2f(x + x1 * width, y + y1 * height)
                glVertex2f(x + x2 * width, y + y2 * height)
    
    def draw_text(self, x, y, text, color=(1, 1, 1), font_size=1.0):
        """Renderiza texto"""
        # Salva estado do depth test (não forçamos mudança aqui)
        depth_test_was_enabled = glIsEnabled(GL_DEPTH_TEST)
        
        glLineWidth(2.0 * font_size)  # Linhas mais grossas para melhor visualização
        glColor4f(color[0], color[1], color[2], 1.0)
        
        # Proporções ajustadas para melhor visualização
        # Mantém aspect ratio quadrado para evitar deformação
        char_width = 10.0 * font_size
        char_height = 14.0 * font_size
        spacing = 12.0 * font_size  # Espaçamento entre caracteres
        
        glBegin(GL_LINES)
        for i, char in enumerate(text):
            cx = x + i * spacing
            self.draw_char(char, cx, y, char_width, char_height)
        glEnd()
        
        glLineWidth(1.0)
        
        # Restaura depth test apenas se estava desabilitado
        if not depth_test_was_enabled:
            glDisable(GL_DEPTH_TEST)

    def measure_text(self, text, font_size=1.0):
        """Mede a largura do texto em pixels"""
        spacing = 12.0 * font_size
        return len(text) * spacing
    def add_custom_char(self, char, strokes):
        """
        Adiciona caractere customizado ao dicionário
        
        Args:
            char: Caractere (string)
            strokes: Lista de tuplas (x1, y1, x2, y2) normalizadas
        """
        self.strokes[char.upper()] = strokes
