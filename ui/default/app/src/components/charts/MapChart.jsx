import React, { memo } from "react";
import {
  ComposableMap,
  Geographies,
  Graticule,
  Geography,
  Marker,
  ZoomableGroup,
  Line
} from "react-simple-maps";

const geoUrl =
  "https://raw.githubusercontent.com/zcreativelabs/react-simple-maps/master/topojson-maps/world-110m.json";

const homeMarker = {
  coordinates: [-95.712891, 37.09024]
}

const markers = [
  { markerOffset: 0, name: "TW", coordinates: [120.960515, 23.69781], data: '35kb' },
  { markerOffset: 0, name: "US", coordinates: [-95.712891	, 37.09024], data: '160mb' },
  { markerOffset: 0, name: "CN", coordinates: [104.195397, 35.86166], data: '800mb' },
  { markerOffset: 0, name: "KR", coordinates: [127.766922	, 35.907757], data: '80b' },
  { markerOffset: 0, name: "US", coordinates: [-95.712891	, 37.09024], data: '5mb' },
];

const MapChart = ({ setTooltipContent }) => {
  return (
    <div className="my-4 border rounded-lg border-dark bg-secondary/20">
    <ComposableMap
      projection="geoMercator"
      height="350"
      data-tip=""
      projectionConfig={{
        rotate: [0, 0, 0],
        scale: 140
      }}
    >
      <ZoomableGroup
        // Center World
        center= {[30.802498, 26.820553]}
        // Center US/Home
        // center= {[-95.712891, 37.09024]}
      >
      <Geographies geography={geoUrl}>
        {({ geographies }) =>
          geographies.map(geo => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#fff"
                stroke="#fff"
                onMouseEnter={() => {
                    const { NAME } = geo.properties;
                    setTooltipContent(`${NAME}`);
                  }}
                  onMouseLeave={() => {
                    setTooltipContent("");
                  }}
                  style={{
                    default: {
                      fill: "#fff",
                      outline: "none",
                      transition: "200ms"
                    },
                    hover: {
                      fill: "#08103F",
                      outline: "none"
                    },
                    pressed: {
                      fill: "#08103F",
                      outline: "none"
                    }
                  }}
              />
            ))
        }
      </Geographies>

      {markers.map(({ name, coordinates, markerOffset, data }) => (
        <>
        <Marker key={name} coordinates={coordinates}>
          <circle r={8} fill="#007BC7" stroke="#E5E5E5" strokeWidth={4} />
          <text
            textAnchor="middle"
            y={markerOffset}
            style={{ fontFamily: "system-ui", fill: "#5D5A6D" }}
          >
            {data}
          </text>
        </Marker>
        <Line
          from={homeMarker.coordinates}
          to={coordinates}
          stroke="#007BC7"
          strokeWidth={2}
          strokeLinecap="round"
        />
      </>
      ))}
      </ZoomableGroup>
    </ComposableMap>
    </div>
  );
};

export default memo(MapChart);
