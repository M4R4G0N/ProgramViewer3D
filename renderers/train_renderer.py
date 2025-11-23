"""
Renderizador para simulação de trem 3D
Integrado com o sistema de renderização de nuvens de pontos
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class TrainRenderer:
    """
    Renderizador otimizado para o trem
    Usa os mesmos conceitos de VBO que o PointCloudRenderer
    """
    
    def __init__(self, train_simulator):
        """
        Inicializa o renderizador do trem
        
        Args:
            train_simulator: Instância de TrainSimulator
        """
        self.train = train_simulator
        
        # VBO handles
        self.vbo_vertices = None
        self.vbo_colors = None
        
        self.vertices = None
        self.colors = None
        self.n_vertices = 0
        
        self.point_size = 2.0
        self.visible = True
        self.use_vbo = True
        
        # Cache de velocidade de atualização
        self.last_z_pos = -999999
        self.update_threshold = 0.1  # Atualiza VBO cada 0.1 unidades de Z
    
    def update(self, dt=1.0):
        """
        Atualiza posição do trem
        
        Args:
            dt: Delta de tempo
        """
        self.train.update(dt)
        
        # Verifica se precisa recalcular VBO
        if abs(self.train.get_position() - self.last_z_pos) > self.update_threshold:
            self._update_vbo_data()
            self.last_z_pos = self.train.get_position()
    
    def _update_vbo_data(self):
        """Atualiza dados dos VBOs baseado na posição atual do trem"""
        points, colors = self.train.get_points()
        
        if len(points) == 0:
            return
        
        # Limpa VBO antigo
        self._cleanup_vbo()
        
        # Normaliza cores para 0-1 se estiverem em 0-255
        if colors.max() > 1.0:
            colors = colors / 255.0
        
        # Flatten para formato OpenGL
        self.vertices = points.flatten().astype(np.float32)
        
        # Garante cores em formato RGB (3 componentes)
        if colors.shape[1] == 4:
            # Se tem RGBA, tira alfa
            colors = colors[:, :3]
        
        self.colors = colors.flatten().astype(np.float32)
        self.n_vertices = len(points)
        
        # Cria VBO
        if self.use_vbo and self.n_vertices > 0:
            self._create_vbo()
    
    def _create_vbo(self):
        """Cria Vertex Buffer Objects para os dados"""
        if self.n_vertices == 0:
            return
        
        # Gera buffers
        self.vbo_vertices = glGenBuffers(1)
        self.vbo_colors = glGenBuffers(1)
        
        # Buffer de vértices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)
        
        # Buffer de cores
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_colors)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_DYNAMIC_DRAW)
        
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
        """Define tamanho dos pontos"""
        self.point_size = max(1.0, min(10.0, size))
        glPointSize(self.point_size)
    
    def render(self):
        """Renderiza o trem"""
        if not self.visible or self.n_vertices == 0:
            return
        
        glPointSize(self.point_size)
        
        if self.vbo_vertices is not None:
            self._render_vbo()
        else:
            self._render_vertex_array()
    
    def _render_vbo(self):
        """Renderiza usando VBOs"""
        if self.n_vertices == 0:
            return
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Bind vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        # Bind color buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_colors)
        glColorPointer(3, GL_FLOAT, 0, None)
        
        # Desenha
        glDrawArrays(GL_POINTS, 0, self.n_vertices)
        
        # Cleanup
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
    
    def _render_vertex_array(self):
        """Renderiza usando vertex arrays"""
        if self.vertices is None or self.n_vertices == 0:
            return
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Define ponteiros para os dados
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glColorPointer(3, GL_FLOAT, 0, self.colors)
        
        # Renderiza
        glDrawArrays(GL_POINTS, 0, self.n_vertices)
        
        # Desabilita vertex arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
    
    def get_bounds(self):
        """Retorna bounding box do trem"""
        return self.train.get_bounds()
    
    def get_center(self):
        """Retorna centro do trem"""
        min_b, max_b = self.get_bounds()
        return tuple((min_b[i] + max_b[i]) / 2 for i in range(3))
    
    def get_stats(self):
        """Retorna estatísticas do renderizador"""
        return {
            'total_points': self.n_vertices,
            'z_position': self.train.get_position(),
            'velocity': self.train.get_velocity(),
            'train_stats': self.train.get_stats()
        }
    
    def clear(self):
        """Limpa dados"""
        self._cleanup_vbo()
        self.vertices = None
        self.colors = None
        self.n_vertices = 0
    
    def __del__(self):
        """Destrutor"""
        self._cleanup_vbo()


class TrainVisualizationMode:
    """
    Modo de visualização que combina nuvem de pontos com simulação de trem
    Permite visualizar o trem passando por uma nuvem de pontos estática
    """
    
    def __init__(self, point_cloud_renderer, train_renderer):
        """
        Inicializa modo de visualização
        
        Args:
            point_cloud_renderer: PointCloudRenderer da aplicação
            train_renderer: TrainRenderer
        """
        self.point_cloud = point_cloud_renderer
        self.train = train_renderer
        
        self.show_point_cloud = True
        self.show_train = True
        self.show_grid = False
        
        # Opções de interação
        self.auto_follow_train = True  # Câmera segue o trem
        self.train_speed_factor = 1.0
    
    def update(self, dt=1.0):
        """Atualiza trem com fator de velocidade"""
        self.train.train.set_velocity(
            self.train.train.z_velocity / self.train_speed_factor
        )
        self.train.update(dt * self.train_speed_factor)
    
    def render(self):
        """Renderiza ambos os elementos"""
        if self.show_point_cloud:
            self.point_cloud.render()
        
        if self.show_train:
            self.train.render()
        
        if self.show_grid:
            self._render_grid()
    
    def _render_grid(self):
        """Renderiza grade 3D para referência"""
        glLineWidth(0.5)
        glColor3f(0.5, 0.5, 0.5)
        
        glBegin(GL_LINES)
        
        # Grade XY
        for i in range(-50, 51, 10):
            glVertex3f(i, -50, 0)
            glVertex3f(i, 50, 0)
            glVertex3f(-50, i, 0)
            glVertex3f(50, i, 0)
        
        glEnd()
        glLineWidth(1.0)
    
    def get_camera_focus(self):
        """
        Retorna ponto de foco para câmera quando em modo de seguimento
        
        Returns:
            Tupla (x, y, z) do ponto de foco
        """
        if self.auto_follow_train:
            return self.train.get_center()
        else:
            return self.point_cloud.get_center()
    
    def set_train_speed_factor(self, factor):
        """Controla velocidade relativa do trem vs câmera"""
        self.train_speed_factor = max(0.1, factor)
