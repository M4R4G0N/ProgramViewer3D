#!/usr/bin/env python3
"""
GUIA RÁPIDO: Como usar o Simulador de Trem
Exemplos prontos para copiar e colar
"""

# ==============================================================================
# EXEMPLO 1: USO BÁSICO - Gerar pontos do trem
# ==============================================================================

def exemplo1_basico():
    """
    Exemplo mais simples: criar trem e obter seus pontos
    """
    from utils.train_simulator import TrainSimulator
    
    # Cria um trem
    trem = TrainSimulator(
        num_wagons=3,           # 3 vagões
        wagon_length=15.0,      # 15 unidades de comprimento
        wagon_width=6.0,        # 6 de largura
        wagon_height=4.0,       # 4 de altura
        points_per_wagon=500    # 500 pontos por vagão
    )
    
    # Obtém os pontos na posição inicial
    pontos, cores = trem.get_points()
    
    print(f"✅ Trem criado com {len(pontos):,} pontos")
    print(f"   Cores: shape={cores.shape}")
    print(f"   Posição Z: {trem.get_position():.2f}")


# ==============================================================================
# EXEMPLO 2: SIMULAR MOVIMENTO
# ==============================================================================

def exemplo2_movimento():
    """
    Mover o trem através do espaço 3D
    """
    from utils.train_simulator import TrainSimulator
    
    trem = TrainSimulator(num_wagons=4, wagon_length=12.0)
    
    # Simula 10 frames
    for frame in range(10):
        # Atualiza posição (move ao longo do eixo Z)
        trem.update(dt=1.0)
        
        # Obtém pontos
        pontos, cores = trem.get_points()
        
        print(f"Frame {frame}: Z={trem.get_position():6.2f} | Pontos: {len(pontos):,}")
    
    # Informações
    min_bounds, max_bounds = trem.get_bounds()
    print(f"\nBounding box:")
    print(f"  Min: {min_bounds}")
    print(f"  Max: {max_bounds}")


# ==============================================================================
# EXEMPLO 3: TREM AVANÇADO COM FUMAÇA
# ==============================================================================

def exemplo3_avancado():
    """
    Usar o trem avançado com locomotora e efeito de fumaça
    """
    from utils.train_simulator import AdvancedTrainSimulator
    
    trem = AdvancedTrainSimulator(
        num_wagons=5,
        has_locomotive=True,    # Inclui locomotora
        has_smoke_effect=True   # Gera fumaça
    )
    
    # Simula alguns frames
    for frame in range(5):
        trem.update(dt=1.0)
        pontos, cores = trem.get_points()
        print(f"Frame {frame}: Pontos (incluindo fumaça): {len(pontos):,}")


# ==============================================================================
# EXEMPLO 4: SALVAR TREM EM ARQUIVO PTS
# ==============================================================================

def exemplo4_salvar():
    """
    Gerar arquivo PTS com o trem para visualizar no visualizador 3D
    """
    from utils.train_simulator import TrainSimulator
    import numpy as np
    
    # Cria trem
    trem = TrainSimulator(num_wagons=6, points_per_wagon=1000)
    
    # Obtém pontos
    pontos, cores = trem.get_points()
    
    # Normaliza cores se necessário
    if cores.max() > 1.0:
        cores = (cores / 255.0).astype(np.float32)
    
    # Salva em arquivo PTS (formato: X Y Z R G B)
    filename = "meu_trem.pts"
    with open(filename, 'w') as f:
        for i, (x, y, z) in enumerate(pontos):
            r, g, b = (cores[i] * 255).astype(int)
            r = np.clip(r, 0, 255)
            g = np.clip(g, 0, 255)
            b = np.clip(b, 0, 255)
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b}\n")
    
    print(f"✅ Arquivo salvo: {filename}")
    print(f"   Para visualizar, execute:")
    print(f"   python main.py {filename}")


# ==============================================================================
# EXEMPLO 5: CONTROLAR VELOCIDADE
# ==============================================================================

def exemplo5_velocidade():
    """
    Controlar a velocidade do trem
    """
    from utils.train_simulator import TrainSimulator
    
    trem = TrainSimulator(num_wagons=3)
    
    # Lento
    print("⚡ Teste de velocidades:")
    trem.set_velocity(0.2)
    for i in range(3):
        trem.update(dt=1.0)
        print(f"  Lento (0.2): Z={trem.get_position():.1f}")
    
    # Rápido
    trem.reset()
    trem.set_velocity(2.0)
    print()
    for i in range(3):
        trem.update(dt=1.0)
        print(f"  Rápido (2.0): Z={trem.get_position():.1f}")


