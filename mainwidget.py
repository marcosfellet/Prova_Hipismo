from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from typing import Optional, List, Dict, Any
from kivy.uix.widget import Widget
import os
import numpy as np

from popups import(
    ParametrosPopup, ObstaculosPopup
)

class AlunoInput(BoxLayout):
    """
    Widget personalizado para representar um aluno
    """
    
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
            if texto and self._validar_tempo(float(texto)):
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

    def calcula_resultados(self):
         #Método para calcular pontuação

        self._tempo = self._get_tempo()
        self._tempo_concedido = self.calcula_TC()
        self._tempo_ideal = self.calcula_TI()
        self._faltas = int(self.ids.faltas)
        self._tempo_limite = self.calcula_TL()

        self._diferenca_tempo = np.abs(self._tempo - self._tempo_concedido)
        self._diferenca_tempo_limite = np.abs(self._tempo - self._tempo_limite)
        if self._tempo == self._tempo_concedido:
            self._penalidade_tempo = 1
        elif self._tempo < self._tempo_limite or self._tempo >= self._tempo_concedido:
            if self._diferenca_tempo >= 0.01:
                self._penalidade_tempo = round(self._diferenca_tempo, 0)
                if round(self._diferenca_tempo, 0) == 0:
                    self._penalidade_tempo = 1
            elif self._diferenca_tempo_limite >= 0.01:
                self._penalidade_tempo = round(self._diferenca_tempo_limite, 0)
                if round(self._diferenca_tempo_limite, 0) == 0:
                    self._penalidade_tempo = 1
        elif self._tempo == self._tempo_concedido:
            self._penalidade_tempo = 1

        # elif (self._tempo - self._tempo_limite) == -0.01:
        #     self._penalidade_tempo = 1

        self._pontucao = np.abs(self._tempo - self._tempo_ideal) + self._faltas*4 + self._penalidade_tempo

        return self._pontucao
    

    def calcula_TI(self, tempo_concedido):
        
        #Método para calcular tempo ideal
        
        self._tempo_ideal = round(tempo_concedido *0.95, 0) #ja arredondando para 0 casas decimais
        return self._tempo_ideal

    def calcula_TC(self):
        
        #Método para calcular tempo concedido
       
        ############################## PEGAR DO TEXTINPUT
        self._pista = self.ids.pista.text()
        self._velocidade = self.ids.velocidade.text()
        self._tempo_concedido = round((self._pista*60)/self._velocidade, 0) #ja arredondando para 0 casas decimais
        return self._tempo_concedido

    def calcula_TL(self):
        
        #Método para calcular tempo limite
        
        self._tempo_ideal = self.calcula_TI()
        self._tempo_limite = self._tempo_ideal - 3
        return self._tempo_limite

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
        
    def abrir_popup_parametros(self):
        """Abre o popup de parâmetros"""
        self.popup = ParametrosPopup()
        self.popup.open()
    
    def pegar_valores_do_popup(self):
        """Pega os valores do popup após fechado"""
        if hasattr(self, 'popup'):
            pista, velocidade = self.popup.get_valores()
            if pista is not None and velocidade is not None:
                print(f"Pista: {pista}m, Velocidade: {velocidade}m/s")
                # Agora você pode usar os valores no main.py
                self.calcular_tempo_concedido(pista, velocidade)
            else:
                print("Valores inválidos no popup")
    
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
    
    def atualizar_altura(self, **kwargs):
        """Atualiza a altura do grid baseado no número de alunos"""
        self.height = len(self.alunos) * 50 + self.padding[0] * 2

    




    """
    def calcular_estatisticas(self) -> Optional[Dict[str, Any]]:
        #Calcula estatísticas dos tempos
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
    """



"""
class MainWidget(BoxLayout):
    #Widget principal da aplicação

    # Propriedades para ajudar na referência
    alunos_grid = ObjectProperty(None)  # Referência para o grid pai
    def __init__(self, alunos_grid=None, **kwargs):
       # Construtor da classe MainWidget
        
        super().__init__(**kwargs)
        self.alunos_grid = alunos_grid
    
    def remover_aluno(self):
        #Remove este aluno da lista
       
        if self.alunos_grid:
            self.alunos_grid.remover_aluno(self)

    def updateGUI(self):
        
        #Método para a atualização da interface gráfica a partir dos dados lidos
        

    def guardar_dados(self):
        
       # Método para guardar dados na tabela
        

    def calcula_TI(self, tempo_concedido):
        
        #Método para calcular tempo ideal
        
        self._tempo_concedido = tempo_concedido
        self._tempo_ideal = round(self._tempo_concedido *0.95, 0) #ja arredondando para 0 casas decimais
        return self._tempo_ideal

    def calcula_TC(self, pista, velocidade):
        
        #Método para calcular tempo concedido
       
        ############################## PEGAR DO TEXTINPUT
        self._pista = pista
        self._velocidade = velocidade
        self._tempo_concedido = round((self._pista*60)/self._velocidade, 0) #ja arredondando para 0 casas decimais
        return self._tempo_concedido

    def calcula_TL(self):
        
        #Método para calcular tempo limite
        
        self._tempo_ideal = self.calcula_TI()
        self._tempo_limite = self._tempo_ideal - 3
        return self._tempo_limite

    def pontuacao(self, tempo):
        
        #Método para calcular pontuação
        
        self._tempo = tempo
        self._tempo_concedido = self.calcula_TC()
        self._tempo_ideal = self.calcula_TI()
        self._faltas = int(self.ids.faltas)
        self._tempo_limite = self.calcula_TL()

        self._diferenca_tempo = np.abs(self._tempo - self._tempo_concedido)
        self._diferenca_tempo_limite = np.abs(self._tempo - self._tempo_limite)
        if self._tempo == self._tempo_concedido:
            self._penalidade_tempo = 1
        elif self._tempo < self._tempo_limite or self._tempo >= self._tempo_concedido:
            if self._diferenca_tempo >= 0.01:
                self._penalidade_tempo = round(self._diferenca_tempo, 0)
                if round(self._diferenca_tempo, 0) == 0:
                    self._penalidade_tempo = 1
            elif self._diferenca_tempo_limite >= 0.01:
                self._penalidade_tempo = round(self._diferenca_tempo_limite, 0)
                if round(self._diferenca_tempo_limite, 0) == 0:
                    self._penalidade_tempo = 1
        elif self._tempo == self._tempo_concedido:
            self._penalidade_tempo = 1

        # elif (self._tempo - self._tempo_limite) == -0.01:
        #     self._penalidade_tempo = 1

        self._pontucao = np.abs(self._tempo - self._tempo_ideal) + self._faltas*4 + self._penalidade_tempo

        return self._pontucao
"""

