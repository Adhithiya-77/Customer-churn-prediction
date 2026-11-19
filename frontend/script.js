// ==========================================
// CONFIGURATION
// ==========================================

const API_URL = "http://127.0.0.1:5000";

let churnChart = null;
let riskChart = null;
let contractChart = null;
let tenureChart = null;

let customerRecords = [];


// ==========================================
// 1. FETCH CUSTOMERS FROM DATABASE
// ==========================================

async function fetchCustomers() {

    const response = await fetch(`${API_URL}/customers`);

    if (!response.ok) {
        throw new Error("Unable to fetch customers");
    }

    return await response.json();

}


// ==========================================
// 2. UPDATE DASHBOARD STATISTICS
// ==========================================

function updateStatistics(customers) {

    const total = customers.length;

    const churned = customers.filter(
        customer => customer.ChurnPrediction === "Yes"
    ).length;

    const retained = customers.filter(
        customer => customer.ChurnPrediction === "No"
    ).length;

    const highRisk = customers.filter(
        customer => customer.RiskLevel === "High"
    ).length;


    document.getElementById("total-customers").textContent = total;

    document.getElementById("churned-customers").textContent = churned;

    document.getElementById("retained-customers").textContent = retained;

    document.getElementById("high-risk").textContent = highRisk;

}


// ==========================================
// 3. CHURN DISTRIBUTION CHART
// ==========================================

function createChurnChart(customers) {

    const churned = customers.filter(
        customer => customer.ChurnPrediction === "Yes"
    ).length;

    const retained = customers.filter(
        customer => customer.ChurnPrediction === "No"
    ).length;


    if (churnChart) {
        churnChart.destroy();
    }


    churnChart = new Chart(
        document.getElementById("churnChart"),
        {

            type: "doughnut",

            data: {

                labels: ["Churned", "Retained"],

                datasets: [{

                    data: [churned, retained],

                    backgroundColor: [
                        "#9b6658",
                        "#737f5b"
                    ],

                    borderWidth: 2,

                    borderColor: "#ffffff"

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        position: "bottom"
                    }

                }

            }

        }
    );

}


// ==========================================
// 4. CUSTOMER RISK DISTRIBUTION CHART
// ==========================================

function createRiskChart(customers) {

    const low = customers.filter(
        customer => customer.RiskLevel === "Low"
    ).length;

    const medium = customers.filter(
        customer => customer.RiskLevel === "Medium"
    ).length;

    const high = customers.filter(
        customer => customer.RiskLevel === "High"
    ).length;


    if (riskChart) {
        riskChart.destroy();
    }


    riskChart = new Chart(
        document.getElementById("riskChart"),
        {

            type: "pie",

            data: {

                labels: [
                    "Low Risk",
                    "Medium Risk",
                    "High Risk"
                ],

                datasets: [{

                    data: [low, medium, high],

                    backgroundColor: [
                        "#737f5b",
                        "#d5b56b",
                        "#9b6658"
                    ]

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        position: "bottom"
                    }

                }

            }

        }
    );

}


// ==========================================
// 5. CONTRACT-WISE CHURN CHART
// ==========================================

function createContractChart(customers) {

    const contracts = [
        "Month-to-month",
        "One year",
        "Two year"
    ];


    const churned = contracts.map(contract => {

        return customers.filter(customer =>

            customer.Contract === contract &&
            customer.ChurnPrediction === "Yes"

        ).length;

    });


    const retained = contracts.map(contract => {

        return customers.filter(customer =>

            customer.Contract === contract &&
            customer.ChurnPrediction === "No"

        ).length;

    });


    if (contractChart) {
        contractChart.destroy();
    }


    contractChart = new Chart(
        document.getElementById("contractChart"),
        {

            type: "bar",

            data: {

                labels: contracts,

                datasets: [

                    {
                        label: "Churned",
                        data: churned,
                        backgroundColor: "#9b6658"
                    },

                    {
                        label: "Retained",
                        data: retained,
                        backgroundColor: "#737f5b"
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }

                }

            }

        }
    );

}


