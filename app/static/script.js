const uploadDiv = document.getElementById("uploadDiv");
const fileInput = document.getElementById("fileInput");
const table = document.getElementById("table");
const tableBody = document.getElementById("tableBody");
const downloadLink = document.getElementById("downloadLink");
const recordButton = document.getElementById("recordButton");
const modal = document.getElementById("optionsModal");
const optionsButton = document.getElementById("optionsButton");
const closeSpan = document.getElementsByClassName("close")[0];
const fileTypeCheckbox = document.getElementById("fileTypeCheckbox");
const modelMixingDiv = document.getElementById("modelMixingDiv");
const modelSelectionDiv = document.getElementById("modelSelectionDiv");
const modelSelect = document.getElementById("modelSelect");
const sliderValues = document.querySelectorAll(".sliderValue");

const instruments = [
  "cel",
  "cla",
  "flu",
  "gac",
  "gel",
  "org",
  "pia",
  "sax",
  "tru",
  "vio",
  "voi",
];

let filePredictions;
let predictionsFileType = "json";
let modelMixing = false;
let modelWeights = new Map();
const CSV_SONG_NAME_COLUMN = "name";
const CSV_HEADERS = CSV_SONG_NAME_COLUMN + "," + instruments.join(",");
const MODEL_COUNT = 4;

for (modelName of modelNames) {
  modelWeights[modelName] = 0;
}
modelWeights[selectedModelName] = 1;

console.log(modelWeights);

uploadDiv.addEventListener("dragover", (event) => {
  event.preventDefault();
  uploadDiv.style.backgroundColor = "#eee";
});

uploadDiv.addEventListener("dragleave", (event) => {
  event.preventDefault();
  uploadDiv.style.backgroundColor = "";
});

uploadDiv.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => handleUpload(fileInput.files));

downloadLink.addEventListener("click", generateAndDownloadData);

recordButton.onclick = handleStartRecording;

optionsButton.onclick = () => modal.classList.add("modal-visible");

closeSpan.onclick = () => modal.classList.remove("modal-visible");

window.onclick = (event) => {
  if (event.target === modal) {
    modal.classList.remove("modal-visible");
  }
};

fileTypeCheckbox.addEventListener("change", () => {
  if (fileTypeCheckbox.checked) {
    predictionsFileType = "csv";
  } else {
    predictionsFileType = "json";
  }
});

modelSelect.value = selectedModelName;

function updateSliderValue(element, modelName) {
  const slider = document.getElementById(`slider-${modelName}`);
  const valueInput = document.getElementById(`value-${modelName}`);

  if (element.type === "range") {
    valueInput.value = element.value;
  } else {
    slider.value = element.value;
  }

  // Ensure the value is not greater than 1
  if (parseFloat(element.value) > 1) {
    element.value = "1";
  }

  // Calculate the sum of all slider values
  let sum = 0;
  sliderValues.forEach((sliderValue) => {
    sum += parseFloat(sliderValue.value);
  });

  // Ensure the sum of all sliders is always 1
  if (sum > 1) {
    const remainingValue = 1 - (sum - parseFloat(element.value));
    element.value = remainingValue.toFixed(2);
  }

  modelWeights[modelName] = element.value;

  // Update the corresponding slider/value input
  if (element.type === "range") {
    valueInput.value = element.value;
  } else {
    slider.value = element.value;
  }
}

function onDrop(event) {
  event.preventDefault();
  uploadDiv.style.backgroundColor = "";

  handleUpload(event.dataTransfer.files);
}

function handleUpload(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("wav_files", files[i]);
  }
  sendRequestAndHandleResponse(formData);
}

async function sendRequestAndHandleResponse(formData) {
  let url = "/analyze_files";
  if (modelMixing) {
    url += "/mix_model";
    formData.append("model_weights", JSON.stringify(modelWeights));
  } else {
    url += "/single_model";
    formData.append("model_name", selectedModelName);
  }

  let response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (response.ok) {
    console.log(response);
    filePredictions = await response.json();

    makeTable(filePredictions);
    downloadLink.classList.remove("disabled");
  } else {
    console.log("Error: " + response.status);
  }
}

function makeTable(filePredictions) {
  clearTable();

  const fileNames = Object.keys(filePredictions);

  for (let i = 0; i < fileNames.length; i++) {
    const row = tableBody.insertRow(i);
    const nameCell = row.insertCell(0);
    const fileName = fileNames[i];
    const filePrediction = filePredictions[fileName];
    nameCell.innerHTML = fileName;

    for (let j = 0; j < instruments.length; j++) {
      const cell = row.insertCell(j + 1);
      const instrument = instruments[j];
      let innerHTML = "NO";
      if (filePrediction[instrument] === 1) {
        innerHTML = "YES";
      }
      cell.innerHTML = innerHTML;
    }
  }

  table.hidden = false;
}

function clearTable() {
  while (tableBody.childNodes.length) {
    tableBody.removeChild(tableBody.childNodes[0]);
  }
}

function generateAndDownloadData() {
  let blobData;
  if (predictionsFileType === "json") {
    blobData = JSON.stringify(filePredictions, null, 2);
  } else {
    blobData = jsonPredictionToCsv(filePredictions);
  }

  console.log(blobData);

  const blob = new Blob([blobData], {
    type: `text/${predictionsFileType}`,
  });
  const url = URL.createObjectURL(blob);

  downloadLink.href = url;
  downloadLink.download = `wav-files-instruments-predictions.${predictionsFileType}`;
}

async function handleStartRecording() {
  const audioContext = new AudioContext();

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaStreamSource = audioContext.createMediaStreamSource(stream);
  const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
  const audioData = [];
  scriptProcessor.onaudioprocess = (event) => {
    audioData.push(event.inputBuffer.getChannelData(0));
  };

  mediaStreamSource.connect(scriptProcessor);
  scriptProcessor.connect(audioContext.destination);
  recordButton.textContent = "Stop Recording";
  recordButton.classList.add("stop");

  recordButton.onclick = () => {
    const formData = new FormData();
    fileNames = ["Recording"];
    formData.append("wav_files", audioData);

    sendRequestAndHandleResponse(formData);
    handleStopRecording(stream, mediaStreamSource, scriptProcessor);
  };
}

function handleStopRecording(stream, mediaStreamSource, scriptProcessor) {
  stream.getTracks().forEach((track) => track.stop());
  mediaStreamSource.disconnect();
  scriptProcessor.disconnect();

  recordButton.textContent = "Start Recording";
  recordButton.classList.remove("stop");
  recordButton.onclick = handleStartRecording;
}

function setModel(modelName) {
  selectedModelName = modelName;
}

function toggleModelMixing() {
  modelMixing = !modelMixing;

  if (modelMixing) {
    modelSelectionDiv.hidden = true;
    modelMixingDiv.hidden = false;
  } else {
    modelSelectionDiv.hidden = false;
    modelMixingDiv.hidden = true;
  }
}

function jsonPredictionToCsv(jsonPredictions) {
  const rowItems = Object.keys(jsonPredictions).map((fileName) => {
    const prediction = jsonPredictions[fileName];
    return (
      fileName +
      "," +
      instruments.map((instr) => JSON.stringify(prediction[instr])).join(",")
    );
  });
  const csv = [CSV_HEADERS, ...rowItems].join("\r\n");

  return csv;
}
