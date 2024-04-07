<script>

// setting up the dimensions and margins of our graph
var margin = {top: 10, right: 30, bottom: 30, left: 60},
width = 460 - margin.left - margin.right,
height = 400 - margin.top - margin.bottom;

// appending the svg image to the body of the page
var svg = d3.select("#my-chart")
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform',
        'translate(' + margin.left + ',' + margin.top + ')');

// reading our data
d3.csv('master_solar_data.csv',

// formatting our data so it can be read 
function(data) {
    return {date: d3.timeParse('%m/%d/%Y')(d.period), value : d.value }
}, 

// now we can use the dataset
function(data) {

    // adding the x axis component, which is a data type 
    var x = d3.scaleTime()
        .domain(d3.extent(data, function (d) { return d.period; }))
        .range([0, width]);
    svg.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .call(d3.axisBottom(x));
    
    // adding the y axis component, which should be shown as an integer
    var y = d3.scaleLinear()
        .domain([0, d3.max(data, function (d) { return +d.value; })])
        .range([height, 0]);
    svg.append('g')
        .call(d3.axisLeft(y));
    
    // adding the line now
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', d3.line()
            .x(function(d) { return x(d.period) })
            .y(function (d) { return y(d.value) })
        )
}))
    
</script>
