# 3D Point Cloud Viewer# 3D Point Cloud Viewer



Um visualizador interativo de nuvens de pontos 3D com interface gráfica customizada, desenvolvido com OpenGL e Python. Suporta múltiplos formatos de arquivo e oferece controles avançados de câmera, renderização e customização visual.Sistema modular de visualização de nuvens de pontos 3D com OpenGL, suportando múltiplos formatos de arquivo.



![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)## 🎯 Características

![License](https://img.shields.io/badge/license-MIT-green.svg)

- **Alta Performance**: Renderização acelerada por GPU com OpenGL vertex arrays

## 🚀 Características- **Arquitetura Modular**: Código organizado em componentes reutilizáveis

- **Múltiplos Formatos**: Suporte a UPL, CSV e formatos personalizados

- **Renderização 3D de Alto Desempenho**: Utilizando OpenGL com aceleração por hardware- **Interface Intuitiva**: Menu de configuração OpenGL nativo

- **Múltiplos Formatos de Arquivo**: Suporte para UPL, CSV, JSON e PTS- **Câmera Avançada**: Sistema orbital com rotação, pan e zoom

- **Interface Gráfica Customizada**: UI vetorial desenhada com OpenGL- **Customizável**: Sistema de configuração com persistência JSON

- **Controles de Câmera Avançados**: Navegação intuitiva com mouse e teclado

- **Indicadores de Eixos**: Visualização de orientação espacial## 📁 Estrutura do Projeto

- **Tabela de Pontos**: Inspeção detalhada dos dados

- **Editor de Fontes**: Personalização de caracteres vetoriais```

- **Sistema de Configuração**: Persistência de preferências do usuárioviewer3d/

- **Otimização com Numba**: JIT compilation para performance máxima├── core/                    # Componentes principais

│   ├── camera.py           # Sistema de câmera orbital 3D

## 📋 Pré-requisitos│   ├── configuration.py    # Gerenciador de configurações

│   └── application.py      # Aplicação principal (orchestrator)

- Python 3.8 ou superior│

- OpenGL 3.3+├── ui/                      # Interface de usuário

- Sistema operacional: Linux, Windows ou macOS│   ├── vector_font.py      # Sistema de fontes vetoriais

│   └── components.py       # Widgets OpenGL (botões, sliders, etc)

## 🔧 Instalação│

├── loaders/                 # Carregadores de dados

1. Clone o repositório:│   └── data_loader.py      # Factory e loaders (UPL, CSV)

```bash│

git clone https://github.com/seu-usuario/ProgramViewer3D.git├── renderers/               # Renderizadores

cd ProgramViewer3D│   └── point_cloud.py      # Renderizador de nuvens de pontos

```│

├── utils/                   # Utilitários

2. Crie um ambiente virtual (recomendado):│

```bash└── main.py                  # Script principal

python3 -m venv venv```

source venv/bin/activate  # Linux/macOS

# ou## 🚀 Instalação

venv\Scripts\activate  # Windows

``````bash

# Clone ou copie o projeto

3. Instale as dependências:cd viewer3d

```bash

pip install -r requirements.txt# Instale dependências

```pip install -r requirements.txt

```

## 🎮 Uso

## 💻 Uso

### Uso Básico

### Básico

```bash

# Abrir visualizador vazio```bash

python3 main.py# Visualizar arquivo UPL

python3 main.py arquivo.upl

# Carregar arquivo específico

python3 main.py test_data/test_sphere.pts# Visualizar arquivo CSV

python3 main.py data.uplpython3 main.py pontos.csv

python3 main.py points.csv

```# Abrir visualizador vazio

python3 main.py

### Controles```



#### Mouse### Programático

- **Botão Esquerdo + Arrastar**: Rotacionar câmera

- **Botão Direito + Arrastar**: Pan (mover lateralmente)```python

- **Scroll**: Zoom in/outfrom core.application import Viewer3DApplication



#### Teclado# Cria aplicação

- **W/S**: Mover câmera para frente/trásapp = Viewer3DApplication()

- **A/D**: Mover câmera para esquerda/direita

- **Q/E**: Mover câmera para cima/baixo# Carrega arquivo

- **Setas**: Rotacionar câmeraapp.load_file("data.upl")

- **R**: Resetar câmera para posição inicial

- **ESC**: Fechar aplicação# Inicia loop

app.run()

#### Interface```

- **Menu Arquivo**: Abrir/Salvar arquivos

- **Menu Visualização**: Toggle de eixos e indicadores## 🎮 Controles

- **Menu Janelas**: Abrir tabela de pontos e editor de fontes

- **Sliders**: Ajustar tamanho dos pontos### Mouse

- **Botões de Cor**: Alterar cor de fundo- **Arrastar Esquerdo**: Rotacionar câmera

- **Ctrl + Arrastar Esquerdo**: Pan (mover lateral)

## 📁 Estrutura do Projeto- **Ctrl + Arrastar Direito**: Mover frente/trás

- **Scroll**: Zoom in/out

```

ProgramViewer3D/### Teclado

├── core/                   # Componentes principais- **↑↓←→**: Mover ponto de interesse

│   ├── application.py      # Aplicação principal- **J/K**: Mover eixo Y (cima/baixo)

│   ├── camera.py          # Sistema de câmera 3D- **X/Y/Z**: Vistas perpendiculares aos eixos

│   └── configuration.py   # Gerenciamento de configuração- **R**: Reset câmera

├── loaders/               # Carregadores de dados- **C**: Menu de configuração

│   └── data_loader.py     # Factory e loaders para diferentes formatos- **U**: Recarregar arquivo

├── renderers/             # Renderizadores- **ESC**: Sair

│   └── point_cloud.py     # Renderização de pontos e eixos

├── ui/                    # Interface do usuário## 🔧 Configuração

│   ├── components.py      # Componentes UI (botões, sliders, etc)

│   ├── vector_font.py     # Sistema de fontes vetoriaisO arquivo `config.json` é gerado automaticamente e permite personalizar:

│   ├── font_editor.py     # Editor de fontes

│   ├── menu_bar.py        # Barra de menus```json

│   └── points_table.py    # Tabela de pontos{

├── test_data/             # Dados de exemplo    "background_color": [0.1, 0.1, 0.1, 1.0],

│   ├── test_sphere.pts    "point_size": 3.0,

│   ├── test_torus.pts    "show_axes": true,

│   └── ...    "camera_distance": 400.0,

├── main.py                # Script principal    "window_width": 1200,

├── config.json            # Configuração do usuário    "window_height": 900,

├── requirements.txt       # Dependências Python    "max_points": 500000

└── README.md             # Este arquivo}

``````



## 📊 Formatos de Arquivo Suportados## 📦 Componentes Principais



### UPL (Tunnel Inspection)### Camera3D

Formato específico para inspeção de túneis com cabeçalhos EFVM:Sistema de câmera orbital com controles intuitivos:

```

EFVM <version>```python

SECTION <number>from core.camera import Camera3D

<x> <y> <z> [r g b]

...camera = Camera3D(distance=400.0, pitch=30.0, yaw=0.0)

```camera.rotate(delta_yaw=5.0, delta_pitch=2.0)

camera.zoom(-50.0)

### CSVcamera.pan(dx=10, dy=5)

Arquivo de valores separados por vírgula:camera.apply()  # Aplica transformação OpenGL

``````

x,y,z,r,g,b

1.0,2.0,3.0,255,0,0### DataLoaderFactory

...Carregamento automático baseado em extensão:

```

```python

### JSONfrom loaders.data_loader import DataLoaderFactory

Formato JSON estruturado:

```jsonloader = DataLoaderFactory()

{vertices, colors = loader.load("arquivo.upl")

  "points": [```

    {"x": 1.0, "y": 2.0, "z": 3.0, "r": 1.0, "g": 0.0, "b": 0.0},

    ...### PointCloudRenderer

  ]Renderização otimizada de nuvens de pontos:

}

``````python

from renderers.point_cloud import PointCloudRenderer

### PTSimport numpy as np

Formato simples de texto (X Y Z ou X Y Z R G B):

```renderer = PointCloudRenderer()

1.0 2.0 3.0 255 0 0vertices = np.array([[x1, y1, z1], [x2, y2, z2], ...])

4.0 5.0 6.0 0 255 0colors = np.array([[r1, g1, b1], [r2, g2, b2], ...])

...renderer.set_data(vertices, colors)

```renderer.render()

```

## 🛠️ Desenvolvimento

### VectorFont

### Gerando Dados de TesteRenderização de texto sem dependências externas:



O projeto inclui scripts para gerar dados sintéticos:```python

from ui.vector_font import VectorFont

```bash

# Gerar galáxia com 10 milhões de pontosfont = VectorFont()

python3 generate_galaxy_10M.pyfont.draw_text(x=100, y=200, text="Hello World", 

               color=(1, 1, 1), font_size=1.2)

# Gerar múltiplas formas geométricas```

python3 generate_test_data.py

```## 🔌 Extensibilidade



### Adicionando Novo Formato de Arquivo### Adicionar Novo Formato de Arquivo



1. Crie uma nova classe em `loaders/data_loader.py`:```python

```pythonfrom loaders.data_loader import DataLoader

class MyFormatLoader(DataLoader):import numpy as np

    def supports(self, filepath):

        return filepath.endswith('.myext')class MyCustomLoader(DataLoader):

        def supports(self, filepath):

    def load(self, filepath):        return filepath.endswith('.xyz')

        # Seu código de carregamento    

        vertices = np.array(...)  # Shape (N, 3)    def load(self, filepath):

        colors = np.array(...)    # Shape (N, 3)        # Lê arquivo customizado

        return vertices, colors        data = parse_custom_format(filepath)

```        vertices = np.array(data['points'])

        colors = np.array(data['colors'])

2. Registre o loader na factory:        return vertices, colors

```python

# Em DataLoaderFactory.__init__# Registra loader

self.register_loader(MyFormatLoader())from loaders.data_loader import DataLoaderFactory

```factory = DataLoaderFactory()

factory.loaders.append(MyCustomLoader())

### Testes```



```bash### Adicionar Widget Customizado

# Testar estrutura do projeto

python3 test_structure.py```python

```from ui.components import UIComponent

from OpenGL.GL import *

## ⚙️ Configuração

class MyWidget(UIComponent):

O arquivo `config.json` armazena preferências do usuário:    def __init__(self, x, y, width, height):

        super().__init__(x, y, width, height)

```json    

{    def draw(self):

  "background_color": [0.0, 0.0, 0.0, 1.0],        # Renderiza widget

  "point_size": 1.18,        glColor3f(1, 0, 0)

  "show_axes": false,        glBegin(GL_QUADS)

  "show_axis_indicator": true,        # ... desenha forma

  "camera_distance": 10.0,        glEnd()

  "window_width": 1920,    

  "window_height": 1008,    def on_click(self, x, y):

  "max_points": 500000,        # Lógica de clique

  "enable_antialiasing": true        print("Clicado!")

}```

```

## 🎨 Formatos Suportados

## 🎨 Editor de Fontes

### Arquivo UPL (Tunnel Inspection)

O visualizador inclui um editor de fontes vetoriais que permite customizar os caracteres usados na interface:Formato específico para inspeção de túneis com classificação de segurança:

- 🟢 Verde: Pontos seguros

1. Abra o editor: Menu → Janelas → Editor de Fontes- 🟡 Amarelo: Pontos em alerta

2. Selecione um caractere- 🔴 Vermelho: Pontos de invasão

3. Adicione pontos com clique esquerdo

4. Remova pontos próximos com clique direito### Arquivo CSV

5. Salve as alteraçõesFormato genérico com colunas:

```

## 📈 PerformanceX, Y, Z, R, G, B

1.0, 2.0, 3.0, 255, 0, 0

- Otimizado com Numba JIT compilation...

- Suporta até 10M+ pontos em hardware moderno```

- Renderização com OpenGL acelerada por hardware

- Sistema de culling para objetos fora da tela## 🐛 Troubleshooting



## 🐛 Troubleshooting### Erro: "Falha ao inicializar GLFW"

- Instale GLFW: `sudo apt-get install libglfw3`

### Erro: "Falha ao inicializar GLFW"

- Instale GLFW: `sudo apt-get install libglfw3`### Erro: "NullFunctionError"

- Verifique drivers OpenGL: `glxinfo | grep OpenGL`

### Erro: "NullFunctionError"- AMD: `sudo apt-get install mesa-utils`

- Verifique drivers OpenGL: `glxinfo | grep OpenGL`

- Instale drivers: `sudo apt-get install mesa-utils`### Performance baixa

- Reduza `max_points` em `config.json`

### Performance baixa- Desabilite antialiasing: `"enable_antialiasing": false`

- Reduza `max_points` em `config.json`

- Desabilite antialiasing: `"enable_antialiasing": false`## 📝 Licença



## 🤝 ContribuindoMIT License - Sinta-se livre para usar e modificar.



Contribuições são bem-vindas! Por favor:## 🤝 Contribuindo



1. Faça um fork do projetoContribuições são bem-vindas! Áreas de melhoria:

2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)- [ ] Suporte a mais formatos (PLY, PCD, LAS)

3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)- [ ] Shaders customizados

4. Push para a branch (`git push origin feature/AmazingFeature`)- [ ] Seleção de pontos

5. Abra um Pull Request- [ ] Medições 3D

- [ ] Exportação de vistas

## 📝 Licença

## 📧 Contato

Este projeto está sob a licença MIT. Sinta-se livre para usar e modificar.

Para dúvidas e sugestões, abra uma issue no repositório.

## 🙏 Agradecimentos

- OpenGL por fornecer a base de renderização
- GLFW por gerenciamento de janelas
- NumPy e Numba por computação numérica eficiente

## 📞 Contato

Para questões e suporte, abra uma issue no GitHub.

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
