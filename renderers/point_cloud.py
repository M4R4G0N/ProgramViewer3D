"""
Renderizador de nuvens de pontos 3D com OpenGL
Suporta grandes volumes de dados com VBOs (Vertex Buffer Objects)
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class PointCloudRenderer:
    """
    Renderizador otimizado para nuvens de pontos 3D
    Usa VBOs (Vertex Buffer Objects) para máxima performance com milhões de pontos
    """
    
    def __init__(self):
        """Inicializa o renderizador"""
        self.vertices = None
        self.colors = None
        self.n_vertices = 0
        self.point_size = 3.0
        self.visible = True
        
        # VBO handles
        self.vbo_vertices = None
        self.vbo_colors = None
        self.use_vbo = True
        
        # LOD (Level of Detail) - renderiza apenas uma fração dos pontos quando há muitos
        self.enable_lod = False
        self.lod_threshold = 1000000  # Acima de 1M pontos, usa LOD
        self.max_points_render = 2000000  # Máximo de pontos a renderizar por frame
        
        # Cache de centro (evita recalcular média a cada frame)
        self._cached_center = None
    
    def set_data(self, vertices, colors):
        """
        Define os dados a serem renderizados
        
        Args:
            vertices: np.array shape (N, 3) com coordenadas X, Y, Z
            colors: np.array shape (N, 3) com cores R, G, B (0-1)
        """
        if vertices.shape[1] != 3:
            raise ValueError("Vertices devem ter shape (N, 3)")
        if colors.shape[1] != 3:
            raise ValueError("Colors devem ter shape (N, 3)")
        if len(vertices) != len(colors):
            raise ValueError("Vertices e colors devem ter mesmo comprimento")
        
        # Limpa VBOs antigos se existirem
        self._cleanup_vbo()
        
        # Flatten para formato OpenGL
        self.vertices = vertices.flatten().astype(np.float32)
        self.colors = colors.flatten().astype(np.float32)
        self.n_vertices = len(vertices)
        
        # Calcula e cacheia o centro AGORA (uma vez só)
        verts = vertices  # vertices original em (N, 3)
        self._cached_center = tuple(verts.mean(axis=0))
        
        # Cria VBOs para dados grandes (>100k pontos)
        if self.use_vbo and self.n_vertices > 100000:
            self._create_vbo()
            
            # Info sobre LOD
            if self.enable_lod and self.n_vertices > self.lod_threshold:
                stride = max(1, self.n_vertices // self.max_points_render)
                points_rendered = self.n_vertices // stride
                print(f"✅ Renderer configurado: {self.n_vertices:,} pontos (usando VBO)")
                print(f"⚡ LOD ativo: renderizando {points_rendered:,} pontos (~{100*points_rendered/self.n_vertices:.1f}%) para melhor desempenho")
            else:
                print(f"✅ Renderer configurado: {self.n_vertices:,} pontos (usando VBO)")
        else:
            print(f"✅ Renderer configurado: {self.n_vertices:,} pontos (usando vertex arrays)")
    
    def _create_vbo(self):
        """Cria Vertex Buffer Objects para os dados"""
        # Gera buffers
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_colors = glGenBuffers(1)
        
        # Buffer de vértices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Buffer de cores
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_colors)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
        
        # Desliga binding
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    def _cleanup_vbo(self):
        """Libera VBOs antigos"""
        if self.vbo_vertices is not None:
            glDeleteBuffers(1, [self.vbo_vertices])
            self.vbo_vertices = None
        if self.vbo_colors is not None:
            glDeleteBuffers(1, [self.vbo_colors])
            self.vbo_colors = None
    
    def set_point_size(self, size):
        """
        Define o tamanho dos pontos
        
        Args:
            size: Tamanho em pixels (1.0 - 10.0)
        """
        self.point_size = max(1.0, min(10.0, size))
        glPointSize(self.point_size)
    
    def get_point_size(self):
        """Retorna tamanho atual dos pontos"""
        return self.point_size
    
    def set_lod_enabled(self, enabled):
        """
        Ativa/desativa Level of Detail
        
        Args:
            enabled: True para ativar LOD, False para desativar
        """
        self.enable_lod = enabled
        if enabled:
            print(f"⚡ LOD ativado (max {self.max_points_render:,} pontos/frame)")
        else:
            print(f"🎨 LOD desativado (renderiza todos os {self.n_vertices:,} pontos)")
    
    def set_lod_max_points(self, max_points):
        """
        Define quantidade máxima de pontos a renderizar quando LOD está ativo
        
        Args:
            max_points: Número máximo de pontos (sugere-se entre 500k e 5M)
        """
        self.max_points_render = max(100000, int(max_points))
        print(f"⚡ LOD: máximo de {self.max_points_render:,} pontos por frame")
    
    def get_render_stats(self):
        """
        Retorna estatísticas de renderização
        
        Returns:
            Dict com info sobre pontos renderizados
        """
        stride = 1
        points_rendered = self.n_vertices
        
        if self.enable_lod and self.n_vertices > self.lod_threshold:
            stride = max(1, self.n_vertices // self.max_points_render)
            points_rendered = self.n_vertices // stride
        
        return {
            'total_points': self.n_vertices,
            'rendered_points': points_rendered,
            'stride': stride,
            'percentage': 100.0 * points_rendered / max(1, self.n_vertices),
            'lod_active': self.enable_lod and self.n_vertices > self.lod_threshold
        }
    
    def render(self):
        """Renderiza a nuvem de pontos"""
        if not self.visible or self.vertices is None:
            return
        
        # Configura tamanho dos pontos
        glPointSize(self.point_size)
        
        # Calcula quantos pontos renderizar (LOD)
        points_to_render = self.n_vertices
        stride = 1  # Passo entre pontos (1 = todos, 2 = metade, etc)
        
        if self.enable_lod and self.n_vertices > self.lod_threshold:
            # Calcula stride necessário para ficar dentro do limite
            stride = max(1, self.n_vertices // self.max_points_render)
            points_to_render = self.n_vertices // stride
        
        # Renderiza usando VBO ou vertex arrays
        if self.vbo_vertices is not None:
            self._render_vbo(points_to_render, stride)
        else:
            self._render_vertex_array(points_to_render, stride)
    
    def _render_vbo(self, points_to_render=None, stride=1):
        """Renderiza usando VBOs (mais eficiente para muitos pontos)
        
        Args:
            points_to_render: Quantidade de pontos a renderizar (None = todos)
            stride: Passo entre pontos (1 = todos, 2 = metade, etc)
        """
        if points_to_render is None:
            points_to_render = self.n_vertices
            
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Bind vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, stride * 3 * 4, None)  # stride em bytes
        
        # Bind color buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_colors)
        glColorPointer(3, GL_FLOAT, stride * 3 * 4, None)  # stride em bytes
        
        # Desenha
        glDrawArrays(GL_POINTS, 0, points_to_render)
        
        # Cleanup
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
    
    def _render_vertex_array(self, points_to_render=None, stride=1):
        """Renderiza usando vertex arrays (para poucos pontos)
        
        Args:
            points_to_render: Quantidade de pontos a renderizar (None = todos)
            stride: Passo entre pontos (1 = todos, 2 = metade, etc)
        """
        if points_to_render is None:
            points_to_render = self.n_vertices
            
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Define ponteiros para os dados com stride
        glVertexPointer(3, GL_FLOAT, stride * 3 * 4, self.vertices)
        glColorPointer(3, GL_FLOAT, stride * 3 * 4, self.colors)
        
        # Renderiza
        glDrawArrays(GL_POINTS, 0, points_to_render)
        
        # Desabilita vertex arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
    
    def get_bounds(self):
        """
        Retorna os limites (bounding box) dos dados
        
        Returns:
            Tupla ((min_x, min_y, min_z), (max_x, max_y, max_z))
        """
        if self.vertices is None:
            return ((0, 0, 0), (0, 0, 0))
        
        # Reshape para (N, 3)
        verts = self.vertices.reshape(-1, 3)
        
        mins = verts.min(axis=0)
        maxs = verts.max(axis=0)
        
        return (tuple(mins), tuple(maxs))
    
    def get_center(self):
        """
        Retorna o centro da nuvem de pontos (valor em cache)
        
        Returns:
            Tupla (x, y, z) do centro
        """
        if self._cached_center is None:
            return (0, 0, 0)
        
        return self._cached_center
    
    def clear(self):
        """Remove todos os dados"""
        self._cleanup_vbo()
        self.vertices = None
        self.colors = None
        self.n_vertices = 0
        self._cached_center = None
    
    def __del__(self):
        """Destrutor - limpa VBOs"""
        self._cleanup_vbo()


class AxesRenderer:
    """
    Renderizador de eixos 3D (X, Y, Z)
    """
    
    def __init__(self, length=100.0):
        """
        Args:
            length: Comprimento dos eixos
        """
        self.length = length
        self.visible = True
    
    def set_length(self, length):
        """Define comprimento dos eixos"""
        self.length = length
    
    def render(self):
        """Renderiza os eixos XYZ"""
        if not self.visible:
            return
        
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # Eixo X (Vermelho)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.length, 0, 0)
        
        # Eixo Y (Verde)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.length, 0)
        
        # Eixo Z (Azul)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.length)
        
        glEnd()
        glLineWidth(1.0)


class AxisIndicator:
    """
    Indicador de orientação dos eixos (miniatura no canto da tela)
    """
    
    def __init__(self, screen_width, screen_height, size=50):
        """
        Args:
            screen_width, screen_height: Dimensões da janela
            size: Tamanho do indicador em pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = size
        self.visible = True
        self.position = (80, 80)  # Canto inferior esquerdo
    
    def update_screen_size(self, width, height):
        """Atualiza dimensões da tela"""
        self.screen_width = width
        self.screen_height = height
    
    def render(self, camera_pitch, camera_yaw):
        """
        Renderiza o indicador de eixos
        
        Args:
            camera_pitch, camera_yaw: Ângulos da câmera em graus
        """
        if not self.visible:
            return
        
        # Salva estado atual
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Configuração ortogonal
        glOrtho(0, self.screen_width, 0, self.screen_height, -100, 100)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Posiciona no canto
        glTranslatef(self.position[0], self.position[1], 0)
        
        # Aplica rotações da câmera
        glRotatef(camera_pitch, 1, 0, 0)
        glRotatef(camera_yaw, 0, 1, 0)
        
        # Desenha eixos
        glLineWidth(3.0)
        glBegin(GL_LINES)
        
        # Eixo X (Vermelho)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.size, 0, 0)
        
        # Eixo Y (Verde)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.size, 0)
        
        # Eixo Z (Azul)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, self.size)
        
        glEnd()
        
        # Desenha setas nas pontas
        arrow_size = 8
        
        # Seta X (vermelho)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(self.size, 0, 0)
        glVertex3f(self.size - arrow_size, arrow_size/2, 0)
        glVertex3f(self.size - arrow_size, -arrow_size/2, 0)
        glEnd()
        
        # Seta Y (verde)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, self.size, 0)
        glVertex3f(arrow_size/2, self.size - arrow_size, 0)
        glVertex3f(-arrow_size/2, self.size - arrow_size, 0)
        glEnd()
        
        # Seta Z (azul)
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, self.size)
        glVertex3f(0, arrow_size/2, self.size - arrow_size)
        glVertex3f(0, -arrow_size/2, self.size - arrow_size)
        glEnd()
        
        glLineWidth(1.0)
        
        # Restaura matrizes
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
