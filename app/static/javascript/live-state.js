import {fetchTheme} from "./general.js";

document.addEventListener("DOMContentLoaded",  () => {

	let temp_max = 50;
	let hum_min = 30;
	let hum_max = 70;
	let theme = 0;

	fetch('/get_all_config', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    })
	.then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
	.then(data => {
        console.log('Received data:', data);
        if (data.hasOwnProperty('temperature_max')) {
			temp_max = data['temperature_max'];
		}
		if (data.hasOwnProperty('humidity_min')) {
			hum_min = data['humidity_min'];
		}
		if (data.hasOwnProperty('humidity_max')) {
			hum_max = data['humidity_max'];
		}
		if (data.hasOwnProperty('color_format')) {
			theme = data['color_format'];
		}
    })
	.catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

	var socket = io();
    socket.on('connect', () => {
        console.log("connected")
    });
	socket.on('sensors', sensors => {
		console.log(sensors)
		document.querySelector("#temperature").innerHTML = sensors["temperature"] + "°C";
		let colour = "green";
		if (theme === "3") {
			colour = "cyan";
		}
		if (sensors["temperature"] > temp_max) { colour = "red"; }
		document.querySelector("#temperature").style.color = colour;

		document.querySelector("#humidity").innerHTML = sensors["humidity"] + "%";
		colour = "green";
		if (theme === "3") {
			colour = "cyan";
		}
		if (sensors["humidity"] > hum_max || sensors["humidity"] < hum_min) { colour = "red"; }
		document.querySelector("#humidity").style.color = colour;

		document.querySelector("#smoke").innerHTML = bool_to_msg(sensors["smoke"], "smoke");
		document.querySelector("#smoke").style.color = bool_to_colour(sensors["smoke"], theme);

		document.querySelector("#gas").innerHTML = bool_to_msg(sensors["gas"], "gas");
		document.querySelector("#gas").style.color = bool_to_colour(sensors["gas"], theme);

		document.querySelector("#flame").innerHTML = bool_to_msg(sensors["flame"], "fire");
		document.querySelector("#flame").style.color = bool_to_colour(sensors["flame"], theme);

		document.querySelector("#earthquake").innerHTML = bool_to_msg(sensors["earthquake"], "earthquake");
		document.querySelector("#earthquake").style.color = bool_to_colour(sensors["earthquake"], theme);

		document.querySelector("#time").innerHTML = sensors["time"].split(' ')[1];
		document.querySelector("#date").innerHTML = sensors["time"].split(' ')[0];
	});

	fetchTheme();
});

function bool_to_msg(bool, name) {
	if (bool) {
		return `${name.charAt(0).toUpperCase()}${name.slice(1)} detected!`
	} else {
		return `No ${name} detected`
	}
}

function bool_to_colour(bool, theme) {
	if (bool) {
		return "red";
	} else {
		if (theme === "3") {
			return "cyan";
		}
		return "green";
	}
}
