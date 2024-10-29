document.getElementById('admin-settings-form').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior

    // Collect the form data
    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        name: document.getElementById('name').value,
        phone: document.getElementById('phone').value,
        userRole: document.getElementById('user-role').value,
        siteStatus: document.getElementById('site-status').value,
    };

    try {
        // Send form data to the backend using the Fetch API
        const response = await fetch('http://localhost:5000/admin/admin_panel/settings', { // Updated the URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        // Handle the response
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update settings');
    }
});
