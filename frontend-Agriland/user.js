document.addEventListener('DOMContentLoaded', function() {
    // Fetch users when the page loads
    fetch('/api/users')
        .then(response => response.json())
        .then(users => populateUserTable(users))
        .catch(error => console.error('Error fetching users:', error));
});

// Populate the user table
function populateUserTable(users) {
    const userTableBody = document.getElementById('userTableBody');
    userTableBody.innerHTML = ''; // Clear existing rows

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user._id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>${user.gender}</td>
            <td>${user.age}</td>
            <td>
                <button onclick="editUser('${user._id}')">Edit</button>
                <button onclick="deleteUser('${user._id}')">Delete</button>
            </td>
        `;
        userTableBody.appendChild(row);
    });
}

// Edit user function
function editUser(userId) {
    const userData = {
        name: prompt('Enter new name:'),
        email: prompt('Enter new email:'),
        role: prompt('Enter new role:'),
        gender: prompt('Enter new gender:'),
        age: prompt('Enter new age:')
    };

    fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload(); // Refresh page after update
    })
    .catch(error => console.error('Error updating user:', error));
}

// Delete user function
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload(); // Refresh page after deletion
        })
        .catch(error => console.error('Error deleting user:', error));
    }
}

// Search/filter users by name or other attributes
function filterUsers() {
    const filter = document.getElementById('searchUser').value.toLowerCase();
    const rows = document.getElementById('userTableBody').getElementsByTagName('tr');

    Array.from(rows).forEach(row => {
        const cells = row.getElementsByTagName('td');
        const name = cells[1].textContent.toLowerCase();
        if (name.includes(filter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}
