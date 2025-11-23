# 🔄 Guia de Migração: De Menu de Trem para Sistema de Gabaritos

## O que mudou?

### ❌ Modelo Antigo (TrainSelectorMenu)
```
Menu:
  1. Escolher MODELO DE TREM (ES43, DASH BB, etc)
  2. Número de VAGÕES
  3. POSIÇÃO Y do trem

Resultado:
  ✓ Animava trem em diferentes modelos
  ✗ Gabarito era SEMPRE ferrovia padrão
  ✗ Não havia forma de mudar classificação de segurança
  ✗ Y-offset era apenas visual, sem significado
```

### ✅ Modelo Novo (Sistema de Gabaritos)
```
Fluxo:
  1. Carrega arquivo UPL
  2. Escolher GABARITO (Ferrovia/Rodovia/Aqüeduto/etc)
     ↓ Reclassifica TODOS os pontos
  3. Escolher TREM (ES43, DASH BB, etc) - OPCIONAL
     ↓ Apenas animação visual

Resultado:
  ✓ Mesmo arquivo = diferentes classificações por gabarito
  ✓ Mudança de gabarito recarrega cores em tempo real
  ✓ Significado: gabarito define o que é "invasão"
  ✓ Trem é apenas para visualização/teste
```

---

## 📋 Comparação Lado a Lado

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Foco Principal** | Modelo de trem | Tipo de gabarito |
| **Determinante de Cores** | Hardcoded (ferrovia) | Selecionável |
| **Mudança de Gabarito** | ❌ Não era possível | ✅ Recarrega arquivo |
| **Y-offset** | Menu | Painel (controle real-time) |
| **Trem** | Obrigatório para ver tudo | Opcional |
| **Use Case** | Visualizar trens diferentes | Analisar segurança do túnel |

---

## 🎯 Casos de Uso

### Antes: "Qual trem passa aqui?"
```python
# Escolhia modelo → via trem diferentes modelos passando
# Mas sempre com mesma classificação de segurança
```

### Depois: "Qual é a segurança desta seção?"
```python
# Carrega arquivo UPL
# Testa com gabaritos diferentes:
#   - Ferrovia? 2.2m de invasão
#   - Rodovia? Espaço central é seguro
#   - Aqüeduto? 3.0m de profundidade
# Identifica qual gabarito melhor encaixa
```

---

## 🔧 Migração de Código

### Se você tem código usando TrainSelectorMenu:

**Antes:**
```python
from ui.train_selector_menu import TrainSelectorMenu

menu = TrainSelectorMenu(width, height, font)
menu.on_confirm_callback = on_train_selected

def on_train_selected(model, vagons, y_offset):
    # model = 'ES43'
    # vagons = 30
    # y_offset = 5.0
    pass
```

**Depois:**
```python
from ui.gabarit_selector_menu import GabaritSelectorMenu
from ui.train_model_selector_menu import TrainModelSelectorMenu

# Dois menus separados
gabarit_menu = GabaritSelectorMenu(width, height, font)
gabarit_menu.on_gabarit_selected = on_gabarit_selected

train_menu = TrainModelSelectorMenu(width, height, font)
train_menu.on_train_selected = on_train_selected

def on_gabarit_selected(gabarit_key):
    # gabarit_key = 'ferrovia'
    # Recarrega arquivo com novo gabarito
    pass

def on_train_selected(model, vagons):
    # model = 'ES43'
    # vagons = 30
    # Y não mais como parâmetro - usa painel
    pass
```

---

## 📂 Arquivos para Deletar (Opcionalmente)

```
ui/train_selector_menu.py  ← Substituído por:
                              - ui/gabarit_selector_menu.py
                              - ui/train_model_selector_menu.py
```

Se quer manter compatibilidade, deixe os dois.

---

## 🚀 Como Usar a Nova Versão

### Instalação Rápida

1. Copie os novos arquivos:
   ```
   utils/tunnel_templates.py
   ui/gabarit_selector_menu.py
   ui/train_model_selector_menu.py
   main_gabarit.py
   ```

2. Execute:
   ```bash
   python main_gabarit.py seu_arquivo.upl
   ```

3. Pressione **G** para mudar gabarito

### Ou integre em seu código:

```python
from utils.tunnel_templates import TemplateRegistry
from loaders.data_loader import UPLLoader

# Muda gabarito em tempo de execução
novo_gabarit = TemplateRegistry.get('rodovia')
loader = UPLLoader(template=novo_gabarit)
vertices, colors = loader.load('arquivo.upl')

# Recarrega tudo com novas cores
```

---

## ⚠️ O Que Muda Para o Usuário

### Session Anterior:
```
Usuário: Pressiono 'T' para ver trem
Menu: Escolho ES43 com 30 vagões
Y offset: -5.0
Resultado: Trem passa a -5m de altura
```

### Nova Session:
```
Usuário: Pressiono 'G' para escolher gabarito
Menu: Escolho "Ferrovia"
Resultado: Todos os pontos reclassificados como SEGURO/ALERTA/INVASÃO

Usuário: Pressiono 'T' para ver trem (opcional)
Menu: Escolho ES43 com 30 vagões
Resultado: Trem anima passando - mas foco é na segurança

Usuário: Pressiono 'G' novamente, escolho "Rodovia"
Resultado: MESMOS pontos, MAS cores diferentes!
```

---

## 🔗 Relação com Painel Lateral

### Painel de Controle (TrainControlPanel)

Continua praticamente igual, com:
- ✅ Botões TREM/NUVEM
- ✅ Botões MENU/PAUSA
- ✅ Botão RESET
- ✅ Velocidade (slider)
- ✅ Posição Y (slider)
- ✅ 9 presets de velocidade

**Mudança:** Agora Y é apenas para trem, não mais "resultado" do menu.

---

## 🎓 Fluxo de Aprendizado Recomendado

1. **Compreender gabaritos**: Leia `tunnel_templates.py`
2. **Testar classificação**: Execute `python utils/tunnel_templates.py`
3. **Entender menus**: Analise `gabarit_selector_menu.py`
4. **Rodar aplicação**: `python main_gabarit.py seu_arquivo.upl`
5. **Customizar**: Crie novo gabarito

---

## ❓ Perguntas Frequentes

**P: Posso ainda usar o trem para "passar" por diferentes alturas?**
R: Sim! Use o slider de Y no painel para isso. Não é mais no menu.

**P: E se eu quiser o menu antigo?**
R: Mantenha ambos os scripts. Use `main.py` para modo antigo, `main_gabarit.py` para novo.

**P: Como ajusto as dimensões do gabarito?**
R: Em `tunnel_templates.py`, modifique `safe_zone` e `warning_zone` dos retângulos/semicírculos.

**P: Posso combinar dois gabaritos?**
R: Sim, crie `GabaritComposto` que herda de `TunnelTemplate` e checa múltiplas zonas.

**P: E se os dados em X,Y estiverem em formato diferente?**
R: Normalize antes: `loader = UPLLoader(template=gabarit); vertices, colors = loader.load(arquivo)`
A normalização já é feita internamente.

