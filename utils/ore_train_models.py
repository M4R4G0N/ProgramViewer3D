"""
Modelos de Trens de Minério Reais
Especificações técnicas e parâmetros para simulação
Modelos: ES43, DASH BB, SD 40, GT, G22, UB, U20, AC 44i, DASH 9, ES44, C30
"""

import numpy as np


class TrainModel:
    """
    Classe base para modelos de trem com especificações técnicas
    """
    
    def __init__(self, name, locomotoras=1, vagoes_minério=30):
        """
        Args:
            name: Nome do modelo (ex: 'ES43')
            locomotoras: Número de locomotoras
            vagoes_minério: Número de vagões de minério
        """
        self.name = name
        self.num_locomotives = locomotoras
        self.num_ore_cars = vagoes_minério
        
        # Dimensões em metros (aproximadas)
        self.locomotive_length = 20.0      # Comprimento da locomotora
        self.locomotive_width = 3.0        # Largura
        self.locomotive_height = 4.0       # Altura
        
        self.ore_car_length = 12.0         # Comprimento do vagão
        self.ore_car_width = 2.8           # Largura
        self.ore_car_height = 3.5          # Altura (aberto)
        
        # Performance
        self.max_speed = 80.0              # km/h
        self.power_hp = 3000               # Cavalos de potência
        self.tractive_effort_ton = 350     # Esforço de tração em toneladas
        
        # Peso (toneladas)
        self.locomotive_weight = 200
        self.ore_car_loaded_weight = 130   # Carregado
        self.ore_car_empty_weight = 30     # Vazio
        
        # Cores (RGB 0-255)
        self.locomotive_color = (50, 50, 50)     # Cinza escuro
        self.ore_car_color = (180, 120, 60)      # Marrom (minério)
    
    def get_total_length(self):
        """Comprimento total do trem em metros"""
        gap = 0.5  # Espaço entre vagões
        length = (self.num_locomotives * self.locomotive_length + 
                 self.num_ore_cars * self.ore_car_length +
                 (self.num_locomotives + self.num_ore_cars - 1) * gap)
        return length
    
    def get_total_weight(self):
        """Peso total do trem em toneladas"""
        weight = (self.num_locomotives * self.locomotive_weight +
                 self.num_ore_cars * self.ore_car_loaded_weight)
        return weight
    
    def __repr__(self):
        return f"Train({self.name}: {self.num_locomotives}L + {self.num_ore_cars}C, {self.get_total_length():.0f}m)"


