"""
Simulador de trem passando pelo eixo Z
Gera pontos que formam um trem em movimento ao longo do eixo Z
"""

import numpy as np


class TrainSimulator:
    """
    Simula um trem passando pelo eixo Z
    O trem é composto por vagões que se movem lineamente ao longo do eixo Z
    """
    
    def __init__(self, 
                 num_wagons=5, 
                 wagon_length=10.0,
                 wagon_width=5.0,
                 wagon_height=4.0,
                 points_per_wagon=1000,
                 gap_between_wagons=2.0):
        """
        Inicializa o simulador de trem
        
        Args:
            num_wagons: Número de vagões
            wagon_length: Comprimento de cada vagão (eixo Z)
            wagon_width: Largura de cada vagão (eixo X)
            wagon_height: Altura de cada vagão (eixo Y)
            points_per_wagon: Número de pontos por vagão
            gap_between_wagons: Espaço entre vagões
        """
        self.num_wagons = num_wagons
        self.wagon_length = wagon_length
        self.wagon_width = wagon_width
        self.wagon_height = wagon_height
        self.points_per_wagon = points_per_wagon
        self.gap_between_wagons = gap_between_wagons
        
        # Posição Z do trem (avança ao longo do eixo Z)
        self.z_position = 0.0
        self.z_velocity = 0.5  # Unidades por frame
        
        # Dimensões da pista (opcional, para limitar movimento)
        self.track_start = -100.0
        self.track_end = 100.0
        
        # Cores dos vagões (gradiente de cores)
        self.wagon_colors = self._generate_wagon_colors()
        
        # Renderização
        self.visible = True
        self.wireframe = False
        
        print(f"🚂 Simulador de Trem Inicializado")
        print(f"   Vagões: {num_wagons}")
        print(f"   Dimensões: {wagon_width:.1f}m x {wagon_height:.1f}m x {wagon_length:.1f}m")
        print(f"   Pontos por vagão: {points_per_wagon:,}")
    
    def _generate_wagon_colors(self):
        """Gera cores para cada vagão (gradiente)"""
        colors = []
        for i in range(self.num_wagons):
            hue = i / max(1, self.num_wagons - 1)
            # Vermelho -> Amarelo -> Verde
            if hue < 0.5:
                r = 255
                g = int(255 * hue * 2)
                b = 0
            else:
                r = int(255 * (1 - (hue - 0.5) * 2))
                g = 255
                b = 0
            colors.append((r, g, b))
        return colors
    
    def _create_wagon_points(self, wagon_index, z_offset):
        """
        Cria pontos para um vagão individual
        
        Args:
            wagon_index: Índice do vagão (0 a num_wagons-1)
            z_offset: Posição Z do vagão
            
        Returns:
            Tupla (points, colors) com arrays (N, 3)
        """
        # Posição do vagão
        z_start = z_offset + wagon_index * (self.wagon_length + self.gap_between_wagons)
        
        # Gera pontos do vagão com distribuição uniforme
        # Cria um retângulo 3D preenchido
        
        # Número de pontos em cada dimensão
        n_x = int(np.sqrt(self.points_per_wagon * self.wagon_width / 
                          (self.wagon_length * self.wagon_height)))
        n_y = int(np.sqrt(self.points_per_wagon * self.wagon_height / 
                          (self.wagon_length * self.wagon_width)))
        n_z = int(np.sqrt(self.points_per_wagon * self.wagon_length / 
                          (self.wagon_width * self.wagon_height)))
        
        # Cria malha de pontos
        x_range = np.linspace(-self.wagon_width/2, self.wagon_width/2, max(2, n_x))
        y_range = np.linspace(-self.wagon_height/2, self.wagon_height/2, max(2, n_y))
        z_range = np.linspace(z_start, z_start + self.wagon_length, max(2, n_z))
        
        points_list = []
        colors_list = []
        
        # Distribui pontos uniformemente no volume do vagão
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    points_list.append([x, y, z])
        
        points = np.array(points_list, dtype=np.float32)
        
        # Cores baseadas no índice do vagão
        wagon_color = self.wagon_colors[wagon_index % len(self.wagon_colors)]
        colors = np.tile(wagon_color, (len(points), 1)).astype(np.float32) / 255.0
        
        return points, colors
    
    def get_points(self):
        """
        Retorna pontos do trem na posição atual
        
        Returns:
            Tupla (points, colors) com arrays (N, 3) em formato normalizado 0-1
        """
        all_points = []
        all_colors = []
        
        for wagon_idx in range(self.num_wagons):
            points, colors = self._create_wagon_points(wagon_idx, self.z_position)
            all_points.append(points)
            all_colors.append(colors)
        
        # Junta todos os pontos
        points = np.vstack(all_points) if all_points else np.array([], dtype=np.float32).reshape(0, 3)
        colors = np.vstack(all_colors) if all_colors else np.array([], dtype=np.float32).reshape(0, 3)
        
        return points, colors
    
    def update(self, dt=1.0):
        """
        Atualiza a posição do trem
        
        Args:
            dt: Delta de tempo (em frames, padrão 1.0)
        """
        self.z_position += self.z_velocity * dt
        
        # Volta ao início se sair da pista
        total_length = self.num_wagons * (self.wagon_length + self.gap_between_wagons)
        
        if self.z_position > self.track_end + total_length:
            self.z_position = self.track_start - total_length
    
    def set_velocity(self, velocity):
        """Define velocidade do trem (unidades/frame)"""
        self.z_velocity = velocity
    
    def get_velocity(self):
        """Retorna velocidade atual"""
        return self.z_velocity
    
    def set_position(self, z_position):
        """Define posição Z do trem"""
        self.z_position = z_position
    
    def get_position(self):
        """Retorna posição Z atual"""
        return self.z_position
    
    def reset(self):
        """Reseta o trem para posição inicial"""
        self.z_position = self.track_start
    
    def get_bounds(self):
        """
        Retorna bounding box do trem
        
        Returns:
            Tupla ((min_x, min_y, min_z), (max_x, max_y, max_z))
        """
        z_min = self.z_position
        z_max = self.z_position + (self.num_wagons * (self.wagon_length + self.gap_between_wagons))
        
        return (
            (-self.wagon_width/2, -self.wagon_height/2, z_min),
            (self.wagon_width/2, self.wagon_height/2, z_max)
        )
    
    def get_stats(self):
        """Retorna estatísticas do simulador"""
        points, _ = self.get_points()
        return {
            'num_wagons': self.num_wagons,
            'total_points': len(points),
            'z_position': self.z_position,
            'velocity': self.z_velocity,
            'bounds': self.get_bounds()
        }


