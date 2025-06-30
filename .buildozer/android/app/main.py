from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from jnius import autoclass, cast, PythonJavaClass, java_method

from kivy_garden.mapview import MapView

# Java classes
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
LocationManager = autoclass('android.location.LocationManager')


# Listener para localização
class MyLocationListener(PythonJavaClass):
    __javainterfaces__ = ['android/location/LocationListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        latitude = location.getLatitude()
        longitude = location.getLongitude()
        self.callback(latitude, longitude)

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
        self.layout = BoxLayout(orientation='vertical')

        self.mapview = MapView(zoom=15, lat=0, lon=0)
        self.label = Label(text="Localização não iniciada", size_hint_y=0.1)

        self.layout.add_widget(self.mapview)
        self.layout.add_widget(self.label)

        return self.layout

    def on_start(self):
        self.iniciar_gps()

    def mostrar_localizacao(self, lat, lon):
        self.label.text = f"Latitude: {lat:.6f}\nLongitude: {lon:.6f}"
        self.mapview.center_on(lat, lon)

    def iniciar_gps(self):
        activity = PythonActivity.mActivity
        self.location_manager = cast(LocationManager, activity.getSystemService(Context.LOCATION_SERVICE))
        self.listener = MyLocationListener(self.mostrar_localizacao)

        def start_location_updates():
            provider = self.location_manager.GPS_PROVIDER
            self.location_manager.requestLocationUpdates(provider, 1000, 1, self.listener)

        activity.runOnUiThread(start_location_updates)


if __name__ == "__main__":
    GeoApp().run()
