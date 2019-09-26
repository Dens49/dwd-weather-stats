"use strict";

const padNumber = (num, length, paddingString) => ("" + num).padStart(length, paddingString);
const zeroPadTwo = num => padNumber(num, 2, "0");

const getBaseUrl = () => {
    const fullUrl = location.href.split("/");
    return fullUrl[0] + "//" + fullUrl[2];
}

// address and date are strings
// date format: YYYYmmdd
const getWeatherForDayOfYearAtAddressHtml = (address, date, callback) => {
    const url = new URL(getBaseUrl() + "/api/html/weather_for_day_of_year_at_address");
    url.searchParams.append("address", address);
    url.searchParams.append("date", date),
        fetch(url)
            .then(response => response.text()
                .then(text => callback(text))
            )
            .catch(error => {
                console.log(error.message);
            })
        ;
};

const formatDate = (date) => {
    return ("" + date.getFullYear())
        + zeroPadTwo(date.getMonth() + 1)
        + zeroPadTwo(date.getDate());
};
