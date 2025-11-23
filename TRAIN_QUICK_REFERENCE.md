# 🚂 SIMULADOR DE TREM - RESUMO VISUAL

## 📁 Arquivos Criados

```
ProgramViewer3D-main/
├── utils/
│   └── train_simulator.py          ← Core do simulador
├── renderers/
│   └── train_renderer.py           ← Renderização OpenGL
├── train_viewer.py                 ← Integração com app
├── train_simulation.py             ← Script principal (pronto para rodar)
├── examples_train.py               ← Exemplos práticos
├── quick_start_train.py            ← Guia rápido
└── TRAIN_SIMULATOR_README.md       ← Documentação completa
```

## 🚀 Como Usar (3 Opções)

### ✨ Opção 1: Forma Mais Fácil (Recomendado)
```bash
# Gera visualização apenas do trem
python examples_train.py

# Gera trem + nuvem de pontos
python train_simulation.py
python train_simulation.py arquivo.pts
```

### 🎓 Opção 2: Aprender Rápido
```bash
# Mostra 8 exemplos de uso
python quick_start_train.py
```

### 🔧 Opção 3: Integração Manual
```python
from utils.train_simulator import TrainSimulator
from renderers.train_renderer import TrainRenderer

trem = TrainSimulator(num_wagons=5)
renderer = TrainRenderer(trem)

# No seu loop:
trem.update(dt=1.0)
renderer.render()
```

## 🎯 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────┐
│         Viewer3DApplication (App Principal)         │
└────────────────┬──────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
    ┌───┴────┐       ┌────┴──────┐
    │ Point  │       │ TrainViewer│  ← Integra tudo
    │ Cloud  │       │            │
    └───────┘       └────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───┴──────┐   ┌────┴──────┐   ┌────┴──────┐
    │ Train    │   │ Train      │   │Train Viz  │
    │Simulator │   │Renderer    │   │Mode       │
    └──────────┘   └───────────┘   └───────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                 ┌───────┴────────┐
                 │  OpenGL (VBO)  │
                 └────────────────┘
```

## 📊 Fluxo de Dados

```
TrainSimulator
    ↓
update(dt) ← Avança posição Z
    ↓
get_points() ← Gera pontos 3D
    ├─ 3 arrays NumPy
    └─ (pontos, cores)
    ↓
TrainRenderer
    ├─ _update_vbo_data()
    ├─ Converte para GPU
    └─ render() ← Desenha na tela
```

## ⌨️ Controles Rápidos

| Tecla | O quê |
|-------|-------|
| **K** | Trem on/off |
| **L** | Nuvem on/off |
| **G** | Grade on/off |
| **+/-** | Velocidade |
| **SPACE** | Pausa |
| **R** | Reset |

## 🎨 Visualização

```
Vista de cima (Eixo Z apontando para longe):

     +Y (altura)
     ↑
     │    ┌─────────────┐
     │    │             │  Vagão 1 (vermelho)
     │    └─────────────┘
     │    ┌─────────────┐
     │    │             │  Vagão 2 (laranja)
     │    └─────────────┘
     │    ┌─────────────┐
     │    │             │  Vagão 3 (amarelo)
     │    └─────────────┘
     │
     └──────────────────→ +X (largura)

Movimento: Trem avança no eixo +Z (para longe da câmera)
```

## 🎲 Exemplo de Saída

```
🚂 SIMULADOR DE TREM 3D
============================================================

🎬 Iniciando simulação...

Frame 0: Z = -120.00 | Pontos: 3,000 | Cores: (3000, 3)
Frame 1: Z = -119.50 | Pontos: 3,000 | Cores: (3000, 3)
Frame 2: Z = -119.00 | Pontos: 3,000 | Cores: (3000, 3)
Frame 3: Z = -118.50 | Pontos: 3,000 | Cores: (3000, 3)

Pressione K para ocultar/mostrar trem...
Pressione + ou - para ajustar velocidade...

Z = -50.25 | Vel = 1.5 | Pontos renderizados: 3,000
```

## 💻 Requisitos

```
- Python 3.7+
- NumPy (para cálculos)
- PyOpenGL (para renderização)
- GLFW (para janela OpenGL)
```

Já estão em `requirements.txt` do projeto!

## 📈 Performance

```
Configuração          │ Pontos/Vagão │ Vagões │ FPS
──────────────────────┼──────────────┼────────┼────────
Leve                  │ 300          │ 3      │ 60+
Normal (recomendado)  │ 800          │ 5      │ 60+
Pesado                │ 2000         │ 8      │ 30+
Ultra                 │ 5000         │ 10     │ 15+
```

## 🔧 Parâmetros Personalizáveis

```python
config = {
    'mode': 'advanced',           # advanced | basic
    'num_wagons': 6,              # 1-20
    'wagon_length': 20.0,         # 5.0-50.0
    'wagon_width': 8.0,           # 3.0-15.0
    'wagon_height': 5.0,          # 2.0-10.0
    'points_per_wagon': 800,      # 100-5000
    'gap_between_wagons': 3.0,    # 0.5-10.0
}
```

## 🎓 Estrutura de Dados

### Pontos (vertices)
- Shape: (N, 3)
- Range: X ∈ [-width/2, +width/2], Y ∈ [-height/2, +height/2], Z ∈ [z_start, z_start+length]
- Tipo: float32

### Cores (RGB)
- Shape: (N, 3)
- Range: [0.0, 1.0] ou [0, 255]
- Tipo: float32 ou uint8

## 📚 Documentação Completa

Para mais detalhes:
- `TRAIN_SIMULATOR_README.md` - Documentação completa
- `examples_train.py` - Exemplos de código
- `quick_start_train.py` - Guia interativo

## ✅ Checklist de Funcionalidades

- [x] TrainSimulator básico
- [x] AdvancedTrainSimulator com fumaça
- [x] TrainRenderer com VBO
- [x] Controles de velocidade
- [x] Integração com visualizador
- [x] Exemplos de código
- [x] Documentação completa
- [ ] Curvas na trajetória (futura)
- [ ] Múltiplos trilhos (futuro)
- [ ] Exportar para vídeo (futuro)

## 🎉 Pronto para Usar!

Teste agora:
```bash
python examples_train.py
# ou
python train_simulation.py
```

Divirta-se! 🚂✨