class AdvancedTrainSimulator(TrainSimulator):
    """
    Simulador avançado de trem com recursos adicionais:
    - Formato mais realista (locomotora + vagões)
    - Efeitos de fumaça
    - Iluminação
    """
    
    def __init__(self, 
                 num_wagons=5,
                 has_locomotive=True,
                 has_smoke_effect=True,
                 **kwargs):
        """
        Inicializa simulador avançado
        
        Args:
            num_wagons: Número de vagões (sem contar locomotora)
            has_locomotive: Se deve incluir locomotora
            has_smoke_effect: Se deve gerar partículas de fumaça
            **kwargs: Argumentos para TrainSimulator
        """
        super().__init__(num_wagons=num_wagons, **kwargs)
        
        self.has_locomotive = has_locomotive
        self.has_smoke_effect = has_smoke_effect
        self.smoke_particles = []
        
        if has_locomotive:
            self.num_wagons += 1
            self.wagon_colors.insert(0, (50, 50, 50))  # Locomotora cinza escura
    
    def _create_locomotive(self, z_offset):
        """
        Cria pontos da locomotora (maior e mais detalhada)
        
        Returns:
            Tupla (points, colors)
        """
        z_start = z_offset
        loco_length = self.wagon_length * 1.5
        
        # Locomotora é mais longa e tem mais massa
        n_x = int(np.sqrt(self.points_per_wagon * 1.5))
        n_y = int(np.sqrt(self.points_per_wagon * 1.5))
        n_z = int(np.sqrt(self.points_per_wagon * 2.0))
        
        x_range = np.linspace(-self.wagon_width * 0.6, self.wagon_width * 0.6, max(2, n_x))
        y_range = np.linspace(0, self.wagon_height, max(2, n_y))  # Mais alta na frente
        z_range = np.linspace(z_start, z_start + loco_length, max(2, n_z))
        
        points_list = []
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    points_list.append([x, y, z])
        
        points = np.array(points_list, dtype=np.float32)
        colors = np.ones((len(points), 3), dtype=np.float32) * 0.2  # Cinza escura
        
        return points, colors
    
    def _generate_smoke(self, z_pos):
        """
        Gera partículas de fumaça atrás da locomotora
        
        Returns:
            Tupla (points, colors)
        """
        num_smoke_particles = 500
        
        # Fumaça sai da frente da locomotora
        smoke_pos_z = z_pos
        
        # Dispersão aleatória
        np.random.seed(int(self.z_position * 100) % 10000)  # Pseudo-aleatório mas consistente
        
        points_list = []
        colors_list = []
        
        for i in range(num_smoke_particles):
            # Dispersão em X e Y
            x = np.random.normal(0, self.wagon_width * 0.3)
            y = np.random.normal(self.wagon_height * 0.7, self.wagon_height * 0.3)
            z = smoke_pos_z + np.random.uniform(-5, 5)
            
            points_list.append([x, y, z])
            
            # Cor: cinza claro com transparência
            opacity = np.random.uniform(0.3, 0.8)
            colors_list.append([0.8, 0.8, 0.8, opacity])
        
        points = np.array(points_list, dtype=np.float32)
        colors = np.array(colors_list, dtype=np.float32) / 255.0
        
        return points, colors
    
    def get_points(self):
        """Retorna pontos do trem incluindo fumaça se habilitado"""
        points, colors = super().get_points()
        
        if self.has_smoke_effect and self.has_locomotive:
            # Adiciona fumaça atrás da locomotora
            smoke_pts, smoke_colors = self._generate_smoke(self.z_position)
            
            # Junta com pontos principais
            points = np.vstack([points, smoke_pts]) if len(smoke_pts) > 0 else points
            
            # Ajusta cores para 4 componentes (RGBA) se necessário
            if colors.shape[1] == 3 and smoke_colors.shape[1] == 4:
                # Adiciona alfa aos pontos originais
                alpha = np.ones((colors.shape[0], 1))
                colors = np.hstack([colors, alpha])
                colors = np.vstack([colors, smoke_colors])
            else:
                colors = np.vstack([colors, smoke_colors[:, :3]]) if smoke_colors.shape[1] > 3 else np.vstack([colors, smoke_colors])
        
        return points, colors
