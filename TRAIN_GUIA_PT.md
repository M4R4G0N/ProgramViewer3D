# 🚂 SIMULADOR DE TREM - GUIA EM PORTUGUÊS

## O Que Foi Criado?

Você agora tem um **simulador de trem 3D completo** que funciona dentro do seu visualizador de nuvem de pontos!

### ✨ Principais Funcionalidades

✅ **Simulação Realista**: Trem se move linearmente pelo eixo Z  
✅ **Múltiplos Vagões**: Configure quantos vagões quiser  
✅ **Cores Automáticas**: Gradiente de cores nos vagões  
✅ **Efeito de Fumaça**: Versão avançada com partículas  
✅ **Renderização Rápida**: Otimizado com VBO (OpenGL)  
✅ **Controles Interativos**: Ajuste velocidade em tempo real  
✅ **Integrado com Nuvem**: Combine com seus arquivos de dados  

---

## 🚀 Como Começar (3 Passos)

### Passo 1: Teste os Exemplos
```bash
cd c:\3D\ProgramViewer3D-main
python examples_train.py
```

Isso gera 2 arquivos:
- `train_example.pts` (trem básico)
- `train_advanced.pts` (trem com fumaça)

### Passo 2: Visualize os Arquivos
```bash
python main.py train_example.pts
python main.py train_advanced.pts
```

### Passo 3: Use com Seus Dados
```bash
# Vê trem passando por sua nuvem de pontos
python train_simulation.py seu_arquivo.pts
```

---

## 📖 Exemplos de Código

### Exemplo 1: Trem Básico (Código Mínimo)
```python
from utils.train_simulator import TrainSimulator

# Cria um trem com 5 vagões
trem = TrainSimulator(num_wagons=5)

# Obtém os pontos
pontos, cores = trem.get_points()

print(f"Total de pontos: {len(pontos):,}")
```

### Exemplo 2: Trem em Movimento
```python
from utils.train_simulator import TrainSimulator

trem = TrainSimulator(num_wagons=5)

# Simula 10 quadros
for i in range(10):
    trem.update(dt=1.0)  # Avança o trem
    pontos, cores = trem.get_points()
    print(f"Frame {i}: Posição Z = {trem.get_position():.1f}")
```

### Exemplo 3: Trem Customizado
```python
from utils.train_simulator import AdvancedTrainSimulator

# Trem avançado com locomotora e fumaça
trem = AdvancedTrainSimulator(
    num_wagons=8,              # 8 vagões + locomotora
    wagon_length=25.0,         # Vagões maiores
    wagon_width=10.0,
    wagon_height=6.0,
    has_locomotive=True,       # Com locomotora
    has_smoke_effect=True      # Com fumaça
)

pontos, cores = trem.get_points()
print(f"Pontos (com fumaça): {len(pontos):,}")
```

### Exemplo 4: Controlar Velocidade
```python
trem = TrainSimulator(num_wagons=5)

# Rápido
trem.set_velocity(2.0)
trem.update(dt=1.0)
print(f"Rápido: Z = {trem.get_position():.1f}")

# Lento
trem.set_velocity(0.5)
trem.update(dt=1.0)
print(f"Lento: Z = {trem.get_position():.1f}")

# Reseta
trem.reset()
print(f"Reset: Z = {trem.get_position():.1f}")
```

---

## 🎮 Controles Interativos

Quando rodar `train_simulation.py`, use:

```
┌────────────────────────────────────┐
│         CONTROLES DO TREM          │
├────────────────────────────────────┤
│ K         Mostra/Esconde Trem      │
│ L         Mostra/Esconde Nuvem     │
│ G         Mostra/Esconde Grade     │
│           (referência de eixos)    │
│ + (Plus)  Aumenta Velocidade       │
│ - (Minus) Diminui Velocidade       │
│ SPACE     Pausa/Retoma Trem        │
│ R         Reseta Posição           │
├────────────────────────────────────┤
│ Mouse ESQ Rotaciona Câmera         │
│ Mouse DIR Pan/Zoom                 │
│ Scroll    Zoom In/Out              │
│ ESC       Sair                     │
└────────────────────────────────────┘
```

---

## 📁 Arquivos Criados

```
Seu Projeto/
├── utils/
│   └── train_simulator.py
│       ├─ TrainSimulator (básico)
│       └─ AdvancedTrainSimulator (com fumaça)
│
├── renderers/
│   └── train_renderer.py
│       ├─ TrainRenderer (renderização)
│       └─ TrainVisualizationMode (integração)
│
├── train_viewer.py (integração automática)
├── train_simulation.py (script principal - USE ISTO!)
├── examples_train.py (exemplos)
├── quick_start_train.py (guia interativo)
│
├── TRAIN_SIMULATOR_README.md (doc completa)
├── TRAIN_QUICK_REFERENCE.md (referência rápida)
└── TRAIN_GUIA_PT.md (este arquivo)
```

---

## 🎨 Características do Trem

### Cores
- Cada vagão tem uma cor diferente (gradiente)
- Vermelho → Amarelo → Verde
- Locomotora = Cinza escura

### Formas
- Vagões: Caixas retangulares 3D
- Preenchimento: Pontos distribuídos uniformemente
- Dimensões: Totalmente personalizáveis

