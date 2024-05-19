import sys
import json
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, QtNetwork

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no"/>
    <style type="text/css">
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        #map_canvas {
            height: 100%;
        }
    </style>
    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script async defer
            src="https://maps.googleapis.com/maps/api/js?key=API_KEY"
            type="text/javascript"></script>
    <script type="text/javascript">
        var map;
        var markers = [];
        var qtWidget;

        function initialize() {
            var myOptions = {
                center: {lat: -34.397, lng: 150.644},
                zoom: 8
            };

            map = new google.maps.Map(document.getElementById('map_canvas'), myOptions);

            new QWebChannel(qt.webChannelTransport, function (channel) {
                qtWidget = channel.objects.qGoogleMap;
            });

            google.maps.event.addListener(map, 'dragend', function () {
                var center = map.getCenter();
                qtWidget.mapIsMoved(center.lat(), center.lng());
            });
            google.maps.event.addListener(map, 'click', function (ev) {
                qtWidget.mapIsClicked(ev.latLng.lat(), ev.latLng.lng());
            });
            google.maps.event.addListener(map, 'rightclick', function (ev) {
                qtWidget.mapIsRightClicked(ev.latLng.lat(), ev.latLng.lng());
            });
            google.maps.event.addListener(map, 'dblclick', function (ev) {
                qtWidget.mapIsDoubleClicked(ev.latLng.lat(), ev.latLng.lng());
            });
        }

        function gmap_setCenter(lat, lng) {
            map.setCenter(new google.maps.LatLng(lat, lng));
        }

        function gmap_getCenter() {
            return [map.getCenter().lat(), map.getCenter().lng()];
        }

        function gmap_setZoom(zoom) {
            map.setZoom(zoom);
        }

        function gmap_addMarker(key, latitude, longitude, parameters) {
            if (key in markers) {
                gmap_deleteMarker(key);
            }
            var coords = new google.maps.LatLng(latitude, longitude);
            parameters['map'] = map;
            parameters['position'] = coords;
            var marker = new google.maps.Marker(parameters);
            google.maps.event.addListener(marker, 'dragend', function () {
                qtWidget.markerIsMoved(key, marker.position.lat(), marker.position.lng());
            });
            google.maps.event.addListener(marker, 'click', function () {
                qtWidget.markerIsClicked(key, marker.position.lat(), marker.position.lng());
            });
            google.maps.event.addListener(marker, 'dblclick', function () {
                qtWidget.markerIsDoubleClicked(key, marker.position.lat(), marker.position.lng());
            });
            google.maps.event.addListener(marker, 'rightclick', function () {
                qtWidget.markerIsRightClicked(key, marker.position.lat(), marker.position.lng());
            });
            markers[key] = marker;
            return key;
        }

        function gmap_moveMarker(key, latitude, longitude) {
            var coords = new google.maps.LatLng(latitude, longitude);
            markers[key].setPosition(coords);
        }

        function gmap_deleteMarker(key) {
            markers[key].setMap(null);
            delete markers[key];
        }

        function gmap_changeMarker(key, extras) {
            if (!(key in markers)) {
                return;
            }
            markers[key].setOptions(extras);
        }

        window.onload = initialize;
    </script>
