const express = require('express');
const router = express.Router();

// Define your routes
router.get('/', (req, res) => {
    res.send('Admin route');
});

// Export the router
module.exports = router;