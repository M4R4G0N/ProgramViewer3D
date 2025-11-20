"""
Editor de fontes vetoriais interativo
Permite criar e editar caracteres customizados com preview em tempo real
"""

from OpenGL.GL import *
import math


class FontEditor:
    """
    Editor interativo de fontes vetoriais
    Permite adicionar linhas e arcos, visualizar em tempo real e exportar código
    """
    
    def __init__(self, width, height):
        """
        Inicializa o editor de fontes
        
        Args:
            width, height: Dimensões da janela
        """
        self.width = width
        self.height = height
        self.active = False
        
        # Estado do editor
        self.strokes = []  # Lista de strokes [(tipo, dados)]
        self.current_char = 'A'
        self.mode = 'line'  # 'line', 'polyline', 'arc', 'bezier'
        
        # Pontos temporários para construção
        self.temp_points = []
        self.hover_point = None
        
        # Edição de pontos existentes
        self.edit_mode = False
        self.selected_stroke = None
        self.selected_point = None
        self.dragging = False
        
        # Grid de desenho (0-1 normalizado)
        self.grid_x = 100
        self.grid_y = 100
        self.grid_size = 400
        
        # Configurações de snap/travamento
        self.snap_enabled = True
        self.snap_divisions = 20  # Divide o grid em 20x20 células (melhor caligrafia)
        
        # Configurações de arco
        self.arc_segments = 8
        
        # UI
        self.smoothness = 8
    
    def activate(self):
        """Ativa o editor"""
        self.active = True
        print("\n" + "="*60)
        print("✏️  EDITOR DE FONTES VETORIAIS")
        print("="*60)
        print("Controles:")
        print("  [Clique Esq]  Adicionar ponto / Selecionar para editar")
        print("  [Arrastar]    Mover ponto selecionado")
        print("  [Enter]       Finalizar polilinha")
        print("  [Tab]         Alternar Linha/Polilinha/Arco")
        print("  [D]           Toggle Modo Edição (arrastar pontos)")
        print("  [S]           Toggle Snap/Travamento")
        print("  [E]           Exportar código Python")
        print("  [J]           Salvar JSON")
        print("  [L]           Carregar JSON")
        print("  [C]           Limpar tudo")
        print("  [Del]         Deletar stroke selecionado")
        print("  [+/-]         Ajustar suavidade arcos")
        print("  [ESC]         Fechar editor")
        print(f"  Snap: {'✅ ATIVADO' if self.snap_enabled else '❌ DESATIVADO'}")
        print(f"  Modo: {self.mode.upper()}")
        print("="*60)
    
    def deactivate(self):
        """Desativa o editor"""
        self.active = False
        print("✅ Editor de fontes fechado")
    
    def toggle_mode(self):
        """Alterna entre modo linha, polilinha, arco e bezier"""
        modes = ['line', 'polyline', 'arc', 'bezier']
        current_idx = modes.index(self.mode)
        self.mode = modes[(current_idx + 1) % len(modes)]
        self.temp_points = []
        print(f"🔧 Modo: {self.mode.upper()}")
    
    def toggle_edit_mode(self):
        """Alterna modo de edição (arrastar pontos)"""
        self.edit_mode = not self.edit_mode
        self.selected_stroke = None
        self.selected_point = None
        print(f"✏️  Modo Edição: {'ATIVADO' if self.edit_mode else 'DESATIVADO'}")
    
    def toggle_snap(self):
        """Alterna snap/travamento no grid"""
        self.snap_enabled = not self.snap_enabled
        print(f"🧲 Snap: {'ATIVADO' if self.snap_enabled else 'DESATIVADO'}")
    
    def set_current_char(self, char):
        """
        Define caractere atual e carrega do char.json automaticamente
        
        Args:
            char: Caractere a ser editado (A-Z, 0-9, etc)
        """
        self.current_char = char.upper()
        print(f"🔤 Caractere: {self.current_char}")
        
        # Carrega automaticamente do char.json
        self.load_from_char_json()
    
    def load_from_char_json(self):
        """Carrega stroke do char.json para o caractere atual"""
        import json
        import os
        
        json_path = 'char.json'
        if not os.path.exists(json_path):
            print(f"⚠️  char.json não encontrado")
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            char_key = self.current_char.upper()
            if char_key not in char_data:
                print(f"⚠️  Caractere '{char_key}' não existe em char.json")
                self.strokes = []
                return
            
            stroke_list = char_data[char_key]
            self.strokes = []
            
            # Agrupa linhas consecutivas em polylines
            current_polyline = []
            
            for stroke in stroke_list:
                if stroke['type'] == 'line':
                    # Adiciona à polyline atual
                    segment = (stroke['x1'], stroke['y1'], stroke['x2'], stroke['y2'])
                    current_polyline.append(segment)
                elif stroke['type'] == 'arc':
                    # Salva polyline acumulada (se houver)
                    if current_polyline:
                        self.strokes.append(('polyline', current_polyline))
                        current_polyline = []
                    
                    # Adiciona arco
                    arc_data = (
                        stroke['cx'],
                        stroke['cy'],
                        stroke['radius'],
                        stroke['start_angle'],
                        stroke['end_angle'],
                        stroke.get('segments', 12)
                    )
                    self.strokes.append(('arc', arc_data))
                elif stroke['type'] == 'bezier':
                    # Salva polyline acumulada (se houver)
                    if current_polyline:
                        self.strokes.append(('polyline', current_polyline))
                        current_polyline = []
                    
                    # Adiciona curva Bezier quadrática
                    bezier_data = (
                        stroke['x0'],
                        stroke['y0'],
                        stroke['cx'],
                        stroke['cy'],
                        stroke['x1'],
                        stroke['y1'],
                        stroke.get('segments', 12)
                    )
                    self.strokes.append(('bezier', bezier_data))
                elif stroke['type'] == 'bezier_cubic':
                    # Salva polyline acumulada (se houver)
                    if current_polyline:
                        self.strokes.append(('polyline', current_polyline))
                        current_polyline = []
                    
                    # Adiciona curva Bezier cúbica
                    bezier_data = (
                        stroke['x0'],
                        stroke['y0'],
                        stroke['cx1'],
                        stroke['cy1'],
                        stroke['cx2'],
                        stroke['cy2'],
                        stroke['x1'],
                        stroke['y1'],
                        stroke.get('segments', 12)
                    )
                    self.strokes.append(('bezier', bezier_data))
            
            # Salva polyline final (se houver)
            if current_polyline:
                self.strokes.append(('polyline', current_polyline))
            
            print(f"📥 '{char_key}' carregado: {len(self.strokes)} strokes")
            # Debug: mostra estrutura
            for i, (stype, sdata) in enumerate(self.strokes):
                if stype == 'polyline':
                    print(f"  Stroke {i}: polyline com {len(sdata)} segmentos")
                elif stype == 'arc':
                    print(f"  Stroke {i}: arc")
                elif stype == 'bezier':
                    print(f"  Stroke {i}: bezier")
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
    
    def _snap_to_grid(self, norm_x, norm_y):
        """
        Trava coordenadas normalizadas no grid
        
        Args:
            norm_x, norm_y: Coordenadas normalizadas (0-1)
            
        Returns:
            Tupla (x, y) travada no grid
        """
        if not self.snap_enabled:
            return (norm_x, norm_y)
        
        # Calcula tamanho de cada célula
        cell_size = 1.0 / self.snap_divisions
        
        # Arredonda para a célula mais próxima
        snapped_x = round(norm_x / cell_size) * cell_size
        snapped_y = round(norm_y / cell_size) * cell_size
        
        # Garante que fica no range 0-1
        snapped_x = max(0.0, min(1.0, snapped_x))
        snapped_y = max(0.0, min(1.0, snapped_y))
        
        return (snapped_x, snapped_y)
    
    def add_point(self, x, y):
        """
        Adiciona ponto ao stroke atual
        
        Args:
            x, y: Coordenadas do clique (pixels)
        """
        # Converte para coordenadas normalizadas (0-1)
        norm_x = (x - self.grid_x) / self.grid_size
        norm_y = (y - self.grid_y) / self.grid_size
        
        # Clamp para grid
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Aplica snap
        norm_x, norm_y = self._snap_to_grid(norm_x, norm_y)
        
        self.temp_points.append((norm_x, norm_y))
        
        if self.mode == 'line':
            # Linha precisa de 2 pontos
            if len(self.temp_points) == 2:
                x1, y1 = self.temp_points[0]
                x2, y2 = self.temp_points[1]
                self.strokes.append(('line', [(x1, y1, x2, y2)]))
                self.temp_points = []
                print(f"  ✅ Linha: ({x1:.2f}, {y1:.2f}) → ({x2:.2f}, {y2:.2f})")
        
        elif self.mode == 'polyline':
            # Polilinha: cada clique adiciona, Enter finaliza
            print(f"  ➕ Ponto {len(self.temp_points)}: ({norm_x:.2f}, {norm_y:.2f})")
        
        elif self.mode == 'arc':
            # Arco precisa de 3 pontos (centro, início, fim)
            if len(self.temp_points) == 3:
                cx, cy = self.temp_points[0]  # Centro
                sx, sy = self.temp_points[1]  # Início
                ex, ey = self.temp_points[2]  # Fim
                
                # Calcula raio e ângulos
                radius = math.sqrt((sx - cx)**2 + (sy - cy)**2)
                start_angle = math.degrees(math.atan2(sy - cy, sx - cx))
                end_angle = math.degrees(math.atan2(ey - cy, ex - cx))
                
                # Normaliza ângulos para 0-360
                start_angle = start_angle % 360
                end_angle = end_angle % 360
                
                # Por padrão, usa o caminho mais curto (sentido anti-horário se end > start)
                # O usuário pode inverter depois arrastando o ponto do meio
                
                self.strokes.append(('arc', (cx, cy, radius, start_angle, end_angle, self.arc_segments)))
                self.temp_points = []
                print(f"  ✅ Arco: centro({cx:.2f}, {cy:.2f}) r={radius:.2f} {start_angle:.0f}°→{end_angle:.0f}°")
        
        elif self.mode == 'bezier':
            # Curva Bezier cúbica precisa de 4 pontos (início, controle1, controle2, fim)
            if len(self.temp_points) == 4:
                x0, y0 = self.temp_points[0]  # Ponto inicial
                cx1, cy1 = self.temp_points[1]  # Ponto de controle 1
                cx2, cy2 = self.temp_points[2]  # Ponto de controle 2
                x1, y1 = self.temp_points[3]  # Ponto final
                
                self.strokes.append(('bezier', (x0, y0, cx1, cy1, cx2, cy2, x1, y1, self.arc_segments)))
                self.temp_points = []
                print(f"  ✅ Bezier: início({x0:.2f}, {y0:.2f}) ctrl1({cx1:.2f}, {cy1:.2f}) ctrl2({cx2:.2f}, {cy2:.2f}) fim({x1:.2f}, {y1:.2f})")
    
    def finalize_shape(self):
        """Finaliza a forma atual (polilinha)"""
        if self.mode == 'polyline' and len(self.temp_points) >= 2:
            # Converte pontos em lista de segmentos
            segments = []
            for i in range(len(self.temp_points) - 1):
                x1, y1 = self.temp_points[i]
                x2, y2 = self.temp_points[i + 1]
                segments.append((x1, y1, x2, y2))
            
            self.strokes.append(('polyline', segments))
            print(f"  ✅ Polilinha: {len(self.temp_points)} pontos, {len(segments)} segmentos")
            self.temp_points = []
        else:
            self.temp_points = []
            print("  ⏸️  Forma finalizada")
    
    def clear_all(self):
        """Limpa todos os strokes"""
        self.strokes = []
        self.temp_points = []
        self.selected_stroke = None
        self.selected_point = None
        print("🗑️  Canvas limpo")
    
    def delete_selected(self):
        """Deleta stroke selecionado"""
        if self.selected_stroke is not None and 0 <= self.selected_stroke < len(self.strokes):
            del self.strokes[self.selected_stroke]
            self.selected_stroke = None
            self.selected_point = None
            print(f"🗑️  Stroke deletado. Restam {len(self.strokes)} strokes")
    
    def reverse_selected_arc(self):
        """Inverte direção do arco selecionado"""
        if self.selected_stroke is None or self.selected_stroke >= len(self.strokes):
            print("⚠️  Nenhum stroke selecionado")
            return
        
        stroke_type, stroke_data = self.strokes[self.selected_stroke]
        
        if stroke_type == 'arc':
            cx, cy, radius, start_angle, end_angle, segments = stroke_data
            # Inverte defasando 180° (vai pro outro lado do círculo)
            new_start = (start_angle + 180) % 360
            new_end = (end_angle + 180) % 360
            new_data = (cx, cy, radius, new_start, new_end, segments)
            self.strokes[self.selected_stroke] = ('arc', new_data)
            print(f"🔄 Arco invertido: {new_start:.1f}°→{new_end:.1f}°")
        else:
            print(f"⚠️  Stroke selecionado não é um arco (é {stroke_type})")
    
    def adjust_smoothness(self, delta):
        """Ajusta suavidade dos arcos"""
        self.arc_segments = max(3, min(20, self.arc_segments + delta))
        print(f"🔧 Suavidade: {self.arc_segments} segmentos")
    
    def export_code(self):
        """Exporta código Python dos strokes"""
        print("\n" + "="*60)
        print(f"📤 CÓDIGO EXPORTADO - Caractere '{self.current_char}'")
        print("="*60)
        
        if not self.strokes:
            print("⚠️  Nenhum stroke para exportar!")
            return
        
        # Gera código
        code_lines = []
        code_lines.append(f"# Caractere '{self.current_char}'")
        code_lines.append(f"strokes['{self.current_char}'] = (")
        
        for stroke_type, data in self.strokes:
            if stroke_type == 'line':
                # Data é lista com um único segmento
                for segment in data:
                    x1, y1, x2, y2 = segment
                    code_lines.append(f"    [({x1:.3f}, {y1:.3f}, {x2:.3f}, {y2:.3f})] +")
            elif stroke_type == 'polyline':
                # Data é lista de segmentos
                code_lines.append("    [")
                for segment in data:
                    x1, y1, x2, y2 = segment
                    code_lines.append(f"        ({x1:.3f}, {y1:.3f}, {x2:.3f}, {y2:.3f}),")
                code_lines.append("    ] +")
            elif stroke_type == 'arc':
                cx, cy, radius, start_angle, end_angle, segments = data
                code_lines.append(f"    self._arc({cx:.3f}, {cy:.3f}, {radius:.3f}, {start_angle:.1f}, {end_angle:.1f}, {segments}) +")
            elif stroke_type == 'bezier':
                if len(data) == 7:
                    x0, y0, cx, cy, x1, y1, segments = data
                    code_lines.append(f"    self._bezier({x0:.3f}, {y0:.3f}, {cx:.3f}, {cy:.3f}, {x1:.3f}, {y1:.3f}, {segments}) +")
                else:
                    x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = data
                    code_lines.append(f"    self._bezier_cubic({x0:.3f}, {y0:.3f}, {cx1:.3f}, {cy1:.3f}, {cx2:.3f}, {cy2:.3f}, {x1:.3f}, {y1:.3f}, {segments}) +")
        
        # Remove último ' +'
        if code_lines:
            code_lines[-1] = code_lines[-1].rstrip(' +')
        
        code_lines.append(")")
        
        # Imprime
        for line in code_lines:
            print(line)
        
        print("="*60 + "\n")
    
    def save_json(self):
        """Salva strokes no char.json (atualiza o caractere atual)"""
        import json
        import os
        
        if not self.strokes:
            print("⚠️  Nenhum stroke para salvar!")
            return
        
        # Carrega char.json existente
        json_path = 'char.json'
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
        else:
            char_data = {}
        
        # Converte strokes para formato char.json
        stroke_list = []
        for stroke_type, stroke_data in self.strokes:
            if stroke_type in ['line', 'polyline']:
                # Cada segmento vira uma linha separada
                for segment in stroke_data:
                    x1, y1, x2, y2 = segment
                    stroke_list.append({
                        'type': 'line',
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2
                    })
            elif stroke_type == 'arc':
                cx, cy, radius, start_angle, end_angle, segments = stroke_data
                stroke_list.append({
                    'type': 'arc',
                    'cx': cx,
                    'cy': cy,
                    'radius': radius,
                    'start_angle': start_angle,
                    'end_angle': end_angle,
                    'segments': segments
                })
            elif stroke_type == 'bezier':
                # Suporta quadrática (7) e cúbica (9)
                if len(stroke_data) == 7:
                    x0, y0, cx, cy, x1, y1, segments = stroke_data
                    stroke_list.append({
                        'type': 'bezier',
                        'x0': x0,
                        'y0': y0,
                        'cx': cx,
                        'cy': cy,
                        'x1': x1,
                        'y1': y1,
                        'segments': segments
                    })
                else:
                    x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = stroke_data
                    stroke_list.append({
                        'type': 'bezier_cubic',
                        'x0': x0,
                        'y0': y0,
                        'cx1': cx1,
                        'cy1': cy1,
                        'cx2': cx2,
                        'cy2': cy2,
                        'x1': x1,
                        'y1': y1,
                        'segments': segments
                    })
        
        # Atualiza o caractere
        char_data[self.current_char] = stroke_list
        
        # Salva de volta
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=2, ensure_ascii=False)
            print(f"💾 '{self.current_char}' salvo em char.json ({len(stroke_list)} strokes)")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def load_json(self):
        """Carrega strokes de arquivo JSON"""
        import json
        
        filename = f"char_{self.current_char}.json"
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.strokes = []
            for stroke in data.get('strokes', []):
                stroke_type = stroke['type']
                
                if stroke_type == 'line':
                    self.strokes.append(('line', stroke['data']))
                elif stroke_type == 'polyline':
                    self.strokes.append(('polyline', stroke['data']))
                elif stroke_type == 'arc':
                    arc_data = (
                        stroke['center'][0],
                        stroke['center'][1],
                        stroke['radius'],
                        stroke['start_angle'],
                        stroke['end_angle'],
                        stroke['segments']
                    )
                    self.strokes.append(('arc', arc_data))
            
            print(f"📂 Carregado: {filename} ({len(self.strokes)} strokes)")
        except FileNotFoundError:
            print(f"⚠️  Arquivo não encontrado: {filename}")
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
    
    def load_from_vector_font(self):
        """Importa strokes do vector_font.py para edição"""
        from .vector_font import VectorFont
        
        font = VectorFont()
        char_key = self.current_char.upper()
        
        if char_key not in font.strokes:
            print(f"⚠️  Caractere '{char_key}' não existe em VectorFont")
            return
        
        raw_strokes = font.strokes[char_key]
        self.strokes = []
        
        # Converte strokes do VectorFont para formato do editor
        if isinstance(raw_strokes, list):
            # Lista de linhas simples
            segments = []
            for stroke in raw_strokes:
                if len(stroke) == 4:
                    segments.append(stroke)
            if segments:
                self.strokes.append(('polyline', segments))
        
        print(f"📥 Importado '{char_key}' do VectorFont ({len(self.strokes)} strokes)")
        print(f"⚠️  Nota: Arcos foram simplificados em segmentos de linha")
        print(f"💡 Use 'J' para salvar como JSON")
    
    def on_click(self, x, y):
        """
        Processa clique do mouse
        
        Args:
            x, y: Coordenadas do clique
            
        Returns:
            True se o clique foi processado
        """
        if not self.active:
            return False
        
        # Verifica se clicou no grid
        if (self.grid_x <= x <= self.grid_x + self.grid_size and
            self.grid_y <= y <= self.grid_y + self.grid_size):
            
            if self.edit_mode:
                # Modo edição: seleciona ponto próximo
                self._select_nearest_point(x, y)
                if self.selected_point is not None:
                    self.dragging = True
                    print(f"🖱️  Dragging ativado: {self.dragging}")
                else:
                    print("❌ Nenhum ponto próximo - dragging NÃO ativado")
            else:
                # Modo desenho: adiciona ponto
                self.add_point(x, y)
            
            return True
        
        return False
    
    def on_release(self):
        """Processa soltar botão do mouse"""
        self.dragging = False
    
    def on_drag(self, x, y):
        """
        Processa arrasto do mouse
        
        Args:
            x, y: Coordenadas atuais do mouse
        """
        if not self.active or not self.dragging:
            return
        
        if self.selected_stroke is None or self.selected_point is None:
            print("⚠️  Nenhum ponto selecionado para arrastar")
            return
        
        # Converte para normalizado com snap
        norm_x = (x - self.grid_x) / self.grid_size
        norm_y = (y - self.grid_y) / self.grid_size
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        norm_x, norm_y = self._snap_to_grid(norm_x, norm_y)
        
        # Atualiza ponto
        stroke_type, stroke_data = self.strokes[self.selected_stroke]
        
        if stroke_type in ['line', 'polyline']:
            # stroke_data é lista de segmentos (x1, y1, x2, y2)
            seg_idx, point_idx = self.selected_point
            
            if 0 <= seg_idx < len(stroke_data):
                segment = list(stroke_data[seg_idx])
                
                if point_idx == 0:  # Ponto inicial
                    segment[0] = norm_x
                    segment[1] = norm_y
                elif point_idx == 1:  # Ponto final
                    segment[2] = norm_x
                    segment[3] = norm_y
                
                stroke_data[seg_idx] = tuple(segment)
                
                # Atualiza segmentos conectados para polilinhas
                if stroke_type == 'polyline':
                    # Se moveu ponto final, atualiza início do próximo segmento
                    if point_idx == 1 and seg_idx + 1 < len(stroke_data):
                        next_seg = list(stroke_data[seg_idx + 1])
                        next_seg[0] = norm_x
                        next_seg[1] = norm_y
                        stroke_data[seg_idx + 1] = tuple(next_seg)
                    
                    # Se moveu ponto inicial, atualiza final do segmento anterior
                    if point_idx == 0 and seg_idx > 0:
                        prev_seg = list(stroke_data[seg_idx - 1])
                        prev_seg[2] = norm_x
                        prev_seg[3] = norm_y
                        stroke_data[seg_idx - 1] = tuple(prev_seg)
        
        elif stroke_type == 'arc':
            # Edita arco
            cx, cy, radius, start_angle, end_angle, segments = stroke_data
            point_type, point_id = self.selected_point
            
            if point_id == 'center':
                # Move o centro
                cx = norm_x
                cy = norm_y
            elif point_id == 'start':
                # Move o ponto inicial (ajusta ângulo inicial)
                dx = norm_x - cx
                dy = norm_y - cy
                start_angle = math.degrees(math.atan2(dy, dx))
                # Atualiza raio se necessário
                new_radius = math.sqrt(dx**2 + dy**2)
                radius = new_radius
            elif point_id == 'end':
                # Move o ponto final (ajusta ângulo final)
                dx = norm_x - cx
                dy = norm_y - cy
                end_angle = math.degrees(math.atan2(dy, dx))
                # Atualiza raio se necessário
                new_radius = math.sqrt(dx**2 + dy**2)
                radius = new_radius
            elif point_id == 'mid':
                # Move o ponto do meio - permite inverter direção do arco
                dx = norm_x - cx
                dy = norm_y - cy
                
                # Calcula novo raio
                new_radius = math.sqrt(dx**2 + dy**2)
                if new_radius > 0.01:
                    radius = new_radius
                
                # Calcula para onde o usuário está arrastando
                drag_angle = math.degrees(math.atan2(dy, dx))
                if drag_angle < 0:
                    drag_angle += 360
                
                # Normaliza ângulos para 0-360
                norm_start = start_angle % 360
                norm_end = end_angle % 360
                
                # Calcula caminho atual (sentido anti-horário)
                if norm_end >= norm_start:
                    current_span = norm_end - norm_start
                else:
                    current_span = (360 - norm_start) + norm_end
                
                # Ponto do meio esperado no caminho atual
                expected_mid = (norm_start + current_span / 2) % 360
                
                # Calcula diferença angular entre onde está arrastando e onde deveria estar
                diff = drag_angle - expected_mid
                if diff > 180:
                    diff -= 360
                elif diff < -180:
                    diff += 360
                
                # Se a diferença é grande (>90°), inverte o arco
                if abs(diff) > 90:
                    # Troca start e end para inverter direção
                    start_angle, end_angle = end_angle, start_angle
                    print(f"🔄 Arco invertido! Novo: {start_angle:.1f}°→{end_angle:.1f}°")
            
            # Atualiza arc_data
            self.strokes[self.selected_stroke] = ('arc', (cx, cy, radius, start_angle, end_angle, segments))
        
        elif stroke_type == 'bezier':
            # Edita curva Bezier (quadrática ou cúbica)
            point_type, point_id = self.selected_point
            
            if len(stroke_data) == 7:
                # Bezier quadrática
                x0, y0, cx, cy, x1, y1, segments = stroke_data
                
                if point_id == 'start':
                    x0 = norm_x
                    y0 = norm_y
                elif point_id == 'control':
                    cx = norm_x
                    cy = norm_y
                elif point_id == 'end':
                    x1 = norm_x
                    y1 = norm_y
                
                new_bezier_data = (x0, y0, cx, cy, x1, y1, segments)
            else:
                # Bezier cúbica
                x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = stroke_data
                
                if point_id == 'start':
                    x0 = norm_x
                    y0 = norm_y
                elif point_id == 'control1':
                    cx1 = norm_x
                    cy1 = norm_y
                elif point_id == 'control2':
                    cx2 = norm_x
                    cy2 = norm_y
                elif point_id == 'end':
                    x1 = norm_x
                    y1 = norm_y
                
                new_bezier_data = (x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments)
            
            self.strokes[self.selected_stroke] = ('bezier', new_bezier_data)
    
    def _select_nearest_point(self, x, y):
        """
        Seleciona o ponto mais próximo do clique
        
        Args:
            x, y: Coordenadas do clique em pixels
        """
        threshold = 15  # Pixels de tolerância
        min_dist = float('inf')
        best_stroke = None
        best_point = None
        
        for stroke_idx, (stroke_type, stroke_data) in enumerate(self.strokes):
            if stroke_type in ['line', 'polyline']:
                for seg_idx, segment in enumerate(stroke_data):
                    x1, y1, x2, y2 = segment
                    
                    # Converte para pixels
                    px1 = self.grid_x + x1 * self.grid_size
                    py1 = self.grid_y + y1 * self.grid_size
                    px2 = self.grid_x + x2 * self.grid_size
                    py2 = self.grid_y + y2 * self.grid_size
                    
                    # Distância ao ponto inicial
                    dist1 = math.sqrt((x - px1)**2 + (y - py1)**2)
                    if dist1 < min_dist and dist1 < threshold:
                        min_dist = dist1
                        best_stroke = stroke_idx
                        best_point = (seg_idx, 0)
                    
                    # Distância ao ponto final
                    dist2 = math.sqrt((x - px2)**2 + (y - py2)**2)
                    if dist2 < min_dist and dist2 < threshold:
                        min_dist = dist2
                        best_stroke = stroke_idx
                        best_point = (seg_idx, 1)
            
            elif stroke_type == 'arc':
                # Verifica pontos de controle do arco
                cx, cy, radius, start_angle, end_angle, segments = stroke_data
                
                # Ponto central
                pcx = self.grid_x + cx * self.grid_size
                pcy = self.grid_y + cy * self.grid_size
                dist_center = math.sqrt((x - pcx)**2 + (y - pcy)**2)
                if dist_center < min_dist and dist_center < threshold:
                    min_dist = dist_center
                    best_stroke = stroke_idx
                    best_point = ('arc', 'center')
                
                # Ponto inicial
                start_rad = math.radians(start_angle)
                psx = pcx + radius * self.grid_size * math.cos(start_rad)
                psy = pcy + radius * self.grid_size * math.sin(start_rad)
                dist_start = math.sqrt((x - psx)**2 + (y - psy)**2)
                if dist_start < min_dist and dist_start < threshold:
                    min_dist = dist_start
                    best_stroke = stroke_idx
                    best_point = ('arc', 'start')
                
                # Ponto final
                end_rad = math.radians(end_angle)
                pex = pcx + radius * self.grid_size * math.cos(end_rad)
                pey = pcy + radius * self.grid_size * math.sin(end_rad)
                dist_end = math.sqrt((x - pex)**2 + (y - pey)**2)
                if dist_end < min_dist and dist_end < threshold:
                    min_dist = dist_end
                    best_stroke = stroke_idx
                    best_point = ('arc', 'end')
                
                # Ponto do meio (controle de direção)
                mid_angle = start_angle + (end_angle - start_angle) / 2
                mid_rad = math.radians(mid_angle)
                pmx = pcx + radius * self.grid_size * math.cos(mid_rad)
                pmy = pcy + radius * self.grid_size * math.sin(mid_rad)
                dist_mid = math.sqrt((x - pmx)**2 + (y - pmy)**2)
                if dist_mid < min_dist and dist_mid < threshold:
                    min_dist = dist_mid
                    best_stroke = stroke_idx
                    best_point = ('arc', 'mid')
            
            elif stroke_type == 'bezier':
                # Verifica pontos de controle da curva Bezier
                # Quadrática (7) ou cúbica (9)
                if len(stroke_data) == 7:
                    x0, y0, cx, cy, x1, y1, segments = stroke_data
                    
                    # Ponto inicial
                    px0 = self.grid_x + x0 * self.grid_size
                    py0 = self.grid_y + y0 * self.grid_size
                    dist_start = math.sqrt((x - px0)**2 + (y - py0)**2)
                    if dist_start < min_dist and dist_start < threshold:
                        min_dist = dist_start
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'start')
                    
                    # Ponto de controle
                    pcx = self.grid_x + cx * self.grid_size
                    pcy = self.grid_y + cy * self.grid_size
                    dist_control = math.sqrt((x - pcx)**2 + (y - pcy)**2)
                    if dist_control < min_dist and dist_control < threshold:
                        min_dist = dist_control
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'control')
                    
                    # Ponto final
                    px1 = self.grid_x + x1 * self.grid_size
                    py1 = self.grid_y + y1 * self.grid_size
                    dist_end = math.sqrt((x - px1)**2 + (y - py1)**2)
                    if dist_end < min_dist and dist_end < threshold:
                        min_dist = dist_end
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'end')
                else:
                    # Bezier cúbica
                    x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = stroke_data
                    
                    # Ponto inicial
                    px0 = self.grid_x + x0 * self.grid_size
                    py0 = self.grid_y + y0 * self.grid_size
                    dist_start = math.sqrt((x - px0)**2 + (y - py0)**2)
                    if dist_start < min_dist and dist_start < threshold:
                        min_dist = dist_start
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'start')
                    
                    # Ponto de controle 1
                    pcx1 = self.grid_x + cx1 * self.grid_size
                    pcy1 = self.grid_y + cy1 * self.grid_size
                    dist_c1 = math.sqrt((x - pcx1)**2 + (y - pcy1)**2)
                    if dist_c1 < min_dist and dist_c1 < threshold:
                        min_dist = dist_c1
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'control1')
                    
                    # Ponto de controle 2
                    pcx2 = self.grid_x + cx2 * self.grid_size
                    pcy2 = self.grid_y + cy2 * self.grid_size
                    dist_c2 = math.sqrt((x - pcx2)**2 + (y - pcy2)**2)
                    if dist_c2 < min_dist and dist_c2 < threshold:
                        min_dist = dist_c2
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'control2')
                    
                    # Ponto final
                    px1 = self.grid_x + x1 * self.grid_size
                    py1 = self.grid_y + y1 * self.grid_size
                    dist_end = math.sqrt((x - px1)**2 + (y - py1)**2)
                    if dist_end < min_dist and dist_end < threshold:
                        min_dist = dist_end
                        best_stroke = stroke_idx
                        best_point = ('bezier', 'end')
        
        self.selected_stroke = best_stroke
        self.selected_point = best_point
        
        if best_stroke is not None:
            print(f"🎯 Ponto selecionado: Stroke {best_stroke}, Ponto {best_point}")
        else:
            print("  Nenhum ponto próximo")
    
    def update_hover(self, x, y):
        """Atualiza ponto de hover"""
        if (self.grid_x <= x <= self.grid_x + self.grid_size and
            self.grid_y <= y <= self.grid_y + self.grid_size):
            norm_x = (x - self.grid_x) / self.grid_size
            norm_y = (y - self.grid_y) / self.grid_size
            
            # Clamp
            norm_x = max(0, min(1, norm_x))
            norm_y = max(0, min(1, norm_y))
            
            # Aplica snap ao hover também
            norm_x, norm_y = self._snap_to_grid(norm_x, norm_y)
            
            self.hover_point = (norm_x, norm_y)
        else:
            self.hover_point = None
    
    def render(self):
        """Renderiza o editor na tela"""
        if not self.active:
            return
        
        # Configura projeção 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Fundo semi-transparente
        glColor4f(0, 0, 0, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # Grid de desenho
        self._render_grid()
        
        # Renderiza strokes finalizados
        self._render_strokes()
        
        # Renderiza pontos temporários
        self._render_temp_points()
        
        # Renderiza hover point
        if self.hover_point:
            self._render_hover()
        
        # Renderiza UI
        self._render_ui()
        
        # Restaura estado
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _render_grid(self):
        """Renderiza o grid de desenho"""
        # Fundo do grid
        glColor4f(0.15, 0.15, 0.15, 1)
        glBegin(GL_QUADS)
        glVertex2f(self.grid_x, self.grid_y)
        glVertex2f(self.grid_x + self.grid_size, self.grid_y)
        glVertex2f(self.grid_x + self.grid_size, self.grid_y + self.grid_size)
        glVertex2f(self.grid_x, self.grid_y + self.grid_size)
        glEnd()
        
        # Borda do grid
        glColor4f(0.5, 0.5, 0.5, 1)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.grid_x, self.grid_y)
        glVertex2f(self.grid_x + self.grid_size, self.grid_y)
        glVertex2f(self.grid_x + self.grid_size, self.grid_y + self.grid_size)
        glVertex2f(self.grid_x, self.grid_y + self.grid_size)
        glEnd()
        
        # Linhas de grade
        glColor4f(0.3, 0.3, 0.3, 0.5)
        glLineWidth(1)
        glBegin(GL_LINES)
        
        # Verticais
        for i in range(1, 10):
            x = self.grid_x + (self.grid_size / 10) * i
            glVertex2f(x, self.grid_y)
            glVertex2f(x, self.grid_y + self.grid_size)
        
        # Horizontais
        for i in range(1, 10):
            y = self.grid_y + (self.grid_size / 10) * i
            glVertex2f(self.grid_x, y)
            glVertex2f(self.grid_x + self.grid_size, y)
        
        glEnd()
        
        # Centro (linhas mais grossas)
        glColor4f(0.5, 0.5, 0.5, 0.8)
        glLineWidth(2)
        glBegin(GL_LINES)
        # Vertical centro
        x_center = self.grid_x + self.grid_size / 2
        glVertex2f(x_center, self.grid_y)
        glVertex2f(x_center, self.grid_y + self.grid_size)
        # Horizontal centro
        y_center = self.grid_y + self.grid_size / 2
        glVertex2f(self.grid_x, y_center)
        glVertex2f(self.grid_x + self.grid_size, y_center)
        glEnd()
        glLineWidth(1)
    
    def _render_strokes(self):
        """Renderiza strokes finalizados"""
        for stroke_idx, (stroke_type, data) in enumerate(self.strokes):
            # Cor do stroke (verde normal, amarelo se selecionado)
            is_selected = (stroke_idx == self.selected_stroke)
            stroke_color = (1, 1, 0, 1) if is_selected else (0, 1, 0, 1)
            
            glColor4f(*stroke_color)
            glLineWidth(3)
            
            if stroke_type in ['line', 'polyline']:
                # Renderiza segmentos
                for segment in data:
                    x1, y1, x2, y2 = segment
                    px1 = self.grid_x + x1 * self.grid_size
                    py1 = self.grid_y + y1 * self.grid_size
                    px2 = self.grid_x + x2 * self.grid_size
                    py2 = self.grid_y + y2 * self.grid_size
                    
                    glBegin(GL_LINES)
                    glVertex2f(px1, py1)
                    glVertex2f(px2, py2)
                    glEnd()
                
                # Renderiza pontos editáveis (se modo edição)
                if self.edit_mode:
                    self._render_editable_points(stroke_idx, data)
            
            elif stroke_type == 'arc':
                cx, cy, radius, start_angle, end_angle, segments = data
                pcx = self.grid_x + cx * self.grid_size
                pcy = self.grid_y + cy * self.grid_size
                pradius = radius * self.grid_size
                
                # Calcula o span do arco (sempre no sentido anti-horário)
                angle_diff = end_angle - start_angle
                # Normaliza para sempre ir no caminho mais curto
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360
                
                glBegin(GL_LINE_STRIP)
                for i in range(segments + 1):
                    t = i / segments
                    angle = math.radians(start_angle + angle_diff * t)
                    x = pcx + pradius * math.cos(angle)
                    y = pcy + pradius * math.sin(angle)
                    glVertex2f(x, y)
                glEnd()
                
                # Renderiza pontos de controle do arco (se modo edição)
                if self.edit_mode:
                    self._render_arc_control_points(stroke_idx, data)
            
            elif stroke_type == 'bezier':
                # Verifica se é bezier quadrática (7 valores) ou cúbica (9 valores)
                if len(data) == 7:
                    # Bezier quadrática (legado)
                    x0, y0, cx, cy, x1, y1, segments = data
                    glBegin(GL_LINE_STRIP)
                    for i in range(segments + 1):
                        t = i / segments
                        bx = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
                        by = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
                        px = self.grid_x + bx * self.grid_size
                        py = self.grid_y + by * self.grid_size
                        glVertex2f(px, py)
                    glEnd()
                else:
                    # Bezier cúbica (4 pontos)
                    x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = data
                    glBegin(GL_LINE_STRIP)
                    for i in range(segments + 1):
                        t = i / segments
                        # Fórmula de Bezier cúbica: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
                        bx = (1-t)**3 * x0 + 3*(1-t)**2*t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x1
                        by = (1-t)**3 * y0 + 3*(1-t)**2*t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y1
                        px = self.grid_x + bx * self.grid_size
                        py = self.grid_y + by * self.grid_size
                        glVertex2f(px, py)
                    glEnd()
                
                # Renderiza pontos de controle da bezier (se modo edição)
                if self.edit_mode:
                    self._render_bezier_control_points(stroke_idx, data)
        
        glLineWidth(1)
    
    def _render_editable_points(self, stroke_idx, stroke_data):
        """Renderiza pontos editáveis de um stroke"""
        rendered_points = set()  # Evita duplicatas em polylines
        
        for seg_idx, segment in enumerate(stroke_data):
            x1, y1, x2, y2 = segment
            
            # Ponto inicial
            p1_key = (stroke_idx, seg_idx, 0)
            if p1_key not in rendered_points:
                self._render_edit_point(
                    stroke_idx, seg_idx, 0,
                    self.grid_x + x1 * self.grid_size,
                    self.grid_y + y1 * self.grid_size
                )
                rendered_points.add(p1_key)
            
            # Ponto final
            p2_key = (stroke_idx, seg_idx, 1)
            if p2_key not in rendered_points:
                self._render_edit_point(
                    stroke_idx, seg_idx, 1,
                    self.grid_x + x2 * self.grid_size,
                    self.grid_y + y2 * self.grid_size
                )
                rendered_points.add(p2_key)
    
    def _render_arc_control_points(self, stroke_idx, arc_data):
        """Renderiza pontos de controle de um arco (centro, início, fim, meio)"""
        cx, cy, radius, start_angle, end_angle, segments = arc_data
        
        # Ponto central
        pcx = self.grid_x + cx * self.grid_size
        pcy = self.grid_y + cy * self.grid_size
        
        is_center_selected = (
            self.selected_stroke == stroke_idx and
            self.selected_point == ('arc', 'center')
        )
        self._render_arc_point(is_center_selected, pcx, pcy, (0, 1, 1))  # Ciano para centro
        
        # Ponto inicial do arco
        start_rad = math.radians(start_angle)
        psx = pcx + radius * self.grid_size * math.cos(start_rad)
        psy = pcy + radius * self.grid_size * math.sin(start_rad)
        
        is_start_selected = (
            self.selected_stroke == stroke_idx and
            self.selected_point == ('arc', 'start')
        )
        self._render_arc_point(is_start_selected, psx, psy, (1, 1, 0))  # Amarelo para início
        
        # Ponto final do arco
        end_rad = math.radians(end_angle)
        pex = pcx + radius * self.grid_size * math.cos(end_rad)
        pey = pcy + radius * self.grid_size * math.sin(end_rad)
        
        is_end_selected = (
            self.selected_stroke == stroke_idx and
            self.selected_point == ('arc', 'end')
        )
        self._render_arc_point(is_end_selected, pex, pey, (1, 0.5, 0))  # Laranja para fim
        
        # Ponto do meio do arco (para controlar direção/curvatura)
        # Calcula considerando o caminho mais curto
        angle_diff = end_angle - start_angle
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        
        mid_angle = start_angle + angle_diff / 2
        mid_rad = math.radians(mid_angle)
        pmx = pcx + radius * self.grid_size * math.cos(mid_rad)
        pmy = pcy + radius * self.grid_size * math.sin(mid_rad)
        
        is_mid_selected = (
            self.selected_stroke == stroke_idx and
            self.selected_point == ('arc', 'mid')
        )
        self._render_arc_point(is_mid_selected, pmx, pmy, (1, 0, 1))  # Magenta para meio
        
        # Linha do centro até o meio (indicador de direção)
        glColor4f(1, 0, 1, 0.3)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f(pcx, pcy)
        glVertex2f(pmx, pmy)
        glEnd()
    
    def _render_arc_point(self, is_selected, px, py, color):
        """Renderiza um ponto de controle de arco"""
        point_size = 12 if is_selected else 8
        
        glPointSize(point_size)
        glColor4f(*color, 1)
        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()
        glPointSize(1)
        
        # Contorno preto
        glColor4f(0, 0, 0, 1)
        glLineWidth(2)
        size = 5 if is_selected else 3
        glBegin(GL_LINE_LOOP)
        glVertex2f(px - size, py - size)
        glVertex2f(px + size, py - size)
        glVertex2f(px + size, py + size)
        glVertex2f(px - size, py + size)
        glEnd()
        glLineWidth(1)
    
    def _render_edit_point(self, stroke_idx, seg_idx, point_idx, px, py):
        """Renderiza um ponto editável"""
        is_selected = (
            self.selected_stroke == stroke_idx and
            self.selected_point == (seg_idx, point_idx)
        )
        
        # Ponto maior se selecionado
        point_size = 12 if is_selected else 8
        point_color = (1, 0, 0) if is_selected else (1, 1, 1)
        
        glPointSize(point_size)
        glColor4f(*point_color, 1)
        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()
        glPointSize(1)
        
        # Contorno preto para contraste
        glColor4f(0, 0, 0, 1)
        glLineWidth(2)
        size = 5 if is_selected else 3
        glBegin(GL_LINE_LOOP)
        glVertex2f(px - size, py - size)
        glVertex2f(px + size, py - size)
        glVertex2f(px + size, py + size)
        glVertex2f(px - size, py + size)
        glEnd()
        glLineWidth(1)
    
    def _render_bezier_control_points(self, stroke_idx, bezier_data):
        """Renderiza pontos de controle de uma curva Bezier"""
        # Verifica se é quadrática (7) ou cúbica (9)
        if len(bezier_data) == 7:
            # Bezier quadrática (legado: início, controle, fim)
            x0, y0, cx, cy, x1, y1, segments = bezier_data
            
            # Ponto inicial
            px0 = self.grid_x + x0 * self.grid_size
            py0 = self.grid_y + y0 * self.grid_size
            is_start_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'start'))
            self._render_arc_point(is_start_selected, px0, py0, (1, 1, 0))  # Amarelo
            
            # Ponto de controle
            pcx = self.grid_x + cx * self.grid_size
            pcy = self.grid_y + cy * self.grid_size
            is_control_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'control'))
            self._render_arc_point(is_control_selected, pcx, pcy, (1, 0, 1))  # Magenta
            
            # Ponto final
            px1 = self.grid_x + x1 * self.grid_size
            py1 = self.grid_y + y1 * self.grid_size
            is_end_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'end'))
            self._render_arc_point(is_end_selected, px1, py1, (1, 0.5, 0))  # Laranja
            
            # Linhas de guia
            glColor4f(1, 0, 1, 0.3)
            glLineWidth(1)
            glBegin(GL_LINES)
            glVertex2f(px0, py0)
            glVertex2f(pcx, pcy)
            glVertex2f(pcx, pcy)
            glVertex2f(px1, py1)
            glEnd()
        else:
            # Bezier cúbica (início, controle1, controle2, fim)
            x0, y0, cx1, cy1, cx2, cy2, x1, y1, segments = bezier_data
            
            # Ponto inicial (amarelo)
            px0 = self.grid_x + x0 * self.grid_size
            py0 = self.grid_y + y0 * self.grid_size
            is_start_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'start'))
            self._render_arc_point(is_start_selected, px0, py0, (1, 1, 0))
            
            # Ponto de controle 1 (magenta)
            pcx1 = self.grid_x + cx1 * self.grid_size
            pcy1 = self.grid_y + cy1 * self.grid_size
            is_c1_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'control1'))
            self._render_arc_point(is_c1_selected, pcx1, pcy1, (1, 0, 1))
            
            # Ponto de controle 2 (magenta)
            pcx2 = self.grid_x + cx2 * self.grid_size
            pcy2 = self.grid_y + cy2 * self.grid_size
            is_c2_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'control2'))
            self._render_arc_point(is_c2_selected, pcx2, pcy2, (1, 0, 1))
            
            # Ponto final (laranja)
            px1 = self.grid_x + x1 * self.grid_size
            py1 = self.grid_y + y1 * self.grid_size
            is_end_selected = (self.selected_stroke == stroke_idx and self.selected_point == ('bezier', 'end'))
            self._render_arc_point(is_end_selected, px1, py1, (1, 0.5, 0))
            
            # Linhas de guia
            glColor4f(1, 0, 1, 0.3)
            glLineWidth(1)
            glBegin(GL_LINES)
            glVertex2f(px0, py0)
            glVertex2f(pcx1, pcy1)
            glVertex2f(pcx2, pcy2)
            glVertex2f(px1, py1)
            glEnd()
    
    def _render_temp_points(self):
        """Renderiza pontos temporários"""
        if not self.temp_points:
            return
        
        # Pontos
        glPointSize(10)
        glColor4f(1, 1, 0, 1)
        glBegin(GL_POINTS)
        for x, y in self.temp_points:
            px = self.grid_x + x * self.grid_size
            py = self.grid_y + y * self.grid_size
            glVertex2f(px, py)
        glEnd()
        glPointSize(1)
        
        # Preview do que vai ser criado
        if self.mode == 'line' and len(self.temp_points) == 1:
            # Linha do ponto até o cursor
            if self.hover_point:
                glColor4f(1, 1, 0, 0.5)
                glLineWidth(2)
                glBegin(GL_LINES)
                x1, y1 = self.temp_points[0]
                x2, y2 = self.hover_point
                glVertex2f(self.grid_x + x1 * self.grid_size, self.grid_y + y1 * self.grid_size)
                glVertex2f(self.grid_x + x2 * self.grid_size, self.grid_y + y2 * self.grid_size)
                glEnd()
                glLineWidth(1)
        
        elif self.mode == 'arc':
            if len(self.temp_points) >= 2 and self.hover_point:
                # Preview do arco
                cx, cy = self.temp_points[0]
                sx, sy = self.temp_points[1]
                ex, ey = self.hover_point if len(self.temp_points) == 2 else self.temp_points[2]
                
                radius = math.sqrt((sx - cx)**2 + (sy - cy)**2)
                start_angle = math.degrees(math.atan2(sy - cy, sx - cx))
                end_angle = math.degrees(math.atan2(ey - cy, ex - cx))
                
                # Calcula o span do arco (sempre no sentido anti-horário)
                angle_diff = end_angle - start_angle
                # Normaliza para sempre ir no caminho mais curto
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360
                
                pcx = self.grid_x + cx * self.grid_size
                pcy = self.grid_y + cy * self.grid_size
                pradius = radius * self.grid_size
                
                glColor4f(1, 1, 0, 0.5)
                glLineWidth(2)
                glBegin(GL_LINE_STRIP)
                for i in range(self.arc_segments + 1):
                    t = i / self.arc_segments
                    angle = math.radians(start_angle + angle_diff * t)
                    x = pcx + pradius * math.cos(angle)
                    y = pcy + pradius * math.sin(angle)
                    glVertex2f(x, y)
                glEnd()
                glLineWidth(1)
        
        elif self.mode == 'bezier':
            if len(self.temp_points) >= 1 and self.hover_point:
                # Preview da curva Bezier cúbica (4 pontos)
                if len(self.temp_points) == 1:
                    # Apenas linha reta
                    x0, y0 = self.temp_points[0]
                    x1, y1 = self.hover_point
                    glColor4f(1, 1, 0, 0.5)
                    glLineWidth(2)
                    glBegin(GL_LINES)
                    glVertex2f(self.grid_x + x0 * self.grid_size, self.grid_y + y0 * self.grid_size)
                    glVertex2f(self.grid_x + x1 * self.grid_size, self.grid_y + y1 * self.grid_size)
                    glEnd()
                    glLineWidth(1)
                elif len(self.temp_points) >= 2:
                    # Bezier cúbica
                    x0, y0 = self.temp_points[0]
                    cx1, cy1 = self.temp_points[1]
                    
                    # Define cx2 e x1 baseado em quantos pontos temos
                    if len(self.temp_points) == 2:
                        # Apenas 2 pontos: hover é o terceiro ponto de controle
                        cx2, cy2 = self.hover_point
                        x1, y1 = self.hover_point  # Provisório
                    elif len(self.temp_points) == 3:
                        # 3 pontos: hover é o ponto final
                        cx2, cy2 = self.temp_points[2]
                        x1, y1 = self.hover_point
                    else:
                        # 4 pontos completos (não deveria chegar aqui)
                        cx2, cy2 = self.temp_points[2]
                        x1, y1 = self.temp_points[3]
                    
                    glColor4f(1, 1, 0, 0.5)
                    glLineWidth(2)
                    glBegin(GL_LINE_STRIP)
                    for i in range(self.arc_segments + 1):
                        t = i / self.arc_segments
                        # Fórmula de Bezier cúbica: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
                        bx = (1-t)**3 * x0 + 3*(1-t)**2*t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x1
                        by = (1-t)**3 * y0 + 3*(1-t)**2*t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y1
                        
                        px = self.grid_x + bx * self.grid_size
                        py = self.grid_y + by * self.grid_size
                        glVertex2f(px, py)
                    glEnd()
                    glLineWidth(1)
                    
                    # Linhas de guia (apenas se tiver 2+ pontos)
                    if len(self.temp_points) >= 2:
                        glColor4f(1, 0, 1, 0.3)
                        glLineWidth(1)
                        px0 = self.grid_x + x0 * self.grid_size
                        py0 = self.grid_y + y0 * self.grid_size
                        pcx1 = self.grid_x + cx1 * self.grid_size
                        pcy1 = self.grid_y + cy1 * self.grid_size
                        pcx2 = self.grid_x + cx2 * self.grid_size
                        pcy2 = self.grid_y + cy2 * self.grid_size
                        px1 = self.grid_x + x1 * self.grid_size
                        py1 = self.grid_y + y1 * self.grid_size
                        glBegin(GL_LINES)
                        glVertex2f(px0, py0)
                        glVertex2f(pcx1, pcy1)
                        glVertex2f(pcx2, pcy2)
                        glVertex2f(px1, py1)
                        glEnd()
    
    def _render_hover(self):
        """Renderiza ponto de hover"""
        x, y = self.hover_point
        px = self.grid_x + x * self.grid_size
        py = self.grid_y + y * self.grid_size
        
        # Ponto central destacado
        glPointSize(8)
        glColor4f(1, 1, 0, 1)
        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()
        glPointSize(1)
        
        # Crosshair
        glColor4f(1, 1, 1, 0.5)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f(px - 10, py)
        glVertex2f(px + 10, py)
        glVertex2f(px, py - 10)
        glVertex2f(px, py + 10)
        glEnd()
        
        # Se snap ativado, mostra a célula destacada
        if self.snap_enabled:
            cell_size = self.grid_size / self.snap_divisions
            # Encontra célula
            cell_x = int(x * self.snap_divisions)
            cell_y = int(y * self.snap_divisions)
            
            # Desenha contorno da célula
            glColor4f(1, 1, 0, 0.3)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.grid_x + cell_x * cell_size, self.grid_y + cell_y * cell_size)
            glVertex2f(self.grid_x + (cell_x + 1) * cell_size, self.grid_y + cell_y * cell_size)
            glVertex2f(self.grid_x + (cell_x + 1) * cell_size, self.grid_y + (cell_y + 1) * cell_size)
            glVertex2f(self.grid_x + cell_x * cell_size, self.grid_y + (cell_y + 1) * cell_size)
            glEnd()
            glLineWidth(1)
    
    def _render_ui(self):
        """Renderiza elementos da UI"""
        from .vector_font import VectorFont
        font = VectorFont()
        
        # Título com caractere atual
        title = f"EDITOR DE FONTES - Caractere: {self.current_char}"
        font.draw_text(20, self.height - 30, title, (1, 1, 1), 1.2)
        
        # Modo atual
        if self.edit_mode:
            mode_text = f"Modo: {self.mode.upper()} [EDIT MODE]"
            color = (1, 1, 0)  # Amarelo
        else:
            mode_text = f"Modo: {self.mode.upper()}"
            color = (1, 1, 0) if self.mode == 'line' else (0, 1, 1)
        font.draw_text(20, self.height - 60, mode_text, color, 1.0)
        
        # Contador de strokes
        font.draw_text(20, self.height - 85, f"Strokes: {len(self.strokes)}", (0.7, 0.7, 0.7), 0.8)
        
        # Instruções
        y_pos = 40
        
        if self.edit_mode:
            # Instruções modo edição
            font.draw_text(20, y_pos, "Click: Selecionar ponto", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "Drag: Mover ponto", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[D] Sair do modo edicao", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[Del] Deletar stroke", (0.7, 0.7, 0.7), 0.7)
        else:
            # Instruções modo desenho
            font.draw_text(20, y_pos, "[Shift+A-Z/0-9] Trocar char", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[I] Importar do VectorFont", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[Tab] Trocar modo", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[S] Toggle snap", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[E] Exportar Python", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[Enter] Finalizar stroke", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[D] Modo edicao", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[J] Salvar JSON", (0.7, 0.7, 0.7), 0.7)
            y_pos += 20
            font.draw_text(20, y_pos, "[L] Carregar JSON", (0.7, 0.7, 0.7), 0.7)
        instructions = [
            "Clique: Adicionar ponto",
            f"{'2 pontos' if self.mode == 'line' else '3 pontos (centro, inicio, fim)'} para completar",
            "[TAB] Alternar modo  [E] Exportar  [C] Limpar"
        ]
        for i, text in enumerate(instructions):
            font.draw_text(20, y_pos + i * 20, text, (0.6, 0.6, 0.6), 0.7)
        
        # Indicador de pontos temporários
        if self.temp_points:
            points_needed = 2 if self.mode == 'line' else 3
            font.draw_text(self.grid_x + self.grid_size + 20, self.grid_y + self.grid_size - 20,
                          f"Pontos: {len(self.temp_points)}/{points_needed}", (1, 1, 0), 0.9)
        
        # Indicador de Snap
        snap_color = (0, 1, 0) if self.snap_enabled else (0.5, 0.5, 0.5)
        snap_text = f"Snap: {'ON' if self.snap_enabled else 'OFF'}"
        font.draw_text(self.grid_x + self.grid_size + 20, self.grid_y + 20, snap_text, snap_color, 0.8)
