// =====================================================
// CONFIGURATION
// =====================================================

const API_URL = "http://127.0.0.1:5000";

let currentSearchBy = "name";
let currentSearch = "";

let currentPage = 1;
let totalPages = 1;
let perPage = 10;

let churnChart = null;
let riskChart = null;


// =====================================================
// DASHBOARD
// =====================================================

async function loadDashboard() {

    try {

        const response = await fetch(`${API_URL}/dashboard-stats`);

        if (!response.ok) {
            throw new Error("Unable to load dashboard");
        }

        const data = await response.json();

        document.getElementById("total-customers").textContent =
            data.total_customers;

        document.getElementById("churned-customers").textContent =
            data.churned_customers;

        document.getElementById("retained-customers").textContent =
            data.retained_customers;

        document.getElementById("high-risk").textContent =
            data.high_risk_customers;


        updateCharts(data);

    } catch (error) {

        console.error("Dashboard error:", error);

    }

}


// =====================================================
// DASHBOARD CHARTS
// =====================================================

function updateCharts(data) {

    const churnCanvas = document.getElementById("churnChart");

    const riskCanvas = document.getElementById("riskChart");


    if (churnChart) {
        churnChart.destroy();
    }

    if (riskChart) {
        riskChart.destroy();
    }


    churnChart = new Chart(churnCanvas, {

        type: "doughnut",

        data: {
            labels: ["Churned", "Retained"],

            datasets: [{
                data: [
                    data.churned_customers,
                    data.retained_customers
                ],

                backgroundColor: [
                    "#A66B5B",
                    "#77835F"
                ]
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false
        }

    });


    const risk = data.risk_distribution;

    riskChart = new Chart(riskCanvas, {

        type: "pie",

        data: {
            labels: ["Low Risk", "Medium Risk", "High Risk"],

            datasets: [{
                data: [
                    risk.Low,
                    risk.Medium,
                    risk.High
                ],

                backgroundColor: [
                    "#77835F",
                    "#D8B76B",
                    "#A66B5B"
                ]
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false
        }

    });

}


// =====================================================
// REFRESH DASHBOARD
// =====================================================

async function refreshDashboard() {

    await loadDashboard();

    await loadTopCustomers();

    await loadCustomerRecords(currentPage);

}


// =====================================================
// TOP 20 CUSTOMERS
// =====================================================

async function loadTopCustomers() {

    try {

        const response = await fetch(`${API_URL}/top-customers`);

        const customers = await response.json();

        const table = document.getElementById("top-customers-table");

        table.innerHTML = "";

        if (customers.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="6">No churn customers found.</td>
                </tr>
            `;

            return;
        }


        customers.forEach(customer => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${customer.id}</td>
                <td>${escapeHTML(customer.customer_name)}</td>
                <td>${escapeHTML(customer.Contract)}</td>
                <td>${customer.tenure} months</td>
                <td>${customer.ChurnProbability}%</td>
                <td class="${getRiskClass(customer.RiskLevel)}">
                    ${escapeHTML(customer.RiskLevel)}
                </td>
            `;

            table.appendChild(row);

        });

    } catch (error) {

        console.error("Top customers error:", error);

    }

}


// =====================================================
// CUSTOMER SEARCH
// =====================================================

async function loadCustomerRecords(page = 1) {

    currentPage = page;

    perPage = Number(document.getElementById("per-page").value);

    try {

        const params = new URLSearchParams({

            search: currentSearch,

            search_by: currentSearchBy,

            page: currentPage,

            per_page: perPage

        });


        const response = await fetch(
            `${API_URL}/customers/search?${params}`
        );

        if (!response.ok) {
            throw new Error("Unable to load customer records");
        }

        const data = await response.json();

        const table = document.getElementById("customer-table");

        table.innerHTML = "";

        totalPages = data.total_pages;


        document.getElementById("records-info").textContent =
            `Showing ${data.customers.length} of ${data.total} matching customers`;


        document.getElementById("page-info").textContent =
            `Page ${currentPage} of ${totalPages || 1}`;


        document.getElementById("previous-btn").disabled =
            currentPage <= 1;

        document.getElementById("next-btn").disabled =
            currentPage >= totalPages;


        if (data.customers.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="8">No matching customers found.</td>
                </tr>
            `;

            return;
        }


        data.customers.forEach(customer => {

            const row = document.createElement("tr");

            row.innerHTML = `

                <td>${customer.id}</td>

                <td>${escapeHTML(customer.customer_name)}</td>

                <td>${escapeHTML(customer.Contract)}</td>

                <td>${customer.tenure} months</td>

                <td class="${getPredictionClass(customer.ChurnPrediction)}">
                    ${escapeHTML(customer.ChurnPrediction)}
                </td>

                <td>${customer.ChurnProbability}%</td>

                <td class="${getRiskClass(customer.RiskLevel)}">
                    ${escapeHTML(customer.RiskLevel)}
                </td>

                <td>
                    <button
                        class="delete-btn"
                        onclick="deleteCustomer(${customer.id})">
                        Delete
                    </button>
                </td>

            `;

            table.appendChild(row);

        });

    } catch (error) {

        console.error("Customer records error:", error);

        document.getElementById("records-info").textContent =
            "Unable to load customer records.";

    }

}


// =====================================================
// SEARCH CATEGORY BUTTONS
// =====================================================

document.querySelectorAll(".search-option").forEach(button => {

    button.addEventListener("click", function() {

        document.querySelectorAll(".search-option").forEach(option => {

            option.classList.remove("active");

        });

        this.classList.add("active");

        currentSearchBy = this.dataset.search;

        const input = document.getElementById("customer-search");

        const placeholders = {

            name: "Enter customer name...",

            id: "Enter customer ID...",

            contract: "Enter contract: Month-to-month, One year, Two year...",

            risk: "Enter risk: Low, Medium, High...",

            all: "Search across all available fields..."

        };

        input.placeholder = placeholders[currentSearchBy];

        input.value = "";

        currentSearch = "";

        loadCustomerRecords(1);

    });

});


// =====================================================
// SEARCH BUTTON
// =====================================================

document.getElementById("search-btn").addEventListener("click", function() {

    currentSearch = document.getElementById("customer-search").value.trim();

    loadCustomerRecords(1);

});


// =====================================================
// ENTER KEY SEARCH
// =====================================================

document.getElementById("customer-search").addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        currentSearch = this.value.trim();

        loadCustomerRecords(1);

    }

});


// =====================================================
// CLEAR SEARCH
// =====================================================

document.getElementById("clear-search-btn").addEventListener("click", function() {

    document.getElementById("customer-search").value = "";

    currentSearch = "";

    currentPage = 1;

    loadCustomerRecords(1);

});


// =====================================================
// RECORDS PER PAGE
// =====================================================

document.getElementById("per-page").addEventListener("change", function() {

    perPage = Number(this.value);

    loadCustomerRecords(1);

});


// =====================================================
// PREVIOUS PAGE
// =====================================================

document.getElementById("previous-btn").addEventListener("click", function() {

    if (currentPage > 1) {

        loadCustomerRecords(currentPage - 1);

    }

});


// =====================================================
// NEXT PAGE
// =====================================================

document.getElementById("next-btn").addEventListener("click", function() {

    if (currentPage < totalPages) {

        loadCustomerRecords(currentPage + 1);

    }

});


// =====================================================
// DELETE CUSTOMER
// =====================================================

async function deleteCustomer(customerId) {

    const confirmation = confirm(
        `Are you sure you want to delete customer ID ${customerId}?`
    );

    if (!confirmation) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/customers/${customerId}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        if (!response.ok) {

            alert(result.error || "Unable to delete customer");

            return;

        }

        alert("Customer deleted successfully!");

        await refreshDashboard();

    } catch (error) {

        console.error("Delete error:", error);

        alert("Something went wrong while deleting the customer.");

    }

}


// =====================================================
// ADD CUSTOMER AND PREDICT
// =====================================================

document.getElementById("customer-form").addEventListener("submit", async function(event) {

    event.preventDefault();

    const form = event.target;

    const formData = new FormData(form);

    const customer = Object.fromEntries(formData.entries());


    customer.SeniorCitizen = Number(customer.SeniorCitizen);

    customer.tenure = Number(customer.tenure);

    customer.MonthlyCharges = Number(customer.MonthlyCharges);

    customer.TotalCharges = Number(customer.TotalCharges);


    try {

        const response = await fetch(`${API_URL}/add-customer`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(customer)

        });


        const result = await response.json();


        if (!response.ok) {

            alert(result.error || "Unable to add customer");

            return;

        }


        document.getElementById("prediction-result").textContent =
            result.prediction === "Yes"
                ? "Customer Likely to Churn"
                : "Customer Likely to Stay";


        document.getElementById("prediction-probability").textContent =
            result.probability + "%";


        document.getElementById("prediction-risk").textContent =
            result.risk;


        alert("Customer added and prediction generated successfully!");


        form.reset();

        await refreshDashboard();

        document.getElementById("prediction").scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        console.error("Prediction error:", error);

        alert("Unable to connect to the backend.");

    }

});


// =====================================================
// HELPER FUNCTIONS
// =====================================================

function getRiskClass(risk) {

    if (risk === "High") {
        return "risk-high";
    }

    if (risk === "Medium") {
        return "risk-medium";
    }

    return "risk-low";

}


function getPredictionClass(prediction) {

    return prediction === "Yes"
        ? "prediction-yes"
        : "prediction-no";

}


function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, character => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];

    });

}


// =====================================================
// INITIAL PAGE LOAD
// =====================================================

document.addEventListener("DOMContentLoaded", async function() {

    await loadDashboard();

    await loadTopCustomers();

    await loadCustomerRecords(1);

});