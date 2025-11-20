# Guia de Contribuição

Obrigado por considerar contribuir para o ProgramViewer3D! Este documento fornece diretrizes para contribuir com o projeto.

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug, por favor abra uma issue incluindo:

- Descrição clara do problema
- Passos para reproduzir o bug
- Comportamento esperado vs. comportamento atual
- Versão do Python e sistema operacional
- Screenshots ou logs, se aplicável

### Sugerindo Melhorias

Adoramos receber sugestões! Para propor uma nova funcionalidade:

1. Verifique se já não existe uma issue similar
2. Abra uma nova issue descrevendo:
   - O problema que a funcionalidade resolve
   - Como você imagina que ela deveria funcionar
   - Exemplos de uso, se possível

### Enviando Pull Requests

1. **Fork o repositório**
   ```bash
   git clone https://github.com/seu-usuario/ProgramViewer3D.git
   cd ProgramViewer3D
   ```

2. **Crie uma branch para sua feature**
   ```bash
   git checkout -b feature/minha-feature
   ```

3. **Faça suas alterações**
   - Siga o estilo de código existente
   - Adicione comentários quando necessário
   - Atualize a documentação se aplicável

4. **Teste suas alterações**
   ```bash
   python3 test_structure.py
   python3 main.py  # Teste manualmente
   ```

5. **Commit suas mudanças**
   ```bash
   git add .
   git commit -m "feat: adiciona funcionalidade X"
   ```

   Use prefixos nos commits:
   - `feat:` - Nova funcionalidade
   - `fix:` - Correção de bug
   - `docs:` - Alterações na documentação
   - `style:` - Formatação, sem mudança de código
   - `refactor:` - Refatoração de código
   - `test:` - Adição ou correção de testes
   - `chore:` - Manutenção geral

6. **Push para seu fork**
   ```bash
   git push origin feature/minha-feature
   ```

7. **Abra um Pull Request**
   - Descreva claramente o que foi alterado
   - Referencie issues relacionadas
   - Aguarde o review

## Estilo de Código

### Python

- Siga PEP 8
- Use nomes descritivos para variáveis e funções
- Adicione docstrings para classes e funções públicas
- Mantenha funções pequenas e focadas
- Use type hints quando apropriado

Exemplo:
```python
def calculate_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    Calcula a distância euclidiana entre dois pontos.
    
    Args:
        point1: Primeiro ponto como array numpy [x, y, z]
        point2: Segundo ponto como array numpy [x, y, z]
        
    Returns:
        Distância euclidiana entre os pontos
    """
    return np.linalg.norm(point1 - point2)
```

### Organização

- Mantenha a estrutura de diretórios existente:
  - `core/` - Componentes principais
  - `loaders/` - Carregadores de dados
  - `renderers/` - Renderizadores
  - `ui/` - Interface de usuário
  - `utils/` - Utilitários

## Áreas que Precisam de Ajuda

Contribuições são especialmente bem-vindas nestas áreas:

- [ ] **Novos formatos de arquivo**: PLY, PCD, LAS, E57
- [ ] **Otimização de performance**: LOD, octrees, culling
- [ ] **Shaders customizados**: Iluminação, efeitos visuais
- [ ] **Ferramentas de medição**: Distâncias, áreas, volumes
- [ ] **Seleção de pontos**: Ferramentas de seleção e filtragem
- [ ] **Exportação**: Salvar vistas, screenshots, dados filtrados
- [ ] **Testes**: Cobertura de testes unitários
- [ ] **Documentação**: Tutoriais, exemplos, API docs
- [ ] **Internacionalização**: Suporte a múltiplos idiomas

## Adicionando Novos Formatos de Arquivo

Para adicionar suporte a um novo formato:

1. Crie uma classe que herda de `DataLoader`:
```python
from loaders.data_loader import DataLoader
import numpy as np

class MyFormatLoader(DataLoader):
    def supports(self, filepath: str) -> bool:
        return filepath.endswith('.myformat')
    
    def load(self, filepath: str) -> tuple[np.ndarray, np.ndarray]:
        # Implementar lógica de carregamento
        vertices = np.array(...)  # Shape (N, 3)
        colors = np.array(...)    # Shape (N, 3)
        return vertices, colors
```

2. Registre o loader na `DataLoaderFactory` em `loaders/data_loader.py`

3. Adicione testes e exemplos

4. Atualize a documentação no README.md

## Processo de Review

- Todo PR será revisado por um mantenedor
- Podem ser solicitadas alterações
- PRs serão mesclados quando aprovados
- Mantenha o PR focado em uma única funcionalidade/correção

## Código de Conduta

Este projeto segue um código de conduta simples:

- Seja respeitoso com outros contribuidores
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros da comunidade

## Dúvidas?

Se tiver dúvidas sobre como contribuir, sinta-se à vontade para:

- Abrir uma issue com sua pergunta
- Comentar em issues existentes
- Entrar em contato através do GitHub

---

Obrigado por contribuir! 🎉
