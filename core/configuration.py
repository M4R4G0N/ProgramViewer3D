"""
Gerenciador de configurações da aplicação
Suporta persistência em arquivo JSON
"""

import json
import os


class Configuration:
    """
    Gerenciador de configurações com valores padrão e persistência
    """
    
    DEFAULT_CONFIG = {
        # Configurações visuais
        "background_color": [0.1, 0.1, 0.1, 1.0],
        "point_size": 3.0,
        "show_axes": True,
        "show_axis_indicator": True,
        
        # Configurações de câmera
        "camera_distance": 400.0,
        "camera_pitch": 30.0,
        "camera_yaw": 0.0,
        "camera_move_speed": 5.0,
        
        # Configurações de janela
        "window_width": 1200,
        "window_height": 900,
        "window_title": "3D Point Cloud Viewer",
        
        # Configurações de performance
        "max_points": 500000,
        "enable_antialiasing": True,
        
        # Presets de cores de fundo
        "background_presets": [
            {"name": "Preto", "color": [0.0, 0.0, 0.0, 1.0]},
            {"name": "Cinza Escuro", "color": [0.1, 0.1, 0.1, 1.0]},
            {"name": "Cinza Médio", "color": [0.3, 0.3, 0.3, 1.0]},
            {"name": "Branco", "color": [1.0, 1.0, 1.0, 1.0]},
            {"name": "Azul Escuro", "color": [0.0, 0.0, 0.2, 1.0]}
        ],
        
        # Arquivos recentes
        "recent_files": []
    }
    
    def __init__(self, config_file="config.json"):
        """
        Inicializa gerenciador de configurações
        
        Args:
            config_file: Caminho do arquivo de configuração
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Carrega configurações do arquivo (se existir)"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge com defaults (preserva novos campos)
                    self.config.update(loaded_config)
                print(f"✅ Configurações carregadas de {self.config_file}")
            except Exception as e:
                print(f"⚠️  Erro ao carregar config: {e}")
                print("   Usando configurações padrão")
        else:
            print("ℹ️  Arquivo de configuração não encontrado, usando padrões")
    
    def save(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"✅ Configurações salvas em {self.config_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar config: {e}")
    
    def get(self, key, default=None):
        """
        Obtém valor de configuração
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não existir
            
        Returns:
            Valor da configuração
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Define valor de configuração
        
        Args:
            key: Chave da configuração
            value: Novo valor
        """
        self.config[key] = value
    
    def reset(self):
        """Reseta para configurações padrão"""
        self.config = self.DEFAULT_CONFIG.copy()
        print("🔄 Configurações resetadas para padrão")
    
    def get_background_color(self):
        """Retorna cor de fundo atual"""
        return self.get("background_color", [0.1, 0.1, 0.1, 1.0])
    
    def set_background_color(self, color):
        """Define cor de fundo"""
        self.set("background_color", color)
    
    def get_point_size(self):
        """Retorna tamanho dos pontos"""
        return self.get("point_size", 3.0)
    
    def set_point_size(self, size):
        """Define tamanho dos pontos"""
        self.set("point_size", max(1.0, min(10.0, size)))
    
    def get_show_axes(self):
        """Retorna se deve mostrar eixos"""
        return self.get("show_axes", True)
    
    def set_show_axes(self, show):
        """Define se deve mostrar eixos"""
        self.set("show_axes", show)
    
    def get_camera_params(self):
        """
        Retorna parâmetros da câmera
        
        Returns:
            Dicionário com distance, pitch, yaw
        """
        return {
            "distance": self.get("camera_distance", 400.0),
            "pitch": self.get("camera_pitch", 30.0),
            "yaw": self.get("camera_yaw", 0.0)
        }
    
    def set_camera_params(self, distance, pitch, yaw):
        """Define parâmetros da câmera"""
        self.set("camera_distance", distance)
        self.set("camera_pitch", pitch)
        self.set("camera_yaw", yaw)
    
    def get_window_params(self):
        """
        Retorna parâmetros da janela
        
        Returns:
            Dicionário com width, height, title
        """
        return {
            "width": self.get("window_width", 1200),
            "height": self.get("window_height", 900),
            "title": self.get("window_title", "3D Point Cloud Viewer")
        }
    
    def set_window_params(self, width, height):
        """Define dimensões da janela"""
        self.set("window_width", width)
        self.set("window_height", height)
    
    def get_background_presets(self):
        """Retorna lista de presets de cor de fundo"""
        return self.get("background_presets", self.DEFAULT_CONFIG["background_presets"])
    
    def get_recent_files(self):
        """Retorna lista de arquivos recentes"""
        return self.get("recent_files", [])
    
    def add_recent_file(self, filepath):
        """
        Adiciona arquivo ao histórico de recentes
        Mantém no máximo 5 arquivos, com o mais recente no topo
        
        Args:
            filepath: Caminho do arquivo a adicionar
        """
        recent = self.get("recent_files", [])
        
        # Remove o arquivo se já existir (para evitar duplicatas)
        if filepath in recent:
            recent.remove(filepath)
        
        # Adiciona no início da lista
        recent.insert(0, filepath)
        
        # Mantém apenas os 5 mais recentes
        recent = recent[:5]
        
        # Salva
        self.set("recent_files", recent)
    
    def clear_recent_files(self):
        """Limpa histórico de arquivos recentes"""
        self.set("recent_files", [])
    
    def __getitem__(self, key):
        """Permite acesso via config[key]"""
        return self.config[key]
    
    def __setitem__(self, key, value):
        """Permite atribuição via config[key] = value"""
        self.config[key] = value
