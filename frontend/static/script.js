//////////////////////////////////Javascript for the updating of gathered metrics
// Device metrics
function updateMetrics() {
    fetch('/metrics')
        .then(response => response.json())
        .then(data => {
            if (data) {
                // Update or append dynamic CPU metrics
                document.getElementById('cpu-cores').innerText = data.cpu?.cpu_cores ?? 'N/A';
                document.getElementById('cpu-usage').innerText = data.cpu?.cpu_usage_percent ?? 'N/A';
                document.getElementById('cpu-frequency').innerText = `${data.cpu?.cpu_frequency?.current ?? 'N/A'} MHz (Min: ${data.cpu?.cpu_frequency?.min ?? 'N/A'} MHz, Max: ${data.cpu?.cpu_frequency?.max ?? 'N/A'} MHz)`;

                // Update disk metrics dynamically
                document.getElementById('disk-usage').innerText = `${data.disk?.disk_usage?.used ?? 'N/A'} / ${data.disk?.disk_usage?.total ?? 'N/A'} (${data.disk?.disk_usage?.percent ?? 'N/A'}% used)`;
                document.getElementById('disk-io-read').innerText = `Read: ${data.disk?.disk_io?.read_bytes ?? 'N/A'} bytes`;
                document.getElementById('disk-io-write').innerText = `Write: ${data.disk?.disk_io?.write_bytes ?? 'N/A'} bytes`;

                // Update memory metrics
                document.getElementById('memory-total').innerText = `${((data.memory?.virtual_memory?.total ?? 0) / (1024 ** 3)).toFixed(2)} GB`;
                document.getElementById('memory-used').innerText = `${((data.memory?.virtual_memory?.used ?? 0) / (1024 ** 3)).toFixed(2)} GB`;
                document.getElementById('memory-free').innerText = `${((data.memory?.virtual_memory?.free ?? 0) / (1024 ** 3)).toFixed(2)} GB`;

                // Update system metrics
                document.getElementById('boot-time').innerText = data.system?.boot_time ?? 'N/A';
                document.getElementById('load-average').innerText = `1 min: ${data.system?.load_average?.[0] ?? 'N/A'}, 5 min: ${data.system?.load_average?.[1] ?? 'N/A'}, 15 min: ${data.system?.load_average?.[2] ?? 'N/A'}`;

                // Update GPU metrics
                if (data.gpu) {
                    document.getElementById('gpu-usage').innerText = `${data.gpu?.gpu_usage_percent ?? 'N/A'}% GPU usage`;
                    document.getElementById('gpu-memory-usage').innerText = `${data.gpu?.gpu_memory_usage_percent ?? 'N/A'}% GPU memory usage`;
                } else {
                    document.getElementById('gpu-info').innerText = 'No GPU data available';
                }
            } else {
                console.error("Invalid data received from /metrics endpoint.");
            }
        })
        .catch(error => console.error('Error fetching metrics:', error));
    // Interface metrics gathering
    fetch('/interface_metrics')
        .then(response => response.json())
        .then(networkData => {
            const networkContainer = document.getElementById('network-metrics');
            // Update only dynamic elements
            Object.keys(networkData).forEach(interface => {
                let existingElement = document.querySelector(`[data-interface="${interface}"]`);

                if (!existingElement) {
                    // Create a new element if it doesn't exist
                    existingElement = document.createElement('div');
                    existingElement.classList.add('network-interface');
                    existingElement.setAttribute('data-interface', interface);
                    networkContainer.appendChild(existingElement);
                }

                // Update dynamic content inside the existing element
                existingElement.innerHTML = `
                    <h3>Interface Name: ${interface}</h3>
                    <p><strong>Status:</strong> ${networkData[interface].status}</p>
                    <p><strong>IP Address:</strong> ${networkData[interface].ip_address || 'N/A'}</p>
                    <p><strong>Bytes Received:</strong> ${networkData[interface].bytes_received}</p>
                    <p><strong>Bytes Sent:</strong> ${networkData[interface].bytes_sent}</p>
                    <p><strong>Packets Received:</strong> ${networkData[interface].packets_received}</p>
                    <p><strong>Packets Sent:</strong> ${networkData[interface].packets_sent}</p>
                    <p><strong>Speed:</strong> ${networkData[interface].speed}</p>
                    <p><strong>Input Errors:</strong> ${networkData[interface].input_errors}</p>
                    <p><strong>Output Errors:</strong> ${networkData[interface].output_errors}</p>
                `;
            });

            initializeTooltips(); // Reapply tooltips to updated elements
        })
        .catch(error => console.error('Error fetching network metrics:', error));
}

// Fetch metrics every 5 seconds
setInterval(updateMetrics, 5000);







//////////////////////////////////////////////////////////Tooltips javascript
// Initialize tooltips on page load and reapply after updates
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        // Add your tooltip logic here
        el.addEventListener('mouseover', () => {
            // Show tooltip
        });
        el.addEventListener('mouseout', () => {
            // Hide tooltip
        });
    });
}
// Run updates and initialize tooltips when the page loads
document.addEventListener('DOMContentLoaded', () => {
    updateMetrics();
    initializeTooltips();
});







