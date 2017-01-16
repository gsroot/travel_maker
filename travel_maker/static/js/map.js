function updateMarkers(map, markers) {
    var mapBounds = map.getBounds();
    var marker, position;

    for (var i = 0; i < markers.length; i++) {
        marker = markers[i];
        position = marker.getPosition();

        if (mapBounds.hasLatLng(position)) {
            showMarker(map, marker);
        } else {
            hideMarker(map, marker);
        }
    }
}

function showMarker(map, marker) {
    if (marker.setMap()) return;
    marker.setMap(map);
}

function hideMarker(map, marker) {
    if (!marker.setMap()) return;
    marker.setMap(null);
}