# ==============================================================================
# EXEMPLO 6: CUSTOMIZAR APARÊNCIA
# ==============================================================================

def exemplo6_custom():
    """
    Criar trem com parâmetros customizados
    """
    from utils.train_simulator import TrainSimulator
    
    # Trem longo e fino
    trem1 = TrainSimulator(
        num_wagons=10,           # Muitos vagões
        wagon_length=8.0,        # Compridos
        wagon_width=3.0,         # Estrechos
        wagon_height=2.0,        # Baixos
        points_per_wagon=200     # Menos pontos = mais rápido
    )
    
    # Trem curto e largo
    trem2 = TrainSimulator(
        num_wagons=2,            # Poucos vagões
        wagon_length=20.0,       # Muito compridos
        wagon_width=15.0,        # Largos
        wagon_height=10.0,       # Altos
        points_per_wagon=2000    # Muitos pontos = mais denso
    )
    
    print("Trem 1 (longo e fino):")
    p1, _ = trem1.get_points()
    print(f"  Total: {len(p1):,} pontos")
    
    print("\nTrem 2 (curto e largo):")
    p2, _ = trem2.get_points()
    print(f"  Total: {len(p2):,} pontos")


# ==============================================================================
# EXEMPLO 7: INTEGRAÇÃO COM APLICAÇÃO 3D
# ==============================================================================

def exemplo7_integracao():
    """
    Integrar trem com visualizador 3D existente
    """
    # Este é um exemplo de como fazer a integração manualmente
    # Para uso automático, veja exemplo8_completo()
    
    code = '''
from core.application import Viewer3DApplication
from utils.train_simulator import TrainSimulator
from renderers.train_renderer import TrainRenderer

# Cria app
app = Viewer3DApplication()

# Cria trem e renderizador
trem = TrainSimulator(num_wagons=5)
trem_renderer = TrainRenderer(trem)

# No seu loop de renderização principal:
while not glfw.window_should_close(app.window):
    # ... código de renderização existente ...
    
    # Atualiza e renderiza trem
    trem.update(dt=1.0)
    trem_renderer._update_vbo_data()
    trem_renderer.render()
    
    # ... mais código ...
'''
    print("Código de integração manual:")
    print(code)


# ==============================================================================
# EXEMPLO 8: USO COMPLETO (RECOMENDADO)
# ==============================================================================

def exemplo8_completo():
    """
    Forma recomendada: usar TrainViewer que cuida de tudo
    """
    code = '''
#!/usr/bin/env python3
from core.application import Viewer3DApplication
from train_viewer import TrainViewer

# Configuração do trem
config = {
    'mode': 'advanced',      # Com fumaça
    'num_wagons': 6,
    'wagon_length': 20.0,
    'wagon_width': 8.0,
    'wagon_height': 5.0,
    'points_per_wagon': 800,
}

# Cria aplicação
app = Viewer3DApplication()

# Integra trem (automático!)
train_app = TrainViewer(
    app,
    train_config=config,
    data_file='seu_arquivo.pts'  # Opcional
)

# Tudo funcionando!
app.run()

# Controles:
# K - Toggle trem
# L - Toggle nuvem
# G - Toggle grade
# +/- - Velocidade
# SPACE - Pausa
# R - Reseta
'''
    print("Forma completa recomendada:")
    print(code)


# ==============================================================================
# MAIN - EXECUTA TODOS OS EXEMPLOS
# ==============================================================================

def main():
    """Executa todos os exemplos"""
    
    print("\n" + "="*70)
    print("🚂 GUIA DE USO RÁPIDO - SIMULADOR DE TREM")
    print("="*70 + "\n")
    
    exemplos = [
        ("Básico", exemplo1_basico),
        ("Movimento", exemplo2_movimento),
        ("Avançado com fumaça", exemplo3_avancado),
        ("Salvar em arquivo", exemplo4_salvar),
        ("Controlar velocidade", exemplo5_velocidade),
        ("Customização", exemplo6_custom),
        ("Integração manual", exemplo7_integracao),
        ("Uso completo", exemplo8_completo),
    ]
    
    for titulo, func in exemplos:
        print(f"\n{'─'*70}")
        print(f"📚 Exemplo: {titulo}")
        print(f"{'─'*70}\n")
        
        try:
            func()
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        input("\n[Pressione Enter para continuar...]")
    
    print("\n" + "="*70)
    print("✅ TODOS OS EXEMPLOS COMPLETADOS!")
    print("="*70)
    print("\n💡 Para mais informações, veja TRAIN_SIMULATOR_README.md")


if __name__ == "__main__":
    main()
