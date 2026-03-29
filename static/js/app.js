document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("plan-form");
    const button = document.getElementById("plan-button");

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.classList.add("opacity-80", "cursor-not-allowed");

            const buttonText = button.querySelector(".button-text");
            const loadingText = button.querySelector(".loading-text");

            if (buttonText && loadingText) {
                buttonText.classList.add("hidden");
                loadingText.classList.remove("hidden");
            }
        });
    }

    const chartCanvas = document.getElementById("request-chart");
    if (chartCanvas && window.Chart) {
        const sosCount = Number(chartCanvas.dataset.sos || 0);
        const guidedCount = Number(chartCanvas.dataset.guided || 0);
        const highPriorityCount = Number(chartCanvas.dataset.highPriority || 0);

        new Chart(chartCanvas, {
            type: "doughnut",
            data: {
                labels: ["SOS Alerts", "Guided Routes", "Fastest Priority Requests"],
                datasets: [
                    {
                        data: [sosCount, guidedCount, highPriorityCount],
                        backgroundColor: ["#ef4444", "#14b86a", "#db7c26"],
                        borderColor: ["#fee2e2", "#d7f5e5", "#ffedd5"],
                        borderWidth: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                },
                cutout: "68%"
            }
        });
    }
});
