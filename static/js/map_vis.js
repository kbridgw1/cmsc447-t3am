

Plotly.d3.json('congressional_districts.json', function(geojsonc) {

    Plotly.newPlot('myDiv', [{
      type: 'scattermapbox',
      lat: [39.045753],
      lon: [-76.641273]
    }], {
      title: "Maryland Congressional Districts",
      height: 800,
      width: 800,
      mapbox: {
        center: {
          lat: 39.045753,
          lon: -76.641273
        },
        style: 'light',
        zoom: 6,
        layers: [
          {
            sourcetype: 'geojson',
            source: geojsonc,
            type: 'fill',
            color: 'rgba(40,0,113,0.8)'
          },        
        ]
      }
    }, {
      mapboxAccessToken: 'pk.eyJ1Ijoia2JyaWRndzEiLCJhIjoiY2s4dDN5ZXZsMHc0NzNmcG0zaGYxNW0xNiJ9.FXUNX-3tgb9YbiD-R6WNyA'
    });
      
    
});

