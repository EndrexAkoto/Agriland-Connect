// Mock data for land listings
const landListings = [
    { title: "Land in Nairobi", description: "2 acres, ideal for farming.", location: "Nairobi", size: "2 acres" },
    { title: "Land in Nakuru", description: "5 acres, near the lake.", location: "Nakuru", size: "5 acres" },
    { title: "Land in Kisumu", description: "1 acre, great for crops.", location: "Kisumu", size: "1 acre" },
]

// Function to display land listings
function displayLandListings() {
    const landCards = document.getElementById("land-cards")
    landListings.forEach(land => {
        const card = document.createElement("div")
        card.className = "land-card"
        card.innerHTML = `<h2>${land.title}</h2><p>${land.description}</p><p>Location: ${land.location}</p><p>Size: ${land.size}</p>`
        landCards.appendChild(card)
    })
}

// Search functionality
function searchLand() {
    const searchValue = document.getElementById("search").value.toLowerCase()
    const filteredListings = landListings.filter(land => 
        land.location.toLowerCase().includes(searchValue) || 
        land.size.toLowerCase().includes(searchValue) || 
        land.title.toLowerCase().includes(searchValue) || 
        land.description.toLowerCase().includes(searchValue)
    )

    const landCards = document.getElementById("land-cards")
    landCards.innerHTML = '' // Clear existing cards
    if (filteredListings.length > 0) {
        filteredListings.forEach(land => {
            const card = document.createElement("div")
            card.className = "land-card"
            card.innerHTML = `<h2>${land.title}</h2><p>${land.description}</p><p>Location: ${land.location}</p><p>Size: ${land.size}</p>`
            landCards.appendChild(card)
        })
    } else {
        landCards.innerHTML = '<p>No listings found matching your search criteria.</p>'
    }
}

// Populate lease history for the user profile
function populateLeaseHistory() {
    const leaseHistoryList = document.getElementById('lease-history-list')

    // Sample data for lease history
    const leaseHistory = [
        { id: 1, land: 'Farm A', date: '2024-01-15', status: 'Active' },
        { id: 2, land: 'Farm B', date: '2023-12-10', status: 'Expired' },
    ]

    leaseHistory.forEach(lease => {
        const listItem = document.createElement('li')
        listItem.textContent = `Lease for ${lease.land} started on ${lease.date} - Status: ${lease.status}`
        leaseHistoryList.appendChild(listItem)
    })
}

// Mock data for user leases, notifications, and payment statuses
const userLeases = [
    { id: 1, land: 'Farm A', date: '2024-01-15', status: 'Active' },
    { id: 2, land: 'Farm B', date: '2023-12-10', status: 'Expired' },
]

const notifications = [
    { message: 'Your lease for Farm A is expiring soon.' },
    { message: 'Payment for Farm B is due next week.' },
]

const paymentStatuses = [
    { land: 'Farm A', amount: '$500', status: 'Paid' },
    { land: 'Farm B', amount: '$300', status: 'Pending' },
]

// Populate lease list in the dashboard
function populateLeaseList() {
    const leaseList = document.getElementById('lease-list')
    userLeases.forEach(lease => {
        const listItem = document.createElement('li')
        listItem.textContent = `Lease for ${lease.land} started on ${lease.date} - Status: ${lease.status}`
        leaseList.appendChild(listItem)
    })
}

// Populate notifications in the dashboard
function populateNotifications() {
    const notificationList = document.getElementById('notification-list')
    notifications.forEach(notification => {
        const listItem = document.createElement('li')
        listItem.textContent = notification.message
        notificationList.appendChild(listItem)
    })
}

// Populate payment statuses in the dashboard
function populatePaymentStatuses() {
    const paymentList = document.getElementById('payment-list')
    paymentStatuses.forEach(payment => {
        const listItem = document.createElement('li')
        listItem.textContent = `Payment for ${payment.land} - Amount: ${payment.amount} - Status: ${payment.status}`
        paymentList.appendChild(listItem)
    })
}

// Mock function to simulate payment processing
function processPayment(land, amount, cardDetails) {
    // Simulate successful payment
    const paymentSuccess = true // You can toggle this for testing

    if (paymentSuccess) {
        return `Payment of $${amount} for ${land} was successful!`
    } else {
        return `Payment failed for ${land}. Please try again.`
    }
}

// Unified DOMContentLoaded Event to handle all onload tasks
document.addEventListener('DOMContentLoaded', function () {
    displayLandListings() // Load land listings

    if (document.getElementById('lease-history-list')) {
        populateLeaseHistory() // Populate lease history if element exists
    }

    if (document.getElementById('lease-list')) {
        populateLeaseList()      // Populate lease list
        populateNotifications()  // Populate notifications
        populatePaymentStatuses()// Populate payment statuses
    }

    const hamburgerMenu = document.getElementById('hamburger-menu')
    const navLinks = document.querySelector('.nav-links')

    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', function () {
            navLinks.classList.toggle('active') // Toggle the active class
        })
    }

    // Payment form submission
    const paymentForm = document.getElementById('payment-form')
    if (paymentForm) {
        paymentForm.addEventListener('submit', function (event) {
            event.preventDefault()

            const land = document.getElementById('land').value
            const amount = document.getElementById('amount').value
            const cardDetails = document.getElementById('card-details').value

            const message = processPayment(land, amount, cardDetails)
            document.getElementById('payment-message').textContent = message

            // Reset the form
            event.target.reset()
        })
    }
})
