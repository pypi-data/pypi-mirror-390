  window.addEventListener("contextmenu", function(e) {
    // Get the target element (the element that was clicked)
    let element = e.target;

    e.preventDefault(); // Prevent the default browser context menu
    const ids = [];

      while (element) {
          if (element.id) {
              ids.push(element.id);
          }
          element = element.parentElement;
      }

    // You can pass this information to your HTMX request
    const menu = document.getElementById('custom-menu');
    menu.style.top = `${e.clientY}px`;
    menu.style.left = `${e.clientX}px`;

    // Trigger HTMX request to load the menu content
    // Join ids with ,
    str_ids = ids.join(",")
    htmx.ajax('GET', `/get-context-menu?elementIds=${str_ids}&top=${e.clientY}&left=${e.clientX}`, {
      target: '#custom-menu',
      swap: 'outerHTML',  // Correct usage of swap attribute
      headers: {
        'HX-Swap-OOB': 'true'  // Use correct OOB header for out-of-band swaps
      }
    });
  });

  // Hide the menu when clicking elsewhere
  window.addEventListener("click", () => {
    const menu = document.getElementById('custom-menu');
    menu.style.visibility = "hidden";
  });


function copyToClipboard(container) {
    const text = container.querySelector('.copy-text').innerText;

    navigator.clipboard.writeText(text).then(() => {
      container.classList.add('copied');
      setTimeout(() => {
        container.classList.remove('copied');
      }, 1200);
    });
}


function shiftClickDataGrid(event){
    const el = event.target.closest('.table-row');
    if (!el) return; // Not one of ours
    if (event.ctrlKey || event.metaKey) {
      const originalUrl = el.getAttribute('hx-get'); // e.g. "/default-endpoint?runID=3"
      const url = new URL(originalUrl, window.location.origin); // create full URL to parse
      const params = url.search;

     // Instead of modifying the attribute, trigger htmx manually with the new URL
      htmx.ajax('GET', `/shift_click_row${params}`, {target: el.getAttribute('hx-target') || el});

      // Prevent the original click handler from firing
      event.preventDefault();
      event.stopPropagation();
    }
}
document.addEventListener('click', shiftClickDataGrid);

// New htmx event: open in a new tab when data-new-tab attribute is present
document.addEventListener('htmx:beforeOnLoad', function (event) {
    const redirectUrl = event.detail.xhr.getResponseHeader('HX-Blank-Redirect');
    if (redirectUrl && event.detail.elt.hasAttribute('data-new-tab')) {
        // Prevent htmx from performing the redirect in the current tab
        console.log("Here")
        window.open(redirectUrl, '_blank');
    }
  });

// Custom function that is called when clicking the "Download CSV" button in Plotly plots
function clickDownloadCSV(gd){
    console.log(gd);

    // Helper function to decode base64 binary data
    function decodeBinaryData(bdata, dtype) {
        var binary = atob(bdata);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }

        // Convert based on dtype
        if (dtype === 'f8') {
            // Float64 (8 bytes per value)
            return new Float64Array(bytes.buffer);
        } else if (dtype === 'i1') {
            // Int8 (1 byte per value)
            return new Int8Array(bytes.buffer);
        } else if (dtype === 'i4') {
            // Int32 (4 bytes per value)
            return new Int32Array(bytes.buffer);
        }
        return bytes;
    }

    var csv = 'x,y,trace\n';

    gd.data.forEach(function(trace) {
        // Check if data is in binary format (bdata) or regular array
        var xData = trace.x;
        var yData = trace.y;

        if (trace.x && trace.x.bdata && trace.x.dtype) {
            xData = decodeBinaryData(trace.x.bdata, trace.x.dtype);
        }
        if (trace.y && trace.y.bdata && trace.y.dtype) {
            yData = decodeBinaryData(trace.y.bdata, trace.y.dtype);
        }

        for(var j = 0; j < xData.length; j++) {
            csv += xData[j] + ',' + yData[j] + ',' + trace.name + '\n';
        }
    });

    var blob = new Blob([csv], {type: 'text/csv'});
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'plot_data.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Add a custom htmx event called "outsideClick". Triggered when clicking outside an element.
document.addEventListener('click', (e) => {
    // For each element that wants outside-click detection
    document.querySelectorAll('[hx-trigger~="outsideClick"]').forEach((el) => {
      if (!el.contains(e.target)) {
        // Fire a bubbling custom event that htmx can react to
        el.dispatchEvent(new Event('outsideClick', { bubbles: true }));
      }
    });
});