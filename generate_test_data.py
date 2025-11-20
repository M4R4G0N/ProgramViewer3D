"""
Gerador de dados de teste 3D com funções matemáticas
Cria arquivos .pts com padrões interessantes para visualização
"""

import numpy as np
import os


def save_pts(filename, points, colors=None):
    """
    Salva pontos em formato PTS simples
    Formato: X Y Z R G B (uma linha por ponto)
    
    Args:
        filename: Nome do arquivo
        points: Array (N, 3) com coordenadas XYZ
        colors: Array (N, 3) com cores RGB 0-255 (opcional)
    """
    with open(filename, 'w') as f:
        for i, (x, y, z) in enumerate(points):
            if colors is not None:
                r, g, b = colors[i]
                f.write(f"{x:.6f} {y:.6f} {z:.6f} {int(r)} {int(g)} {int(b)}\n")
            else:
                # Cor baseada em altura (Z)
                z_norm = (z - points[:, 2].min()) / (points[:, 2].max() - points[:, 2].min() + 0.0001)
                r = int(255 * (1 - z_norm))
                g = int(128)
                b = int(255 * z_norm)
                f.write(f"{x:.6f} {y:.6f} {z:.6f} {r} {g} {b}\n")
    
    print(f"✅ Arquivo criado: {filename} ({len(points)} pontos)")


def generate_sine_wave():
    """Onda senoidal 3D - ALTA RESOLUÇÃO"""
    print("\n🌊 Gerando onda senoidal (alta resolução)...")
    
    x = np.linspace(-10, 10, 200)  # 100 -> 500
    y = np.linspace(-10, 10, 200)  # 100 -> 500
    X, Y = np.meshgrid(x, y)
    
    # Z = sin(sqrt(x² + y²))
    R = np.sqrt(X**2 + Y**2)
    Z = 5 * np.sin(R) / (R + 1)
    
    # Achata arrays
    points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    
    save_pts('test_sine_wave.pts', points)


def generate_helix():
    """Hélice 3D - ULTRA DETALHADA"""
    print("\n🌀 Gerando hélice (ultra detalhada)...")
    
    t = np.linspace(0, 8 * np.pi, 10000)  # Mais voltas e mais pontos
    
    x = 5 * np.cos(t)
    y = 5 * np.sin(t)
    z = t * 2
    
    points = np.column_stack([x, y, z])
    
    # Cores do arco-íris (vetorizado para performance)
    hue = np.arange(len(points)) / len(points)
    colors = np.zeros((len(points), 3))
    colors[:, 0] = 255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi))
    colors[:, 1] = 255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi + 2 * np.pi / 3))
    colors[:, 2] = 255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi + 4 * np.pi / 3))
    
    save_pts('test_helix.pts', points, colors)


def generate_sphere():
    """Esfera - ALTA DENSIDADE"""
    print("\n🌍 Gerando esfera (alta densidade)...")
    
    phi = np.linspace(0, np.pi, 300)      # 50 -> 300
    theta = np.linspace(0, 2 * np.pi, 600)  # 100 -> 600
    PHI, THETA = np.meshgrid(phi, theta)
    
    radius = 10
    x = radius * np.sin(PHI) * np.cos(THETA)
    y = radius * np.sin(PHI) * np.sin(THETA)
    z = radius * np.cos(PHI)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    save_pts('test_sphere.pts', points)


def generate_torus():
    """Toroide (rosquinha) - SUPER DETALHADO"""
    print("\n🍩 Gerando toroide (super detalhado)...")
    
    u = np.linspace(0, 2 * np.pi, 500)  # 100 -> 500
    v = np.linspace(0, 2 * np.pi, 250)  # 50 -> 250
    U, V = np.meshgrid(u, v)
    
    R = 10  # Raio maior
    r = 3   # Raio menor
    
    x = (R + r * np.cos(V)) * np.cos(U)
    y = (R + r * np.cos(V)) * np.sin(U)
    z = r * np.sin(V)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    save_pts('test_torus.pts', points)


