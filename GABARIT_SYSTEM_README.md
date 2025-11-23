# 🎯 Sistema de Gabaritos de Túnel v2.0

## Visão Geral

Você reorganizou o sistema de forma muito mais inteligente:

### Antes:
- Usuário escolhia **modelo de trem**
- Todos os trens usavam o **mesmo gabarito padrão** (ferrovia)
- Parâmetro: modelo_trem → determina velocidade/aparência apenas

### Depois (Novo):
- Usuário escolhe **tipo de túnel (gabarito)**
- Gabarito determina **quais pontos são SEGURO/ALERTA/INVASÃO**
- Depois escolhe **modelo de trem** (opcional)
- Cada gabarito muda a **classificação de TODOS os pontos** do arquivo UPL

---

## 🗂️ Arquitetura

### 1️⃣ **Sistema de Gabaritos** (`utils/tunnel_templates.py`)

Define 3 gabaritos + suporte a personalizados:

#### **FerroviaTunel** - Seção férrea simples
```
Dimensões:
- Seguro (INVASÃO se dentro): Retângulo 2.2m × semicírculo 2.2m
- Alerta (AMARELO): Margem 0.5m ao redor
- Fora: SEGURO (verde)
```

#### **RodoviaDupla** - Duas pistas independentes
```
Dimensões:
- Pista 1: X [-4.5, -2.0], Y [0, 4.0]
- Pista 2: X [2.0, 4.5], Y [0, 4.0]
- Espaço central: SEGURO (verde)
```

#### **TuneloAqued** - Seção complexa com canaleta
```
Dimensões:
- Trapézio inferior + arco superior
- Mais espaço que ferrovia
```

#### **GabaritPersonalizado** - Para casos específicos
```python
gabarit = GabaritPersonalizado(
    name="Meu Túnel",
    safe_bounds={'x_min': -2.0, 'x_max': 2.0, 'y_min': 1.0, 'y_max': 4.0},
    warning_bounds={'x_min': -2.5, 'x_max': 2.5, 'y_min': 0.5, 'y_max': 4.5}
)
```

### 2️⃣ **Menu de Gabarit** (`ui/gabarit_selector_menu.py`)

Menu modal para escolher gabarito:
- **Navegação**: ↑/↓ ou clique
- **Confirmação**: ENTER
- **Cancelar**: ESC
- Mostra nome + descrição de cada gabarito

### 3️⃣ **Menu de Trem** (`ui/train_model_selector_menu.py`)

Menu simplificado para escolher trem:
- **Stage 1**: Escolher modelo de trem (11 opções)
- **Stage 2**: Número de vagões (1-200)
- **Sem Y-offset**: Focus é apenas no trem agora

### 4️⃣ **Data Loader Melhorado** (`loaders/data_loader.py`)

UPLLoader agora aceita gabarito:
```python
# Usa gabarito padrão (ferrovia)
loader = UPLLoader()
vertices, colors = loader.load('arquivo.upl')

# Usa gabarito específico
gabarit = TemplateRegistry.get('rodovia')
loader = UPLLoader(template=gabarit)
vertices, colors = loader.load('arquivo.upl')
```

---

## 🎮 Fluxo de Uso

### Passo 1: Iniciar
```bash
python main_gabarit.py arquivo.upl
# ou sem arquivo:
python main_gabarit.py
```

### Passo 2: Selecionar Gabarito
- Pressione **G**
- Escolha com **↑/↓** ou clique
- Pressione **ENTER**
- ✅ Arquivo UPL é **RECARREGADO** com novas cores

### Passo 3: Animar Trem (opcional)
- Pressione **T**
- Escolha modelo e vagões
- Pressione **ENTER**
- Trem aparece animado na cena

### Passo 4: Controlar
- **K**: Mostrar/esconder trem
- **L**: Mostrar/esconder nuvem
- **SPACE**: Pausa/resume
- **Painel**: Velocidade, posição Y, botões

---

## 📊 Classificação de Pontos

### Cores Resultantes:

| Cor | Significado | Classificação |
|-----|-----------|----------------|
| 🟢 Verde | Seguro - fora do gabarito | OK |
| 🟡 Amarelo | Alerta - na margem | Aviso |
| 🔴 Vermelho | Invasão - dentro do túnel | ❌ Perigoso |

### Exemplo - Ferrovia vs Rodovia:

**Mesmo arquivo UPL, pontos diferentes classificados:**

```
Ponto (0, 3):
  - Ferrovia: INVASÃO (vermelho)
  - Rodovia: SEGURO (verde) - está no espaço central

Ponto (3, 3):
  - Ferrovia: SEGURO (verde)
  - Rodovia: INVASÃO (vermelho) - está na pista direita
```

