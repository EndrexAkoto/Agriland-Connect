const mongoose = require('mongoose');

const AdminSettingsSchema = new mongoose.Schema({
    email: { type: String, required: true },
    password: { type: String, required: true },
    name: { type: String, required: true },
    phone: { type: String, required: true },
    userRole: { type: String, required: true },
    siteStatus: { type: String, required: true },
});

const AdminSettings = mongoose.model('AdminSettings', AdminSettingsSchema);

module.exports = AdminSettings;
