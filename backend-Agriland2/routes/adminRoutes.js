const express = require('express')
const router = express.Router();
const AdminSettings = require('../models/adminsetting');  // Import the model
const User = require('../models/User'); 

// POST route to save form data
router.post('/admin_panel/settings', async (req, res) => {
    try {
        console.log(req.body);
        const newSettings = new AdminSettings(req.body);
        await newSettings.save();
        res.status(201).json({ message: 'Settings saved successfully!' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to save settings' });
    }
});

router.get('admin/manage_users', async (req, res) => {
    try {
        const users = await User.find();  // Find all users in manage_users collection
        res.json(users);  // Send the retrieved data as JSON
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch users' });
    }

});

// Export the router
module.exports = router;