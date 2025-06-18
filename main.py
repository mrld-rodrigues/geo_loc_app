from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.mapview import MapView, MapMarker

class MapaRoot(BoxLayout):
    pass

class MapaApp(App):
    def build(self):         
        return MapaRoot()

    def mostrar_local(self):
        root = self.root
        try:
            lat = float(root.ids.lat_input.text)
            lon = float(root.ids.lon_input.text)
            mapview = root.ids.mapview

            # Limpa marcadores antigos
            for child in list(mapview.children):
                if isinstance(child, MapMarker):
                    mapview.remove_widget(child)

            # Centraliza e adiciona novo marcador
            mapview.center_on(lat, lon)
            marker = MapMarker(lat=lat, lon=lon)
            mapview.add_widget(marker)

            print(f"Marcador adicionado em {lat}, {lon}")

        except ValueError:
            print("Erro: latitude e longitude inválidas")

if __name__ == '__main__':
    MapaApp().run()
