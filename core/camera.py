"""
Sistema de câmera orbital 3D para OpenGL
Suporta rotação, zoom, pan e posicionamento baseado em target
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import math


class Camera3D:
    """
    Câmera orbital 3D que gira em torno de um ponto de interesse (target)
    Suporta controles de rotação, zoom e movimento (pan)
    """
    
    def __init__(self, distance=400.0, pitch=30.0, yaw=0.0):
        """
        Inicializa a câmera
        
        Args:
            distance: Distância inicial do target (zoom)
            pitch: Rotação vertical em graus (-89 a 89)
            yaw: Rotação horizontal em graus (0-360)
        """
        # Ângulos de rotação
        self.pitch = pitch  # Rotação vertical (X)
        self.yaw = yaw      # Rotação horizontal (Y)
        
        # Distância ao target (zoom)
        self.distance = distance
        
        # Ponto de interesse (onde a câmera olha)
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0
        
        # Limites
        self.min_distance = 10.0
        self.max_distance = 2000.0
        self.min_pitch = -89.0
        self.max_pitch = 89.0
        
        # Cache de cálculos trigonométricos (otimização)
        self._cache_dirty = True
        self._cached_position = (0.0, 0.0, 0.0)
        self._cached_pitch_rad = 0.0
        self._cached_yaw_rad = 0.0
    
    def rotate(self, delta_yaw, delta_pitch):
        """
        Rotaciona a câmera em torno do target
        
        Args:
            delta_yaw: Mudança no ângulo horizontal
            delta_pitch: Mudança no ângulo vertical
        """
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        
        # Normaliza yaw para manter entre 0-360
        self.yaw = self.yaw % 360
        if self.yaw < 0:
            self.yaw += 360
        
        # Limita pitch para evitar gimbal lock
        self.pitch = max(self.min_pitch, min(self.max_pitch, self.pitch))
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def zoom(self, delta):
        """
        Ajusta a distância ao target (zoom in/out)
        
        Args:
            delta: Mudança na distância (positivo = afastar)
        """
        self.distance += delta
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def pan(self, delta_x, delta_y):
        """
        Move o target lateralmente (pan camera)
        
        Args:
            delta_x: Movimento horizontal no plano da câmera
            delta_y: Movimento vertical no plano da câmera
        """
        # Usa valores em cache ou recalcula
        self._update_cache()
        pitch_rad = self._cached_pitch_rad
        yaw_rad = self._cached_yaw_rad
        
        # Velocidade baseada na distância
        pan_speed = self.distance * 0.001
        
        # Calcula vetores de direção da câmera
        # Vetor "direita"
        right_x = math.cos(yaw_rad)
        right_z = -math.sin(yaw_rad)
        
        # Vetor "cima"
        sin_pitch = math.sin(pitch_rad)
        cos_pitch = math.cos(pitch_rad)
        sin_yaw = math.sin(yaw_rad)
        cos_yaw = math.cos(yaw_rad)
        
        up_x = -sin_yaw * sin_pitch
        up_y = cos_pitch
        up_z = -cos_yaw * sin_pitch
        
        # Aplica movimento ao target
        self.target_x += (right_x * delta_x - up_x * delta_y) * pan_speed
        self.target_y += up_y * delta_y * pan_speed
        self.target_z += (right_z * delta_x - up_z * delta_y) * pan_speed
    
    def move_forward(self, delta):
        """
        Move o target ao longo do eixo de visão da câmera
        
        Args:
            delta: Distância a mover (positivo = para frente)
        """
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)
        
        # Vetor de direção da câmera
        dir_x = math.sin(yaw_rad) * math.cos(pitch_rad)
        dir_y = -math.sin(pitch_rad)
        dir_z = math.cos(yaw_rad) * math.cos(pitch_rad)
        
        # Move o target
        move_speed = self.distance * 0.01
        self.target_x += dir_x * delta * move_speed
        self.target_y += dir_y * delta * move_speed
        self.target_z += dir_z * delta * move_speed
    
    def move_target(self, delta_x, delta_y, delta_z):
        """
        Move o target em coordenadas globais
        
        Args:
            delta_x, delta_y, delta_z: Deslocamento nos eixos X, Y, Z
        """
        self.target_x += delta_x
        self.target_y += delta_y
        self.target_z += delta_z
    
    def move_camera_global(self, delta_x, delta_y, delta_z):
        """
        Move a posição da câmera (e o target junto) em coordenadas globais
        Mantém a direção de visão e distância
        
        Args:
            delta_x, delta_y, delta_z: Deslocamento nos eixos X, Y, Z globais
        """
        self.target_x += delta_x
        self.target_y += delta_y
        self.target_z += delta_z
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def move_camera_relative(self, forward=0, right=0, up=0):
        """
        Move a câmera relativo à sua orientação atual nos eixos globais
        O movimento é projetado nos eixos XYZ globais baseado na direção da câmera
        
        Args:
            forward: Movimento para frente/trás (positivo = frente na direção da visão)
            right: Movimento para direita/esquerda (positivo = direita)
            up: Movimento para cima/baixo no plano vertical global (positivo = cima no eixo Y)
        """
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)
        
        # Vetor forward projetado no plano XZ (horizontal)
        # Ignora o pitch para manter movimento horizontal
        forward_x = -math.sin(yaw_rad)
        forward_z = -math.cos(yaw_rad)
        
        # Vetor right (perpendicular ao forward no plano XZ)
        right_x = math.cos(yaw_rad)
        right_z = -math.sin(yaw_rad)
        
        # Movimento no plano horizontal (XZ)
        self.target_x += forward_x * forward + right_x * right
        self.target_z += forward_z * forward + right_z * right
        
        # Movimento vertical (Y) é sempre no eixo Y global
        self.target_y += up
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def set_target(self, x, y, z):
        """
        Define o ponto de interesse da câmera
        
        Args:
            x, y, z: Coordenadas do novo target
        """
        self.target_x = x
        self.target_y = y
        self.target_z = z
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def set_view(self, pitch, yaw):
        """
        Define ângulos de visualização diretamente
        
        Args:
            pitch: Ângulo vertical em graus
            yaw: Ângulo horizontal em graus
        """
        self.pitch = max(self.min_pitch, min(self.max_pitch, pitch))
        self.yaw = yaw % 360
        if self.yaw < 0:
            self.yaw += 360
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def reset(self):
        """Reseta a câmera para posição inicial"""
        self.pitch = 30.0
        self.yaw = 0.0
        self.distance = 400.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0
        
        # Marca cache como sujo
        self._cache_dirty = True
    
    def get_position(self):
        """
        Calcula a posição atual da câmera no espaço 3D
        
        Returns:
            Tupla (x, y, z) da posição da câmera
        """
        # Retorna posição em cache se disponível
        if not self._cache_dirty:
            return self._cached_position
        
        # Recalcula e atualiza cache
        self._update_cache()
        return self._cached_position
    
    def _update_cache(self):
        """Atualiza cache de cálculos trigonométricos"""
        if not self._cache_dirty:
            return
        
        # Converte para radianos (uma vez só)
        self._cached_pitch_rad = math.radians(self.pitch)
        self._cached_yaw_rad = math.radians(self.yaw)
        
        # Pré-calcula senos e cossenos
        sin_pitch = math.sin(self._cached_pitch_rad)
        cos_pitch = math.cos(self._cached_pitch_rad)
        sin_yaw = math.sin(self._cached_yaw_rad)
        cos_yaw = math.cos(self._cached_yaw_rad)
        
        # Calcula posição da câmera
        cam_x = self.target_x + self.distance * sin_yaw * cos_pitch
        cam_y = self.target_y + self.distance * sin_pitch
        cam_z = self.target_z + self.distance * cos_yaw * cos_pitch
        
        self._cached_position = (cam_x, cam_y, cam_z)
        self._cache_dirty = False
    
    def apply(self):
        """
        Aplica a transformação da câmera usando gluLookAt
        Chame este método antes de renderizar a cena 3D
        """
        glLoadIdentity()
        
        # Calcula posição da câmera
        cam_x, cam_y, cam_z = self.get_position()
        
        # Configura visualização
        gluLookAt(
            cam_x, cam_y, cam_z,                           # Posição da câmera
            self.target_x, self.target_y, self.target_z,   # Ponto de interesse
            0, 1, 0                                        # Vetor "up"
        )
    
    def get_rotation_matrix(self):
        """
        Retorna a matriz de rotação da câmera (útil para indicadores)
        
        Returns:
            Tupla (pitch, yaw) em graus
        """
        return (self.pitch, self.yaw)
    
    def get_movement_multipliers(self):
        """
        Calcula multiplicadores de direção baseado na orientação da câmera
        Para inverter controles quando a câmera está flipada
        
        Returns:
            Tupla (x_mult, y_mult, z_mult) com valores 1 ou -1
        """
        # Normaliza yaw
        yaw_norm = self.yaw % 360
        if yaw_norm < 0:
            yaw_norm += 360
        
        # Multiplier para X (esquerda/direita)
        # Inverte se estiver olhando "de trás" (yaw entre 90 e 270)
        if 90 < yaw_norm < 270:
            x_mult = -1
        else:
            x_mult = 1
        
        # Multiplier para Y (cima/baixo)
        # Inverte se estiver olhando de baixo para cima (pitch negativo)
        if self.pitch < -45:
            y_mult = -1
        else:
            y_mult = 1
        
        # Multiplier para Z (frente/trás)
        # Inverte se estiver olhando na direção oposta (yaw perto de 180)
        if 90 < yaw_norm < 270:
            z_mult = -1
        else:
            z_mult = 1
        
        return (x_mult, y_mult, z_mult)
