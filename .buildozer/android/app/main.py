from kivy.app import App  # Importa a classe base para criar o aplicativo Kivy
from kivy.clock import Clock  # Permite agendar eventos no tempo
from kivy.uix.boxlayout import BoxLayout  # Layout de caixas (componentes em linhas ou colunas)
from kivy_garden.mapview import MapView, MapMarker  # Importa o mapa e marcadores da extensão Kivy Garden
from plyer import gps  # Usado para acessar o GPS do dispositivo (funciona principalmente em Android)


class MapaRoot(BoxLayout):
    pass


class MapaApp(App):  # Classe principal do aplicativo
    def build(self):
        return MapaRoot()  # Retorna o layout principal como a interface do app


    def on_start(self):  # Método executado automaticamente ao iniciar o app
        try:
            gps.configure(
                on_location=self.atualizar_localizacao,  # Define função chamada ao receber localização
                on_status=self.on_gps_status  # Define função chamada quando o status do GPS muda
            )
            gps.start(minTime=1000, minDistance=0)  # Inicia o GPS: atualiza a cada 1 segundo (1000ms), mesmo sem mover
        except NotImplementedError:
            print("GPS não suportado neste dispositivo.")  # Mostra erro caso o dispositivo não suporte o GPS


    def atualizar_localizacao(self, **kwargs):  # Função chamada quando nova localização é recebida
        lat = kwargs['lat']  # Latitude recebida
        lon = kwargs['lon']  # Longitude recebida
        print(f"Localização recebida: {lat}, {lon}")  # Imprime a localização no console


        mapview = self.root.ids.mapview  # Acessa o widget de mapa pelo id (definido no .kv)

        # Limpa marcadores antigos do mapa
        for child in list(mapview.children):
            if isinstance(child, MapMarker):
                mapview.remove_widget(child)

        mapview.center_on(lat, lon)  # Centraliza o mapa na nova localização

        mapker = MapMarker(lat=lat, lon=lon)  # Cria novo marcador na posição
        mapview.add_widget(mapker)  # Adiciona o marcador ao mapa


    def on_gps_status(self, stype, status):  # Função chamada quando o status do GPS muda
        print(f"GPS status: {stype} - {status}")  # Imprime o status


    def encerrar_app(self):  # Função para encerrar a aplicação
        print("Encerrando aplicativo...")
        self.stop()


if __name__ == '__main__':  # Verifica se o script está sendo executado diretamente
    MapaApp().run()  # Inicia o app
