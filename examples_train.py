#!/usr/bin/env python3
"""
Exemplo simples: Visualizar apenas o trem (sem arquivo de nuvem de pontos)
Use isto como ponto de partida para entender como o trem funciona
"""

from utils.train_simulator import TrainSimulator, AdvancedTrainSimulator
import numpy as np


def demo_basic_train():
    """Demonstra uso basico do TrainSimulator"""
    
    print("\n" + "=" * 60)
    print("[DEMO] TREM BASICO")
    print("=" * 60)
    
    # Cria um trem simples
    train = TrainSimulator(
        num_wagons=3,
        wagon_length=15.0,
        wagon_width=6.0,
        wagon_height=4.0,
        points_per_wagon=500
    )
    
    # Simula alguns frames
    print("\n[INFO] Simulando movimento do trem...")
    print(f"Posição inicial: Z = {train.get_position():.2f}")
    
    for frame in range(10):
        train.update(dt=1.0)
        points, colors = train.get_points()
        print(f"Frame {frame}: Z = {train.get_position():7.2f} | Pontos: {len(points):,} | Cores: {colors.shape}")
    
    print(f"\n[OK] Total de pontos gerados: {len(points):,}")
    print(f"Bounding box: {train.get_bounds()}")
    
    # Salva exemplo em arquivo PTS
    print("\n[SAVE] Salvando primeiro frame em arquivo...")
    train.reset()
    points, colors = train.get_points()
    
    # Normaliza cores se necessário
    if colors.max() > 1.0:
        colors = colors / 255.0
    
    # Salva em formato simples
    filename = "train_example.pts"
    with open(filename, 'w') as f:
        for i, (x, y, z) in enumerate(points):
            r, g, b = (colors[i] * 255).astype(int)
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b}\n")
    
    print(f"✅ Arquivo salvo: {filename}")
    print(f"   Use para visualizar: python main.py {filename}")


def demo_advanced_train():
    """Demonstra uso avancado do TrainSimulator com fumaca"""
    
    print("\n" + "=" * 60)
    print("[DEMO] TREM AVANCADO (COM FUMACA)")
    print("=" * 60)
    
    # Cria trem avançado
    train = AdvancedTrainSimulator(
        num_wagons=4,
        wagon_length=18.0,
        wagon_width=7.0,
        wagon_height=5.0,
        points_per_wagon=600,
        has_locomotive=True,
        has_smoke_effect=True
    )
    
    # Simula
    print("\n[INFO] Simulando trem com locomotora e fumaca...")
    print(f"Posição inicial: Z = {train.get_position():.2f}")
    
    for frame in range(5):
        train.update(dt=1.0)
        points, colors = train.get_points()
        print(f"Frame {frame}: Z = {train.get_position():7.2f} | Pontos: {len(points):,}")
    
    print(f"\n[OK] Total de pontos (incluindo fumaca): {len(points):,}")
    
    # Salva frame com fumaca
    print("\n[SAVE] Salvando frame com fumaca...")
    filename = "train_advanced.pts"
    
    # Normaliza cores
    if colors.shape[1] > 3:
        colors = colors[:, :3]  # Remove alfa se existe
    if colors.max() > 1.0:
        colors = colors / 255.0
    
    with open(filename, 'w') as f:
        for i, (x, y, z) in enumerate(points):
            r, g, b = (colors[i] * 255).astype(int)
            r = np.clip(r, 0, 255).astype(int)
            g = np.clip(g, 0, 255).astype(int)
            b = np.clip(b, 0, 255).astype(int)
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b}\n")
    
    print(f"[OK] Arquivo salvo: {filename}")


def demo_train_customization():
    """Demonstra customizacao do trem"""
    
    print("\n" + "=" * 60)
    print("[DEMO] CUSTOMIZACAO")
    print("=" * 60)
    
    # Cria trem com diferentes parâmetros
    train = TrainSimulator(
        num_wagons=8,           # Trem longo
        wagon_length=25.0,      # Vagoes grandes
        wagon_width=10.0,
        wagon_height=6.0,
        points_per_wagon=1000,  # Mais denso
        gap_between_wagons=5.0   # Espaco maior entre vagoes
    )
    
    print(f"\n[INFO] Trem customizado:")
    print(f"  - {train.num_wagons} vagoes")
    print(f"  - Tamanho: {train.wagon_width:.1f}m x {train.wagon_height:.1f}m x {train.wagon_length:.1f}m")
    print(f"  - Pontos por vagao: {train.points_per_wagon:,}")
    print(f"  - Total de pontos: {train.num_wagons * train.points_per_wagon:,}")
    
    # Controla velocidade
    print(f"\n[TEST] Teste de velocidade:")
    train.set_velocity(1.0)
    for frame in range(5):
        train.update(dt=1.0)
        print(f"  V={train.get_velocity():.1f}: Z = {train.get_position():.2f}")
    
    # Reseta e aumenta velocidade
    train.reset()
    train.set_velocity(2.0)
    print(f"\nAumentando velocidade para {train.get_velocity()}...")
    for frame in range(5):
        train.update(dt=1.0)
        print(f"  V={train.get_velocity():.1f}: Z = {train.get_position():.2f}")


def main():
    """Executa todos os demos"""
    
    print("\n" + "=" * 60)
    print("[TRAIN] EXEMPLOS DE USO - TRAIN SIMULATOR")
    print("=" * 60)
    
    # Demo 1
    demo_basic_train()
    
    # Demo 2
    demo_advanced_train()
    
    # Demo 3
    demo_train_customization()
    
    print("\n" + "=" * 60)
    print("[OK] TODOS OS EXEMPLOS COMPLETADOS!")
    print("=" * 60)
    print("\n[TIP] Proximas etapas:")
    print("1. Visualize os arquivos PTS gerados:")
    print("   python main.py train_example.pts")
    print("   python main.py train_advanced.pts")
    print()
    print("2. Para simular trem com nuvem de pontos:")
    print("   python train_simulation.py seu_arquivo.pts")
    print()
    print("3. Estude os controles em train_simulation.py")
    print()


if __name__ == "__main__":
    main()