def generate_lorenz_attractor():
    """Atrator de Lorenz (caos) - TRAJETÓRIA LONGA"""
    print("\n🦋 Gerando atrator de Lorenz (trajetória longa)...")
    
    def lorenz(x, y, z, s=10, r=28, b=2.667):
        dx = s * (y - x)
        dy = r * x - y - x * z
        dz = x * y - b * z
        return dx, dy, dz
    
    dt = 0.005  # Mais preciso
    num_steps = 100000  # Muito mais pontos
    
    # Inicializa
    xs = np.empty(num_steps)
    ys = np.empty(num_steps)
    zs = np.empty(num_steps)
    
    xs[0], ys[0], zs[0] = (0., 1., 1.05)
    
    # Integração de Euler
    for i in range(num_steps - 1):
        dx, dy, dz = lorenz(xs[i], ys[i], zs[i])
        xs[i + 1] = xs[i] + dx * dt
        ys[i + 1] = ys[i] + dy * dt
        zs[i + 1] = zs[i] + dz * dt
    
    points = np.column_stack([xs, ys, zs])
    
    # Cores baseadas na velocidade (vetorizado)
    diff = np.diff(points, axis=0, prepend=points[0:1])
    speed = np.linalg.norm(diff, axis=1)
    speed_norm = np.minimum(speed * 10, 1.0)
    
    colors = np.zeros((len(points), 3))
    colors[:, 0] = 255 * speed_norm
    colors[:, 1] = 128
    colors[:, 2] = 255 * (1 - speed_norm)
    
    save_pts('test_lorenz.pts', points, colors)


def generate_mobius_strip():
    """Fita de Möbius - RESOLUÇÃO MÁXIMA"""
    print("\n♾️  Gerando fita de Möbius (resolução máxima)...")
    
    u = np.linspace(0, 2 * np.pi, 800)  # 100 -> 800
    v = np.linspace(-1, 1, 100)          # 20 -> 100
    U, V = np.meshgrid(u, v)
    
    radius = 10
    x = (radius + V * np.cos(U / 2)) * np.cos(U)
    y = (radius + V * np.cos(U / 2)) * np.sin(U)
    z = V * np.sin(U / 2)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    save_pts('test_mobius.pts', points)


def generate_klein_bottle():
    """Garrafa de Klein - ALTA RESOLUÇÃO"""
    print("\n🍾 Gerando garrafa de Klein (alta resolução)...")
    
    u = np.linspace(0, 2 * np.pi, 400)  # 100 -> 400
    v = np.linspace(0, 2 * np.pi, 400)  # 100 -> 400
    U, V = np.meshgrid(u, v)
    
    # Parametrização da garrafa de Klein
    r = 4 * (1 - np.cos(U) / 2)
    x = 6 * np.cos(U) * (1 + np.sin(U)) + r * np.cos(U) * np.cos(V)
    y = 16 * np.sin(U) + r * np.sin(U) * np.cos(V)
    z = r * np.sin(V)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    save_pts('test_klein.pts', points)


def generate_harmonics():
    """Superfície com harmônicos esféricos - DETALHAMENTO EXTREMO"""
    print("\n🎵 Gerando harmônicos esféricos (detalhamento extremo)...")
    
    phi = np.linspace(0, np.pi, 300)      # 50 -> 300
    theta = np.linspace(0, 2 * np.pi, 600)  # 100 -> 600
    PHI, THETA = np.meshgrid(phi, theta)
    
    # Combinação de harmônicos
    R = 10 + 2 * np.sin(3 * THETA) * np.sin(2 * PHI) + 1.5 * np.cos(5 * THETA) * np.cos(PHI)
    
    x = R * np.sin(PHI) * np.cos(THETA)
    y = R * np.sin(PHI) * np.sin(THETA)
    z = R * np.cos(PHI)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    save_pts('test_harmonics.pts', points)


def generate_trefoil_knot():
    """Nó trefoil (trevo) - ULTRA SUAVE"""
    print("\n🍀 Gerando nó trefoil (ultra suave)...")
    
    t = np.linspace(0, 2 * np.pi, 20000)  # 1000 -> 20000
    
    x = np.sin(t) + 2 * np.sin(2 * t)
    y = np.cos(t) - 2 * np.cos(2 * t)
    z = -np.sin(3 * t)
    
    # Escala
    points = np.column_stack([x * 5, y * 5, z * 5])
    
    save_pts('test_trefoil.pts', points)


