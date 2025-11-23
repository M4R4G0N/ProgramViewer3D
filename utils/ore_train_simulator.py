"""
Simulador de Trem de Minério com Integração UPL
Simula trens de minério reais passando pelos pontos carregados de arquivo .upl
"""

import numpy as np
from utils.ore_train_models import create_train_model, list_available_models


class OreTrainSimulator:
    """
    Simulador de trem de minério que passa pelos pontos 3D
    Usa os modelos reais de trem (ES43, DASH BB, etc)
    """
    
    def __init__(self, train_model_name='ES43', num_ore_cars=30):
        """
        Inicializa o simulador
        
        Args:
            train_model_name: Nome do modelo ('ES43', 'DASH BB', etc)
            num_ore_cars: Número de vagões de minério
        """
        # Carrega modelo do trem
        self.train_model = create_train_model(train_model_name, num_ore_cars)
        
        # Posição ao longo da trajetória
        self.z_position = 0.0
        self.z_velocity = 0.5  # unidades/frame
        
        # Limites de movimento
        self.track_start = -150.0
        self.track_end = 150.0
        
        # Visibilidade
        self.visible = True
        
        print(f"\n[ORE TRAIN] Simulador Inicializado")
        print(f"  Modelo: {self.train_model.name}")
        print(f"  Locomotoras: {self.train_model.num_locomotives}")
        print(f"  Vagões de minério: {self.train_model.num_ore_cars}")
        print(f"  Comprimento total: {self.train_model.get_total_length():.1f}m")
        print(f"  Peso total: {self.train_model.get_total_weight():.0f} ton")
    
    def _create_locomotive_points(self, loco_index, z_offset):
        """
        Cria pontos da locomotora
        
        Args:
            loco_index: Índice da locomotora
            z_offset: Posição Z da locomotora
            
        Returns:
            Tupla (points, colors)
        """
        # Posição da locomotora
        z_start = z_offset + loco_index * (self.train_model.locomotive_length + 0.5)
        
        # Gera pontos da locomotora (mais densa que vagões)
        n_points = 1000
        n_x = int(np.sqrt(n_points * self.train_model.locomotive_width / 
                         (self.train_model.locomotive_length * self.train_model.locomotive_height)))
        n_y = int(np.sqrt(n_points * self.train_model.locomotive_height / 
                         (self.train_model.locomotive_length * self.train_model.locomotive_width)))
        n_z = int(np.sqrt(n_points * self.train_model.locomotive_length / 
                         (self.train_model.locomotive_width * self.train_model.locomotive_height)))
        
        x_range = np.linspace(-self.train_model.locomotive_width/2, 
                             self.train_model.locomotive_width/2, max(2, n_x))
        y_range = np.linspace(0, self.train_model.locomotive_height, max(2, n_y))
        z_range = np.linspace(z_start, z_start + self.train_model.locomotive_length, max(2, n_z))
        
        points_list = []
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    points_list.append([x, y, z])
        
        points = np.array(points_list, dtype=np.float32)
        
        # Cores da locomotora (mais escura)
        color = self.train_model.locomotive_color
        colors = np.tile(np.array(color, dtype=np.float32) / 255.0, (len(points), 1))
        
        return points, colors
    
    def _create_ore_car_points(self, car_index, z_offset):
        """
        Cria pontos de um vagão de minério
        
        Args:
            car_index: Índice do vagão
            z_offset: Posição Z do vagão
            
        Returns:
            Tupla (points, colors)
        """
        # Posição do vagão
        z_start = (z_offset + 
                  self.train_model.num_locomotives * (self.train_model.locomotive_length + 0.5) +
                  car_index * (self.train_model.ore_car_length + 0.5))
        
        # Gera pontos do vagão
        n_points = 500  # Menos que locomotora
        n_x = int(np.sqrt(n_points * self.train_model.ore_car_width / 
                         (self.train_model.ore_car_length * self.train_model.ore_car_height)))
        n_y = int(np.sqrt(n_points * self.train_model.ore_car_height / 
                         (self.train_model.ore_car_length * self.train_model.ore_car_width)))
        n_z = int(np.sqrt(n_points * self.train_model.ore_car_length / 
                         (self.train_model.ore_car_width * self.train_model.ore_car_height)))
        
        x_range = np.linspace(-self.train_model.ore_car_width/2, 
                             self.train_model.ore_car_width/2, max(2, n_x))
        y_range = np.linspace(0, self.train_model.ore_car_height, max(2, n_y))
        z_range = np.linspace(z_start, z_start + self.train_model.ore_car_length, max(2, n_z))
        
        points_list = []
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    points_list.append([x, y, z])
        
        points = np.array(points_list, dtype=np.float32)
        
        # Cores dos vagões (marrom de minério)
        color = self.train_model.ore_car_color
        colors = np.tile(np.array(color, dtype=np.float32) / 255.0, (len(points), 1))
        
        return points, colors
    
    def get_points(self):
        """
        Retorna pontos do trem na posição atual
        
        Returns:
            Tupla (points, colors) com arrays (N, 3)
        """
        all_points = []
        all_colors = []
        
        # Locomotoras
        for loco_idx in range(self.train_model.num_locomotives):
            points, colors = self._create_locomotive_points(loco_idx, self.z_position)
            all_points.append(points)
            all_colors.append(colors)
        
        # Vagões de minério
        for car_idx in range(self.train_model.num_ore_cars):
            points, colors = self._create_ore_car_points(car_idx, self.z_position)
            all_points.append(points)
            all_colors.append(colors)
        
        # Junta todos
        points = np.vstack(all_points) if all_points else np.array([], dtype=np.float32).reshape(0, 3)
        colors = np.vstack(all_colors) if all_colors else np.array([], dtype=np.float32).reshape(0, 3)
        
        return points, colors
    
    def update(self, dt=1.0):
        """Atualiza posição do trem"""
        self.z_position += self.z_velocity * dt
        
        # Volta ao início se sair do trilho
        total_length = self.train_model.get_total_length()
        if self.z_position > self.track_end + total_length:
            self.z_position = self.track_start - total_length
    
    def set_velocity(self, velocity):
        """Define velocidade em unidades/frame"""
        self.z_velocity = velocity
    
    def get_velocity(self):
        """Retorna velocidade atual"""
        return self.z_velocity
    
    def set_position(self, z):
        """Define posição Z"""
        self.z_position = z
    
    def get_position(self):
        """Retorna posição Z atual"""
        return self.z_position
    
    def reset(self):
        """Reseta trem para posição inicial"""
        self.z_position = self.track_start
    
    def get_bounds(self):
        """Retorna bounding box do trem"""
        z_min = self.z_position
        z_max = self.z_position + self.train_model.get_total_length()
        
        # Dimensões X e Y baseadas na locomotora (maior)
        x_half = max(self.train_model.locomotive_width, self.train_model.ore_car_width) / 2
        y_max = max(self.train_model.locomotive_height, self.train_model.ore_car_height)
        
        return (
            (-x_half, 0, z_min),
            (x_half, y_max, z_max)
        )
    
    def get_stats(self):
        """Retorna estatísticas do simulador"""
        points, _ = self.get_points()
        return {
            'model': self.train_model.name,
            'locomotives': self.train_model.num_locomotives,
            'ore_cars': self.train_model.num_ore_cars,
            'total_points': len(points),
            'total_length_m': self.train_model.get_total_length(),
            'total_weight_ton': self.train_model.get_total_weight(),
            'z_position': self.z_position,
            'velocity': self.z_velocity,
            'bounds': self.get_bounds()
        }


def demo_ore_train_models():
    """Demonstra os modelos disponíveis"""
    
    print("\n" + "="*60)
    print("[INFO] MODELOS DE TREM DE MINÉRIO DISPONÍVEIS")
    print("="*60 + "\n")
    
    for model_name in list_available_models():
        sim = OreTrainSimulator(train_model_name=model_name, num_ore_cars=30)
        stats = sim.get_stats()
        print(f"\n{model_name:15} - {stats['total_length_m']:6.1f}m | "
              f"{stats['total_weight_ton']:7.0f}t | Pontos: {stats['total_points']:6,}")


if __name__ == "__main__":
    demo_ore_train_models()
