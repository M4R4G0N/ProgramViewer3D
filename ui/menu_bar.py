"""
Barra de menu superior
"""

from OpenGL.GL import *
import glfw
from ui.vector_font import VectorFont


class MenuBar:
    """Barra de menu no topo da janela"""
    
    def __init__(self, width, height):
        """
        Inicializa barra de menu
        
        Args:
            width: Largura da janela
            height: Altura da janela
        """
        self.width = width
        self.height = height
        self.menu_height = 30
        self.font = VectorFont()
        
        # Menus
        self.menus = [
            {
                'label': 'Arquivo',
                'items': [
                    {'label': 'Abrir (O)', 'action': 'open_file'},
                    {'label': 'Recarregar (U)', 'action': 'reload_file'},
                    {'separator': True},
                    {'label': 'Recentes', 'action': 'recent_files_submenu', 'is_submenu': True},
                    {'separator': True},
                    {'label': 'Estatísticas do Cache', 'action': 'cache_stats'},
                    {'label': 'Limpar Cache', 'action': 'clear_cache'},
                    {'separator': True},
                    {'label': 'Sair (ESC)', 'action': 'exit'}
                ]
            },
            {
                'label': 'Visualizar',
                'items': [
                    {'label': 'Tabela de Pontos (T)', 'action': 'show_table'},
                    {'label': 'Configurações (C)', 'action': 'show_config'},
                    {'separator': True},
                    {'label': 'Auto-rotacionar X (V)', 'action': 'toggle_auto_rotate_x', 'checked': False},
                    {'label': 'Mostrar todos os pontos (L)', 'action': 'toggle_show_all_points', 'checked': False},
                    {'separator': True},
                    {'label': 'Vista X', 'action': 'view_x'},
                    {'label': 'Vista Y', 'action': 'view_y'},
                    {'label': 'Vista Z', 'action': 'view_z'},
                    {'separator': True},
                    {'label': 'Resetar Câmera (R)', 'action': 'reset_camera'}
                ]
            },
            {
                'label': 'Ferramentas',
                'items': [
                    {'label': 'Editor de Fontes (F)', 'action': 'font_editor'},
                    {'separator': True},
                    {'label': 'Seletor de Trem (Shift+T)', 'action': 'open_train_selector'},
                    {'label': 'Painel de Controle (P)', 'action': 'toggle_control_panel', 'checked': False}
                ]
            }
        ]
        
        # Estado
        self.active_menu = None
        self.hovered_item = None
        self.menu_widths = []
        
        # Calcula larguras dos menus
        self._calculate_menu_widths()
    
    def _calculate_menu_widths(self):
        """Calcula largura de cada menu"""
        self.menu_widths = []
        for menu in self.menus:
            # Calcula largura baseado no texto real com VectorFont
            # font_size 1.0, spacing 12 pixels por char
            width = len(menu['label']) * 12 + 30
            self.menu_widths.append(width)
    
    def update_size(self, width, height):
        """Atualiza tamanho da janela"""
        self.width = width
        self.height = height
    
    def update_recent_files(self, recent_files):
        """
        Atualiza lista de arquivos recentes no menu
        
        Args:
            recent_files: Lista de caminhos de arquivos recentes
        """
        # Encontra o menu Arquivo
        for menu in self.menus:
            if menu['label'] == 'Arquivo':
                # Encontra o item "Recentes"
                for i, item in enumerate(menu['items']):
                    if item.get('action') == 'recent_files_submenu':
                        # Remove itens antigos de arquivos recentes (se existirem)
                        # Remove todos os itens após "Recentes" até o próximo separador
                        items_to_remove = []
                        for j in range(i + 1, len(menu['items'])):
                            if menu['items'][j].get('separator'):
                                break
                            if menu['items'][j].get('action', '').startswith('open_recent_'):
                                items_to_remove.append(j)
                        
                        # Remove de trás para frente para não bagunçar os índices
                        for j in reversed(items_to_remove):
                            menu['items'].pop(j)
                        
                        # Adiciona novos arquivos recentes
                        if recent_files:
                            insert_pos = i + 1
                            for idx, filepath in enumerate(recent_files):
                                import os
                                filename = os.path.basename(filepath)
                                menu['items'].insert(insert_pos + idx, {
                                    'label': f'  {idx + 1}. {filename}',
                                    'action': f'open_recent_{idx}',
                                    'filepath': filepath
                                })
                        else:
                            # Nenhum arquivo recente
                            menu['items'].insert(i + 1, {
                                'label': '  (vazio)',
                                'action': 'none',
                                'disabled': True
                            })
                        break
                break
    
    def is_over_menu(self, x, y):
        """
        Verifica se mouse está sobre a barra de menu
        
        Args:
            x, y: Coordenadas do mouse (sistema OpenGL - Y crescendo para cima)
        """
        # Barra de menu está no topo da janela
        return y >= self.height - self.menu_height
    
    def handle_click(self, x, y):
        """
        Processa clique na barra de menu
        
        Args:
            x, y: Coordenadas do clique (sistema OpenGL - Y crescendo para cima)
            
        Returns:
            Action string se clicou em item, None caso contrário
        """
        # Verifica se clicou na barra principal (topo da janela)
        if y >= self.height - self.menu_height:
            # Verifica qual menu foi clicado
            menu_x = 10
            for i, menu in enumerate(self.menus):
                menu_width = self.menu_widths[i]
                if menu_x <= x < menu_x + menu_width:
                    if self.active_menu == i:
                        self.active_menu = None
                    else:
                        self.active_menu = i
                    return None
                menu_x += menu_width + 5
            
            # Clicou fora de qualquer menu
            self.active_menu = None
            return None
        
        # Verifica se clicou em dropdown
        if self.active_menu is not None:
            menu = self.menus[self.active_menu]
            dropdown_x, dropdown_y = self._get_dropdown_position(self.active_menu)
            dropdown_width = self._get_dropdown_width(self.active_menu)
            item_height = 25
            
            y_offset = 0
            for idx, item in enumerate(menu['items']):
                if item.get('separator'):
                    y_offset += 5
                    continue

                item_y_bottom = dropdown_y - y_offset - item_height
                item_y_top = dropdown_y - y_offset

                if (dropdown_x <= x < dropdown_x + dropdown_width and
                    item_y_bottom <= y < item_y_top):
                    
                    # Ignora items desabilitados ou submenus sem ação
                    if item.get('disabled') or item.get('is_submenu'):
                        return None
                    
                    # Pega a ação
                    action = item.get('action')
                    
                    # Se item for do tipo checkbox, toggla seu estado
                    if 'checked' in item:
                        item['checked'] = not item.get('checked', False)
                    
                    # Fecha o menu
                    self.active_menu = None
                    
                    # Retorna ação (pode ser None)
                    return action

                y_offset += item_height
        
        # Clicou fora do menu
        self.active_menu = None
        return None
    
    def handle_hover(self, x, y):
        """
        Atualiza item sob o mouse
        
        Args:
            x, y: Coordenadas do mouse (sistema OpenGL - Y crescendo para cima)
        """
        self.hovered_item = None
        
        if self.active_menu is not None:
            menu = self.menus[self.active_menu]
            dropdown_x, dropdown_y = self._get_dropdown_position(self.active_menu)
            dropdown_width = self._get_dropdown_width(self.active_menu)
            item_height = 25
            
            y_offset = 0
            for idx, item in enumerate(menu['items']):
                if item.get('separator'):
                    y_offset += 5
                    continue
                
                item_y_bottom = dropdown_y - y_offset - item_height
                item_y_top = dropdown_y - y_offset
                
                if (dropdown_x <= x < dropdown_x + dropdown_width and
                    item_y_bottom <= y < item_y_top):
                    self.hovered_item = idx
                    break
                
                y_offset += item_height
    
    def _get_dropdown_position(self, menu_index):
        """
        Calcula posição do dropdown (sistema OpenGL - Y crescendo para cima)
        
        Returns:
            Tupla (x, y) onde Y é a base do dropdown
        """
        menu_x = 10
        for i in range(menu_index):
            menu_x += self.menu_widths[i] + 5
        
        # Dropdown começa logo abaixo da barra de menu
        return menu_x, self.height - self.menu_height
    
    def _get_dropdown_width(self, menu_index):
        """
        Calcula largura do dropdown baseada no texto mais longo
        
        Returns:
            Largura em pixels
        """
        menu = self.menus[menu_index]
        max_text_width = 0
        for item in menu['items']:
            if not item.get('separator'):
                text_width = self.font.measure_text(item['label'], font_size=0.85)
                max_text_width = max(max_text_width, text_width)
        
        # Adiciona padding para checkbox e margens
        dropdown_width = max_text_width + 40  # 10 padding + 20 checkbox + 10 padding
        return max(dropdown_width, 150)  # Largura mínima
    
    def render(self):
        """Renderiza barra de menu"""
        # Configura projeção 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Desabilita depth test para UI
        glDisable(GL_DEPTH_TEST)
        
        # Aplica escala para corrigir aspect ratio da fonte
        # Salva estado da modelview para aplicar escala apenas no texto
        glPushMatrix()
        
        # Renderiza barra principal
        self._render_main_bar()
        
        # Renderiza dropdown se ativo
        if self.active_menu is not None:
            self._render_dropdown(self.active_menu)
        
        glPopMatrix()
        
        # Restaura estado
        glEnable(GL_DEPTH_TEST)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _render_main_bar(self):
        """Renderiza barra principal"""
        # Fundo
        glColor4f(0.2, 0.2, 0.2, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(0, self.height - self.menu_height)
        glVertex2f(self.width, self.height - self.menu_height)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # Linha inferior
        glColor4f(0.4, 0.4, 0.4, 1.0)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f(0, self.height - self.menu_height)
        glVertex2f(self.width, self.height - self.menu_height)
        glEnd()
        
        # Menus
        menu_x = 10
        for i, menu in enumerate(self.menus):
            menu_width = self.menu_widths[i]
            menu_y = self.height - self.menu_height
            
            # Fundo se ativo
            if i == self.active_menu:
                glColor4f(0.3, 0.3, 0.3, 1.0)
                glBegin(GL_QUADS)
                glVertex2f(menu_x, menu_y)
                glVertex2f(menu_x + menu_width, menu_y)
                glVertex2f(menu_x + menu_width, menu_y + self.menu_height)
                glVertex2f(menu_x, menu_y + self.menu_height)
                glEnd()
            
            # Desenha texto do menu com VectorFont
            text_x = menu_x + 10
            text_y = menu_y + self.menu_height // 2 - 6
            self.font.draw_text(text_x, text_y, menu['label'], 
                               color=(1.0, 1.0, 1.0), font_size=1.0)
            
            menu_x += menu_width + 5
    
    def _render_dropdown(self, menu_index):
        """Renderiza dropdown do menu (sistema OpenGL - Y crescendo para cima)"""
        menu = self.menus[menu_index]
        dropdown_x, dropdown_y = self._get_dropdown_position(menu_index)
        dropdown_width = self._get_dropdown_width(menu_index)
        item_height = 25
        
        # Calcula altura total
        total_height = 0
        for item in menu['items']:
            if item.get('separator'):
                total_height += 5
            else:
                total_height += item_height
        
        # Fundo do dropdown
        glColor4f(0.25, 0.25, 0.25, 0.98)
        glBegin(GL_QUADS)
        glVertex2f(dropdown_x, dropdown_y - total_height)
        glVertex2f(dropdown_x + dropdown_width, dropdown_y - total_height)
        glVertex2f(dropdown_x + dropdown_width, dropdown_y)
        glVertex2f(dropdown_x, dropdown_y)
        glEnd()
        
        # Borda
        glColor4f(0.4, 0.4, 0.4, 1.0)
        glLineWidth(1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(dropdown_x, dropdown_y - total_height)
        glVertex2f(dropdown_x + dropdown_width, dropdown_y - total_height)
        glVertex2f(dropdown_x + dropdown_width, dropdown_y)
        glVertex2f(dropdown_x, dropdown_y)
        glEnd()
        
        # Items
        y_offset = 0
        for idx, item in enumerate(menu['items']):
            if item.get('separator'):
                # Linha separadora
                sep_y = dropdown_y - y_offset - 2
                glColor4f(0.4, 0.4, 0.4, 1.0)
                glBegin(GL_LINES)
                glVertex2f(dropdown_x + 5, sep_y)
                glVertex2f(dropdown_x + dropdown_width - 5, sep_y)
                glEnd()
                y_offset += 5
                continue
            
            item_y_bottom = dropdown_y - y_offset - item_height
            item_y_top = dropdown_y - y_offset
            
            # Fundo se hover
            if self.hovered_item == idx:
                glColor4f(0.35, 0.35, 0.35, 1.0)
                glBegin(GL_QUADS)
                glVertex2f(dropdown_x, item_y_bottom)
                glVertex2f(dropdown_x + dropdown_width, item_y_bottom)
                glVertex2f(dropdown_x + dropdown_width, item_y_top)
                glVertex2f(dropdown_x, item_y_top)
                glEnd()
            
            # Se o item estiver marcado (checked), desenha um checkbox
            checkbox_offset = 0
            if item.get('checked'):
                glColor4f(0.8, 0.9, 0.3, 1.0)
                box_x = dropdown_x + 10
                box_y = item_y_bottom + item_height/2 - 6
                box_w = 12
                glBegin(GL_QUADS)
                glVertex2f(box_x, box_y)
                glVertex2f(box_x + box_w, box_y)
                glVertex2f(box_x + box_w, box_y + box_w)
                glVertex2f(box_x, box_y + box_w)
                glEnd()
                checkbox_offset = 20
            
            # Desenha texto do item com VectorFont
            text_x = dropdown_x + 10 + checkbox_offset
            text_y = item_y_bottom + item_height // 2 - 6
            self.font.draw_text(text_x, text_y, item['label'],
                               color=(1.0, 1.0, 1.0), font_size=0.85)
            
            y_offset += item_height
