import React, { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import * as turf from '@turf/turf'

const generateArc = (start, destination) => {
  const radius = turf.rhumbDistance(start, destination)
  const midpoint = turf.midpoint(start, destination)
  const bearing = turf.rhumbBearing(start, destination) - 89
  const origin = turf.rhumbDestination(midpoint, radius, bearing)

  const arc = turf.lineArc(
    origin,
    turf.distance(origin, start),
    turf.bearing(origin, destination),
    turf.bearing(origin, start),
    {
      steps: 128,
    }
  )

  return arc.geometry.coordinates
}

// https://jsfiddle.net/r9c4khbs/2/
const MapChart = ({ data }) => {
  mapboxgl.accessToken =
    'pk.eyJ1Ijoib2N1cG9wIiwiYSI6ImNqa3ZnOTc4cTBicjAzc29iZWNrZHQwa3kifQ.PDkTbHFNjtqvXZTK14eUiw' // ocupops account key

  const mapContainer = useRef(null)
  const map = useRef(null)
  const [userLng, setUserLng] = useState(-70.9) // TODO: Set to users location
  const [userLat, setUserLat] = useState(42.35)
  const [zoom, setZoom] = useState(1)

  const endPoint1 = [120.960515, 23.69781]
  //

  useEffect(() => {
    if (!data.length) return
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [userLng, userLat],
      zoom: zoom,
    })
    map.current.on('load', () => {
      for (const country of data) {
        const coords = generateArc([userLng, userLat],[country.longitude, country.latitude])
        map.current.addSource(country.name+country.device_id, {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: coords,
            },
          },
        })
        map.current.addLayer({
          id: country.name+country.device_id,
          type: 'line',
          source: country.name+country.device_id,
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': '#888',
            'line-width': 2,
          },
        })
      }
    })
  }, [data])

  return (
    <div>
      <div
        ref={mapContainer}
        style={{ height: '600px' }}
        className="map-container"
      />
    </div>
  )
}

export default MapChart
