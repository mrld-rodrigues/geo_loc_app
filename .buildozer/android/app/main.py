# Importa a classe base do aplicativo Kivy
from kivy.app import App

# Importa Clock para agendar tarefas (como iniciar o GPS após 1 segundo)
from kivy.clock import Clock

# Importa BoxLayout, que será o layout raiz do app
from kivy.uix.boxlayout import BoxLayout

# Importa o MapView (mapa interativo) e MapMarker (marcador no mapa) da extensão kivy_garden.mapview
from kivy_garden.mapview import MapView, MapMarker

# Importa Popup e Label para exibir mensagens de erro
from kivy.uix.popup import Popup
from kivy.uix.label import Label

# Pyjnius imports for Android GPS
from kivy.utils import platform
if platform == 'android':
    from jnius import autoclass, PythonJavaClass, java_method, cast
    from android.runnable import run_on_ui_thread  # type: ignore

# Classe do layout principal. Está vazia aqui, mas espera-se que esteja definida no .kv file (interface)
class MainRoot(BoxLayout):
    pass

class GPSListener(PythonJavaClass):
    __javainterfaces__ = ['android/location/LocationListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        lat = location.getLatitude()
        lon = location.getLongitude()
        self.callback(lat, lon)

    @java_method('(Ljava/util/List;)V')
    def onLocationChanged(self, locations):
        # Handle batched location updates (Android 12+)
        if locations is not None and locations.size() > 0:
            location = locations.get(0)
            lat = location.getLatitude()
            lon = location.getLongitude()
            self.callback(lat, lon)

    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, provider):
        pass

    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, provider):
        pass

    @java_method('(Ljava/lang/String;ILandroid/os/Bundle;)V')
    def onStatusChanged(self, provider, status, extras):
        pass

class GeoApp(App):

    def build(self):
        from kivy.lang import Builder

        Builder.load_file("mapa.kv")
        return MainRoot()  # Retorna o layout raiz

    def on_start(self):
        if platform == 'android':
            # Request permissions at runtime
            from android.permissions import request_permissions, Permission, check_permission
            if (not check_permission(Permission.ACCESS_FINE_LOCATION)
                or not check_permission(Permission.ACCESS_COARSE_LOCATION)):
                def callback(permissions, results):
                    if all(results):
                        self.start_android_gps()
                    else:
                        self.show_popup("Location permission denied. App cannot function.")
                request_permissions(
                    [Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION],
                    callback
                )
            else:
                self.start_android_gps()
        else:
            self.show_popup("GPS only works on Android device.")

    # Ensure this runs on the Android UI thread
    if platform == 'android':
        @run_on_ui_thread
        def start_android_gps(self):
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            LocationManager = autoclass('android.location.LocationManager')
            activity = PythonActivity.mActivity
            self.location_manager = activity.getSystemService(Context.LOCATION_SERVICE)
            provider = self.location_manager.GPS_PROVIDER
            self.gps_listener = GPSListener(self.update_location_from_android)
            # Request location updates (minTime=1000ms, minDistance=0m)
            self.location_manager.requestLocationUpdates(provider, 1000, 0, self.gps_listener)
    else:
        def start_android_gps(self):
            pass

    def update_location_from_android(self, lat, lon):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.update_location(lat=lat, lon=lon))

    def update_location(self, **kwargs):
        lat = float(kwargs.get('lat', 0))
        lon = float(kwargs.get('lon', 0))

        # Filtra pequenas variações (ex: só atualiza se mudou mais de 5 metros)
        min_distance = 5  # metros
        from math import radians, cos, sin, sqrt, atan2
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # raio da Terra em metros
            phi1, phi2 = radians(lat1), radians(lat2)
            dphi = radians(lat2 - lat1)
            dlambda = radians(lon2 - lon1)
            a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
            return 2*R*atan2(sqrt(a), sqrt(1 - a))

        if hasattr(self, 'last_lat') and hasattr(self, 'last_lon'):
            dist = haversine(self.last_lat, self.last_lon, lat, lon)
            print(f"Distância do último ponto: {dist:.2f} m")
            if dist < min_distance:
                print(f"Mudança menor que {min_distance}m, ignorando atualização.")
                return
        self.last_lat = lat
        self.last_lon = lon

        print(f"Location received: {lat}, {lon}")
        print(f"Root ids: {self.root.ids}")

        mapview = self.root.ids.get('mapview')
        if not mapview:
            print("MapView widget not found in ids.")
            return

        coord_label = self.root.ids.get('coordinates')
        if coord_label:
            coord_label.text = f"Location: {lat:.5f}, {lon:.5f}"

        # Remove previous marker if it exists
        if hasattr(self, 'current_marker'):
            try:
                mapview.remove_widget(self.current_marker)
                print("Removed previous marker.")
            except Exception as e:
                print(f"Could not remove previous marker: {e}")

        # Always create and add a new marker (use default image)
        self.current_marker = MapMarker(lat=lat, lon=lon)
        mapview.add_widget(self.current_marker)
        print(f"Added marker at: {lat}, {lon} (default image)")
        print(f"MapView children: {mapview.children}")
        # Force mapview update
        if hasattr(mapview, 'do_update'):
            mapview.do_update(0)
            print("Called mapview.do_update(0)")

        mapview.center_on(lat, lon)
        print(f"Centered map on: {lat}, {lon}")

    def show_popup(self, message):
        popup = Popup(title="Error", content=Label(text=message), size_hint=(0.8, 0.3))
        popup.open()

    def exit_app(self):
        print("Exiting application...")
        self.stop()

if __name__ == '__main__':
    GeoApp().run()