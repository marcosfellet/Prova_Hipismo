from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import  ObjectProperty, StringProperty


class ParametrosPopup(Popup):
    # Callback para quando confirmar
    on_confirmar = ObjectProperty(lambda pista, vel: None)
    
    def confirmar(self):
        try:
            pista = float(self.ids.txt_pista.text)
            velocidade = float(self.ids.txt_velocidade.text)
            
            if pista <= 0:
                ErroPopup("Comprimento da pista deve ser positivo.").open()
                return
            
            if velocidade <= 0:
                ErroPopup("Velocidade deve ser positiva.").open()
                return
            
            self.on_confirmar(pista, velocidade)
            self.dismiss()
            
        except ValueError:
            ErroPopup("Digite valores válidos.").open()
    
    def cancelar(self):
        """Chamado quando o usuário cancela"""
        self.dismiss()

class ObstaculosPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 5
        self.padding = 10
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

class ErroPopup(Popup):
    mensagem = StringProperty("Erro!")
    
    def __init__(self, mensagem="Erro!", **kwargs):
        super().__init__(**kwargs)
        self.mensagem = mensagem