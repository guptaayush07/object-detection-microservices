document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const statusEl = document.getElementById("status");
  const resultsDiv = document.getElementById("results");
  const detectionsList = document.getElementById("detectionsList");
  const annotatedImage = document.getElementById("annotatedImage");

  statusEl.textContent = "⏳ Uploading and processing...";
  resultsDiv.classList.add("hidden");

  const formData = new FormData();
  formData.append("image", document.getElementById("image").files[0]);

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (data.success) {
      statusEl.textContent = "✅ Image processed successfully";

      // Show results
      document.getElementById("totalDetections").textContent = data.total_detections;
      detectionsList.innerHTML = "";
      data.detections.forEach((det, i) => {
        const li = document.createElement("li");
        li.textContent = `${i + 1}. ${det.class_name} (conf: ${det.confidence.toFixed(2)})`;
        detectionsList.appendChild(li);
      });

      if (data.annotated_image_file) {
        annotatedImage.src = `/download/${data.annotated_image_file}`;
      }

      // Download links
      document.getElementById("downloadJson").href = `/download/${data.json_file}`;
      if (data.annotated_image_file) {
        document.getElementById("downloadImage").href = `/download/${data.annotated_image_file}`;
      }

      resultsDiv.classList.remove("hidden");
    } else {
      statusEl.textContent = "❌ Error: " + (data.error || "Unknown error");
    }
  } catch (err) {
    statusEl.textContent = "❌ Error: " + err.message;
  }
});

async function fetchResults() {
  const listEl = document.getElementById("resultsList");
  listEl.innerHTML = "⏳ Loading...";

  try {
    const res = await fetch("/results");
    const data = await res.json();
    if (data.files) {
      listEl.innerHTML = "";
      data.files.forEach((file) => {
        const li = document.createElement("li");
        li.innerHTML = `<a href="/download/${file.filename}" target="_blank">${file.filename}</a> (${(file.size/1024).toFixed(1)} KB)`;
        listEl.appendChild(li);
      });
    }
  } catch (err) {
    listEl.innerHTML = "❌ Error loading results";
  }
}

async function fetchModelInfo() {
  const infoEl = document.getElementById("modelInfoContent");
  infoEl.textContent = "⏳ Loading...";

  try {
    const res = await fetch("/model_info");
    const data = await res.json();
    infoEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    infoEl.textContent = "❌ Error loading model info";
  }
}
