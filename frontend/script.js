const API_URL = "http://127.0.0.1:5000";

// ==========================================
// 1. LOAD DASHBOARD STATISTICS
// ==========================================

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/customers`);

        if (!response.ok) {
            throw new Error("Failed to load dashboard data");
        }

        const customers = await response.json();

        // Total customers
        document.getElementById("total-customers").textContent =
            customers.length;

        // Customers predicted to churn
        const churned = customers.filter(
            customer => customer.ChurnPrediction === "Yes"
        ).length;

        // High-risk customers
        const highRisk = customers.filter(
            customer => customer.RiskLevel === "High"
        ).length;

        document.getElementById("churned-customers").textContent =
            churned;

        document.getElementById("high-risk").textContent =
            highRisk;

    } catch (error) {
        console.error("Dashboard loading failed:", error);
    }
}


// ==========================================
// 2. LOAD CUSTOMER RECORDS
// ==========================================

async function loadCustomers() {
    try {
        const response = await fetch(`${API_URL}/customers`);

        if (!response.ok) {
            throw new Error("Failed to load customer records");
        }

        const customers = await response.json();

        const table = document.getElementById("customer-table");

        table.innerHTML = "";

        if (customers.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="4">No customer records found.</td>
                </tr>
            `;
            return;
        }

        customers.forEach(customer => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${customer.id}</td>
                <td>${customer.ChurnPrediction}</td>
                <td>${customer.ChurnProbability}%</td>
                <td>${customer.RiskLevel}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {
        console.error("Customer loading failed:", error);
    }
}


// ==========================================
// 3. REFRESH DASHBOARD
// ==========================================

async function refreshDashboard() {
    await loadDashboard();
    await loadCustomers();
}


// ==========================================
// 4. RUN WHEN PAGE LOADS
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    refreshDashboard();
});