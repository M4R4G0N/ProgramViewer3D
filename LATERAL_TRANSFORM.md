# Transformação Lateral de Coordenadas UPL

## 📖 Visão Geral

Sistema de transformação de coordenadas para arquivos UPL que usa **latitude e longitude** para posicionar corretamente as seções transversais do túnel no espaço 3D.

## 🎯 Problema

Em arquivos UPL tradicionais:
- **Z** = distância ao longo do túnel (km)
- **X** = posição lateral na seção
- **Y** = altura

**Limitação**: Se o túnel faz curvas, as seções ficam empilhadas em linha reta no eixo Z, não seguindo a geometria real do trajeto.

## ✨ Solução

Usa lat/lon de cada seção para:
1. Criar **linha de referência** do início ao fim do trajeto
2. Calcular **deslocamento lateral** de cada seção em relação a essa linha
3. Mover pontos **para esquerda/direita** conforme a curvatura real

## 🔧 Como Funciona

### Passo 1: Extração de Lat/Lon

```python
# No cabeçalho EFVM de cada seção:
# partes[8] = Latitude
# partes[9] = Longitude

lat = float(partes[8].replace(',', '.'))
lon = float(partes[9].replace(',', '.'))
```

### Passo 2: Linha de Referência

```
Início: (lat_start, lon_start)  ──────────────────> Fim: (lat_end, lon_end)
                                   Vetor Direção
```

Converte para coordenadas planas:
```python
# 1 grau lat ≈ 111 km
# 1 grau lon ≈ 111 km × cos(latitude)

dx_ref = (lon_end - lon_start) * 111000 * cos(lat_mid)
dy_ref = (lat_end - lat_start) * 111000
```

### Passo 3: Vetor Perpendicular

Para medir deslocamento lateral, cria vetor perpendicular (90° anti-horário):

```python
perp_x = -dy_ref
perp_y = dx_ref
```

```
        ↑ Perpendicular (esquerda)
        |
        |
Início ─┼────────────────> Direção (fim)
        |
        ↓ Perpendicular (direita)
```

### Passo 4: Cálculo de Deslocamentos

Para cada seção:

```python
# Posição da seção em relação ao início
dx_section = (lon_section - lon_start) * 111000 * cos(lat_mid)
dy_section = (lat_section - lat_start) * 111000

# Deslocamento LATERAL (produto escalar com perpendicular)
lateral_offset = dx_section * perp_x + dy_section * perp_y

# Deslocamento LONGITUDINAL (produto escalar com direção)
longitudinal_offset = dx_section * dx_ref + dy_section * dy_ref
```

### Passo 5: Aplicação

```python
# Move pontos lateralmente (eixo X)
X_novo = X_original + lateral_offset

# Reposiciona ao longo do trajeto (eixo Z)
Z_novo = longitudinal_offset
```

## 📊 Exemplo Visual

### Antes (Sem Transformação)

```
Vista de Cima (X-Z):

Z →
    |                   Seções empilhadas
    |                   em linha reta
    |  ████  Seção 1
    |  ████  Seção 2
    |  ████  Seção 3
    |  ████  Seção 4
    └──────────────── X
```

### Depois (Com Transformação)

```
Vista de Cima (X-Z):

Z →
    |
    |  ████          Seções seguem
    |      ████      a curvatura real
    |          ████  do trajeto
    |              ████
    └──────────────────── X
                    ↑
                Deslocamento lateral
```

## 🧮 Matemática

### Produto Escalar

```
lateral_offset = (dx_section, dy_section) · (perp_x, perp_y)
               = dx_section * perp_x + dy_section * perp_y
```

**Resultado**:
- `> 0` → Seção está **à direita** da linha
- `< 0` → Seção está **à esquerda** da linha
- `= 0` → Seção está **exatamente na linha**

### Conversão Lat/Lon → Metros

```
Δx (metros) = Δlon (graus) × 111,000 × cos(latitude)
Δy (metros) = Δlat (graus) × 111,000
```

**Observação**: Aproximação válida para distâncias < 100 km

## 💻 Uso

### Automático

Transformação é aplicada **automaticamente** ao carregar arquivo UPL:

```python
app.load_file("tunel.upl")
# ✅ Lat/lon detectado e transformação aplicada
```

### Output no Terminal

```
📍 Transformação lateral:
   Início: lat=-20.123456, lon=-43.987654
   Fim: lat=-20.234567, lon=-43.876543
   Vetor direção: (0.707, 0.707)
   Vetor perpendicular: (-0.707, 0.707)
   ✅ Transformação aplicada!
   Novo X range: [-25.3, 18.7] m
   Novo Z range: [0.0, 5432.1] m
```

### Fallback

Se lat/lon não estiver disponível ou for inválido:

```
⚠️  Lat/Lon não disponível, mantendo coordenadas originais
```

## 🎯 Aplicações

### Túneis Curvos

Túneis ferroviários com curvas agora são visualizados com geometria correta:

```
Túnel Reto:
════════════════════════

Túnel com Curva:
════╗
    ║
    ╚════════
```

### Análise de Deformações

Com posicionamento correto, é possível:
- Identificar **setores com problemas**
- Correlacionar **deformações com curvatura**
- Medir **deslocamento lateral real**

### Inspeção Visual

Operador pode:
- Navegar pelo túnel como se estivesse **dentro dele**
- Ver **curvas** e **rampas** reais
- Identificar **anomalias geométricas**

## 🔍 Troubleshooting

### Transformação não aplicada

**Causa**: Lat/lon zerado ou ausente no arquivo

**Solução**: Verificar se cabeçalho EFVM tem campos 8 e 9 preenchidos

### Distorções estranhas

**Causa**: Lat/lon em formato incorreto

**Verificar**:
```python
# Lat deve estar entre -90 e 90
# Lon deve estar entre -180 e 180
```

### Seções invertidas

**Causa**: Lat/lon da primeira e última seção estão invertidos

**Solução**: Arquivo pode estar com seções em ordem reversa

## 📐 Limitações

1. **Aproximação planar**: Válido para < 100 km
2. **Ignora elevação**: Assume terreno plano
3. **Sem correção geodésica**: Usa geometria euclidiana

Para trajetos > 100 km, considerar projeção cartográfica adequada (UTM, etc.)

## 🚀 Desenvolvimentos Futuros

- [ ] Suporte para elevação (3D completo)
- [ ] Projeção UTM para grandes distâncias
- [ ] Interpolação de lat/lon entre seções
- [ ] Visualização do trajeto 2D (mapa)
- [ ] Export de KML para Google Earth

---

**Implementado em**: `loaders/data_loader.py`  
**Método**: `UPLLoader._apply_lateral_transform()`