---

## 🔧 Registrar Novo Gabarito

### Opção 1: Adicionar à classe
```python
# Em utils/tunnel_templates.py
class MeuTunel(TunnelTemplate):
    @property
    def name(self):
        return "Meu Túnel Personalizado"
    
    @property
    def safe_zone(self):
        return {...}  # Define zona segura
    
    @property
    def warning_zone(self):
        return {...}  # Define zona alerta
    
    @staticmethod
    def _point_in_zone(x, y, zone):
        # Lógica de classificação
        return False

# Registrar
TemplateRegistry.register('meu_tunel', MeuTunel())
```

### Opção 2: Usar personalizado
```python
from utils.tunnel_templates import GabaritPersonalizado, TemplateRegistry

gabarit = GabaritPersonalizado(
    name="Túnel Reto 3m",
    safe_bounds={'x_min': -1.5, 'x_max': 1.5, 'y_min': 0, 'y_max': 3},
    warning_bounds={'x_min': -2.0, 'x_max': 2.0, 'y_min': -0.5, 'y_max': 3.5}
)

TemplateRegistry.register('reto_3m', gabarit)
```

---

## 📁 Arquivos Criados

### Novos:
```
utils/
  └─ tunnel_templates.py          # Sistema de gabaritos
ui/
  ├─ gabarit_selector_menu.py     # Menu de gabarito
  └─ train_model_selector_menu.py # Menu de trem simplificado
main_gabarit.py                   # Aplicação principal (versão 2)
```

### Modificados:
```
loaders/data_loader.py  # Suporta template em UPLLoader
```

---

## 🚀 Vantagens da Nova Arquitetura

1. **Separação de conceitos**
   - Gabarito = define segurança
   - Trem = apenas animação visual

2. **Reutilizabilidade**
   - Mesmo arquivo UPL com gabaritos diferentes = resultados diferentes
   - Sem recarregar arquivo

3. **Extensibilidade**
   - Adicionar novo gabarito = ~20 linhas de código
   - Suporta templates customizados

4. **Melhor UX**
   - Usuário entende: "escolho o tipo de túnel, depois a animação do trem"
   - Não confunde com "modelo de trem"

5. **Análise de dados**
   - Comparar invasões com gabaritos diferentes
   - Identificar pontos críticos por tipo

---

## 💻 Exemplo de Código Programático

```python
from utils.tunnel_templates import TemplateRegistry
from loaders.data_loader import UPLLoader
import numpy as np

# Carrega mesmo arquivo com 3 gabaritos diferentes
arquivo = 'dados_tunel.upl'

for gabarit_key in ['ferrovia', 'rodovia', 'aqueduto']:
    gabarit = TemplateRegistry.get(gabarit_key)
    loader = UPLLoader(template=gabarit)
    vertices, colors = loader.load(arquivo)
    
    # Conta pontos por classificação
    n_seguro = np.sum(colors[:, 1] == 1.0)  # Verde
    n_alerta = np.sum((colors[:, 0] == 1.0) & (colors[:, 1] == 1.0))  # Amarelo
    n_invasao = np.sum((colors[:, 0] == 1.0) & (colors[:, 1] == 0.0))  # Vermelho
    
    print(f"{gabarit.name}:")
    print(f"  Seguro: {n_seguro}, Alerta: {n_alerta}, Invasão: {n_invasao}")
```

---

## 🎓 Próximos Passos

1. **Teste dos gabaritos** - Verificar se as zonas estão corretas
2. **Adicionar mais gabaritos** - Túnel mineiro, metrô, etc.
3. **Visualizar zonas** - Renderizar limites do gabarito como wireframe
4. **Estatísticas** - Mostrar % invasão/alerta por gabarito
5. **Export** - Salvar análise em JSON/CSV

---

## ❓ FAQ

**P: E se eu quiser adicionar Y-offset de novo?**
R: Pode voltar ao `train_selector_menu.py` anterior, mas agora seria um "Stage 2" após vagões, sem afetar gabarito.

**P: Como adiciono mais gabaritos padrão?**
R: Em `utils/tunnel_templates.py`, crie nova classe + adicione em `TemplateRegistry._templates`

**P: Posso usar este sistema sem trem?**
R: Sim! Use apenas o gabarito para classificar pontos - trem é opcional.

**P: E se os dados X,Y do arquivo forem em unidades diferentes?**
R: Modifique `safe_zone` e `warning_zone` com as unidades corretas (metros, cm, mm, etc)

