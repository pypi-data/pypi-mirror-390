function getChartDimensions() {
    let dimensions = [...document.getElementsByClassName("chart-container")].map((chart) => {
        const style = getComputedStyle(chart);
        return {
            [chart.id]: {
                "width": chart.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight),
                "height": chart.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom),
            }
        }
    });

    return dimensions;
}

document.body.addEventListener("htmx:configRequest", (event) => {
    event.detail.parameters["dimensions"] = JSON.stringify(getChartDimensions());
});