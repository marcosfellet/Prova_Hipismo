from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from typing import Optional, List, Dict, Any
# Para ajudar o Pylance a reconhecer os tipos
from kivy.uix.widget import Widget
import numpy as np


class MainWidget(BoxLayout):
    """
    Widget principal da aplicação
    """
    # Propriedades para ajudar na referência
    alunos_grid = ObjectProperty(None)  # Referência para o grid pai
    def __init__(self, alunos_grid=None, **kwargs):
        """
        Construtor da classe MainWidget
        """
        super().__init__(**kwargs)
        self.alunos_grid = alunos_grid
    
    def remover_aluno(self):
        """Remove este aluno da lista"""
        if self.alunos_grid:
            self.alunos_grid.remover_aluno(self)

    def updateGUI(self):
        '''
        Método para a atualização da interface gráfica a partir dos dados lidos
        '''

    def guardar_dados(self):
        """
        Método para guardar dados na tabela
        """

    def calcula_TI(self, tempo_concedido):
        """
        Método para calcular tempo ideal
        """
        self._tempo_concedido = tempo_concedido
        self._tempo_ideal = round(self._tempo_concedido *0.95, 0) #ja arredondando para 0 casas decimais
        return self._tempo_ideal

    def calcula_TC(self, pista, velocidade):
        """
        Método para calcular tempo concedido
        """
        ############################## PEGAR DO TEXTINPUT
        self._pista = pista
        self._velocidade = velocidade
        self._tempo_concedido = round((self._pista*60)/self._velocidade, 0) #ja arredondando para 0 casas decimais
        return self._tempo_concedido

    def calcula_TL(self):
        """
        Método para calcular tempo limite
        """
        self._tempo_ideal = self.calcula_TI()
        self._tempo_limite = self._tempo_ideal - 3
        return self._tempo_limite

    def pontuacao(self, tempo):
        """
        Método para calcular pontuação
        """
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

