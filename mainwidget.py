from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
import os
from typing import Optional, List, Dict, Any

# Configurar tamanho da janela (opcional)
Window.size = (800, 600)


class AlunoInput(BoxLayout):
    """Widget personalizado para representar um aluno"""
    
    alunos_grid = ObjectProperty(None)
    carregou_imagem = BooleanProperty(False)
    
    def __init__(self, alunos_grid=None, **kwargs):
        super().__init__(**kwargs)
        self.alunos_grid = alunos_grid
        
        # Verifica se a imagem existe
        imagem_path = 'images/lixeira.png'
        if os.path.exists(imagem_path):
            self.carregou_imagem = True
    
    def remover_aluno(self):
        """Remove este aluno da lista"""
        if self.alunos_grid:
            self.alunos_grid.remover_aluno(self)
    
    def get_tempo(self) -> Optional[float]:
        """Retorna o tempo como float, ou None se inválido"""
        try:
            texto = self.ids.tempo_input.text.strip()
            if texto:
                return float(texto)
            return None
        except ValueError:
            return None
    
    def validar_tempo(self) -> bool:
        """Valida se o tempo é um número positivo"""
        tempo = self.get_tempo()
        if tempo is None or tempo <= 0:
            self.ids.tempo_input.background_color = (1, 0.8, 0.8, 1)
            return False
        else:
            self.ids.tempo_input.background_color = (1, 1, 1, 1)
            return True
    
    def validar_tempo_ao_digitar(self):
        """Valida o tempo enquanto o usuário digita"""
        self.validar_tempo()
    
    def validar_nome(self) -> bool:
        """Valida se o nome foi preenchido"""
        if not self.ids.nome_input.text.strip():
            self.ids.nome_input.background_color = (1, 0.8, 0.8, 1)
            return False
        else:
            self.ids.nome_input.background_color = (1, 1, 1, 1)
            return True
    
    def validar_nome_ao_digitar(self):
        """Valida o nome enquanto o usuário digita"""
        self.validar_nome()


class AlunosGrid(GridLayout):
    """Grid principal que contém todos os alunos"""
    
    alunos = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 5
        self.padding = 10
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
    
    def adicionar_aluno(self):
        """Adiciona um novo aluno à grade"""
        novo_aluno = AlunoInput(alunos_grid=self)
        self.alunos.append(novo_aluno)
        self.add_widget(novo_aluno)
        self.atualizar_altura()
    
    def remover_aluno(self, aluno_widget: AlunoInput):
        """Remove um aluno da grade"""
        if aluno_widget in self.alunos:
            self.alunos.remove(aluno_widget)
            self.remove_widget(aluno_widget)
            self.atualizar_altura()
    
    def atualizar_altura(self, *args):
        """Atualiza a altura do grid baseado no número de alunos"""
        self.height = len(self.alunos) * 50 + self.padding[0] * 2
    
    def calcular_estatisticas(self) -> Optional[Dict[str, Any]]:
        """Calcula estatísticas dos tempos"""
        tempos = []
        resultados = []
        
        for aluno in self.alunos:
            nome_valido = aluno.validar_nome()
            tempo_valido = aluno.validar_tempo()
            
            if nome_valido and tempo_valido:
                tempo = aluno.get_tempo()
                if tempo is not None:
                    tempos.append(tempo)
                    resultados.append({
                        'nome': aluno.ids.nome_input.text.strip(),
                        'montaria': aluno.ids.montaria_input.text.strip() or "Sem montaria",
                        'tempo': tempo
                    })
        
        if tempos:
            return {
                'resultados': resultados,
                'media': sum(tempos) / len(tempos),
                'menor': min(tempos),
                'maior': max(tempos),
                'total_alunos': len(tempos)
            }
        return None


class MainWidget(BoxLayout):
    """Tela principal do aplicativo"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Carrega o arquivo KV
        Builder.load_file('main.kv')
    
    def adicionar_aluno(self):
        """Adiciona um novo aluno"""
        self.ids.grid_alunos.adicionar_aluno()
    
    