const mongoose = require('mongoose');

const LandSchema = new mongoose.Schema({
    land_size: String,
    location: String,
    price_per_acre: Number,
    amenities: String,
    road_access: Boolean,
    fencing: Boolean,
    title_deed: String,
    lease_duration: String,
    payment_frequency: String,
    farm_image: String,
});

module.exports = mongoose.model('Land', LandSchema);
