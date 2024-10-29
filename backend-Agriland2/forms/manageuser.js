async function fetchUsers() {
    try {
        const response = await fetch('http://localhost:5000/admin/manage_users');  // Fetch data from the backend
        const users = await response.json();

        // Get the table body element
        const userTableBody = document.getElementById('userTableBody');

        // Clear any existing rows
        userTableBody.innerHTML = '';

        // Iterate over each user and create a new row in the table
        users.forEach((user, index) => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>${user.gender}</td>
                <td>${user.age}</td>
                <td>
                    <button>Edit</button>
                    <button>Delete</button>
                </td>
            `;

            userTableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

// Call the fetchUsers function when the page loads
window.onload = fetchUsers;
