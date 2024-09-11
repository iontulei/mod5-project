let theme;

export function fetchTheme() {
        // Make a GET request to fetch the website theme

        fetch('/get_config?name=color_format', {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            console.log('Received data:', data);
            theme = data;
            updateTheme(theme, false);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

export function updateTheme(nr, flag) {
    if (flag) {
        document.getElementsByTagName("body")[0].classList = [];
        document.querySelector(".navbar").classList = ["navbar"];
        document.querySelectorAll(".navbar__links").forEach((elem) => {
            elem.classList = ["navbar__links"];
        })
    }

    if (nr == "2") {
        document.getElementsByTagName("body")[0].classList.add("theme-2-1");
        document.querySelector(".navbar").classList.add("theme-2-2", "theme-2-1-color");
        document.querySelectorAll(".navbar__links").forEach((elem) => {
            elem.classList.add("theme-2-1-color");
        })
        if (document.querySelector(".my-box")) {
            document.querySelectorAll(".my-box").forEach((elem) => {
                elem.classList.add("theme-2-1-color", "theme-2-2");
            })
        } else if (document.querySelector(".history-parameter")) {
            document.querySelectorAll(".history-parameter, .history-analytics").forEach((elem) => {
                elem.classList.add("theme-2-1-color", "theme-2-2");
            })
        }
    } else if (nr == "3") {
        document.getElementsByTagName("body")[0].classList.add("theme-3-1");
        document.querySelector(".navbar").classList.add("theme-3-2", "theme-3-3-color");
        document.querySelectorAll(".navbar__links").forEach((elem) => {
            elem.classList.add("theme-3-3-color");
        })
        if (document.querySelector(".my-box")) {
            document.querySelectorAll(".my-box").forEach((elem) => {
                elem.classList.add("theme-3-1-color", "theme-3-2");
            })
        } else if (document.querySelector(".history-parameter")) {
            document.querySelectorAll(".history-parameter, .history-analytics").forEach((elem) => {
                elem.classList.add("theme-3-1-color", "theme-3-2");
            })
        }
    } else {
        document.getElementsByTagName("body")[0].classList.add("theme-1-1");
        document.querySelector(".navbar").classList.add("theme-1-2", "theme-1-1-color");
        document.querySelectorAll(".navbar__links").forEach((elem) => {
            elem.classList.add("theme-1-1-color");
        })
        if (document.querySelector(".my-box")) {
            document.querySelectorAll(".my-box").forEach((elem) => {
                elem.classList.add("theme-1-2-color", "theme-1-2");
            })
        } else if (document.querySelector(".history-parameter")) {
            document.querySelectorAll(".history-parameter, .history-analytics").forEach((elem) => {
                elem.classList.add("theme-1-2-color", "theme-1-2");
            });
        }
    }
}