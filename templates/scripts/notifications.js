document.addEventListener('DOMContentLoaded', function () {
    // Mock notification data
    const notifications = [
        { message: "New lease agreement signed!", status: "unread" },
        { message: "Land listing expired", status: "read" },
        { message: "Payment received for your land listing", status: "unread" },
        { message: "Lease expiring in 3 days", status: "read" }
    ]

    // Function to render notifications
    function renderNotifications() {
        const notificationList = document.getElementById('notification-list')
        notificationList.innerHTML = '' // Clear the list first

        notifications.forEach(notification => {
            const listItem = document.createElement('li')
            listItem.textContent = notification.message

            // Add a class based on read/unread status
            if (notification.status === "unread") {
                listItem.classList.add('unread-notification')
            }

            notificationList.appendChild(listItem)
        })
    }

    // Call the function to render the notifications
    renderNotifications()
})
