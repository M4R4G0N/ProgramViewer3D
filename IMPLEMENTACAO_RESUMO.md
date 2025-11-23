# 🚀 Nova Arquitetura: Sistema de Gabaritos de Túnel v2.0

## 📌 Resumo Executivo

Você identifi cou um problema importante na arquitetura anterior:
- **Antes**: Usuário escolhia modelo de trem, mas gabarito era fixo (ferrovia)
- **Depois**: Usuário escolhe tipo de gabarito (que muda classificação), trem é opcional

Isto é fundamentalmente mais inteligente para análise de dados de túnel.

---

## 🎯 O Que Mudou

### Conceitual

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOVO FLUXO DE DADOS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Arquivo UPL → Carregar Pontos (X, Y, Z) ─┐                   │
│                                           │                   │
│                                           ▼                   │
│                                  ┌─────────────────┐           │
│                              ┌──▶│  Gabarito 1     │◀──┐       │
│                              │   │  (Ferrovia)     │   │       │
│  Selecionar    ───────────┐  │   └─────────────────┘   │       │
│  Gabarito                 │  │                         │       │
│                           ▼  │   ┌─────────────────┐   │       │
│                      ╔════════╬──▶│  Gabarito 2     │───┼──▶   │
│                      ║        │   │  (Rodovia)      │   │      │
│                      ║        │   └─────────────────┘   │      │
│                      ║        │                         │      │
│                      ║        │   ┌─────────────────┐   │      │
│                      ║        └──▶│  Gabarito 3     │◀──┘      │
│                      ║            │  (Aqüeduto)     │          │
│                      ║            └─────────────────┘          │
│                      ║                     │                   │
│    Classifi car         │                   │                   │
│    Pontos            │  ▼                   │                   │
│                      ║  ┌──────────────────────────┐          │
│                      ║  │ Pontos com Cores:        │          │
│                      ║  │ 🟢 SEGURO (verde)        │          │
│                      ║  │ 🟡 ALERTA (amarelo)      │          │
│                      ║  │ 🔴 INVASÃO (vermelho)    │          │
│                      ║  └──────────────────────────┘          │
│                      ║         │                               │
│                      ║         ▼                               │
│   Selecionar   ──────╚────▶ Animar com Trem (opcional)        │
│   Trem?                      🚂 ← ES43, DASH BB, etc           │
│                                                                 │
│                            ▼                                   │
│                      📊 Visualização Final                    │
│                      - Nuvem de pontos colorida               │
│                      - Trem passando                           │
│                      - Controles em painel                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Arquivos

### Criados
```
utils/
  ├─ tunnel_templates.py          (NEW) Sistema de gabaritos
  └─ [ore_train_models.py]        (EXIST) Modelos de trem

ui/
  ├─ gabarit_selector_menu.py     (NEW) Menu de gabarito
  ├─ train_model_selector_menu.py (NEW) Menu de trem
  ├─ train_control_panel.py       (EXIST) Painel de controle
  └─ [train_selector_menu.py]     (OLD) Deprecado

loaders/
  └─ data_loader.py               (MOD) UPLLoader agora suporta template

main_gabarit.py                   (NEW) Aplicação versão 2.0

Documentação:
  ├─ GABARIT_SYSTEM_README.md     (NEW) Guia completo
  ├─ MIGRATION_GUIDE.md           (NEW) Migração de código
  ├─ exemplo_gabaritos.py         (NEW) Exemplos de uso
  └─ [main.py]                    (EXIST) Versão antiga
```

---

## 🔧 Componentes Principais

### 1. `tunnel_templates.py` (300 linhas)

Define hierarquia de gabaritos:

```
TunnelTemplate (abstrata)
├─ FerroviaTunel
│  └─ Seção simples: retângulo + semicírculo
├─ RodoviaDupla
│  └─ Duas pistas independentes
├─ TuneloAqued
│  └─ Trapézio + arco (mais espaço)
├─ GabaritPersonalizado
│  └─ Retângulos customizados
└─ TemplateRegistry
   └─ Registro central de gabaritos
```

**Funcionalidades:**
- `classify_point(x, y)` → Retorna 0/1/2 (SEGURO/ALERTA/INVASÃO)
- `_point_in_zone(x, y, zone)` → Verifica posição em zona
- `get_description()` → Retorna nome + detalhes

