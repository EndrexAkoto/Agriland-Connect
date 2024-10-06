document.addEventListener("DOMContentLoaded", function() {
    console.log("Admin Panel Loaded")

    // Example: Fetching Dashboard Data (placeholder)
    fetchDashboardData()
})

// Example function to fetch dashboard data
function fetchDashboardData() {
    // Simulated data fetching (replace with your API call)
    const dashboardData = {
        totalUsers: 120,
        totalListings: 58,
        activeLeases: 45,
        pendingPayments: 5,
        newUsers: 20,
        farmers: 80,
        landowners: 40,
        genderDistribution: "Male: 70%, Female: 30%",
        ageBracket: "18-25: 30%, 26-35: 50%, 36-50: 20%"
    }

    // Update the dashboard metrics
    document.getElementById("totalUsers").innerText = dashboardData.totalUsers
    document.getElementById("totalListings").innerText = dashboardData.totalListings
    document.getElementById("activeLeases").innerText = dashboardData.activeLeases
    document.getElementById("pendingPayments").innerText = dashboardData.pendingPayments

    // Update user statistics
    document.getElementById("userCount").innerText = dashboardData.totalUsers
    document.getElementById("newUserCount").innerText = dashboardData.newUsers
    document.getElementById("farmersCount").innerText = dashboardData.farmers
    document.getElementById("landownersCount").innerText = dashboardData.landowners
    document.getElementById("genderDistribution").innerText = dashboardData.genderDistribution
    document.getElementById("ageBracket").innerText = dashboardData.ageBracket
    document.getElementById("activeLeasesCount").innerText = dashboardData.activeLeases
    document.getElementById("pendingPaymentsCount").innerText = dashboardData.pendingPayments
}

// Filter users based on input in the search box
function filterUsers() {
    const searchInput = document.getElementById("searchUser").value.toLowerCase()
    const userRows = document.querySelectorAll("#userTableBody tr")

    userRows.forEach(row => {
        const cells = row.getElementsByTagName("td")
        let match = false
        for (let i = 1; i < cells.length - 1; i++) { // skip ID and Action
            if (cells[i].innerText.toLowerCase().includes(searchInput)) {
                match = true
            }
        }
        row.style.display = match ? "" : "none"
    })
}

// Burger Menu Toggle
const burger = document.querySelector('.burger')
const navLinks = document.querySelector('.nav-links')

burger.addEventListener('click', () => {
    navLinks.classList.toggle('active')
})
