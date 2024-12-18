from flask import Flask, render_template, jsonify, request
from data_fetcher import fetch_device_metrics, fetch_interface_metrics, fetch_network_info  # Import your data-fetching function
import subprocess
from flask_cors import CORS

# Set the template and static folders to point to the frontend folder
app = Flask(
    __name__,
    template_folder="../frontend/templates",  # Path to templates folder
    static_folder="../frontend/static"         # Path to static folder (for JS, CSS, etc.)
)
CORS(app, resources={r"/*": {"origins": "*"}})


################## INDEX PAGE (DEVICE METRICS) ####################
@app.route('/')
def home():
    # Render the index page (this will load the frontend)
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    # Fetch device metrics (from the data_fetcher function)
    device_metrics = fetch_device_metrics()
    
    # If you have other metrics (e.g., network stats), you can merge them here
    # Example:
    # network_metrics = fetch_network_metrics()
    # all_metrics = {**device_metrics, **network_metrics}

    all_metrics = {**device_metrics}  # Combine all metrics into one dictionary
    
    # Return the combined metrics as a JSON response
    return jsonify(all_metrics)






################## INTERFACE PAGE #######################
@app.route('/interface_metrics')
def network_metrics():
    # Fetch network data (totals and interface metrics)
    totals_metrics, interface_metrics = fetch_interface_metrics()  # Unpack the two dictionaries
    
    # Return both totals_metrics and interface_metrics as JSON
    return jsonify({'totals_metrics': totals_metrics, 'interface_metrics': interface_metrics})


@app.route('/interfaces')
def interface():
    # Fetch network data (totals and interface metrics)
    totals_metrics, interface_metrics = fetch_interface_metrics()  # Now unpack the two dictionaries
    
    # Pass both totals_metrics and interface_metrics to the template
    return render_template('interfaces.html', totals_metrics=totals_metrics, interface_metrics=interface_metrics)






################################ NETWORKING PAGE #############################
@app.route('/network_metrics')
def network_info():
    network_information = fetch_network_info()  # Call the function by adding parentheses
    return jsonify(network_information)  # Return the fetched network information as JSON


@app.route('/networking')
def networking():
    network_information = fetch_network_info()
    return render_template('networking.html', network_information=network_information)


################################# GLOBAL PAGE ##############################
@app.route('/globe')
def globe():
    return render_template('global.html')

@app.route('/perform_tracert')
def perform_tracert():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "No domain provided"}), 400

    # Run the tracert/traceroute command
    result = subprocess.run(["traceroute", domain], capture_output=True, text=True)
    
    # Return the output as JSON
    return jsonify({
        "tracerouteResult": result.stdout
    })


# Ensure the app runs only if this script is called directly
if __name__ == "__main__":
    app.run(debug=True)





