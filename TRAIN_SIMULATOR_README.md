# 🚂 Simulador de Trem 3D - Documentação

Um simulador de trem 3D que passa pelo eixo Z, integrável com seu visualizador de nuvem de pontos.

## 🎯 Características

- **TrainSimulator**: Simulador básico de trem com vagões coloridos
- **AdvancedTrainSimulator**: Versão avançada com locomotora e efeito de fumaça
- **TrainRenderer**: Renderização otimizada com VBO (Vertex Buffer Objects)
- **Integração perfeita**: Funciona com o visualizador de nuvem de pontos existente
- **Controles interativos**: Velocidade, pausa, visibilidade em tempo real

## 📦 Componentes

### 1. `utils/train_simulator.py`
Define as classes simuladoras:
- `TrainSimulator`: Trem simples
- `AdvancedTrainSimulator`: Trem com fumaça e locomotora

```python
from utils.train_simulator import TrainSimulator, AdvancedTrainSimulator

# Trem básico
train = TrainSimulator(
    num_wagons=5,
    wagon_length=15.0,
    wagon_width=8.0,
    wagon_height=5.0,
    points_per_wagon=1000
)

# Atualiza posição
train.update(dt=1.0)

# Obtém pontos para renderização
points, colors = train.get_points()
```

### 2. `renderers/train_renderer.py`
Define renderizadores:
- `TrainRenderer`: Renderiza o trem com VBO otimizado
- `TrainVisualizationMode`: Modo que combina trem + nuvem de pontos

```python
from renderers.train_renderer import TrainRenderer, TrainVisualizationMode

# Cria renderizador
renderer = TrainRenderer(train_simulator)

# Integra com visualização existente
vis_mode = TrainVisualizationMode(point_cloud_renderer, train_renderer)
```

### 3. `train_viewer.py`
Integração com aplicação:
- `TrainViewer`: Aplicação com trem integrado
- Controles de teclado
- Gerenciamento de estados

### 4. Scripts de Uso

#### `examples_train.py` - Exemplos práticos
```bash
python examples_train.py
```
Executa 3 demonstrações:
1. Trem básico
2. Trem avançado com fumaça
3. Trem customizado

#### `train_simulation.py` - Simulação completa
```bash
# Sem arquivo de nuvem
python train_simulation.py

# Com arquivo de nuvem de pontos
python train_simulation.py seu_arquivo.pts
python train_simulation.py test_data/test_helix.pts
```

## 🎮 Controles

### Teclado
| Tecla | Função |
|-------|--------|
| **K** | Mostra/esconde trem |
| **L** | Mostra/esconde nuvem de pontos |
| **G** | Mostra/esconde grade 3D |
| **+/-** | Aumenta/diminui velocidade |
| **SPACE** | Pausa/retoma trem |
| **R** | Reseta posição do trem |
| **ESC** | Sair |

### Mouse
- **Botão esquerdo**: Rotaciona câmera
- **Botão direito**: Pan/zoom
- **Scroll**: Zoom

## 🔧 Customização

### Parâmetros do Trem

```python
train_config = {
    'mode': 'advanced',           # 'basic' ou 'advanced'
    'num_wagons': 6,             # Número de vagões
    'wagon_length': 20.0,        # Comprimento (eixo Z)
    'wagon_width': 8.0,          # Largura (eixo X)
    'wagon_height': 5.0,         # Altura (eixo Y)
    'points_per_wagon': 800,     # Densidade de pontos
    'gap_between_wagons': 3.0,   # Espaço entre vagões
}
```

### Cores

As cores são geradas automaticamente em gradiente:
- Vagão 0: Vermelho → Amarelo → Verde (baseado no índice)
- Fumaça: Cinza claro com transparência

Para customizar cores, modifique `_generate_wagon_colors()` em `train_simulator.py`

### Velocidade