////////////////////////////////////////////Network information
// Fetch network data
fetch('/network_info')
    .then(response => response.json())
    .then(networkData => {
        if (networkData.error) {
            console.error(networkData.error);
            alert("Error fetching network info!");
        } else {
            // Update the UI with network info
            const networkContainer = document.getElementById('network-metrics');
            networkContainer.innerHTML = `
                <h3>Network Information</h3>
                <p><strong>SSID:</strong> ${networkData.SSID}</p>
                <p><strong>IP Address:</strong> ${networkData["IP Address"]}</p>
                <p><strong>Encryption:</strong> ${networkData.Encryption}</p>
                <p><strong>Public IP:</strong> ${networkData["Public IP"]}</p>
                <p><strong>Latency:</strong> ${networkData.Latency} ms</p>
            `;
        }
    })
    .catch(error => {
        console.error('Error fetching network info:', error);
    });
// JavaScript to update the blue box content when hovering over items
document.addEventListener('DOMContentLoaded', function() {
    const hoverItems = document.querySelectorAll('#network-info .hover-item');
    const blueBox = document.querySelector('#network-info-blue p');

    hoverItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const infoText = item.getAttribute('data-info');
            blueBox.textContent = infoText; // Update the text inside the blue box
        });
        
        item.addEventListener('mouseleave', function() {
            blueBox.textContent = 'Hover over an item on the left to learn more about it!'; // Reset the text
        });
    });
});





/////////////////////////////////////////////////////////////Blue box display stuff
document.querySelectorAll('.hover-item').forEach(item => {
    item.addEventListener('mouseenter', function() {
        // Get the content from data-info attribute and replace <br> with newline
        let tooltipText = this.getAttribute('data-info').replace(/<br>/g, '\n');
        
        // Find the #network-info-blue and update the tooltip content
        let tooltip = document.querySelector('#network-info-blue p');
        tooltip.textContent = tooltipText;  // Use textContent to avoid rendering HTML
    });

    // Reset the tooltip when the mouse leaves the item
    item.addEventListener('mouseleave', function() {
        let tooltip = document.querySelector('#network-info-blue p');
        tooltip.textContent = "Hover over an item on the left to learn more about it!";
    });
});






///////////////////////////////////////////////////////////// GLOBAL PAGE STUFF

// Function to filter out private IPs
function isPrivateIP(ip) {
    const privateIpRegex = /^(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})$/;
    return privateIpRegex.test(ip);
}

// Wait for the DOM content to load
document.addEventListener("DOMContentLoaded", function() {
    // Handle the keydown event when the user presses Enter
    document.getElementById("command-input").addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            var userInput = document.getElementById("command-input").value;
            if (userInput) {
                // Show loading message
                document.getElementById("loading-message").style.display = "block";

                // Perform the traceroute operation
                performTraceroute(userInput);
            }
        }
    });

    // Function to perform traceroute by making an AJAX request to the server
    function performTraceroute(domain) {
        fetch(`/perform_tracert?domain=${domain}`)
            .then(response => response.json())
            .then(data => {
                // Hide loading message
                document.getElementById("loading-message").style.display = "none";

                // Display traceroute results
                document.getElementById("result-display").textContent = data.tracerouteResult;

                // Extract IPs from the traceroute result
                var ipAddresses = extractIps(data.tracerouteResult);

                // Clear previous IP list
                document.getElementById("ip-list-container").innerHTML = '';

                // Get geolocation for each IP address
                ipAddresses.forEach(function(ip) {
                    // Skip private IPs
                    if (!isPrivateIP(ip)) {
                        getGeolocation(ip);
                    } else {
                        var locationInfo = `${ip} - Private IP (No geolocation)`;
                        displayIpLocation(locationInfo);
                    }
                });
            })
            .catch(error => {
                // Hide loading message
                document.getElementById("loading-message").style.display = "none";
                
                console.error("Error fetching traceroute:", error);
                document.getElementById("result-display").textContent = "Error performing traceroute.";
            });
    }

    // Extract IPs from traceroute results using a regex
    function extractIps(tracerouteResult) {
        var ips = [];
        var regex = /\((\d+\.\d+\.\d+\.\d+)\)/g;
        var match;
        while ((match = regex.exec(tracerouteResult)) !== null) {
            ips.push(match[1]);
        }
        return ips;
    }

    // Fetch the geographical location for an IP
    function getGeolocation(ip) {
        fetch(`https://ipinfo.io/${ip}/json?token=f60020a1638ef3`)  // Use your API key here
            .then(response => response.json())
            .then(data => {
                var locationInfo = `${data.ip} - ${data.city}, ${data.region}, ${data.country}`;
                displayIpLocation(locationInfo);
            })
            .catch(error => {
                console.error("Error fetching IP geolocation:", error);
                var locationInfo = `${ip} - Location not found`;
                displayIpLocation(locationInfo);
            });
    }

    // Display IP and its geolocation
    function displayIpLocation(locationInfo) {
        var listItem = document.createElement("li");
        listItem.textContent = locationInfo;
        document.getElementById("ip-list-container").appendChild(listItem);
    }
});



//////////////////////////////////////////Recurring commands
// Fetch data every 5 seconds
setInterval(() => {
    updateMetrics();
    initializeTooltips(); // Reapply tooltips
}, 5000);

// Run the function immediately when the page loads
updateMetrics();
