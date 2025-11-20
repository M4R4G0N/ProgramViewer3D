"""
Gerador de galáxia espiral com 10 MILHÕES de pontos
TESTE DE STRESS EXTREMO para o visualizador 3D
"""

import numpy as np
import os
import time


def save_pts(filename, points, colors):
    """Salva pontos em formato PTS"""
    print(f"\n💾 Salvando arquivo: {filename}")
    
    with open(filename, 'w') as f:
        for i in range(len(points)):
            x, y, z = points[i]
            r, g, b = colors[i]
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {int(r)} {int(g)} {int(b)}\n")
    
    file_size_mb = os.path.getsize(filename) / 1024 / 1024
    print(f"✅ Arquivo criado: {filename}")
    print(f"   Tamanho: {file_size_mb:.1f} MB")
    print(f"   Pontos: {len(points):,}")


def generate_galaxy(n_points=10_000_000):
    """
    Gera uma galáxia espiral com milhões de pontos
    
    Args:
        n_points: Número de pontos (padrão: 10 milhões)
    """
    print("🌌 GERADOR DE GALÁXIA ESPIRAL")
    print("=" * 60)
    print(f"   Pontos: {n_points:,}")
    print(f"   Tamanho estimado: ~{n_points * 40 / 1024 / 1024:.0f} MB")
    print("=" * 60)
    
    start_time = time.time()
    
    # Gera pontos em lotes para economizar memória
    batch_size = 1_000_000
    n_batches = n_points // batch_size
    
    all_points = []
    all_colors = []
    
    for batch in range(n_batches):
        batch_start = time.time()
        print(f"\n📊 Processando lote {batch + 1}/{n_batches}...")
        
        # Parâmetros da galáxia espiral
        t = np.random.uniform(0, 10 * np.pi, batch_size)
        r_base = np.random.exponential(12, batch_size)  # Distribuição exponencial (mais denso no centro)
        
        # Número de braços espirais
        n_arms = 4
        arm_angle = (t % (2 * np.pi / n_arms)) * n_arms + np.random.normal(0, 0.2, batch_size)
        
        # Posição no braço espiral
        r = r_base + np.random.normal(0, 1.5, batch_size)
        theta = t + arm_angle
        
        # Altura (achatamento da galáxia)
        z = np.random.normal(0, 1.5, batch_size) * (1 - r / 35)  # Mais fino nas bordas
        
        # Coordenadas cartesianas
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        points = np.column_stack([x, y, z])
        all_points.append(points)
        
        # Cores: azul no centro (estrelas jovens), vermelho/amarelo nas bordas (estrelas velhas)
        r_norm = np.clip(r / 35, 0, 1)
        
        colors = np.zeros((batch_size, 3))
        # Centro azul -> meio branco/amarelo -> bordas vermelho
        colors[:, 0] = 255 * (0.2 + 0.8 * r_norm)  # R: aumenta com distância
        colors[:, 1] = 255 * (0.3 + 0.5 * (1 - abs(r_norm - 0.5) * 2))  # G: pico no meio
        colors[:, 2] = 255 * (0.9 - 0.7 * r_norm)  # B: diminui com distância
        
        # Adiciona estrelas brilhantes aleatórias
        bright_stars = np.random.random(batch_size) > 0.995
        colors[bright_stars] = 255
        
        all_colors.append(colors)
        
        batch_time = time.time() - batch_start
        print(f"   ✓ Lote {batch + 1} concluído em {batch_time:.1f}s")
    
    # Junta todos os lotes
    print("\n🔗 Consolidando dados...")
    all_points = np.vstack(all_points)
    all_colors = np.vstack(all_colors)
    
    generation_time = time.time() - start_time
    print(f"✅ Geração concluída em {generation_time:.1f}s")
    
    # Salva arquivo
    os.makedirs('test_data', exist_ok=True)
    save_pts('test_data/test_galaxy_10M.pts', all_points, all_colors)
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Tempo total: {total_time:.1f}s ({total_time/60:.1f} minutos)")
    print("\n🚀 Para visualizar, execute:")
    print("   python main.py test_data/test_galaxy_10M.pts")


if __name__ == "__main__":
    print("\n")
    generate_galaxy(10_000_000)
    print("\n")