```python
train.set_velocity(0.5)  # Velocidade lenta
train.set_velocity(1.0)  # Normal
train.set_velocity(2.0)  # Rápido
```

## 🚀 Uso Integrado

### Forma 1: Usar com seu arquivo de dados

```python
from core.application import Viewer3DApplication
from train_viewer import TrainViewer

# Cria aplicação
app = Viewer3DApplication()

# Integra trem
config = {'num_wagons': 5, 'wagon_length': 15.0}
train_viewer = TrainViewer(app, train_config=config, data_file='seu_arquivo.pts')

# Loop principal é executado automaticamente
```

### Forma 2: Adicionar trem manualmente

```python
from utils.train_simulator import TrainSimulator
from renderers.train_renderer import TrainRenderer

# No seu loop de renderização:
train_sim = TrainSimulator()
train_renderer = TrainRenderer(train_sim)

# Cada frame:
train_sim.update(dt=1.0)
train_renderer._update_vbo_data()
train_renderer.render()  # Renderiza junto com seus elementos
```

## 📊 Exemplos de Saída

### Arquivo PTS gerado
```
-4.000000 -2.500000 -120.000000 255 0 0
-4.000000 -2.500000 -119.200000 255 10 0
-4.000000 -2.500000 -118.400000 255 20 0
...
```

### Estatísticas

```
🚂 Simulador de Trem Inicializado
   Vagões: 5
   Dimensões: 8.0m x 5.0m x 15.0m
   Pontos por vagão: 1,000
   Total de pontos: ~5,000
```

## ⚡ Performance

- **Otimizado com VBO**: Renderiza milhões de pontos eficientemente
- **LOD (Level of Detail)**: Automático com muitos pontos
- **Atualização dinâmica**: Recalcula apenas quando necessário

### Benchmark (estimado)

| Vagões | Pontos/Vagão | Total | Performance |
|--------|-------------|-------|------------|
| 3 | 500 | 1,500 | 60+ FPS |
| 5 | 1,000 | 5,000 | 60+ FPS |
| 10 | 2,000 | 20,000 | 45+ FPS |
| 15 | 2,000 | 30,000 | 30+ FPS |

## 🎓 Estrutura das Classes

### TrainSimulator

```
__init__(num_wagons, wagon_length, ...)
├── get_points()              → (points, colors)
├── update(dt)                → Avança posição
├── set_velocity(v)           → Controla velocidade
├── get_position()            → Retorna Z atual
├── get_bounds()              → Bounding box
└── reset()                   → Volta ao início
```

### TrainRenderer

```
__init__(train_simulator)
├── update(dt)                → Atualiza VBO
├── render()                  → Renderiza trem
├── set_point_size(size)      → Tamanho dos pontos
├── get_stats()               → Info de renderização
└── get_bounds()              → Bounding box
```

## 🐛 Troubleshooting

### Trem não aparece
1. Verifique se `show_train=True` em `TrainVisualizationMode`
2. Ajuste tamanho com `train_renderer.set_point_size(3.0)`
3. Verifique zoom/posição da câmera

### Performance lenta
1. Reduza `points_per_wagon`
2. Reduza `num_wagons`
3. Ative LOD se disponível

### Cores estranhas
1. Verifique normalização de cores (0-1 ou 0-255)
2. Verifique `_generate_wagon_colors()` em `train_simulator.py`

## 📝 Próximas Melhorias Possíveis

- [ ] Múltiplos trilhos/pistas
- [ ] Curvas na trajetória do trem
- [ ] Física de colisão com nuvem de pontos
- [ ] Efeitos de iluminação dinâmica
- [ ] Animação de rodas/movimento linear
- [ ] Trilho 3D customizável
- [ ] Exportação de animação em vídeo

## 📄 Licença

Mesmo do projeto ProgramViewer3D

## ✨ Créditos

Integração de simulador de trem para visualização 3D
- Compatível com OpenGL/GLFW
- Otimizado para VBO
- Integrado com ProgramViewer3D
