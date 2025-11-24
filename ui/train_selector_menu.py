"""
Menu de seleção de trem dentro da aplicação gráfica
Interface visual para escolher modelo e quantidade de vagões
"""

from OpenGL.GL import *
from ui.components import Button
import glfw


class TrainSelectorMenu:
    """Menu visual para seleção de trem"""
    
    def __init__(self, width, height, font):
        """
        Inicializa menu
        
        Args:
            width, height: Dimensões da tela
            font: VectorFont para renderizar texto
        """
        self.width = width
        self.height = height
        self.font = font
        self.active = False
        
        # Modelos disponíveis
        self.models = [
            'ES43', 'DASH BB', 'SD 40', 'GT', 'G22', 'UB',
            'U20', 'AC 44i', 'DASH 9', 'ES44', 'C30'
        ]
        
        self.selected_model = 'ES43'
        self.selected_vagons = 30
        self.selected_y_offset = 0.0  # Offset no eixo Y
        
        # Estado
        self.page = 0  # Página de modelos
        self.models_per_page = 6
        self.vagons_input = "30"
        self.y_offset_input = "0"
        self.confirming_stage = 0  # 0: modelo, 1: vagões, 2: offset Y
        self.confirming = False
        
        # Callbacks
        self.on_confirm_callback = None
        self.on_cancel_callback = None
    
    def open(self):
        """Abre o menu"""
        self.active = True
        self.page = 0
        self.confirming_stage = 0
        self.confirming = False
        self.vagons_input = str(self.selected_vagons)
        self.y_offset_input = str(self.selected_y_offset)
    
    def close(self):
        """Fecha o menu"""
        self.active = False
    
    def handle_key(self, key, action):
        """Processa entrada de teclado"""
        if not self.active:
            return False
        
        if action == glfw.PRESS:
            # ESC: Cancelar
            if key == glfw.KEY_ESCAPE:
                self.close()
                if self.on_cancel_callback:
                    self.on_cancel_callback()
                return True
            
            # TAB: Alternar entre seleção de modelo, vagões e offset Y
            elif key == glfw.KEY_TAB:
                self.confirming_stage = (self.confirming_stage + 1) % 3
                self.confirming = (self.confirming_stage > 0)
                return True
            
            # ENTER: Confirmar
            elif key == glfw.KEY_ENTER:
                if self.confirming_stage == 0:
                    # Confirma modelo, vai para vagões
                    self.confirming_stage = 1
                    self.confirming = True
                    return True
                elif self.confirming_stage == 1:
                    # Confirma vagões, vai para offset Y
                    try:
                        vagons = int(self.vagons_input)
                        if 1 <= vagons <= 100:
                            self.selected_vagons = vagons
                        else:
                            self.vagons_input = "1-100"
                            return True
                    except ValueError:
                        self.vagons_input = "Inválido"
                        return True
                    self.confirming_stage = 2
                    return True
                elif self.confirming_stage == 2:
                    # Confirma offset Y e finaliza
                    try:
                        y_offset = float(self.y_offset_input)
                        if -50 <= y_offset <= 50:
                            self.selected_y_offset = y_offset
                            self.close()
                            if self.on_confirm_callback:
                                self.on_confirm_callback(self.selected_model, self.selected_vagons, self.selected_y_offset)
                        else:
                            self.y_offset_input = "-50 a 50"
                    except ValueError:
                        self.y_offset_input = "Inválido"
                return True
            
            # Setas para navegar
            elif key == glfw.KEY_UP:
                if not self.confirming:
                    idx = self.models.index(self.selected_model)
                    idx = (idx - 1) % len(self.models)
                    self.selected_model = self.models[idx]
                    self.page = idx // self.models_per_page
                return True
            
            elif key == glfw.KEY_DOWN:
                if not self.confirming:
                    idx = self.models.index(self.selected_model)
                    idx = (idx + 1) % len(self.models)
                    self.selected_model = self.models[idx]
                    self.page = idx // self.models_per_page
                return True
            
            # Números para ajustar vagões ou offset Y
            elif glfw.KEY_0 <= key <= glfw.KEY_9 and self.confirming:
                digit = chr(ord('0') + (key - glfw.KEY_0))
                if self.confirming_stage == 1:  # Vagões
                    if self.vagons_input in ["0", "1-100", "Inválido"]:
                        self.vagons_input = digit
                    elif len(self.vagons_input) < 3:
                        self.vagons_input += digit
                elif self.confirming_stage == 2:  # Offset Y
                    if self.y_offset_input in ["0", "-50 a 50", "Inválido"]:
                        self.y_offset_input = digit
                    elif len(self.y_offset_input) < 5:
                        self.y_offset_input += digit
                return True
            
            # Sinal de menos para offset Y
            elif key == glfw.KEY_MINUS and self.confirming and self.confirming_stage == 2:
                if self.y_offset_input in ["0", "-50 a 50", "Inválido"]:
                    self.y_offset_input = "-"
                elif not self.y_offset_input.startswith("-") and len(self.y_offset_input) < 5:
                    self.y_offset_input = "-" + self.y_offset_input
                return True
            
            # Backspace para deletar
            elif key == glfw.KEY_BACKSPACE and self.confirming:
                if self.confirming_stage == 1:  # Vagões
                    if len(self.vagons_input) > 1:
                        self.vagons_input = self.vagons_input[:-1]
                    else:
                        self.vagons_input = "0"
                elif self.confirming_stage == 2:  # Offset Y
                    if len(self.y_offset_input) > 1:
                        self.y_offset_input = self.y_offset_input[:-1]
                    else:
                        self.y_offset_input = "0"
                return True
        
        return False
    
    def handle_click(self, x, y):
        """Processa clique do mouse"""
        if not self.active:
            return False
        
        menu_width = 600
        menu_height = 500
        menu_x = (self.width - menu_width) / 2
        menu_y = (self.height - menu_height) / 2
        
        # Verifica clique dentro do menu
        if not (menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height):
            return False
        
        # Botões de modelos
        button_y_start = menu_y + menu_height - 120
        for i in range(self.models_per_page):
            model_idx = self.page * self.models_per_page + i
            if model_idx >= len(self.models):
                break
            
            btn_x = menu_x + 20 + (i % 3) * 180
            btn_y = button_y_start - (i // 3) * 60
            btn_width = 160
            btn_height = 50
            
            if btn_x <= x <= btn_x + btn_width and btn_y <= y <= btn_y + btn_height:
                self.selected_model = self.models[model_idx]
                return True
        
        # Input de vagões
        vagons_y = button_y_start - 150
        input_x = menu_x + 20
        input_y = vagons_y - 60
        input_width = 200
        input_height = 40
        
        if input_x <= x <= input_x + input_width and input_y <= y <= input_y + input_height:
            self.confirming_stage = 1
            self.confirming = True
            return True
        
        # Input de offset Y
        offset_y = input_y - 90
        offset_input_x = menu_x + 20
        offset_input_y = offset_y - 60
        offset_input_width = 200
        offset_input_height = 40
        
        if offset_input_x <= x <= offset_input_x + offset_input_width and offset_input_y <= y <= offset_input_y + offset_input_height:
            self.confirming_stage = 2
            self.confirming = True
            return True
        
        # Botão confirmar
        confirm_x = menu_x + menu_width / 2 - 75
        confirm_y = menu_y + 30
        if confirm_x <= x <= confirm_x + 150 and confirm_y <= y <= confirm_y + 40:
            try:
                if self.confirming_stage == 0:
                    # Confirma modelo, avança para vagões
                    self.confirming_stage = 1
                    self.confirming = True
                elif self.confirming_stage == 1:
                    # Confirma vagões, avança para offset Y
                    vagons = int(self.vagons_input)
                    if 1 <= vagons <= 100:
                        self.selected_vagons = vagons
                        self.confirming_stage = 2
                elif self.confirming_stage == 2:
                    # Confirma offset Y, finaliza
                    y_offset = float(self.y_offset_input)
                    if -50 <= y_offset <= 50:
                        self.selected_y_offset = y_offset
                        self.close()
                        if self.on_confirm_callback:
                            self.on_confirm_callback(self.selected_model, self.selected_vagons, self.selected_y_offset)
            except ValueError:
                pass
            return True
        
        # Botão cancelar
        cancel_x = menu_x + 20
        cancel_y = menu_y + 30
        if cancel_x <= x <= cancel_x + 80 and cancel_y <= y <= cancel_y + 40:
            self.close()
            if self.on_cancel_callback:
                self.on_cancel_callback()
            return True
        
        return True
    
    def render(self):
        """Renderiza o menu"""
        if not self.active:
            return
        
        # Overlay semitransparente
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        glDisable(GL_BLEND)
        
        # Painel do menu
        menu_width = 600
        menu_height = 500
        menu_x = (self.width - menu_width) / 2
        menu_y = (self.height - menu_height) / 2
        
        # Fundo
        glColor4f(0.1, 0.1, 0.15, 0.95)
        glBegin(GL_QUADS)
        glVertex2f(menu_x, menu_y)
        glVertex2f(menu_x + menu_width, menu_y)
        glVertex2f(menu_x + menu_width, menu_y + menu_height)
        glVertex2f(menu_x, menu_y + menu_height)
        glEnd()
        
        # Borda
        glColor4f(0.5, 0.7, 1.0, 1.0)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(menu_x, menu_y)
        glVertex2f(menu_x + menu_width, menu_y)
        glVertex2f(menu_x + menu_width, menu_y + menu_height)
        glVertex2f(menu_x, menu_y + menu_height)
        glEnd()
        glLineWidth(1.0)
        
        # Título
        self.font.draw_text(
            menu_x + menu_width / 2 - 100,
            menu_y + menu_height - 40,
            "SELECIONE O TREM",
            color=(1, 1, 1),
            font_size=1.5
        )
        
        # Subtítulo
        self.font.draw_text(
            menu_x + 20,
            menu_y + menu_height - 70,
            "Modelos Disponíveis:",
            color=(0.8, 0.8, 0.8),
            font_size=0.9
        )
        
        # Botões de modelos
        button_y_start = menu_y + menu_height - 120
        for i in range(self.models_per_page):
            model_idx = self.page * self.models_per_page + i
            if model_idx >= len(self.models):
                break
            
            model_name = self.models[model_idx]
            btn_x = menu_x + 20 + (i % 3) * 180
            btn_y = button_y_start - (i // 3) * 60
            btn_width = 160
            btn_height = 50
            
            # Cor do botão
            if model_name == self.selected_model:
                glColor4f(0.2, 0.6, 1.0, 1.0)  # Azul para selecionado
            else:
                glColor4f(0.3, 0.3, 0.4, 1.0)  # Cinza para não selecionado
            
            # Desenha retângulo
            glBegin(GL_QUADS)
            glVertex2f(btn_x, btn_y)
            glVertex2f(btn_x + btn_width, btn_y)
            glVertex2f(btn_x + btn_width, btn_y + btn_height)
            glVertex2f(btn_x, btn_y + btn_height)
            glEnd()
            
            # Borda
            if model_name == self.selected_model:
                glColor4f(1.0, 1.0, 0.0, 1.0)  # Amarelo
                glLineWidth(3.0)
            else:
                glColor4f(0.6, 0.6, 0.6, 1.0)
                glLineWidth(1.0)
            
            glBegin(GL_LINE_LOOP)
            glVertex2f(btn_x, btn_y)
            glVertex2f(btn_x + btn_width, btn_y)
            glVertex2f(btn_x + btn_width, btn_y + btn_height)
            glVertex2f(btn_x, btn_y + btn_height)
            glEnd()
            glLineWidth(1.0)
            
            # Texto
            self.font.draw_text(
                btn_x + 10,
                btn_y + btn_height / 2 - 5,
                model_name,
                color=(1, 1, 1),
                font_size=0.8
            )
        
        # Seção de vagões
        vagons_y = button_y_start - 150
        self.font.draw_text(
            menu_x + 20,
            vagons_y,
            "Vagões de Minério:",
            color=(0.8, 0.8, 0.8),
            font_size=0.9
        )
        
        # Input de vagões
        input_x = menu_x + 20
        input_y = vagons_y - 60
        input_width = 200
        input_height = 40
        
        # Cor do input
        if self.confirming:
            glColor4f(0.2, 0.4, 0.8, 1.0)
            border_color = (1.0, 1.0, 0.0)
        else:
            glColor4f(0.3, 0.3, 0.4, 1.0)
            border_color = (0.6, 0.6, 0.6)
        
        glBegin(GL_QUADS)
        glVertex2f(input_x, input_y)
        glVertex2f(input_x + input_width, input_y)
        glVertex2f(input_x + input_width, input_y + input_height)
        glVertex2f(input_x, input_y + input_height)
        glEnd()
        
        glColor4f(*border_color, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(input_x, input_y)
        glVertex2f(input_x + input_width, input_y)
        glVertex2f(input_x + input_width, input_y + input_height)
        glVertex2f(input_x, input_y + input_height)
        glEnd()
        glLineWidth(1.0)
        
        # Texto do input
        self.font.draw_text(
            input_x + 10,
            input_y + input_height / 2 - 5,
            self.vagons_input,
            color=(1, 1, 1),
            font_size=1.0
        )
        
        # Seção de offset Y
        offset_y = input_y - 90
        self.font.draw_text(
            menu_x + 20,
            offset_y,
            "Posição Y (m):",
            color=(0.8, 0.8, 0.8),
            font_size=0.9
        )
        
        # Input de offset Y
        offset_input_x = menu_x + 20
        offset_input_y = offset_y - 60
        offset_input_width = 200
        offset_input_height = 40
        
        # Cor do input de offset
        if self.confirming_stage == 2:
            glColor4f(0.2, 0.4, 0.8, 1.0)
            offset_border_color = (1.0, 1.0, 0.0)
        else:
            glColor4f(0.3, 0.3, 0.4, 1.0)
            offset_border_color = (0.6, 0.6, 0.6)
        
        glBegin(GL_QUADS)
        glVertex2f(offset_input_x, offset_input_y)
        glVertex2f(offset_input_x + offset_input_width, offset_input_y)
        glVertex2f(offset_input_x + offset_input_width, offset_input_y + offset_input_height)
        glVertex2f(offset_input_x, offset_input_y + offset_input_height)
        glEnd()
        
        glColor4f(*offset_border_color, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(offset_input_x, offset_input_y)
        glVertex2f(offset_input_x + offset_input_width, offset_input_y)
        glVertex2f(offset_input_x + offset_input_width, offset_input_y + offset_input_height)
        glVertex2f(offset_input_x, offset_input_y + offset_input_height)
        glEnd()
        glLineWidth(1.0)
        
        # Texto do input de offset
        self.font.draw_text(
            offset_input_x + 10,
            offset_input_y + offset_input_height / 2 - 5,
            self.y_offset_input,
            color=(1, 1, 1),
            font_size=1.0
        )
        
        # Botões de ação
        btn_height = 40
        btn_width = 80
        confirm_x = menu_x + menu_width / 2 - btn_width / 2 - 50
        cancel_x = menu_x + menu_width / 2 - btn_width / 2 + 50
        btn_y = menu_y + 30
        
        # Botão Cancelar
        glColor4f(0.6, 0.2, 0.2, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(cancel_x, btn_y)
        glVertex2f(cancel_x + btn_width, btn_y)
        glVertex2f(cancel_x + btn_width, btn_y + btn_height)
        glVertex2f(cancel_x, btn_y + btn_height)
        glEnd()
        
        glColor4f(1, 1, 1, 1)
        self.font.draw_text(
            cancel_x + 10,
            btn_y + btn_height / 2 - 5,
            "Cancelar",
            color=(1, 1, 1),
            font_size=0.8
        )
        
        # Botão Confirmar
        glColor4f(0.2, 0.6, 0.2, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(confirm_x, btn_y)
        glVertex2f(confirm_x + btn_width, btn_y)
        glVertex2f(confirm_x + btn_width, btn_y + btn_height)
        glVertex2f(confirm_x, btn_y + btn_height)
        glEnd()
        
        glColor4f(1, 1, 1, 1)
        self.font.draw_text(
            confirm_x + 10,
            btn_y + btn_height / 2 - 5,
            "Confirmar",
            color=(1, 1, 1),
            font_size=0.8
        )
        
        # Instruções
        self.font.draw_text(
            menu_x + 20,
            menu_y + menu_height - 480,
            "Setas: Selecionar | TAB: Próximo | ENTER: Confirmar | ESC: Cancelar",
            color=(0.6, 0.8, 1.0),
            font_size=0.7
        )
