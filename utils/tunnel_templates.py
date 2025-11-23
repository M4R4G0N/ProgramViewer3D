"""
Sistema de Gabaritos de Túnel (Tunnel Templates)
Define as zonas de segurança, alerta e invasão para diferentes tipos de túneis
"""

import numpy as np
from abc import ABC, abstractmethod


class TunnelTemplate(ABC):
    """Classe base para gabaritos de túnel"""
    
    @property
    @abstractmethod
    def name(self):
        """Nome do gabarito (ex: 'Túnel Ferrovia', 'Rodovia Dupla')"""
        pass
    
    @property
    @abstractmethod
    def safe_zone(self):
        """Define a zona segura - pontos aqui NÃO invadem"""
        pass
    
    @property
    @abstractmethod
    def warning_zone(self):
        """Define a zona de alerta - pontos aqui estão em margem"""
        pass
    
    def classify_point(self, x, y):
        """
        Classifica um ponto como SEGURO (0), ALERTA (1) ou INVASÃO (2)
        
        Args:
            x, y: Coordenadas do ponto
            
        Returns:
            0 = Seguro (verde)
            1 = Alerta (amarelo)
            2 = Invasão (vermelho)
        """
        if self._point_in_zone(x, y, self.safe_zone):
            return 2  # INVASÃO - está dentro da zona segura (que é o túnel)
        elif self._point_in_zone(x, y, self.warning_zone):
            return 1  # ALERTA - está na margem
        else:
            return 0  # SEGURO - fora do gabarito
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        """Verifica se ponto está dentro de uma zona (genérico)"""
        return False  # Deve ser sobrescrito
    
    def get_description(self):
        """Retorna descrição do gabarito"""
        return f"{self.name}"


class FerroviaTunel(TunnelTemplate):
    """Gabarito para túnel ferroviário - seção simples"""
    
    @property
    def name(self):
        return "Túnel Ferrovia"
    
    @property
    def safe_zone(self):
        """Zona de segurança do túnel (não pode invadir)"""
        return {
            'type': 'composite',  # Retângulo + semicírculo
            'rect': {'x_min': -2.2, 'x_max': 2.2, 'y_min': 2.5, 'y_max': 5.8},
            'semicircle': {'x_center': 0, 'y_center': 5.8, 'radius': 2.2, 'y_min': 5.8}
        }
    
    @property
    def warning_zone(self):
        """Zona de alerta (margem de segurança)"""
        return {
            'type': 'composite',
            'rect': {'x_min': -2.7, 'x_max': 2.7, 'y_min': 2.4, 'y_max': 5.8},
            'semicircle': {'x_center': 0, 'y_center': 5.8, 'radius': 2.7, 'y_min': 5.8, 'y_max': 8.5}
        }
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        """Verifica se ponto está na zona (ferroviária)"""
        if zone['type'] != 'composite':
            return False
        
        x_abs = abs(x)
        
        # Verifica retângulo
        rect = zone['rect']
        if rect['x_min'] <= x_abs <= rect['x_max'] and rect['y_min'] <= y <= rect['y_max']:
            return True
        
        # Verifica semicírculo superior
        if 'semicircle' in zone:
            semi = zone['semicircle']
            y_center = semi['y_center']
            radius = semi['radius']
            y_min = semi.get('y_min', y_center)
            y_max = semi.get('y_max', float('inf'))
            
            if y_min <= y <= y_max:
                dist = np.sqrt(x**2 + (y - y_center)**2)
                if dist <= radius:
                    return True
        
        return False


class RodoviaDupla(TunnelTemplate):
    """Gabarito para rodovia dupla - duas pistas independentes"""
    
    @property
    def name(self):
        return "Rodovia Dupla (4 faixas)"
    
    @property
    def safe_zone(self):
        """Zona segura: espaço entre duas pistas"""
        return {
            'type': 'two_rectangles',
            'pista1': {'x_min': -4.5, 'x_max': -2.0, 'y_min': 0.0, 'y_max': 4.0},
            'pista2': {'x_min': 2.0, 'x_max': 4.5, 'y_min': 0.0, 'y_max': 4.0}
        }
    
    @property
    def warning_zone(self):
        """Zona de alerta: margens das pistas"""
        return {
            'type': 'two_rectangles',
            'pista1': {'x_min': -5.0, 'x_max': -1.5, 'y_min': -0.5, 'y_max': 4.5},
            'pista2': {'x_min': 1.5, 'x_max': 5.0, 'y_min': -0.5, 'y_max': 4.5}
        }
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        """Verifica se ponto está em zona de rodovia dupla"""
        if zone['type'] != 'two_rectangles':
            return False
        
        for pista_key in ['pista1', 'pista2']:
            if pista_key in zone:
                rect = zone[pista_key]
                if rect['x_min'] <= x <= rect['x_max'] and rect['y_min'] <= y <= rect['y_max']:
                    return True
        
        return False


