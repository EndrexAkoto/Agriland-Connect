const mongoose = require('mongoose');

// Define schema for manage_users
const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    role: { type: String, required: true },
    gender: { type: String, required: true },
    age: { type: Number, required: true },
});

// Create a Mongoose model for manage_users
const User = mongoose.model('manage_users', userSchema);

module.exports = User;
