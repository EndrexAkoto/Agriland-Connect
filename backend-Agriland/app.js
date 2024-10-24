const express = require('express');
const dotenv = require('dotenv');
// const mongoose = require('mongoose');
const path = require('path');
const userRoutes = require('./routes/userRoutes');
const adminRoutes = require('./routes/adminRoutes');
const landRoutes = require('./routes/landRoutes');

// Load environment variables from .env file
dotenv.config();

const app = express();
const frontendPath = path.join(__dirname, '../frontend-Agriland');
app.set('views', frontendPath);
app.use(express.static(frontendPath));

// Middleware to parse incoming JSON requests
app.use(express.json());

// Database connection (similar to MongoClient in Flask)
// mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
//     .then(() => console.log('MongoDB Connected'))
//     .catch(err => console.log(err));

// Routes
app.use('/users', userRoutes);
app.use('/admin', adminRoutes);
app.use('/land', landRoutes);

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
