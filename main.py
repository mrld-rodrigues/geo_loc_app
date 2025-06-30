from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView, MapMarker
from plyer import gps


class MapaRoot(BoxLayout):
    pass


class MapaApp(App):
    def build(self):
        return MapaRoot()

    def on_start(self):
        try:
            gps.configure(
                on_location=self.atualizar_localizacao,
                on_status=self.on_gps_status
            )
            # Inicia o GPS após 1 segundo (para garantir que o app está carregado)
            Clock.schedule_once(lambda dt: gps.start(minTime=1000, minDistance=0), 1)
        except NotImplementedError:
            print("GPS não suportado neste dispositivo.")

    def atualizar_localizacao(self, **kwargs):
        lat = float(kwargs.get('lat', 0))
        lon = float(kwargs.get('lon', 0))
        print(f"Localização recebida: {lat}, {lon}")

        mapview = self.root.ids.mapview

        # Atualiza texto da localização se o Label existir
        if "coordenadas" in self.root.ids:
            self.root.ids.coordenadas.text = f"Localização: {lat:.5f}, {lon:.5f}"

        # Limpa os marcadores antigos e adiciona novo
        mapview.clear_widgets()
        marker = MapMarker(lat=lat, lon=lon)
        mapview.add_marker(marker)

        # Centraliza no marcador
        mapview.center_on(lat, lon)

    def on_gps_status(self, stype, status):
        print(f"GPS status: {stype} - {status}")

    def encerrar_app(self):
        print("Encerrando aplicativo...")
        self.stop()


if __name__ == '__main__':
    MapaApp().run()