// ==========================================
// 6. CUSTOMER TENURE ANALYSIS CHART
// ==========================================

function createTenureChart(customers) {

    const labels = [
        "0–12 Months",
        "13–24 Months",
        "25–36 Months",
        "37–48 Months",
        "49–60 Months",
        "61–72 Months"
    ];


    const counts = [

        customers.filter(
            customer => customer.tenure >= 0 &&
                        customer.tenure <= 12
        ).length,

        customers.filter(
            customer => customer.tenure >= 13 &&
                        customer.tenure <= 24
        ).length,

        customers.filter(
            customer => customer.tenure >= 25 &&
                        customer.tenure <= 36
        ).length,

        customers.filter(
            customer => customer.tenure >= 37 &&
                        customer.tenure <= 48
        ).length,

        customers.filter(
            customer => customer.tenure >= 49 &&
                        customer.tenure <= 60
        ).length,

        customers.filter(
            customer => customer.tenure >= 61 &&
                        customer.tenure <= 72
        ).length

    ];


    if (tenureChart) {
        tenureChart.destroy();
    }


    tenureChart = new Chart(
        document.getElementById("tenureChart"),
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label: "Customers",

                    data: counts,

                    backgroundColor: "#737f5b",

                    borderRadius: 5

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }
                    }

                },

                plugins: {

                    legend: {
                        display: false
                    }

                }

            }

        }
    );

}


// ==========================================
// 7. TOP 20 CHURN CUSTOMERS
// ==========================================

function loadTopChurnCustomers(customers) {

    const table = document.getElementById("top-churn-table");

    table.innerHTML = "";


    const topCustomers = customers

        .filter(customer => customer.ChurnPrediction === "Yes")

        .sort((a, b) => {

            return Number(b.ChurnProbability) -
                   Number(a.ChurnProbability);

        })

        .slice(0, 20);


    if (topCustomers.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    No churn-risk customers found.
                </td>
            </tr>
        `;

        return;

    }


    topCustomers.forEach(customer => {

        const row = document.createElement("tr");


        const values = [

            customer.id,

            customer.customer_name,

            customer.Contract,

            `${customer.tenure} months`,

            `${customer.ChurnProbability}%`,

            customer.RiskLevel

        ];


        values.forEach(value => {

            const cell = document.createElement("td");

            cell.textContent = value ?? "";

            row.appendChild(cell);

        });


        table.appendChild(row);

    });

}


// ==========================================
// 8. DISPLAY CUSTOMER RECORDS
// ==========================================

function loadCustomerTable(customers) {

    const table = document.getElementById("customer-table");

    table.innerHTML = "";


    if (customers.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="8">
                    No matching customers found.
                </td>
            </tr>
        `;

        return;

    }


    customers.forEach(customer => {

        const row = document.createElement("tr");


        const values = [

            customer.id,

            customer.customer_name,

            customer.Contract,

            `${customer.tenure} months`,

            customer.ChurnPrediction,

            `${customer.ChurnProbability}%`,

            customer.RiskLevel

        ];


        values.forEach(value => {

            const cell = document.createElement("td");

            cell.textContent = value ?? "";

            row.appendChild(cell);

        });


        // DELETE BUTTON

        const actionCell = document.createElement("td");

        const deleteButton = document.createElement("button");

        deleteButton.textContent = "Delete";

        deleteButton.className = "delete-btn";


        deleteButton.addEventListener("click", () => {

            deleteCustomer(customer.id);

        });


        actionCell.appendChild(deleteButton);

        row.appendChild(actionCell);

        table.appendChild(row);

    });

}


// ==========================================
// 9. CUSTOMER SEARCH
// ==========================================

function searchCustomers() {

    const input = document.getElementById("customer-search");

    const query = input.value.trim().toLowerCase();

    const count = document.getElementById("search-count");


    if (!query) {

        document.getElementById("customer-table").innerHTML = `
            <tr>
                <td colspan="8">
                    Please enter a search value.
                </td>
            </tr>
        `;

        count.textContent = "Enter a customer detail to search.";

        return;

    }


    const filteredCustomers = customerRecords.filter(customer => {

        return Object.values(customer).some(value => {

            return String(value ?? "")
                .toLowerCase()
                .includes(query);

        });

    });


    loadCustomerTable(filteredCustomers);


    count.textContent =
        `Found ${filteredCustomers.length} matching customer(s).`;

}


