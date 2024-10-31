from flask import Blueprint, render_template, request
from models.land import land_collection  # Import your land model

land_routes = Blueprint('land', __name__)

@land_routes.route("/landlord.html", methods=['GET', 'POST'])
def landlord():
    msg = ''
    if request.method == 'POST':
        land_size = request.form.get('landSize')
        location = request.form.get('location')
        price_per_acre = request.form.get('pricePerAcre')
        amenities = request.form.get('amenities')
        road_access = request.form.get('roadAccess')
        fencing = request.form.get('fencing')
        title_deed = request.form.get('titleDeed')
        lease_duration = request.form.get('leaseDuration')
        payment_frequency = request.form.get('paymentFrequency')

        file = request.files.get('farmImages')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            land_data = {
                'land_size': land_size,
                'location': location,
                'price_per_acre': price_per_acre,
                'amenities': amenities,
                'road_access': road_access,
                'fencing': fencing,
                'title_deed': title_deed,
                'lease_duration': lease_duration,
                'payment_frequency': payment_frequency,
                'image': filename
            }
            add_land_listing(land_data)
            msg = 'Land listing created successfully!'
        else:
            msg = 'Please fill out all fields and upload a valid image!'

    return render_template('landlord.html', msg=msg)

@land_routes.route("/land-listings.html")
def land_listings():
    listings = get_all_land_listings()
    return render_template('land-listings.html', listings=listings)
