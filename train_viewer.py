"""
Script de integração para adicionar simulação de trem à aplicação
Fornece exemplos e funcionalidades para usar o TrainSimulator
"""

from utils.train_simulator import TrainSimulator, AdvancedTrainSimulator
from renderers.train_renderer import TrainRenderer, TrainVisualizationMode


def create_train_simulator(mode='basic', **kwargs):
    """
    Factory para criar simulador de trem
    
    Args:
        mode: 'basic' ou 'advanced'
        **kwargs: Argumentos para o simulador
        
    Returns:
        Instância do simulador
    """
    if mode == 'advanced':
        return AdvancedTrainSimulator(**kwargs)
    else:
        return TrainSimulator(**kwargs)


def integrate_train_to_app(app, train_config=None):
    """
    Integra simulação de trem a uma aplicação existente
    
    Args:
        app: Instância de Viewer3DApplication
        train_config: Dict com configuração do trem
        
    Returns:
        Tupla (train_simulator, train_renderer)
    """
    
    # Configuração padrão do trem
    if train_config is None:
        train_config = {
            'num_wagons': 5,
            'wagon_length': 15.0,
            'wagon_width': 8.0,
            'wagon_height': 5.0,
            'points_per_wagon': 500,
            'gap_between_wagons': 2.0,
            'mode': 'advanced'
        }
    
    # Extrai modo
    mode = train_config.pop('mode', 'basic')
    
    # Cria simulador
    train_sim = create_train_simulator(mode, **train_config)
    
    # Cria renderizador
    train_renderer = TrainRenderer(train_sim)
    
    # Initializa primeira atualização
    train_renderer._update_vbo_data()
    
    print(f"🚂 Trem integrado à aplicação!")
    
    return train_sim, train_renderer


def setup_train_visualization_mode(app, point_cloud_renderer, train_renderer):
    """
    Configura modo de visualização com trem
    
    Args:
        app: Aplicação
        point_cloud_renderer: Renderizador de nuvem de pontos
        train_renderer: Renderizador do trem
        
    Returns:
        TrainVisualizationMode
    """
    mode = TrainVisualizationMode(point_cloud_renderer, train_renderer)
    
    # Adiciona controles de teclado
    print("⌨️  Controles do trem:")
    print("   K: Ativa/desativa trem")
    print("   L: Ativa/desativa nuvem de pontos")
    print("   G: Mostra/esconde grade")
    print("   +/-: Aumenta/diminui velocidade do trem")
    print("   SPACE: Pausa/retoma trem")
    print("   R: Reseta posição do trem")
    
    return mode


# Exemplo de uso integrado
class TrainViewer:
    """
    Aplicação completa com visualização de trem + nuvem de pontos
    """
    
    def __init__(self, app, train_config=None, data_file=None):
        """
        Inicializa viewer com trem
        
        Args:
            app: Aplicação base (Viewer3DApplication)
            train_config: Configuração do trem
            data_file: Arquivo de dados para nuvem de pontos
        """
        self.app = app
        self.data_file = data_file
        
        # Integra trem
        self.train_sim, self.train_renderer = integrate_train_to_app(app, train_config)
        
        # Cria modo de visualização
        self.vis_mode = setup_train_visualization_mode(
            app,
            app.point_renderer,
            self.train_renderer
        )
        
        # Estados de controle
        self.train_paused = False
        self.original_train_velocity = self.train_sim.z_velocity
        
        # Carrega dados se fornecido
        if data_file:
            app.load_file(data_file)
        
        print("✅ Viewer com trem pronto para uso!")
    
    def handle_train_key_input(self, key):
        """
        Trata entrada de teclado para controles do trem
        
        Args:
            key: Código da tecla GLFW
        """
        import glfw
        
        # K: Toggle trem
        if key == glfw.KEY_K:
            self.vis_mode.show_train = not self.vis_mode.show_train
            print(f"🚂 Trem: {'Visível' if self.vis_mode.show_train else 'Oculto'}")
        
        # L: Toggle nuvem de pontos
        elif key == glfw.KEY_L:
            self.vis_mode.show_point_cloud = not self.vis_mode.show_point_cloud
            print(f"☁️  Nuvem: {'Visível' if self.vis_mode.show_point_cloud else 'Oculto'}")
        
        # G: Toggle grade
        elif key == glfw.KEY_G:
            self.vis_mode.show_grid = not self.vis_mode.show_grid
            print(f"📊 Grade: {'Visível' if self.vis_mode.show_grid else 'Oculto'}")
        
        # +/-: Velocidade
        elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
            speed = self.train_sim.z_velocity * 1.2
            self.train_sim.set_velocity(speed)
            print(f"⚡ Velocidade: {speed:.2f}")
        
        elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
            speed = self.train_sim.z_velocity * 0.8
            self.train_sim.set_velocity(max(0.01, speed))
            print(f"⚡ Velocidade: {speed:.2f}")
        
        # SPACE: Pausa/resume
        elif key == glfw.KEY_SPACE:
            self.train_paused = not self.train_paused
            if self.train_paused:
                self.original_train_velocity = self.train_sim.z_velocity
                self.train_sim.set_velocity(0)
                print("⏸️  Trem pausado")
            else:
                self.train_sim.set_velocity(self.original_train_velocity)
                print("▶️  Trem retomado")
        
        # R: Reset
        elif key == glfw.KEY_R:
            self.train_sim.reset()
            self.train_paused = False
            self.train_sim.set_velocity(self.original_train_velocity)
            print("🔄 Trem reposicionado")
    
    def update(self, dt=1.0):
        """Atualiza simulação"""
        self.vis_mode.update(dt)
        self.train_renderer._update_vbo_data()
    
    def render(self):
        """Renderiza cena com trem"""
        self.vis_mode.render()
    
    def get_camera_focus(self):
        """Retorna ponto de foco da câmera"""
        return self.vis_mode.get_camera_focus()