// ==========================================
// 10. CLEAR SEARCH
// ==========================================

function clearSearch() {

    document.getElementById("customer-search").value = "";


    document.getElementById("customer-table").innerHTML = `
        <tr>
            <td colspan="8">
                Search for a customer to display records.
            </td>
        </tr>
    `;


    document.getElementById("search-count").textContent =
        "Search for a customer to view records.";

}


// ==========================================
// 11. DELETE CUSTOMER
// ==========================================

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

            throw new Error(
                result.error || "Unable to delete customer"
            );

        }


        alert("Customer deleted successfully!");


        // Reload database information

        await refreshDashboard();

    }

    catch (error) {

        console.error("Delete error:", error);

        alert(error.message);

    }

}


// ==========================================
// 12. REFRESH DASHBOARD
// ==========================================

async function refreshDashboard() {

    try {

        const customers = await fetchCustomers();

        customerRecords = customers;


        // Update statistics

        updateStatistics(customers);


        // Update charts

        createChurnChart(customers);

        createRiskChart(customers);

        createContractChart(customers);

        createTenureChart(customers);


        // Update Top 20 customers

        loadTopChurnCustomers(customers);


        // Keep Customer Records empty until searched

        clearSearch();


        console.log("Dashboard refreshed successfully");

    }

    catch (error) {

        console.error("Dashboard error:", error);

    }

}


// ==========================================
// 13. DISPLAY PREDICTION RESULT
// ==========================================

function displayPrediction(data) {

    document.getElementById("prediction-result").textContent =

        data.prediction === "Yes"
            ? "Customer Likely to Churn"
            : "Customer Likely to Stay";


    document.getElementById("prediction-probability").textContent =

        `${data.probability}%`;


    document.getElementById("prediction-risk").textContent =

        data.risk;

}


// ==========================================
// 14. ADD CUSTOMER FORM
// ==========================================

document.getElementById("customer-form").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const form = event.target;

        const message = document.getElementById("form-message");

        const button = form.querySelector(
            'button[type="submit"]'
        );


        const formData = new FormData(form);

        const customerData = Object.fromEntries(
            formData.entries()
        );


        // Convert numeric fields

        customerData.SeniorCitizen =
            Number(customerData.SeniorCitizen);

        customerData.tenure =
            Number(customerData.tenure);

        customerData.MonthlyCharges =
            Number(customerData.MonthlyCharges);

        customerData.TotalCharges =
            Number(customerData.TotalCharges);


        try {

            button.disabled = true;

            button.textContent = "Processing...";

            message.textContent = "Generating prediction...";


            const response = await fetch(
                `${API_URL}/add-customer`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(customerData)

                }
            );


            const result = await response.json();


            if (!response.ok) {

                throw new Error(
                    result.error ||
                    result.message ||
                    "Customer submission failed"
                );

            }


            // Display prediction

            displayPrediction(result);


            message.textContent =
                "Customer added successfully!";


            // Reset form

            form.reset();


            // Refresh dashboard

            await refreshDashboard();

        }

        catch (error) {

            console.error("Submission error:", error);

            message.textContent = error.message;

        }

        finally {

            button.disabled = false;

            button.textContent = "Predict Customer Churn";

        }

    }

);


// ==========================================
// 15. INITIALIZE APPLICATION
// ==========================================

document.addEventListener("DOMContentLoaded", () => {


    // Search button

    document.getElementById("search-btn").addEventListener(
        "click",
        searchCustomers
    );


    // Press Enter to search

    document.getElementById("customer-search").addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Enter") {

                searchCustomers();

            }

        }
    );


    // Clear button

    document.getElementById("clear-search").addEventListener(
        "click",
        clearSearch
    );


    // Load dashboard

    refreshDashboard();

});