# Guia: Como Implementar uma Janela no ProgramViewer3D

Este guia explica passo a passo como criar uma nova janela (window) no projeto, usando como exemplo a `PointsTableWindow` e `TrainControlPanel`.

## 📋 Visão Geral

O projeto usa **GLFW** para criar janelas independentes ou **OpenGL overlays** para painéis dentro da janela principal. Este guia cobre ambas abordagens.

---

## 🪟 Opção 1: Janela Independente (GLFW Window)

Use quando precisar de uma janela separada que pode ser movida, redimensionada e fechada independentemente.

### Passo 1: Criar o arquivo da janela

Crie um novo arquivo em `ui/` (exemplo: `ui/minha_janela.py`):

```python
"""
Minha Janela - Descrição da funcionalidade
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from ui.vector_font import VectorFont


class MinhaJanela:
    """
    Janela independente para [descrever funcionalidade]
    """
    
    def __init__(self, width=800, height=600, title="Minha Janela"):
        """
        Inicializa a janela
        
        Args:
            width: Largura da janela
            height: Altura da janela
            title: Título da janela
        """
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.font = VectorFont()
        
        # Seus dados aqui
        self.dados = []
        
    def _init_window(self):
        """Cria a janela GLFW"""
        # Já existe um contexto GLFW ativo (da janela principal)
        # Apenas criamos uma nova janela
        self.window = glfw.create_window(
            self.width, self.height, self.title, None, None
        )
        
        if not self.window:
            raise RuntimeError(f"Falha ao criar janela: {self.title}")
        
        # Callbacks
        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_window_size_callback(self.window, self._resize_callback)
        
        # Ativa contexto desta janela
        glfw.make_context_current(self.window)
        
        # Configuração OpenGL
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        # Configura viewport
        self._resize_viewport(self.width, self.height)
    
    def _resize_viewport(self, width, height):
        """Redimensiona viewport"""
        if height == 0:
            height = 1
        
        self.width = width
        self.height = height
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Projeção ortográfica 2D (para UI)
        glOrtho(0, width, 0, height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def _key_callback(self, window, key, scancode, action, mods):
        """Processa teclas"""
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            # Adicione mais teclas aqui
    
    def _mouse_button_callback(self, window, button, action, mods):
        """Processa cliques do mouse"""
        if action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            # Inverte Y (GLFW usa origem no topo)
            y = self.height - y
            
            if button == glfw.MOUSE_BUTTON_LEFT:
                self._on_click(x, y)
    
    def _cursor_pos_callback(self, window, x, y):
        """Processa movimento do mouse"""
        # Inverte Y
        y = self.height - y
        # Adicione lógica de hover aqui
    
    def _scroll_callback(self, window, xoffset, yoffset):
        """Processa scroll do mouse"""
        # Adicione lógica de scroll aqui
        pass
    
    def _resize_callback(self, window, width, height):
        """Callback de redimensionamento"""
        self._resize_viewport(width, height)
    
    def _on_click(self, x, y):
        """Processa clique na posição (x, y)"""
        print(f"Clique em ({x}, {y})")
        # Adicione sua lógica aqui
    
    def _render(self):
        """Renderiza o conteúdo da janela"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Desenhe seu conteúdo aqui
        self._render_texto("Minha Janela", 10, self.height - 30, 1.0)
        
        # Exemplo: desenhar retângulo
        self._render_retangulo(10, 10, 200, 100, (0.3, 0.5, 0.7))
    
    def _render_texto(self, texto, x, y, tamanho=0.8):
        """Renderiza texto usando VectorFont"""
        glColor3f(1.0, 1.0, 1.0)
        self.font.render_text(texto, x, y, tamanho)
    
    def _render_retangulo(self, x, y, width, height, color):
        """Renderiza um retângulo preenchido"""
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
    
    def run(self):
        """Loop principal da janela"""
        self._init_window()
        
        print(f"🪟 {self.title} aberta")
        
        # Loop de renderização
        while not glfw.window_should_close(self.window):
            self._render()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        # Limpeza
        glfw.destroy_window(self.window)
        print(f"🪟 {self.title} fechada")
```

### Passo 2: Integrar na aplicação principal

Em `core/application.py`, adicione:

```python
# No topo do arquivo, adicione o import
from ui.minha_janela import MinhaJanela

# Adicione um método para abrir a janela
def _abrir_minha_janela(self):
    """Abre a janela personalizada"""
    janela = MinhaJanela(width=800, height=600)
    janela.run()

# No método _process_menu_action, adicione a ação
elif action == 'minha_janela':
    self._abrir_minha_janela()
```