def generate_mandelbrot_3d():
    """Conjunto de Mandelbrot em 3D (fatia) - RESOLUÇÃO 4K"""
    print("\n🎨 Gerando Mandelbrot 3D (resolução 4K)...")
    
    width, height = 2000, 2000  # 200 -> 2000 (10x mais denso!)
    xmin, xmax = -2.5, 1.0
    ymin, ymax = -1.25, 1.25
    max_iter = 100  # 50 -> 100 (mais detalhes)
    
    points = []
    colors = []
    
    print("   Processando pixels (pode levar alguns segundos)...")
    for i in range(width):
        if i % 200 == 0:
            print(f"   Progresso: {i/width*100:.1f}%")
        
        for j in range(height):
            x = xmin + (xmax - xmin) * i / width
            y = ymin + (ymax - ymin) * j / height
            
            c = complex(x, y)
            z = 0
            iter_count = 0
            
            while abs(z) < 2 and iter_count < max_iter:
                z = z * z + c
                iter_count += 1
            
            if iter_count < max_iter:
                points.append([x * 10, y * 10, iter_count * 0.5])
                
                # Cor baseada no número de iterações
                hue = iter_count / max_iter
                colors.append([
                    int(255 * hue),
                    int(255 * (1 - hue)),
                    int(128)
                ])
    
    points = np.array(points)
    colors = np.array(colors)
    
    save_pts('test_mandelbrot.pts', points, colors)


def generate_dragon_curve_3d():
    """Curva do dragão em 3D - ORDEM MÁXIMA"""
    print("\n🐉 Gerando curva do dragão (ordem máxima)...")
    
    def dragon_curve(order):
        if order == 0:
            return [(0, 0)]
        
        curve = dragon_curve(order - 1)
        result = []
        
        # Primeira metade
        for x, y in curve:
            result.append((x, y))
        
        # Segunda metade (rotacionada e invertida)
        for x, y in reversed(curve):
            result.append((-y, x))
        
        return result
    
    print("   Gerando curva fractal (pode demorar)...")
    curve_2d = dragon_curve(16)  # 12 -> 16 (muito mais pontos!)
    print(f"   Curva com {len(curve_2d):,} pontos gerada!")
    
    # Converte para 3D com espiral
    points = []
    for i, (x, y) in enumerate(curve_2d):
        z = i * 0.005  # 0.01 -> 0.005 (mais compacto)
        points.append([x * 2, y * 2, z])
    
    points = np.array(points)
    
    save_pts('test_dragon.pts', points)


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
        
    # Gera pontos em lotes para economizar memória
    batch_size = 1_000_000
    n_batches = n_points // batch_size
    
    all_points = []
    all_colors = []
    
    for batch in range(n_batches):

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
    
    
    # Junta todos os lotes
    print("\n🔗 Consolidando dados...")
    all_points = np.vstack(all_points)
    all_colors = np.vstack(all_colors)

    # Salva arquivo
    os.makedirs('test_data', exist_ok=True)
    save_pts('test_data/test_galaxy_10M.pts', all_points, all_colors)
    



def main():
    """Gera todos os arquivos de teste"""
    print("🎨 GERADOR DE DADOS DE TESTE 3D")
    print("=" * 50)
    
    # Cria diretório de testes se não existir
    os.makedirs('test_data', exist_ok=True)
    os.chdir('test_data')
    
    # Pergunta se quer gerar a galáxia de 10M pontos
    print("\n⚠️  GERAR GALÁXIA DE 10 MILHÕES DE PONTOS?")
    print("   Arquivo: ~400MB, tempo: 1-2 minutos")
    response = input("   Gerar? (s/N): ").strip().lower()
    
    if response == 's':
        generate_galaxy(10_000_000)
    
    # # Gera todos os outros padrões
    # generate_sine_wave()
    # generate_helix()
    # generate_sphere()
    # generate_torus()
    # generate_lorenz_attractor()
    # generate_mobius_strip()
    # generate_klein_bottle()
    # generate_harmonics()
    # generate_trefoil_knot()
    # generate_mandelbrot_3d()
    # generate_dragon_curve_3d()
    
    # print("\n" + "=" * 50)
    # print("✅ Todos os arquivos de teste foram criados na pasta 'test_data/'")
    # print("\nPara visualizar, execute:")
    # print("  python main.py test_data/test_sine_wave.pts")
    # print("  python main.py test_data/test_lorenz.pts")
    if response == 's':
        print("  python main.py test_data/test_galaxy_10M.pts  # 10 MILHÕES!")
    print("  etc...")


if __name__ == "__main__":
    main()