**Uso:**
```python
gabarit = TemplateRegistry.get('ferrovia')
classification = gabarit.classify_point(0.0, 3.0)  # 2 (INVASÃO)

# Ou para todos os pontos
classifications = classify_points_with_template(xs, ys, gabarit)
```

### 2. `gabarit_selector_menu.py` (200 linhas)

Menu modal para escolher gabarito.

**Interface:**
- Exibe lista de gabaritos
- Navegação: ↑/↓ ou mouse
- Confirmação: ENTER
- Callback: `on_gabarit_selected(key)`

**Usado em:**
```python
menu = GabaritSelectorMenu(width, height, font)
menu.on_gabarit_selected = lambda key: reload_with_gabarit(key)
menu.render()  # Desenha na tela
```

### 3. `train_model_selector_menu.py` (300 linhas)

Menu simplificado para trem (sem Y-offset).

**Fluxo:**
1. Stage 0: Escolher modelo (LE, DASH BB, SD 40, etc)
2. Stage 1: Número de vagões (1-200)

**Callback:**
```python
def on_train_selected(model, vagons):
    # model = 'ES43'
    # vagons = 30
    trem = OreTrainSimulator(model, vagons)
```

### 4. `data_loader.py` (Modificado)

UPLLoader agora aceita gabarito:

```python
# Padrão (ferrovia)
loader = UPLLoader()
vertices, colors = loader.load('arquivo.upl')

# Customizado
gabarit = TemplateRegistry.get('rodovia')
loader = UPLLoader(template=gabarit)
vertices, colors = loader.load('arquivo.upl')
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Teste Básico
```python
from utils.tunnel_templates import TemplateRegistry

# Carregar
ferrovia = TemplateRegistry.get('ferrovia')

# Classificar um ponto
cls = ferrovia.classify_point(0.0, 3.0)
print(cls)  # 2 (INVASÃO para ferrovia)

# Mudar para rodovia
rodovia = TemplateRegistry.get('rodovia')
cls = rodovia.classify_point(0.0, 3.0)
print(cls)  # 0 (SEGURO para rodovia - é espaço central)
```

### Exemplo 2: Carregar com Gabarito
```python
from loaders.data_loader import UPLLoader
from utils.tunnel_templates import TemplateRegistry

# Loop: testa arquivo com todos os gabaritos
arquivo = 'tunel.upl'

for gabarit_key in TemplateRegistry.list_all():
    gabarit = TemplateRegistry.get(gabarit_key)
    loader = UPLLoader(template=gabarit)
    vertices, colors = loader.load(arquivo)
    
    # Conta invasões
    n_red = np.sum(colors[:, 0] > 0.5)
    print(f"{gabarit.name}: {n_red} pontos em invasão")
```

### Exemplo 3: Criar Gabarito Personalizado
```python
from utils.tunnel_templates import GabaritPersonalizado, TemplateRegistry

meu_tunel = GabaritPersonalizado(
    name="Túnel Mineiro 3m",
    safe_bounds={'x_min': -1.5, 'x_max': 1.5, 'y_min': 0, 'y_max': 3},
    warning_bounds={'x_min': -2.0, 'x_max': 2.0, 'y_min': -0.5, 'y_max': 3.5}
)

# Registra para uso posterior
TemplateRegistry.register('mineiro_3m', meu_tunel)

# Pronto! Agora pode usar:
gabarit = TemplateRegistry.get('mineiro_3m')
```

---

## 🎮 Interface do Usuário

### Fluxo Típico

```
1. Inicia aplicação
   $ python main_gabarit.py arquivo.upl
   
2. Vê nuvem de pontos (cores padrão = ferrovia)

3. Pressiona 'G' para menu de gabarito
   [Menu Modal]
   - Escolhe "Rodovia Dupla"
   - Pressiona ENTER
   
4. Arquivo recarregado com novas cores!
   → Mesmos pontos, classificações diferentes

5. Pressiona 'T' para animação de trem (opcional)
   [Menu de Trem]
   - Escolhe "ES43"
   - Define "30" vagões
   - Pressiona ENTER
   
6. Trem aparece animado na cena

7. Painel de controle:
   - Ajusta velocidade com slider
   - Controla posição Y
   - Play/Pause/Reset
