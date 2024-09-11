import {fetchTheme} from "./general.js";

document.addEventListener("DOMContentLoaded",  () => {

    const temperatureChart = document.querySelector("#temperature-chart");
    const humidityChart = document.querySelector("#humidity-chart");
    const earhquakeChart = document.querySelector("#earthquake-chart")
    const fireChart = document.querySelector("#fire-chart")
    const smokeChart = document.querySelector("#smoke-chart")
    const gasChart = document.querySelector("#gas-chart")

    // Create Chart Function
    const createDiagram = (divBlock, labels, series) => {
        var elem = new Chartist.Line(divBlock, 
            {
                labels: labels,
                series: series,
            }, 
            {
                width: "100%",
                height: "100%",
                low: 0,
                showArea: true,
                fullWidth: true,
            },
        ); 


        return elem;
    }

    // Function to update a chart
    function updateChart(chart, data, length) {
        while (data.labels.length > length) {
            data.labels.shift();
        }
        for (let i = 0; i < data.series.length; i++) {
            while (data.series[i].length > length) {
                data.series[i].shift();
            }
        }
        chart.update(data);
    }
    
    // Reference to the charts
    let tempCht = createDiagram(temperatureChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[29, 30, 15, 10, 0]]);
    let humidityCht = createDiagram(humidityChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0]]);
    let earthCht = createDiagram(earhquakeChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0], [0, 98, 15, 65, 81], [15, 0, 81, 15, 65]]);
    let fireCht = createDiagram(fireChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0]])
    let smokeCht = createDiagram(smokeChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0]])
    let gasCht = createDiagram(gasChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0]])

    // History Parameters' Dropdowns
    document.addEventListener("click", (e) => {
        const historyParameter = e.target.closest(".history-parameter");
        if (historyParameter) {
            const historyParameterArrow = historyParameter.querySelector("img[alt='Arrow']");
            const historyAnalytics =  historyParameter.nextElementSibling;
            // Animate the lines
            // elem.on('draw', function(data) {
            //     if(data.type === 'line' || data.type === 'area') {
            //         data.element.animate({
            //             d: {
            //                 begin: 2000 * data.index,
            //                 dur: 2000,
            //                 from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
            //                 to: data.path.clone().stringify(),
            //                 easing: Chartist.Svg.Easing.easeOutQuint
            //             }
            //         });
            //     }
            // });

            historyAnalytics.classList.toggle("none");
            if (historyAnalytics.firstElementChild === temperatureChart) {
                // var tempCht = createDiagram(temperatureChart, ['1', 'xx', 'Wed', 'Thu', 'Fri'], [[29, 30, 15, 10, 0]]);
            } else if (historyAnalytics.firstElementChild === humidityChart) {
                // var humidityCht = createDiagram(humidityChart, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], [[81, 65, 15, 98, 0]]);
            }

            historyParameterArrow.style.transform = historyParameterArrow.style.transform === "rotate(180deg)" ? "rotate(0deg)" : "rotate(180deg)";
        }
    })

    var socket = io();
    socket.on('connect', () => {
        console.log("connected");
    });
    socket.on('history', history_data => {
        // console.log(history_data);
        const time_labels = history_data['timestamp'].map(timestamp => {
            const parts = timestamp.split(' ')[1].split(':');
            return parts[0] + ':' + parts[1];
        });

        let data = {
            labels: time_labels,
            series: [history_data['avg_temperature']]
        };
        updateChart(tempCht, data, 20);

        data.labels = time_labels
        data.series = [history_data['avg_humidity']];
        updateChart(humidityCht, data, 20);

        data.labels = time_labels
        data.series = [history_data['avg_delta_x'], history_data['avg_delta_y'], history_data['avg_delta_z']];
        updateChart(earthCht, data, 20);

        data.labels = time_labels
        data.series = [history_data['top_flame']]
        updateChart(fireCht, data, 20)

        data.labels = time_labels
        data.series = [history_data['avg_mq2']]
        updateChart(smokeCht, data, 20)

        data.labels = time_labels
        data.series = [history_data['avg_mq9']]
        updateChart(gasCht, data, 20)
    });

    fetchTheme();
});