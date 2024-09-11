import {fetchTheme, updateTheme} from "./general.js";

document.addEventListener("DOMContentLoaded",  () => {

    const editAddressBtn = document.querySelector("#edit-address-button");
    const emailInput = editAddressBtn.parentElement.previousElementSibling.querySelector(".settings-block__input");
    const enableNotifyBtn = document.querySelector("#enable-notify-button");
    const enableSoundBtn = document.querySelector("#enable-sound-button");
    const enableLightBtn = document.querySelector("#enable-light-button");
    const emailModal = document.querySelector("#email-modal");
    const emailModalClose = emailModal.querySelector(".email-modal__close");
    const emailModalText = emailModal.querySelector(".email-modal__text");

    let timer;
    const temperatureSlider = document.querySelector("#temperature");
    const earthquakeSlider = document.querySelector("#earthquake");
    const humidityMinSlider = document.querySelector("#humidityMin");
    const humidityMaxSlider = document.querySelector("#humidityMax");
    const smokeSlider = document.querySelector("#smoke");
    const flameSlider = document.querySelector("#flame");
    const gasSlider = document.querySelector("#gas");
    const dhtSlider = document.querySelector("#dht");



    // Settings Range Sliders //
    document.querySelectorAll(".settings-block__slider").forEach((element, index) => {
        element.addEventListener("input", () => {
            if (index < 2) {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = element.value + ".0°"; 
            } else if (index < 4){
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = element.value + "%"; 
            } else if (element.value == 0) {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = "OFF"; 
            } else {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = "ON"; 
            }
        })
    });

    // Settings Edit Personal //
    editAddressBtn.addEventListener("click", () => {

        if (!emailInput.readOnly) {
            if (validateDiscord(emailInput.value).isValid) {
                updateConfig('discord_webhook', emailInput.value);
                editAddressBtn.innerHTML = "edit webhook"
                editAddressBtn.classList.remove("settings-block__button_active");
                emailInput.readOnly = true;
            } else {
                emailModal.classList.remove("none");
                emailModalText.innerHTML = validateDiscord(emailInput.value).detail;
            }
        } else {
            emailInput.readOnly = false;
            emailInput.select();
            editAddressBtn.classList.add("settings-block__button_active");
            editAddressBtn.innerHTML = "save webhook"
        }
    })

    enableNotifyBtn.addEventListener("click", () => {
        enableNotifyBtn.classList.toggle("settings-block__button_active");
        if (enableNotifyBtn.classList.contains("settings-block__button_active")) {
            enableNotifyBtn.innerHTML = "enabled"
            updateConfig('notification', "on");
        } else {
            enableNotifyBtn.innerHTML = "disabled"
            updateConfig('notification', "off");
        }
    })

    enableLightBtn.addEventListener("click", () => {
        enableLightBtn.classList.toggle("settings-block__button_active");
        if (enableLightBtn.classList.contains("settings-block__button_active")) {
            enableLightBtn.innerHTML = "enabled"
            updateConfig('enable_led', true);
        } else {
            enableLightBtn.innerHTML = "disabled"
            updateConfig('enable_led', false);
        }
    })

    enableSoundBtn.addEventListener("click", () => {
        enableSoundBtn.classList.toggle("settings-block__button_active");
        if (enableSoundBtn.classList.contains("settings-block__button_active")) {
            enableSoundBtn.innerHTML = "enabled"
            updateConfig('enable_buzzer', true);
        } else {
            enableSoundBtn.innerHTML = "disabled"
            updateConfig('enable_buzzer', false);
        }
    })

    // Modal Listeners //
    emailModalClose.addEventListener("click", function() {
        emailModal.classList.add("none");
    });

    // Discord Validation Function // 
    const validateDiscord = (webhookURL) => {
        const regEx = /^https:\/\/discord\.com\/api\/webhooks\/\d+\/[A-Za-z0-9_-]+$/;
    
        if (!webhookURL) {
            return { isValid: false, detail: "Discord webhook URL is required." };
        }
    
        if (!regEx.test(webhookURL)) {
            return { isValid: false, detail: "Invalid Discord webhook URL." };
        }
    
        return { isValid: true };
    };

    // Settings Edit Preference //
    document.addEventListener("click", (event) => {
        const settingToUpdate = event.target.closest(".settings-block__label");
        if (settingToUpdate) {
            const settingValue = settingToUpdate.getAttribute("for");
            switch (settingValue) {
                case "time1":
                case "time2":
                case "time3":
                    updateConfig("time_format", settingValue.replace(/^\D+/g, ''));
                    break;
                case "date1":
                case "date2":
                case "date3":
                    updateConfig("date_format", settingValue.replace(/^\D+/g, ''));
                    break;
                case "color1":
                    updateTheme(1, true);
                    updateConfig("color_format", settingValue.replace(/^\D+/g, ''));
                    break;
                case "color2":
                    updateTheme(2, true);
                    updateConfig("color_format", settingValue.replace(/^\D+/g, ''));
                    break;
                case "color3":
                    updateTheme(3, true);
                    updateConfig("color_format", settingValue.replace(/^\D+/g, ''));
                    break;
            }
        }   
    })

    // Settings Edit System //
    temperatureSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("temperature_max", Number(temperatureSlider.value)), 5000);
    });
    humidityMinSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("humidity_min", Number(humidityMinSlider.value)), 5000);
    });
    humidityMaxSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("humidity_max", Number(humidityMaxSlider.value)), 5000);
    });
    earthquakeSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("sharp_movement_threshold", earthquakeSlider.value * 5000), 5000);
    });
    flameSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("enable_flame", Boolean(Number(flameSlider.value))), 5000);
    });
    smokeSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("enable_mq2", Boolean(Number(smokeSlider.value))), 5000);
    });
    gasSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("enable_mq9", Boolean(Number(gasSlider.value))), 5000);
    });
    dhtSlider.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(updateConfig("enable_dht", Boolean(Number(dhtSlider.value))), 5000);
    });

    // Update a settings //
    function updateConfig(name, value) {
        const data = {
          name: name,
          value: value
        };
      
        fetch('/set_config', {
          method: 'POST',
          body: JSON.stringify(data),
          headers: {
            'Content-Type': 'application/json'
          }
        })
          .then(response => {
            if (response.ok) {
              return response.text();
            }
            throw new Error('Network response was not ok.');
          })
          .then(data => {
            console.log('Config updated:', data);
          })
          .catch(error => {
            console.error('There was a problem updating the config:', error);
          });
    }      

    // Fetch Settings //
    let configs;

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
        configs = data;
        updateAllSettings(configs);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

    function updateSliders(settings) {
        temperatureSlider.value = settings["temperature_max"];
        earthquakeSlider.value = settings["sharp_movement_threshold"] / 5000;
        humidityMinSlider.value = settings["humidity_min"];
        humidityMaxSlider.value = settings["humidity_max"];
        smokeSlider.value = Number(settings["enable_mq2"]);
        flameSlider.value = Number(settings["enable_flame"]);
        gasSlider.value = Number(settings["enable_mq9"]);
        dhtSlider.value = Number(settings["enable_dht"]);
        document.querySelectorAll(".settings-block__slider").forEach((element, index) => {
            if (index < 2) {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = element.value + ".0°"; 
            } else if (index < 4){
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = element.value + "%"; 
            } else if (element.value == 0) {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = "OFF"; 
            } else {
                element.parentElement.previousElementSibling.querySelector("span.bold").innerHTML = "ON"; 
            }
        });
    }

    function updatePersonalSettings(settings) {
        emailInput.value = settings["discord_webhook"];

        if (settings["enable_led"]) {
            enableLightBtn.classList.add("settings-block__button_active");
            enableLightBtn.innerHTML = "enabled";
        } else {
            enableLightBtn.classList.remove("settings-block__button_active");
            enableLightBtn.innerHTML = "disabled";
        }

        if (settings["enable_buzzer"]) {
            enableSoundBtn.classList.add("settings-block__button_active");
            enableSoundBtn.innerHTML = "enabled";
        } else {
            enableSoundBtn.classList.remove("settings-block__button_active");
            enableSoundBtn.innerHTML = "disabled";
        }

        if (settings["notification"] == "on") {
            enableNotifyBtn.classList.add("settings-block__button_active");
            enableNotifyBtn.innerHTML = "enabled";
        } else {
            enableNotifyBtn.classList.remove("settings-block__button_active");
            enableNotifyBtn.innerHTML = "disabled";
        }
    }

    function updatePreferenceSettings(settings) {
        document.querySelector(`#time${settings["time_format"]}`).checked = true;
        document.querySelector(`#color${settings["color_format"]}`).checked = true;
        document.querySelector(`#date${settings["date_format"]}`).checked = true;
    }

    function updateAllSettings(settings) {
        updateSliders(settings);
        updatePersonalSettings(settings);
        updatePreferenceSettings(settings);
    }
    
    fetchTheme();
});