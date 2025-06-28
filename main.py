from kivy.app import App  # Classe base do Kivy para criar o aplicativo
from kivy.clock import Clock  # Permite agendar ações no tempo (não usamos diretamente aqui)
from kivy.uix.boxlayout import BoxLayout  # Layout de organização vertical ou horizontal
from kivy_garden.mapview import MapView, MapMarker  # Importa mapa e marcadores do Kivy Garden
from plyer import gps  # Biblioteca para acessar sensores do dispositivo, como o GPS
from kivy.utils import platform  # Verifica a plataforma (Android, iOS, etc.)

# Importa permissões do Android caso o app esteja sendo executado no Android

if platform == 'android':
    from android.permissions import request_permissions, Permission


# Classe que representa o layout principal do app. Herda de BoxLayout
class MapaRoot(BoxLayout):
    pass  # O layout é definido no arquivo .kv, então não precisa adicionar nada aqui


# Classe principal do aplicativo
class MapaApp(App):

    def build(self):
        # Cria e retorna o layout principal do app (MapRoot, definido no .kv)
        return MapaRoot()

    def on_start(self):
        """
        Método chamado automaticamente quando o app inicia.
        Aqui é onde pedimos permissão para usar o GPS (no Android).
        """
        print("App iniciado.")

        # Verifica se está rodando no Android
        def on_start(self):
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])


                # Solicita permissão para acessar a localização precisa
                request_permissions([Permission.ACCESS_FINE_LOCATION], self.iniciar_gps)
            else:
                # Se não for Android (ex: PC), apenas inicia o GPS diretamente
                self.iniciar_gps()

    def iniciar_gps(self, permissions=None, results=None):
        """
        Esta função só é chamada após o usuário conceder (ou negar) permissão.
        """
        try:
            # Configura o GPS para chamar funções de localização e status
            gps.configure(
                on_location=self.atualizar_localizacao,  # Chamada quando nova localização é recebida
                on_status=self.on_gps_status  # Chamada quando o status do GPS muda
            )

            # Inicia o GPS: atualiza a cada 1 segundo (1000 ms), mesmo que o dispositivo não se mova
            gps.start(minTime=1000, minDistance=0)
            print("GPS iniciado. Aguardando localização...")
        except NotImplementedError:
            # Se o GPS não for suportado (por exemplo, em um desktop), mostra mensagem
            print("GPS não suportado neste dispositivo.")

    def atualizar_localizacao(self, **kwargs):
        """
        Função chamada automaticamente quando uma nova localização é recebida do GPS.
        """
        lat = kwargs['lat']  # Latitude recebida
        lon = kwargs['lon']  # Longitude recebida
        print(f"Localização recebida: {lat}, {lon}")  # Mostra no console para depuração

        # Acessa o widget MapView definido no arquivo .kv via ID
        mapview = self.root.ids.mapview

        # Remove todos os marcadores antigos (para deixar só o atual)
        for child in list(mapview.children):
            if isinstance(child, MapMarker):
                mapview.remove_widget(child)

        # Centraliza o mapa na nova posição do GPS
        mapview.center_on(lat, lon)

        # Cria e adiciona um novo marcador na localização atual
        marcador = MapMarker(lat=lat, lon=lon)
        mapview.add_widget(marcador)

    def on_gps_status(self, stype, status):
        """
        Função chamada sempre que o status do GPS muda.
        Pode mostrar mensagens como "GPS ligado", "sem sinal", etc.
        """
        print(f"GPS status: {stype} - {status}")

    def encerrar_app(self):
        """
        Encerra o aplicativo (é chamada ao apertar o botão X no layout).
        """
        print("Encerrando aplicativo...")
        self.stop()  # Método do Kivy para fechar o app


# Execução principal do app
if __name__ == '__main__':
    MapaApp().run()  # Inicia o loop principal do aplicativo