### Passo 3: Adicionar ao menu

Em `ui/menu_bar.py`, no `__init__`, adicione um item de menu:

```python
{
    'label': 'Ferramentas',
    'items': [
        # ... outros itens ...
        {'label': 'Minha Janela', 'action': 'minha_janela'},
    ]
}
```

### Passo 4: Adicionar atalho de teclado (opcional)

Em `core/application.py`, no método `_key_callback`:

```python
elif key == glfw.KEY_M and action == glfw.PRESS:
    self._abrir_minha_janela()
```

---

## 🎨 Opção 2: Painel Overlay (dentro da janela principal)

Use quando quiser um painel que aparece sobre a visualização 3D, sem criar uma janela separada.

### Passo 1: Criar o arquivo do painel

Crie `ui/meu_painel.py`:

```python
"""
Meu Painel - Painel overlay na janela principal
"""

from OpenGL.GL import *


class MeuPainel:
    """
    Painel overlay desenhado sobre a janela principal
    """
    
    def __init__(self, window_width, window_height, font):
        """
        Inicializa o painel
        
        Args:
            window_width: Largura da janela principal
            window_height: Altura da janela principal
            font: Instância do VectorFont
        """
        self.window_width = window_width
        self.window_height = window_height
        self.font = font
        
        # Posição e tamanho do painel
        self.panel_width = 300
        self.panel_height = 400
        self.panel_x = window_width - self.panel_width - 10  # Direita
        self.panel_y = 10  # Baixo
        
        # Estado
        self.visible = False
        self.hover_item = None
        
        # Seus dados
        self.items = []
    
    def resize(self, window_width, window_height):
        """Atualiza posição quando janela é redimensionada"""
        self.window_width = window_width
        self.window_height = window_height
        self.panel_x = window_width - self.panel_width - 10
    
    def is_over(self, x, y):
        """Verifica se o mouse está sobre o painel"""
        if not self.visible:
            return False
        
        return (self.panel_x <= x <= self.panel_x + self.panel_width and
                self.panel_y <= y <= self.panel_y + self.panel_height)
    
    def on_click(self, x, y):
        """Processa clique no painel"""
        if not self.is_over(x, y):
            return False
        
        # Coordenadas relativas ao painel
        rel_x = x - self.panel_x
        rel_y = y - self.panel_y
        
        print(f"Clique no painel: ({rel_x}, {rel_y})")
        # Adicione sua lógica aqui
        
        return True  # Consumiu o clique
    
    def on_hover(self, x, y):
        """Atualiza estado de hover"""
        if not self.visible:
            self.hover_item = None
            return
        
        if self.is_over(x, y):
            rel_x = x - self.panel_x
            rel_y = y - self.panel_y
            # Detecte sobre qual item está o mouse
            # self.hover_item = ...
    
    def render(self):
        """Renderiza o painel"""
        if not self.visible:
            return
        
        # Salva estado OpenGL
        glPushMatrix()
        glLoadIdentity()
        
        # Fundo do painel
        glColor4f(0.2, 0.2, 0.25, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y + self.panel_height)
        glVertex2f(self.panel_x, self.panel_y + self.panel_height)
        glEnd()
        
        # Borda
        glColor3f(0.5, 0.5, 0.6)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.panel_x, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y)
        glVertex2f(self.panel_x + self.panel_width, self.panel_y + self.panel_height)
        glVertex2f(self.panel_x, self.panel_y + self.panel_height)
        glEnd()
        
        # Título
        glColor3f(1.0, 1.0, 1.0)
        self.font.render_text(
            "Meu Painel",
            self.panel_x + 10,
            self.panel_y + self.panel_height - 25,
            0.9
        )
        
        # Conteúdo do painel
        self._render_conteudo()
        
        # Restaura estado
        glPopMatrix()
    
    def _render_conteudo(self):
        """Renderiza o conteúdo específico do painel"""
        y = self.panel_y + self.panel_height - 60
        
        # Exemplo: lista de itens
        for i, item in enumerate(self.items):
            cor = (0.8, 0.9, 1.0) if i == self.hover_item else (0.7, 0.7, 0.7)
            glColor3f(*cor)
            self.font.render_text(
                f"{i+1}. {item}",
                self.panel_x + 20,
                y,
                0.7
            )
            y -= 25
```

### Passo 2: Integrar na aplicação

Em `core/application.py`:

```python
# Import
from ui.meu_painel import MeuPainel

# No __init__, após criar outros componentes:
self.meu_painel = MeuPainel(self.width, self.height, self.font)
self.meu_painel.visible = False

# No _render, após renderizar outros elementos:
self.meu_painel.render()

# No _resize_callback:
self.meu_painel.resize(width, height)

# No _mouse_button_callback (para clicks):
if self.meu_painel.on_click(x, y):
    return  # Painel consumiu o click

# No _cursor_pos_callback (para hover):
self.meu_painel.on_hover(x, y)

# No _process_menu_action (para toggle):
elif action == 'toggle_meu_painel':
    self.meu_painel.visible = not self.meu_painel.visible
```

### Passo 3: Adicionar ao menu com checkbox

```python
# Em menu_bar.py
{
    'label': 'Meu Painel (M)',
    'action': 'toggle_meu_painel',
    'checkbox': True,
    'checked': False
}

# Em application.py, atualizar checkbox ao toggle:
elif action == 'toggle_meu_painel':
    self.meu_painel.visible = not self.meu_painel.visible
    for item in self.menu_bar.menus[2]['items']:  # Menu Ferramentas
        if item.get('action') == 'toggle_meu_painel':
            item['checked'] = self.meu_painel.visible
```

---

## 🎯 Decisão: Janela vs Painel?

| Critério | Janela Independente | Painel Overlay |
|----------|-------------------|----------------|
| **Usa caso** | Tabelas, editores, gráficos | Controles, configurações, stats |
| **Complexidade** | Maior (gerenciar contexto GL) | Menor |
| **Mobilidade** | Move/redimensiona livremente | Fixo na tela |
| **Performance** | Dois loops de render | Um loop apenas |
| **Exemplo no projeto** | `PointsTableWindow` | `TrainControlPanel` |

---

## 📝 Checklist de Implementação

- [ ] Criar arquivo em `ui/`
- [ ] Implementar construtor com parâmetros necessários
- [ ] Se janela: criar `_init_window()` e `run()`
- [ ] Se painel: criar `render()` e `is_over()`
- [ ] Implementar callbacks (click, hover, resize)
- [ ] Adicionar import em `application.py`
- [ ] Instanciar no `__init__` da aplicação
- [ ] Adicionar ao loop de render (se painel)
- [ ] Criar método de abertura (se janela)
- [ ] Adicionar ação em `_process_menu_action`
- [ ] Adicionar item no menu (`menu_bar.py`)
- [ ] (Opcional) Adicionar atalho de teclado
- [ ] Testar abertura, fechamento e interação

---

## 🔧 Dicas e Boas Práticas

### Coordenadas OpenGL
```python
# GLFW usa origem no topo-esquerda (0,0)
# OpenGL usa origem no baixo-esquerda (0,0)
# Sempre inverter Y em callbacks GLFW:
y_opengl = window_height - y_glfw
```

### Gerenciar Estado OpenGL
```python
# Sempre salvar/restaurar estado ao renderizar UI
glPushMatrix()
glLoadIdentity()
# ... seu código de render ...
glPopMatrix()
```

### Performance
```python
# Cache medidas de texto:
if not hasattr(self, '_cached_width'):
    self._cached_width = self.font.measure_text("Texto")

# Renderize apenas quando visível:
if not self.visible:
    return
```

### Transparência
```python
# Habilite blending para overlays semi-transparentes:
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glColor4f(0.2, 0.2, 0.25, 0.9)  # Último valor = alpha
# ... render ...
glDisable(GL_BLEND)
```

---

## 📚 Exemplos no Projeto

Estude esses arquivos como referência:

1. **Janela Independente**: `ui/points_table.py`
   - Janela com tabela scrollável
   - Seleção de linhas
   - Navegação 3D integrada

2. **Painel Overlay**: `ui/train_control_panel.py`
   - Painel fixo no canto
   - Botões interativos
   - Hover effects

3. **Editor Complexo**: `ui/font_editor.py`
   - Painel fullscreen overlay
   - Muitos controles
   - Preview em tempo real

---

## ❓ Troubleshooting

**Janela não abre:**
- Verifique se GLFW está inicializado
- Confirme que está usando `glfw.make_context_current()`

**Texto não aparece:**
- Certifique-se que `VectorFont` está instanciado
- Verifique se `glColor` está definido (não branco em fundo branco)

**Cliques não funcionam:**
- Lembre de inverter Y: `y = height - y`
- Debug com `print(f"Click: {x}, {y}")`

**Painel fica atrás de elementos 3D:**
- Renderize painéis por último
- Desabilite depth test: `glDisable(GL_DEPTH_TEST)` antes de render UI

---

Boa sorte com sua implementação! 🚀