### Movimento
- Movimento linear ao longo do eixo Z
- Sem curvas (versão futura)
- Velocidade ajustável em tempo real

### Fumaça (Modo Avançado)
- Partículas cinzas atrás da locomotora
- Padrão pseudo-aleatório
- Apenas modo `AdvancedTrainSimulator`

---

## 🔧 Parâmetros de Customização

```python
config = {
    'mode': 'advanced',           # Tipo: 'basic' ou 'advanced'
    'num_wagons': 6,              # Quantos vagões (1-20)
    'wagon_length': 20.0,         # Comprimento (eixo Z)
    'wagon_width': 8.0,           # Largura (eixo X)
    'wagon_height': 5.0,          # Altura (eixo Y)
    'points_per_wagon': 800,      # Densidade (100-5000)
    'gap_between_wagons': 3.0,    # Espaço entre eles
}
```

### Recomendações de Performance

**Computador Antigo/Lento:**
```python
config = {
    'num_wagons': 3,
    'points_per_wagon': 300,
}  # ~900 pontos, 60+ FPS
```

**Computador Normal:**
```python
config = {
    'num_wagons': 5,
    'points_per_wagon': 800,
}  # ~4000 pontos, 60+ FPS (RECOMENDADO)
```

**Computador Potente:**
```python
config = {
    'num_wagons': 10,
    'points_per_wagon': 2000,
}  # ~20000 pontos, 30+ FPS
```

---

## 📊 Dados de Saída

### Arquivo PTS (gerado por `examples_train.py`)

Formato:
```
X Y Z R G B
-4.000000 -2.500000 -120.000000 255 0 0
-4.000000 -2.500000 -119.200000 255 10 0
-4.000000 -2.500000 -118.400000 255 20 0
...
```

- **X, Y, Z**: Coordenadas 3D em unidades de espaço
- **R, G, B**: Cores em 0-255

---

## 💡 Dicas & Truques

### Dica 1: Trem Muito Pequeno?
Aumentar tamanho dos pontos:
- No visualizador: Menu → Tamanho de Pontos → aumentar

### Dica 2: Muito Lento?
Reduzir densidade:
```python
config = {'points_per_wagon': 300, 'num_wagons': 3}
```

### Dica 3: Quer Trem Mais Longo?
```python
config = {'num_wagons': 15, 'gap_between_wagons': 1.0}
```

### Dica 4: Quer Apenas Visualizar?
```bash
python examples_train.py
python main.py train_example.pts
```

### Dica 5: Quer Programaticamente?
```python
from utils.train_simulator import TrainSimulator
trem = TrainSimulator()
# ... seu código aqui
```

---

## 🐛 Solução de Problemas

### Problema: "Módulo não encontrado"
**Solução**: Certifique-se de estar no diretório correto
```bash
cd c:\3D\ProgramViewer3D-main
python examples_train.py
```

### Problema: Trem não aparece
**Solução**: Pressione K para ativar visibilidade do trem

### Problema: Muito lento
**Solução**: Reduza `points_per_wagon` ou `num_wagons`

### Problema: Erro "OpenGL"
**Solução**: Verifique se sua placa gráfica suporta OpenGL 3.0+

---

## 📈 Próximas Ideias

Você pode estender o simulador adicionando:

- [ ] Curvas na trajetória
- [ ] Múltiplos trilhos paralelos
- [ ] Animação de rodas
- [ ] Colisão com nuvem de pontos
- [ ] Exportar para vídeo
- [ ] Sistema de física
- [ ] Vagões diferentes (combustível, carga, etc)
- [ ] Trilho 3D customizável

---

## 📚 Documentação Completa

Para documentação detalhada:
- **`TRAIN_SIMULATOR_README.md`** - Guia técnico completo
- **`TRAIN_QUICK_REFERENCE.md`** - Referência rápida visual

---

## 🎓 Estrutura de Classes

### TrainSimulator (Básico)
```
TrainSimulator
├── __init__()           - Cria o trem
├── get_points()         - Retorna pontos e cores
├── update(dt)           - Move o trem
├── set_velocity(v)      - Ajusta velocidade
├── get_position()       - Posição atual (Z)
├── reset()              - Volta ao início
└── get_bounds()         - Dimensões
```

### AdvancedTrainSimulator (Com Fumaça)
```
AdvancedTrainSimulator (estende TrainSimulator)
├── Tudo acima +
├── has_locomotive       - Inclui locomotora
├── has_smoke_effect     - Gera fumaça
└── _generate_smoke()    - Partículas
```

---

## ✅ Checklist de Uso

- [ ] Li este guia
- [ ] Rodei `python examples_train.py`
- [ ] Visualizei `train_example.pts`
- [ ] Testei `train_simulation.py`
- [ ] Usei `train_simulation.py` com meu arquivo
- [ ] Customizei os parâmetros
- [ ] Testei os controles (K, L, G, +/-, R)
- [ ] Li a documentação técnica

---

## 🎉 Parabéns!

Você agora tem um simulador de trem 3D fully funcional!

**Próximo passo**: 
```bash
python train_simulation.py seu_arquivo_de_dados.pts
```

Divirta-se! 🚂✨

---

**Dúvidas?** Consulte:
- `TRAIN_SIMULATOR_README.md`
- `examples_train.py`
- `quick_start_train.py`