```

### Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| **G** | Abrir menu de gabarito |
| **T** | Abrir menu de trem |
| **K** | Toggle: mostrar/esconder trem |
| **L** | Toggle: mostrar/esconder nuvem |
| **SPACE** | Pausa/Resume animação |
| **R** | Reset trem (posição inicial) |
| **ESC** | Fechar menu ativo |

---

## 📊 Lógica de Classificação

### Ferrovia
```
Safe Zone (INVASÃO se dentro):
  - X: [-2.2, 2.2]m
  - Y retangular: [2.5, 5.8]m
  - Y semicírculo: [5.8, 8.0]m, raio 2.2m

Warning Zone (ALERTA):
  - X: [-2.7, 2.7]m
  - Margens ao redor do safe zone
  - Raio 2.7m no semicírculo

Resto: SEGURO (verde)
```

### Rodovia
```
Pista 1 (INVASÃO):
  - X: [-4.5, -2.0]
  - Y: [0.0, 4.0]

Pista 2 (INVASÃO):
  - X: [2.0, 4.5]
  - Y: [0.0, 4.0]

Centro (SEGURO):
  - X: [-2.0, 2.0]
  - Espaço entre pistas

Resto: Fora (verde)
```

---

## 🚀 Vantagens da Nova Arquitetura

1. **Modularidade**
   - Gabarito = totalmente separado de trem
   - Pode usar gabarit sem trem, trem sem gabarit

2. **Extensibilidade**
   - Adicionar gabarito = ~30 linhas de código
   - Sem modificar data loader

3. **Reutilizabilidade**
   - Mesmo arquivo UPL → N gabaritos diferentes
   - Sem recarregar arquivo completo

4. **Análise Comparativa**
   - Comparar invasões entre gabaritos
   - Estatísticas claras (% seguro/alerta/invasão)

5. **UX Melhorada**
   - Usuário entende: "tipo de túnel" vs "modelo de trem"
   - Menu claro e separado

---

## 🔍 Validação

### Testes Realizados

```
✅ Sistema de gabaritos (tunnel_templates.py)
   - Testa 7 pontos com 3 gabaritos
   - Resultados corretos

✅ Importações
   - Todos os módulos novos importam corretamente
   - Sem dependências circulares

✅ Classificação de pontos
   - Ponto (0, 3): Ferrovia→INVASÃO, Rodovia→SEGURO, Aqueduto→INVASÃO
   - Comportamento esperado

✅ Carregamento UPL com template
   - Arquivo carregado com ferrovia (padrão)
   - Puntos reclassificados corretamente
```

---

## 📚 Documentação

### Arquivos de Referência

1. **`GABARIT_SYSTEM_README.md`**
   - Visão geral do sistema
   - Arquitetura completa
   - API de gabaritos
   - FAQ

2. **`MIGRATION_GUIDE.md`**
   - Antes vs. Depois
   - Como migrar código antigo
   - Exemplos comparativos

3. **`exemplo_gabaritos.py`**
   - 4 exemplos práticos
   - Testa com arquivo real

---

## 🎓 Próximas Melhorias (Opcional)

1. **Visualizar limites do gabarito**
   - Renderizar retângulos/semicírculos como wireframe
   - Ajuda a entender a zona de invasão

2. **Mais gabaritos pré-definidos**
   - Metrô, Aqüeduto, Minério, etc.
   - Base de dados de dimensões reais

3. **Export de análise**
   - Salvar estatísticas em JSON/CSV
   - Relatório visual

4. **Edição interativa de gabaritos**
   - Ajustar limites com mouse
   - Preview em tempo real

5. **Detecção automática**
   - Analisar arquivo UPL
   - Sugerir melhor gabarito

---

## ✅ Checklist de Implementação

- [x] Criar `tunnel_templates.py` com 3 gabaritos + personalizado
- [x] Criar `gabarit_selector_menu.py` (menu modal)
- [x] Criar `train_model_selector_menu.py` (menu simplificado)
- [x] Modificar `data_loader.py` para suportar template
- [x] Criar `main_gabarit.py` (aplicação v2)
- [x] Documentação: `GABARIT_SYSTEM_README.md`
- [x] Documentação: `MIGRATION_GUIDE.md`
- [x] Exemplos: `exemplo_gabaritos.py`
- [x] Testes básicos
- [x] Validação de imports

---

## 🎯 Conclusão

Nova arquitetura é **muito mais flexível** para análise de dados de túnel:

- **Foco correto**: Gabarito = segurança do túnel
- **Trem = bônus**: Apenas para visualização/teste
- **Extensível**: Fácil adicionar novos gabaritos
- **Reutilizável**: Mesmo arquivo, N perspectivas

Pronto para uso! 🚀

