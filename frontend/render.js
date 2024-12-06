document.getElementById('displaytext').style.display = 'none';

function searchPhoto() {
    var apigClient = apigClientFactory.newClient();

    var user_message = document.getElementById('note-textarea').value;

    var body = {};
    var params = { q: user_message };
    var additionalParams = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    apigClient
        .searchGet(params, body, additionalParams)
        .then(function (res) {
            var resp_data = res.data;
            console.log(resp_data);

            if (resp_data.imagePaths === "No Results found") {
                document.getElementById('displaytext').innerHTML =
                    'Sorry, could not find the image. Try different search words!';
                document.getElementById('displaytext').style.display = 'block';
                return;
            }

            document.getElementById('img-container').innerHTML = '';

            resp_data.imagePaths.forEach(function (obj) {
                // Display images from S3 URLs
                const img = new Image();
                img.src = obj;
                img.setAttribute('class', 'banner-img');
                img.setAttribute('alt', 'image');
                document.getElementById('img-container').appendChild(img);
            });
        })
        .catch(function (error) {
            console.error('Search error:', error);
        });
}

function uploadPhoto() {
    console.log("Uploading file:", file);

    document.getElementById('upload_button').innerHTML = 'Uploading...';
    document.getElementById('upload_button').style.backgroundColor = '#005af0';

    var apigClient = apigClientFactory.newClient();

    var params = {
        object: file.name,
	'x-amz-meta-customLabels': document.getElementById('note_customtag').value,
    };

    var additionalParams = {
        headers: {
            'Content-Type': file.type,
        },
    };

    // Read file as binary data and upload
    var reader = new FileReader();
    reader.onload = function (e) {
        var body = new Uint8Array(e.target.result);

        apigClient.uploadPut(params, body, additionalParams)
            .then(function (res) {
                console.log("Response from API:", res);
                if (res.status === 200) {
                    document.getElementById('upload_button').innerHTML = 'Upload succeeded';
                    document.getElementById('upload_button').style.backgroundColor = '#499C55';
                }
            })
            .catch(function (err) {
                console.error("Upload failed:", err);
                document.getElementById('upload_button').innerHTML = 'Upload failed';
                document.getElementById('upload_button').style.backgroundColor = '#F54234';
            });
    };
    reader.readAsArrayBuffer(file);
}

// Drag-and-Drop and File Upload Section
const dropArea = document.querySelector(".drop_box"),
    button = dropArea.querySelector("button"),
    dragText = dropArea.querySelector("header"),
    input = dropArea.querySelector("input");
let file;

button.onclick = () => {
    input.click();
};

input.addEventListener("change", function (e) {
    file = e.target.files[0]; // Assign file
    var fileName = file.name;

    // Update UI with file details and upload button
    let filedata = `
        <h4>${fileName}</h4>
        <input placeholder="Input Custom tag!" type="text" class="form-control" id="note_customtag">
        <button class="btn" id="upload_button" type="submit" onclick="uploadPhoto()">Upload</button>
    `;
    dropArea.innerHTML = filedata;
});
