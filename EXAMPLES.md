# Exemplos de Uso

Este diretório contém exemplos práticos de como usar o viewer3d.

## Exemplo 1: Uso Básico

```python
from core.application import Viewer3DApplication

app = Viewer3DApplication()
app.load_file("exemplo.upl")
app.run()
```

## Exemplo 2: Configuração Customizada

```python
from core.application import Viewer3DApplication
from core.configuration import Configuration

# Cria configuração customizada
config = Configuration("my_config.json")
config.set_background_color([0.0, 0.0, 0.2, 1.0])
config.set_point_size(5.0)
config.save()

# Usa configuração
app = Viewer3DApplication("my_config.json")
app.run()
```

## Exemplo 3: Gerando Dados Sintéticos

```python
import numpy as np
from core.application import Viewer3DApplication

# Gera nuvem de pontos sintética
n_points = 10000
theta = np.random.uniform(0, 2*np.pi, n_points)
phi = np.random.uniform(0, np.pi, n_points)
r = np.random.uniform(50, 100, n_points)

x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

vertices = np.column_stack((x, y, z)).astype(np.float32)
colors = np.random.rand(n_points, 3).astype(np.float32)

# Visualiza
app = Viewer3DApplication()
app.point_renderer.set_data(vertices, colors)
app.run()
```

## Exemplo 4: Loader Customizado

Ver README.md seção "Adicionar Novo Formato de Arquivo"
