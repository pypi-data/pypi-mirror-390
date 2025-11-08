const activeColors = {
  ATC_ACTIVATED: '#0000ff',
  TACT_ACTIVATED_WITHOUT_FSA: '#6495ed',
  IFPL: '#add8e6',
  RPL: '#add8e6',
  PFD: '#add8e6',
  SUSPENDED: '#c6dbef',
  TACT_ACTIVATED_WITH_FSA: '#deebf7'
};

const inactiveColors = {
  ATC_ACTIVATED: '#ccccff',
  TACT_ACTIVATED_WITHOUT_FSA: '#d6e6f9',
  IFPL: '#e6f2f8',
  RPL: '#e6f2f8',
  PFD: '#e6f2f8',
  SUSPENDED: '#e8f0f7',
  TACT_ACTIVATED_WITH_FSA: '#eff5fb'
};

function makeTraces(curve) {
  
  let traces = [];

  Object.keys(curve.bars).forEach(cat => {
    traces.push({
      x: timestamps,
      y: curve.bars[cat],
      type: 'bar',
      name: cat,
      marker: {color: activeColors[cat]},
      hoverinfo: 'y+name',
      offsetgroup: 0
    });
  });

  Object.keys(curve.bars).forEach(cat => {
    traces.push({
      x: timestamps,
      y: curve.inactive_bars[cat],
      type: 'bar',
      name: cat,
      marker: {color: inactiveColors[cat]},
      hoverinfo: 'y+name',
      offsetgroup: 0,
      showlegend: false
    });
  });

  traces.push({
    x: timestamps,
    y: curve.sustain,
    mode: 'lines',
    line: {shape: 'hv', color: 'orange', width: 2},
    name: 'sustain'
  });

  traces.push({
    x: timestamps,
    y: curve.peak,
    mode: 'lines',
    line: {shape: 'hv', color: 'red', width: 2},
    name: 'peak'
  });

  return traces;

}

function plotCurve(curve) {

  const traces = makeTraces(curve);

  const shapes = (curve.overloaded_periods || []).map(period => ({
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: period.wef,
      x1: period.unt,
      y0: 0,
      y1: 1,
      fillcolor: 'rgba(255,0,0,0.5)',
      line: { width: 0 },
      layer: 'below'
    }));

  const layout = {
    barmode: 'stack',
    xaxis: {type: 'date', title: 'Time'},
    yaxis: {title: 'Occupancy'},
    legend: {itemclick: false},
    margin: {t: 30, r: 30, b: 50, l: 60},
    bargap: 0,
    bargroupgap: 0,
    shapes: shapes
  };

  Plotly.newPlot('graph', traces, layout, {responsive: true});

}

function setActiveButton(id) {
  document.querySelectorAll('#menu button').forEach(btn => {
    btn.classList.toggle('active', btn.id === id);
  });
}

const sectorDiv = document.getElementById('sectors');

Object.keys(window.curves).forEach((curveName, idx) => {
  const btn = document.createElement('button');
  btn.textContent = curveName;
  btn.id = 'btn' + curveName;
  if (idx === 0) btn.classList.add('active');
  btn.onclick = () => {
    plotCurve(window.curves[curveName]);
    setActiveButton(btn.id);
  };
  sectorDiv.appendChild(btn);
});
