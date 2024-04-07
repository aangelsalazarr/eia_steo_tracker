// setting the margins of our graph
const margin = {top: 10, right:30, bottom:30, left:60},
    width = 800 - margin.left - margin.right,
    height = 500 + margin.top + margin.bottom;

// defining scales of our visual
const xScale = d3.scaleTime().range([0, width]);
const yScale = d3.scaleLinear().range([height, 0]);

// parsing through period column given that its a date data type
const parseDate = d3.timeParse("%Y-%m-%d"); 

// line generators
const line = d3.line()
  .x(d => xScale(d.x))
  .y(d => yScale(d.y));

// appending the body of the object to the body of the page
const svg = d3.selectAll('#my-chart')
    .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
    .append('g') 
        .attr('transform', `translate(${margin.left}, ${margin.top})`);


// reading our data
d3.csv('master_solar_data.csv').then( function(data){

    // grabbing parsed date data and value column data
    const processedData = data.map(d => ({
        x: parseDate(d.period),
        y: d.value
    }))

    // updating scale of visual based on data provided
    xScale.domain(d3.extent(processedData, d => d.x));
    yScale.domain(d3.extent(processedData, d => d.y));

    // grouping our data by group
    // here we are grouping by forecast month
    const sumstat = d3.group(data, d => d.forecast_period); 

    // no we are adding our x axis which is in a date format
    const x = d3.scaleTime()
        .domain(d3.extent(data, function(d) { return parseDate(d.period); }))
        .range([ 0, width ]);
    svg.append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)); // we are defining the number of ticks in x axis

    // here we are adding the y axis
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, function(d) {return +d.value; })])
        .range([ height, 0])
    svg.append('g')
        .call(d3.axisLeft(y));

    // setting up our color pallete
    const colorP = d3.scaleOrdinal()
        .range(['#41bbc5','#ca6285', '#cq9828'])

    // drawing our line
    svg.selectAll('.line')
        .data(sumstat)
        .join('path')
            .attr('fill', 'none')
            .attr('stroke', function(d){ return colorP(d[0]) })
            .attr('stroke-width', 1.25)
            .attr('d', function(d){
                return d3.line()
                    .x(function(d) { return x(parseDate(d.period)); })
                    .y(function(d) { return y(+d.value); })
                    (d[1])
            })

    
    // creating a legend group
    const legendGroup = svg.append('g')
        .attr('transform', `translate(${width - 650}, ${margin.top})`);

    // creating a legend tiem for each group (forecast_month)
    sumstat.forEach((d, i) => {
        const legendItem = legendGroup.append('g')
            .attr('transform', `translate(0, ${i * 20})`); // why do we multiply by 20?

        // addding color swatch rectangle
        legendItem.append('rect')
            .attr('width', 15)
            .attr('height', 15)
            .attr('fill', colorP(d[0]));

        // adding text label to our legend
        legendGroup.append('text')
            .attr('x', 15)
            .attr('y', 10n)
            .text(d[0]);
    });

})
