
// setting up the margins of our graphs
const margin = { top: 20, right: 20, bottom: 30, left: 50 };
const width = 800 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

// defining scales of our visual
const xScale = d3.scaleTime().range([0, width]);
const yScale = d3.scaleLinear().range([height, 0]);

// parsing through period column given that its a date data type
const parseDate = d3.timeParse("%Y-%m-%d"); 


// line generators
const line = d3.line()
  .x(d => xScale(d.x))
  .y(d => yScale(d.y));

// loading data into our environment
d3.csv("master_solar_data.csv")
  .then(data => {

    // grabbing parsed date data
    const processedData = data.map(d => ({
      x: parseDate(d.period), 
      y: d.value 
    }));

    // updating scales of visual based on data provided 
    xScale.domain(d3.extent(processedData, d => d.x));
    yScale.domain(d3.extent(processedData, d => d.y));

    // add svg to body element
    const svg = d3.select("body")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // drawing our line
    svg.append("path")
      .datum(processedData)
      .attr("class", "line")
      .attr('stroke', '#791c76')
      .attr("d", line);

    // adding circles for each data point
    svg.append('circle')
      .data(processedData)
      .enter()  
      .append('circle')
      .attr('cx', d => xScale(d.x)) 
      .attr('cy', d => yScale(d.y))
      .attr('r', 4) // setting the radius as 4 
      .attr('fill', 'maroon')
      .attr('stroke', 'white')
      .attr('stroke-width', 2);


    // adding axis
    svg.append("g")
      .attr("transform", `translate(0, ${height})`)
      .call(d3.axisBottom(xScale));

    svg.append("g")
      .call(d3.axisLeft(yScale));

  });