class TuneloAqued(TunnelTemplate):
    """Gabarito para túnel de aqüeduto - seção complexa com canaleta"""
    
    @property
    def name(self):
        return "Túnel Aqüeduto"
    
    @property
    def safe_zone(self):
        """Zona segura: dentro da canaleta"""
        return {
            'type': 'trapezoid',
            'x_min_bottom': -2.5, 'x_max_bottom': 2.5,
            'x_min_top': -2.0, 'x_max_top': 2.0,
            'y_min': 0.0, 'y_max': 3.0,
            'arch_center_y': 3.0, 'arch_radius': 2.5
        }
    
    @property
    def warning_zone(self):
        """Zona de alerta: margens da estrutura"""
        return {
            'type': 'trapezoid',
            'x_min_bottom': -3.0, 'x_max_bottom': 3.0,
            'x_min_top': -1.5, 'x_max_top': 1.5,
            'y_min': -0.5, 'y_max': 3.5,
            'arch_center_y': 3.5, 'arch_radius': 3.0
        }
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        """Verifica se ponto está em zona de aqüeduto"""
        if zone['type'] != 'trapezoid':
            return False
        
        x_abs = abs(x)
        trapez = zone
        
        # Interpola limites X conforme Y
        y_min = trapez['y_min']
        y_max = trapez['y_max'] - 0.1  # Antes do arco
        
        if y_min <= y < y_max:
            # Interpolação linear do trapézio
            ratio = (y - y_min) / (y_max - y_min)
            x_min_interp = trapez['x_min_bottom'] + ratio * (trapez['x_min_top'] - trapez['x_min_bottom'])
            x_max_interp = trapez['x_max_bottom'] + ratio * (trapez['x_max_top'] - trapez['x_max_bottom'])
            
            if x_min_interp <= x_abs <= x_max_interp:
                return True
        
        # Verifica arco superior
        arch_center_y = trapez['arch_center_y']
        arch_radius = trapez['arch_radius']
        if y >= y_max:
            dist = np.sqrt(x**2 + (y - arch_center_y)**2)
            if dist <= arch_radius:
                return True
        
        return False


class GabaritPersonalizado(TunnelTemplate):
    """Gabarito personalizável - para casos específicos"""
    
    def __init__(self, name, safe_bounds, warning_bounds):
        """
        Args:
            name: Nome do gabarito
            safe_bounds: Dicionário com limites da zona segura {'x_min', 'x_max', 'y_min', 'y_max'}
            warning_bounds: Dicionário com limites da zona de alerta
        """
        self._name = name
        self._safe_bounds = safe_bounds
        self._warning_bounds = warning_bounds
    
    @property
    def name(self):
        return self._name
    
    @property
    def safe_zone(self):
        return {'type': 'rectangle', 'bounds': self._safe_bounds}
    
    @property
    def warning_zone(self):
        return {'type': 'rectangle', 'bounds': self._warning_bounds}
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        """Verifica se ponto está em zona retangular"""
        if zone['type'] != 'rectangle':
            return False
        
        bounds = zone['bounds']
        x_abs = abs(x)
        
        return (bounds['x_min'] <= x_abs <= bounds['x_max'] and
                bounds['y_min'] <= y <= bounds['y_max'])


class TemplateRegistry:
    """Registro de gabaritos disponíveis"""
    
    _templates = {
        'ferrovia': FerroviaTunel(),
        'rodovia': RodoviaDupla(),
        'aqueduto': TuneloAqued(),
    }
    
    @classmethod
    def register(cls, key, template):
        """Registra um novo gabarito"""
        cls._templates[key.lower()] = template
    
    @classmethod
    def get(cls, key):
        """Obtém um gabarito pelo nome"""
        return cls._templates.get(key.lower())
    
    @classmethod
    def list_all(cls):
        """Lista todos os gabaritos disponíveis"""
        return list(cls._templates.keys())
    
    @classmethod
    def get_names(cls):
        """Retorna nome formatado de cada gabarito"""
        return {key: template.name for key, template in cls._templates.items()}


def classify_points_with_template(xs, ys, template):
    """
    Classifica pontos usando um gabarito
    
    Args:
        xs, ys: Arrays de coordenadas
        template: Instância de TunnelTemplate
        
    Returns:
        Array de classificações (0=seguro, 1=alerta, 2=invasão)
    """
    classifications = np.zeros(len(xs), dtype=np.int32)
    
    for i in range(len(xs)):
        classifications[i] = template.classify_point(xs[i], ys[i])
    
    return classifications


def colors_from_classification(classifications):
    """
    Converte classificações em cores RGB
    
    Args:
        classifications: Array de valores 0, 1, 2
        
    Returns:
        Array de cores (N, 3) em formato RGB float [0, 1]
    """
    colors = np.zeros((len(classifications), 3), dtype=np.float32)
    
    for i, cls in enumerate(classifications):
        if cls == 0:  # SEGURO
            colors[i] = [0.0, 1.0, 0.0]  # Verde
        elif cls == 1:  # ALERTA
            colors[i] = [1.0, 1.0, 0.0]  # Amarelo
        else:  # INVASÃO (2)
            colors[i] = [1.0, 0.0, 0.0]  # Vermelho
    
    return colors


if __name__ == '__main__':
    # Teste dos gabaritos
    print("🔧 Sistema de Gabaritos de Túnel")
    print("="*60)
    
    for key in TemplateRegistry.list_all():
        template = TemplateRegistry.get(key)
        print(f"\n📋 {template.name}")
        
        # Teste alguns pontos
        test_points = [
            (0.0, 3.0, "Centro do túnel"),
            (2.0, 4.0, "Lado direito, meio do túnel"),
            (2.5, 4.0, "Alerta - margem"),
            (3.0, 4.0, "Seguro - fora"),
        ]
        
        for x, y, desc in test_points:
            cls = template.classify_point(x, y)
            status = ['SEGURO', 'ALERTA', 'INVASÃO'][cls]
            print(f"   ({x:5.1f}, {y:5.1f}) → {status:8} | {desc}")
