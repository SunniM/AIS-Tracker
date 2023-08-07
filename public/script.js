var map; // Declare the map variable
const url = window.location.href

function loadMap() {
  var mapOptions = {
    mapId: 'a9e21ced58ad4189',
    center: new google.maps.LatLng(45.3, -84),
    zoom: 7,
    disableDefaultUI: true
  };
  map = new google.maps.Map(document.getElementById("map"), mapOptions); // Create the map object

  // Function to update text fields with current coordinates
  function updateTextFields(latitude, longitude, zoom) {
    const latitudeInput = document.getElementById('latitude-input');
    const longitudeInput = document.getElementById('longitude-input');
    const zoomInput = document.getElementById('zoom-input')

    latitudeInput.value = latitude.toFixed(3);
    longitudeInput.value = longitude.toFixed(3);
    zoomInput.value = zoom
  }

  // Function to handle latitude input change
  function handleLatitudeChange() {
    const latitude = parseFloat(document.getElementById('latitude-input').value);

    if (!isNaN(latitude)) {
      const center = map.getCenter();
      const longitude = center.lng();

      map.setCenter({ lat: latitude, lng: longitude });
    }
  }

  // Function to handle longitude input change
  function handleLongitudeChange() {
    const longitude = parseFloat(document.getElementById('longitude-input').value);

    if (!isNaN(longitude)) {
      const center = map.getCenter();
      const latitude = center.lat();

      map.setCenter({ lat: latitude, lng: longitude });
    }
  }

  function handleZoomChange() {
    const zoom = parseFloat(document.getElementById('zoom-input').value)
    
    if (!isNaN(zoom)) {
      console.log(zoom)
      map.setZoom(zoom);
    }
    else {
      console.log("Invalid zoom value:", zoom);
    }
  }

  // Function to handle map drag event
  function handleMapChange() {
    const center = map.getCenter();
    const latitude = center.lat();
    const longitude = center.lng();
    const zoom = map.getZoom();

    updateTextFields(latitude, longitude, zoom);
  }

  // Add event listeners to latitude and longitude input fields
  document.getElementById('latitude-input').addEventListener('input', handleLatitudeChange);
  document.getElementById('longitude-input').addEventListener('input', handleLongitudeChange);
  document.getElementById('zoom-input').addEventListener('input', handleZoomChange);
  // Listen for 'dragend' event on the map
  map.addListener('dragend', handleMapChange);
  map.addListener('zoom_changed', handleMapChange);


  // Get the initial coordinates and update the text fields
  const initialCenter = map.getCenter();
  const initialLatitude = initialCenter.lat();
  const initialLongitude = initialCenter.lng();
  const initialzoom = map.getZoom();
  updateTextFields(initialLatitude, initialLongitude, initialzoom);

  // Function to handle button click
  document.getElementById('update-button').addEventListener('click', handleClick);
}

// Function to handle button click
function handleClick() {
  const box = document.getElementById("map");

  const center = map.getCenter();
  const data = {
    latitude: center.lat(),
    longitude: center.lng(),
    zoom: map.getZoom(),
    width: box.offsetWidth,
    height: box.offsetHeight
  };

  // Send the POST request
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(function (response) {
      if (response.ok) {
        console.log("Map data sent successfully");
      } else {
        throw new Error("Error sending map data");
      }
    })
    .catch(function (error) {
      console.error("Error sending map data:", error);
    });

  // Capture the map image using html2canvas
  html2canvas(document.getElementById("map")).then(function (canvas) {
    // Convert the canvas to a data URL (base64-encoded)
    const imageData = canvas.toDataURL();

    // Send another request to save the image
    fetch(url.concat('save-image'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageData
      })
    }).then(function (response) {
      if (response.ok) {
        console.log("Map image saved successfully");
      } else {
        throw new Error("Error saving map image");
      }
    }).catch(function (error) {
      console.error("Error saving map image:", error);
    });
  });
}

function updateAspectRatio(value) {
  console.log(value)
}

// Common resolutions for each aspect ratio
const resolutionsByAspectRatio = {
  '1': ['100x100', '200x200', '500x500'],
  '4/3': ['640x480', '800x600', '1024x768'],
  '16/9': ['1280x720', '1920x1080', '3840x2160'],
  '16/10': ['1280x800', '1920x1200', '2560x1600'],
  '5/4': ['1280x1024', '1600x1280', '2560x2048'],
  '2.39/1': ['1920x800', '2560x1067', '3440x1440'],
  '1.85/1': ['1920x1038', '2560x1386', '4096x2214'],
  '2/1': ['2560x1280', '3840x1920', '5120x2560'],
  '21/9': ['2560x1080', '3440x1440', '5120x2160'],
};

function populateResolutionDropdown() {
  const aspectRatioDropdown = document.getElementById('aspectRatioDropdown');
  const resolutionDropdown = document.getElementById('resolutionDropdown');
  const selectedAspectRatio = aspectRatioDropdown.value;
  console.log(typeof aspectRatioDropdown.value)

  // Clear the previous options
  resolutionDropdown.innerHTML = '';

  // Populate the resolution options based on the selected aspect ratio
  const resolutions = resolutionsByAspectRatio[selectedAspectRatio];
  default_option = document.createElement('option');
  default_option.text = 'Select Resolution';
  default_option.value = '';
  default_option.disabled = true;
  resolutionDropdown.add(default_option)
  if (resolutions) {
    resolutions.forEach(resolution => {
      const option = document.createElement('option');
      option.text = resolution;
      option.value = resolution;
      resolutionDropdown.add(option);
    });
  }
  resolutionDropdown.selectedIndex = 0;

}
function toggleCustomResolution() {
  const customResolutionInputs = document.getElementById('resolution-input');
  const customResolutionCheckbox = document.getElementById('resolution-checkbox');
  const aspectRatioDropdown = document.getElementById('aspectRatioDropdown');
  const resolutionDropdown = document.getElementById('resolutionDropdown');
  const widthInput = document.getElementById('widthInput');
  const heightInput = document.getElementById('heightInput');

  // Show or hide the custom resolution text boxes based on the checkbox state
  is_checked = customResolutionCheckbox.checked;
  customResolutionInputs.style.display = is_checked ? 'flex' : 'none';
  if (!is_checked) {
    // If unchecked, reset the width and height inputs
    document.getElementById('widthInput').value = '';
    document.getElementById('heightInput').value = '';
  }

  aspectRatioDropdown.selectedIndex = 0;
  resolutionDropdown.selectedIndex = 0;
  aspectRatioDropdown.disabled = is_checked;
  resolutionDropdown.disabled = is_checked
  populateResolutionDropdown()

}
toggleCustomResolution()