class ES43(TrainModel):
    """Locomotora ES43 (Brasil - Vale)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("ES43", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 4400
        self.tractive_effort_ton = 320
        self.locomotive_weight = 192
        self.locomotive_color = (180, 0, 0)  # Vermelho (Vale)
        self.max_speed = 120


class DASHBB(TrainModel):
    """Locomotora DASH BB (GE)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("DASH BB", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 3000
        self.tractive_effort_ton = 370
        self.locomotive_weight = 207
        self.locomotive_color = (0, 100, 200)  # Azul
        self.max_speed = 100


class SD40(TrainModel):
    """Locomotora SD 40 (EMD)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("SD 40", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 3000
        self.tractive_effort_ton = 339
        self.locomotive_weight = 196
        self.locomotive_color = (50, 50, 50)  # Cinza
        self.max_speed = 120


class GT(TrainModel):
    """Locomotora GT (Brasil)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("GT", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 3200
        self.tractive_effort_ton = 350
        self.locomotive_weight = 200
        self.locomotive_color = (0, 150, 0)  # Verde
        self.max_speed = 100


class G22(TrainModel):
    """Locomotora G22 (Diesel-Elétrica)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("G22", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 2200
        self.tractive_effort_ton = 290
        self.locomotive_weight = 160
        self.locomotive_color = (100, 100, 100)  # Cinza médio
        self.max_speed = 100


class UB(TrainModel):
    """Locomotora UB (Brasil - antiga)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("UB", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 1600
        self.tractive_effort_ton = 200
        self.locomotive_weight = 120
        self.locomotive_color = (139, 69, 19)  # Marrom
        self.max_speed = 80


class U20(TrainModel):
    """Locomotora U20 (Brasil)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("U20", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 2000
        self.tractive_effort_ton = 250
        self.locomotive_weight = 150
        self.locomotive_color = (200, 100, 0)  # Laranja
        self.max_speed = 95


class AC44i(TrainModel):
    """Locomotora AC 44i (GE - Moderna)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("AC 44i", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 4400
        self.tractive_effort_ton = 350
        self.locomotive_weight = 204
        self.locomotive_color = (255, 200, 0)  # Amarelo/Dourado
        self.max_speed = 100


class DASH9(TrainModel):
    """Locomotora DASH 9 (GE)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("DASH 9", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 4400
        self.tractive_effort_ton = 359
        self.locomotive_weight = 207
        self.locomotive_color = (0, 50, 150)  # Azul escuro
        self.max_speed = 100


class ES44(TrainModel):
    """Locomotora ES44 (GE - Moderna)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("ES44", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 4400
        self.tractive_effort_ton = 359
        self.locomotive_weight = 207
        self.locomotive_color = (200, 0, 0)  # Vermelho
        self.max_speed = 100


class C30(TrainModel):
    """Locomotora C30 (Diesel-Elétrica)"""
    def __init__(self, vagoes_minério=30):
        super().__init__("C30", locomotoras=1, vagoes_minério=vagoes_minério)
        self.power_hp = 3000
        self.tractive_effort_ton = 330
        self.locomotive_weight = 190
        self.locomotive_color = (0, 100, 100)  # Azul-verde
        self.max_speed = 100


# Factory para criar trens por nome
def create_train_model(model_name, vagoes_minério=30):
    """
    Factory para criar modelo de trem
    
    Args:
        model_name: Nome do modelo ('ES43', 'DASH BB', etc)
        vagoes_minério: Número de vagões de minério
        
    Returns:
        Instância do modelo de trem
    """
    models = {
        'ES43': ES43,
        'DASH BB': DASHBB,
        'SD 40': SD40,
        'GT': GT,
        'G22': G22,
        'UB': UB,
        'U20': U20,
        'AC 44i': AC44i,
        'DASH 9': DASH9,
        'ES44': ES44,
        'C30': C30,
    }
    
    if model_name not in models:
        raise ValueError(f"Modelo desconhecido: {model_name}. Modelos disponíveis: {list(models.keys())}")
    
    return models[model_name](vagoes_minério)


def list_available_models():
    """Retorna lista de modelos disponíveis"""
    return [
        'ES43', 'DASH BB', 'SD 40', 'GT', 'G22', 'UB', 
        'U20', 'AC 44i', 'DASH 9', 'ES44', 'C30'
    ]


# Exemplos de trens típicos para minério
TYPICAL_TRAINS = {
    'lightt': {
        'model': 'ES43',
        'num_locomotives': 1,
        'num_ore_cars': 15,
        'description': 'Trem leve - 15 vagões de minério'
    },
    'medium': {
        'model': 'ES43',
        'num_locomotives': 1,
        'num_ore_cars': 30,
        'description': 'Trem médio - 30 vagões de minério (padrão)'
    },
    'heavy': {
        'model': 'ES43',
        'num_locomotives': 2,
        'num_ore_cars': 60,
        'description': 'Trem pesado - 2 locomotoras + 60 vagões'
    },
    'ultra_heavy': {
        'model': 'AC 44i',
        'num_locomotives': 3,
        'num_ore_cars': 100,
        'description': 'Trem ultra pesado - 3 AC 44i + 100 vagões (VALEMAX)'
    },
}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MODELOS DE TRENS DE MINÉRIO DISPONÍVEIS")
    print("="*60 + "\n")
    
    for model_name in list_available_models():
        train = create_train_model(model_name, vagoes_minério=30)
        print(f"\n{train.name}")
        print(f"  Comprimento total: {train.get_total_length():.1f}m")
        print(f"  Peso total: {train.get_total_weight():.0f} ton")
        print(f"  Potência: {train.power_hp} HP")
        print(f"  Esforço de tração: {train.tractive_effort_ton} ton")
        print(f"  Velocidade máxima: {train.max_speed} km/h")
    
    print("\n" + "="*60)
    print("CONFIGURAÇÕES TÍPICAS")
    print("="*60 + "\n")
    
    for config_name, config in TYPICAL_TRAINS.items():
        print(f"{config_name:15} - {config['description']}")
