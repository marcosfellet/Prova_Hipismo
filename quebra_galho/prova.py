import threading
import time
import os
import csv
from datetime import datetime
from pathlib import Path
import numpy as np

class Aluno():
    def __init__(self, metragem, velocidade):
        self._tempo = float(self.get_tempo())
        self._parametros = Paramentros_prova(metragem, velocidade)
        # self._ordem_entrada = Ordem_de_Entrada()
        # self._arquivo_entrada = self._ordem_entrada.importar_ultimo_csv()
        self._tempo_concedido = self._parametros.tempo_concedido
        self._tempo_ideal = self._parametros.tempo_ideal
        self._tempo_limite = self._parametros.tempo_limite
        self._output_faltas = self.get_faltas()
        self._faltas = int(self._output_faltas[0])
        self._obstaculos = self._output_faltas[1].split(',')
        self._penalidade_tempo = self.get_faltas_tempo()
        self._pontuacao = self.pontuacao()

    def get_tempo(self):
        return input('Digite --- COM PONTO COMO SEPARADOR DECIMAL --- o tempo (s) : ')
    
    def get_faltas(self):
        lista = []
        lista[0] = input('Digite o número de faltas: ')
        lista[1] = input('Digite o número de cada obstáculo cuja falta foi feita (usar 1,2,3 para obstaculos 1, 2 e 3, por exemplo): ')
        return lista
    

    
    def get_faltas_tempo(self):
        """
        Método para calcular a penalidade por tempo
        """
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

        return self._penalidade_tempo
    
    def pontuacao(self):
        """
        Método para calcular pontuação
        """
        return np.abs(self._tempo - self._tempo_ideal) + self._faltas*4 + self._penalidade_tempo #pontuacao

    


class Paramentros_prova():
    def __init__(self, metragem=0, velocidade=0):
        self._metragem = float(metragem)
        self._velocidade = float(velocidade)
        self._tempo_concedido = self.calcula_TC() 
        self._tempo_ideal = self.calcula_TI()      
        self._tempo_limite = self.calcula_TL()  

    def calcula_TI(self) -> float:
        """Calcula tempo ideal (95% do tempo concedido)"""
        return round(self._tempo_concedido * 0.95, 0)

    def calcula_TC(self) -> float:
        """Calcula tempo concedido"""
        return round((self._metragem * 60) / self._velocidade, 0)

    def calcula_TL(self) -> float:
        """Calcula tempo limite (tempo ideal - 3)"""
        
        return self._tempo_ideal - 3

    # Propriedades para acesso controlado
    @property
    def tempo_concedido(self):
        return self._tempo_concedido

    @property
    def tempo_ideal(self):
        return self._tempo_ideal
    
    @property
    def tempo_limite(self):
        return self._tempo_limite

class Ordem_de_Entrada:
    def __init__(self):
        self._caminho = Path('./Arquivo_Competidores')
        self._dados = None
        self._arquivo_entrada = self.importar_ultimo_csv()
    
    def importar_ultimo_csv(self):
        """Encontra e importa o arquivo CSV mais recente"""
        # Verificar se pasta existe
        if not self._caminho.exists():
            print(f"Pasta não encontrada: {self._caminho}")
            return None
        
        # Listar arquivos CSV
        arquivos_csv = list(self._caminho.glob("*.csv"))
        
        if not arquivos_csv:
            print("Nenhum arquivo CSV encontrado")
            return None
        
        # Encontrar o mais recente
        ultimo_csv = max(arquivos_csv, key=lambda f: f.stat().st_mtime)
        
        # Importar dados
        try:
            with open(ultimo_csv, 'r', encoding='utf-8') as f:
                leitor = csv.DictReader(f)
                self._dados = list(leitor)
            return self._dados
            
        except Exception as e:
            print(f"Erro: {e}")
            return None