</head>
<body>
<div id="map_canvas" style="width:100%; height:100%"></div>
</body>
</html>
'''

class GeoCoder(QtNetwork.QNetworkAccessManager):
    class NotFoundError(Exception):
        pass

    def geocode(self, location, api_key):
        url = QtCore.QUrl("https://maps.googleapis.com/maps/api/geocode/xml")

        query = QtCore.QUrlQuery()
        query.addQueryItem("key", api_key)
        query.addQueryItem("address", location)
        url.setQuery(query)
        request = QtNetwork.QNetworkRequest(url)
        reply = self.get(request)
        loop = QtCore.QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec_()
        reply.deleteLater()
        self.deleteLater()
        return self._parseResult(reply)

    def _parseResult(self, reply):
        xml = reply.readAll()
        reader = QtCore.QXmlStreamReader(xml)
        while not reader.atEnd():
            reader.readNext()
            if reader.name() != "geometry": continue
            reader.readNextStartElement()
            if reader.name() != "location": continue
            reader.readNextStartElement()
            if reader.name() != "lat": continue
            latitude = float(reader.readElementText())
            reader.readNextStartElement()
            if reader.name() != "lng": continue
            longitude = float(reader.readElementText())
            return latitude, longitude
        raise GeoCoder.NotFoundError


class QGoogleMap(QtWebEngineWidgets.QWebEngineView):
    mapMoved = QtCore.pyqtSignal(float, float)
    mapClicked = QtCore.pyqtSignal(float, float)
    mapRightClicked = QtCore.pyqtSignal(float, float)
    mapDoubleClicked = QtCore.pyqtSignal(float, float)

    markerMoved = QtCore.pyqtSignal(str, float, float)
    markerClicked = QtCore.pyqtSignal(str, float, float)
    markerDoubleClicked = QtCore.pyqtSignal(str, float, float)
    markerRightClicked = QtCore.pyqtSignal(str, float, float)

    def __init__(self, api_key, parent=None):
        super(QGoogleMap, self).__init__(parent)
        self._api_key = api_key
        channel = QtWebChannel.QWebChannel(self)
        self.page().setWebChannel(channel)
        channel.registerObject("qGoogleMap", self)
        self.initialized = False

        html = HTML.replace("API_KEY", self._api_key)
        self.setHtml(html)
        self.loadFinished.connect(self.on_loadFinished)

        self._manager = QtNetwork.QNetworkAccessManager(self)

    @QtCore.pyqtSlot()
    def on_loadFinished(self):
        self.initialized = True
        self.page().runJavaScript('initialize()')

    def waitUntilReady(self):
        if not self.initialized:
            loop = QtCore.QEventLoop()
            self.loadFinished.connect(loop.quit)
            loop.exec_()

    def geocode(self, location):
        return GeoCoder(self).geocode(location, self._api_key)

    def centerAtAddress(self, location):
        try:
            latitude, longitude = self.geocode(location)
        except GeoCoder.NotFoundError:
            print("Not found {}".format(location))
            return None, None
        self.centerAt(latitude, longitude)
        return latitude, longitude

    def addMarkerAtAddress(self, location, **extra):
        if 'title' not in extra:
            extra['title'] = location
        try:
            latitude, longitude = self.geocode(location)
        except GeoCoder.NotFoundError:
            return None
        return self.addMarker(location, latitude, longitude, **extra)

    @QtCore.pyqtSlot(float, float)
    def mapIsMoved(self, lat, lng):
        self.mapMoved.emit(lat, lng)

    @QtCore.pyqtSlot(float, float)
    def mapIsClicked(self, lat, lng):
        self.mapClicked.emit(lat, lng)

    @QtCore.pyqtSlot(float, float)
    def mapIsRightClicked(self, lat, lng):
        self.mapRightClicked.emit(lat, lng)

    @QtCore.pyqtSlot(float, float)
    def mapIsDoubleClicked(self, lat, lng):
        self.mapDoubleClicked.emit(lat, lng)

    # markers
    @QtCore.pyqtSlot(str, float, float)
    def markerIsMoved(self, key, lat, lng):
        self.markerMoved.emit(key, lat, lng)

    @QtCore.pyqtSlot(str, float, float)
    def markerIsClicked(self, key, lat, lng):
        self.markerClicked.emit(key, lat, lng)

    @QtCore.pyqtSlot(str, float, float)
    def markerIsRightClicked(self, key, lat, lng):
        self.markerRightClicked.emit(key, lat, lng)

    @QtCore.pyqtSlot(str, float, float)
    def markerIsDoubleClicked(self, key, lat, lng):
        self.markerDoubleClicked.emit(key, lat, lng)

    def runScript(self, script, callback=None):
        if callback is None:
            self.page().runJavaScript(script)
        else:
            self.page().runJavaScript(script, callback)

    def centerAt(self, latitude, longitude):
        self.runScript("gmap_setCenter({},{})".format(latitude, longitude))

    def center(self):
        self._center = {}
        loop = QtCore.QEventLoop()

        def callback(*args):
            self._center = tuple(args[0])
            loop.quit()

        self.runScript("gmap_getCenter()", callback)
        loop.exec_()
        return self._center

    def setZoom(self, zoom):
        self.runScript("gmap_setZoom({})".format(zoom))

    def addMarker(self, key, latitude, longitude, **extra):
        return self.runScript(
            "gmap_addMarker("
            "key={!r}, "
            "latitude={}, "
            "longitude={}, "
            "{}"
            "); ".format(key, latitude, longitude, json.dumps(extra)))

    def moveMarker(self, key, latitude, longitude):
        return self.runScript(
            "gmap_moveMarker({!r}, {}, {});".format(key, latitude, longitude))

    def setMarkerOptions(self, keys, **extra):
        return self.runScript(
            "gmap_changeMarker("
            "key={!r}, "
            "{}"
            "); ".format(keys, json.dumps(extra)))

    def deleteMarker(self, key):
        return self.runScript(
            "gmap_deleteMarker("
            "key={!r} "
            "); ".format(key))

if __name__ == '__main__':
    API_KEY = "AIzaSyDNESuwm02SRod1FSahttV5aw4gWl5lcYc"

    app = QtWidgets.QApplication(sys.argv)
    w = QGoogleMap(api_key=API_KEY)
    w.resize(640, 480)
    w.show()
    w.waitUntilReady()
    w.setZoom(14)
    lat, lng = w.centerAtAddress("Lima Peru")
    if lat is None and lng is None:
        lat, lng = -12.0463731, -77.042754
        w.centerAt(lat, lng)

    w.addMarker("MyDragableMark", lat, lng, **dict(
        icon="http://maps.gstatic.com/mapfiles/ridefinder-images/mm_20_red.png",
        draggable=True,
        title="Move me!"
    ))

    for place in ["Plaza Ramon Castilla", "Plaza San Martin"]:
        w.addMarkerAtAddress(place, icon="http://maps.gstatic.com/mapfiles/ridefinder-images/mm_20_gray.png")

    w.mapMoved.connect(print)
    w.mapClicked.connect(print)
    w.mapRightClicked.connect(print)
    w.mapDoubleClicked.connect(print)
    sys.exit(app.exec_())
