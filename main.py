from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder
from kivy.core.window import Window

class MainApp(App):
    """

    Classe com o Aplicativo
    
    """

    def build(self):
        """
        
        Método que gera o aplicativo com no widget principal
        
        """
        self.widget = MainWidget()
        return self.widget

if __name__ == '__main__':
    Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True) # codificação da leitura dpara caracteres especiais
    Builder.load_string(open("popups.kv", encoding="utf-8").read(), rulesonly=True)
    Window.size = (800, 600)
    MainApp().run()