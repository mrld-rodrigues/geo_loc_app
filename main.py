# Importa a classe base do aplicativo Kivy
from kivy.app import App

# Importa Clock para agendar tarefas (como iniciar o GPS após 1 segundo)
from kivy.clock import Clock

# Importa BoxLayout, que será o layout raiz do app
from kivy.uix.boxlayout import BoxLayout

# Importa o MapView (mapa interativo) e MapMarker (marcador no mapa) da extensão kivy_garden.mapview
from kivy_garden.mapview import MapView, MapMarker

# Importa o módulo GPS do plyer (biblioteca multiplataforma para acessar hardware)
from plyer import gps


# Classe do layout principal. Está vazia aqui, mas espera-se que esteja definida no .kv file (interface)
class MapaRoot(BoxLayout):
    pass


# Classe principal da aplicação
class MapaApp(App):

    # Método chamado quando o app é construído
    def build(self):
        return MapaRoot()  # Retorna o layout raiz

    # Método chamado ao iniciar o app
    def on_start(self):
        try:
            # Configura o GPS para chamar funções de localização e status
            gps.configure(
                on_location=self.atualizar_localizacao,  # Função chamada quando a localização muda
                on_status=self.on_gps_status              # Função chamada quando o status do GPS muda
            )

            # Aguarda 1 segundo antes de iniciar o GPS (permite que o app termine de carregar)
            Clock.schedule_once(lambda dt: gps.start(minTime=1000, minDistance=0), 1)

        except NotImplementedError:
            # Caso o dispositivo não suporte GPS, exibe mensagem
            print("GPS não suportado neste dispositivo.")


    # Função chamada quando uma nova localização é recebida
    def atualizar_localizacao(self, **kwargs):
        # Extrai latitude e longitude dos dados recebidos (ou usa 0 como padrão)
        lat = float(kwargs.get('lat', 0))
        lon = float(kwargs.get('lon', 0))

        print(f"Localização recebida: {lat}, {lon}")

        # Acessa o widget MapView via id definido no .kv
        mapview = self.root.ids.mapview

        # Atualiza um Label com as coordenadas, se ele existir no layout
        if "coordenadas" in self.root.ids:
            self.root.ids.coordenadas.text = f"Localização: {lat:.5f}, {lon:.5f}"

        # Limpa marcadores anteriores do mapa
        mapview.clear_widgets()

        # Cria um novo marcador na localização atual
        marker = MapMarker(lat=lat, lon=lon)
        mapview.add_marker(marker)

        # Centraliza o mapa na nova posição
        mapview.center_on(lat, lon)


    # Função chamada quando o status do GPS muda (ligado, desligado, etc.)
    def on_gps_status(self, stype, status):
        print(f"GPS status: {stype} - {status}")


    # Função para encerrar o aplicativo (pode ser chamada por um botão)
    def encerrar_app(self):
        print("Encerrando aplicativo...")
        self.stop()


# Ponto de entrada principal do app
if __name__ == '__main__':
    MapaApp().run()
