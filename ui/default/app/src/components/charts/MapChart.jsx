import React from "react";
import {
  ComposableMap,
  Geographies,
  Graticule,
  Geography,
  Marker,
  ZoomableGroup,
  Line
} from "react-simple-maps";
import ReactTooltip from "react-tooltip";

const geoUrl =
  "https://raw.githubusercontent.com/zcreativelabs/react-simple-maps/master/topojson-maps/world-110m.json";

const homeMarker = {
  coordinates: [-95.712891, 37.09024]
}

const markers = [
  { markerOffset: 0, name: "TW", coordinates: [120.960515, 23.69781] },
];

const MapChart = () => {
  return (
    <div className="border rounded-lg border-dark bg-secondary/20">
    <ComposableMap
      // projection="geoAzimuthalEqualArea"
      height="300"
      width="900"
      projectionConfig={{
        rotate: [-25, -5, -5],
        scale: 170
      }}
    >
      <ZoomableGroup
        center= {[30.802498, 26.820553]}
      >
      {/* <Graticule fill="#CFEFFF" stroke="#CFEFFF" /> */}
      <Geographies geography={geoUrl}>
        {({ geographies }) =>
          geographies
            // .filter(d => d.properties.REGION_UN === "Americas")
            .map(geo => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#fff"
                stroke="#fff"
                // onMouseEnter={() => {
                //     const { NAME, POP_EST } = geo.properties;
                //     setTooltipContent(`${NAME} — ${rounded(POP_EST)}`);
                //   }}
                //   onMouseLeave={() => {
                //     setTooltipContent("");
                //   }}
                //   style={{
                //     default: {
                //       fill: "#fff",
                //       outline: "none",
                //       transition: "200ms"
                //     },
                //     hover: {
                //       fill: "#08103F",
                //       outline: "none"
                //     },
                //     pressed: {
                //       fill: "#08103F",
                //       outline: "none"
                //     }
                //   }}
              />
            ))
        }
      </Geographies>

      {markers.map(({ name, coordinates, markerOffset }) => (
        <>
        <Marker key={name} coordinates={coordinates}>
          <circle r={8} fill="#007BC7" stroke="#E5E5E5" strokeWidth={4} />
        </Marker>
        <Line
          from={homeMarker.coordinates}
          to={coordinates}
          stroke="#007BC7"
          strokeWidth={4}
          strokeLinecap="round"
        />
      </>
      ))}
      </ZoomableGroup>
    </ComposableMap>
    </div>
  );
};

export default MapChart;
