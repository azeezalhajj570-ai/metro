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
        const guidedCount = Number(chartCanvas.dataset.guided || 0);
        const staffCount = Number(chartCanvas.dataset.staff || 0);
        const sosCount = Number(chartCanvas.dataset.sos || 0);

        new Chart(chartCanvas, {
            type: "doughnut",
            data: {
                labels: ["Route Guidance", "Staff Assistance", "SOS Alerts"],
                datasets: [
                    {
                        data: [guidedCount, staffCount, sosCount],
                        backgroundColor: ["#0f766e", "#d97706", "#9f1239"],
                        borderColor: ["#ccfbf1", "#fed7aa", "#fecdd3"],
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

    const quickActionStatus = document.getElementById("quick-action-status");
    const quickActionButtons = document.querySelectorAll(".quick-action");

    quickActionButtons.forEach((actionButton) => {
        actionButton.addEventListener("click", async () => {
            if (!form || !quickActionStatus) {
                return;
            }

            const formData = new FormData(form);
            const requestType = actionButton.dataset.requestType || "staff_assistance";
            const payload = {
                traveler_name: formData.get("traveler_name"),
                profile: formData.get("profile"),
                origin: formData.get("origin"),
                destination: formData.get("destination") || formData.get("origin"),
                priority: formData.get("priority"),
                source_device: formData.get("source_device"),
                notes: formData.get("notes"),
                request_type: requestType
            };

            quickActionStatus.textContent = "Sending request...";

            try {
                const response = await fetch("/api/help", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || "Unable to trigger assistance.");
                }

                quickActionStatus.textContent = `${result.message} ${result.zone} is now tagged for follow-up.`;
            } catch (error) {
                quickActionStatus.textContent = error.message;
            }
        });
    });
});
