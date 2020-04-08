var targetContainer = document.getElementById("target_div");
var eventSource = new EventSource("/stream");
eventSource.onmessage = function (e) {
  // targetContainer.innerHTML = e.data;
  $(".progress-bar").css("width", e.data).text(e.data);
};

// Drop handler function to get all files
async function getAllFileEntries(dataTransferItemList) {
  //console.debug("inside get all files.");
  let fileEntries = [];
  // Use BFS to traverse entire directory/file structure
  let queue = [];
  // Unfortunately dataTransferItemList is not iterable i.e. no forEach
  for (let i = 0; i < dataTransferItemList.length; i++) {
    let fo = dataTransferItemList[i].getAsFile();
    //console.debug(fo.size);
    queue.push(dataTransferItemList[i].webkitGetAsEntry());
    //queue.push(dataTransferItemList[i]);
  }

  let filesToProcess = 0;

  while (queue.length > 0) {
    //console.debug('Queue Length: '+queue.length);
    //let dti = queue.shift();
    //let entry = dti.webkitGetAsEntry();
    let entry = queue.shift();
    //console.debug('queue shift');
    if (entry.isFile) {
      //let fileobj = dti.getAsFile();
      //let fileobj = null;
      //console.debug('right before entry.file.');
      filesToProcess += 1;
      entry.file(
        function (fileobj) {
          //fileobj = f;
          var data_we_want = {
            name: fileobj.name,
            mru: fileobj.lastModified,
            size: fileobj.size,
            path: entry.fullPath,
          };
          //console.debug(data_we_want);
          fileEntries.push(data_we_want);
          filesToProcess -= 1;
        },
        function () {
          console.debug("err");
          filesToProcess -= 1;
        }
      );

      //fileEntries.push(entry);
    } else if (entry.isDirectory) {
      //console.debug('found dir.')
      let reader = entry.createReader();
      queue.push(...(await readAllDirectoryEntries(reader)));
    }
  }
  //We need to wait for all the callbacks to complete.
  while (filesToProcess > 0) {
    await new Promise((r) => setTimeout(r, 500));
  }
  //console.debug('End of getAllFileEntries length: '+fileEntries.length);
  return fileEntries;
}

// Get all the entries (files or sub-directories) in a directory by calling readEntries until it returns empty array
async function readAllDirectoryEntries(directoryReader) {
  let entries = [];
  let readEntries = await readEntriesPromise(directoryReader);
  while (readEntries.length > 0) {
    entries.push(...readEntries);
    readEntries = await readEntriesPromise(directoryReader);
  }
  return entries;
}

// Wrap readEntries in a promise to make working with readEntries easier
async function readEntriesPromise(directoryReader) {
  try {
    return await new Promise((resolve, reject) => {
      directoryReader.readEntries(resolve, reject);
    });
  } catch (err) {
    console.log(err);
  }
}

var elDrop = document.getElementById("dropzone");
var elItems = document.getElementById("items");
var elStatus = document.getElementById("lbl_status");
var elfinding = document.getElementById("finding");
var elfindingResult = document.getElementById("finding_result");

elDrop.addEventListener("dragover", function (event) {
  event.preventDefault();
  elItems.innerHTML = 0;
});

elDrop.addEventListener("drop", async function (event) {
  event.preventDefault();
  console.debug(event);
  let files_found = await getAllFileEntries(event.dataTransfer.items);
  console.debug("found " + files_found.length + "...");
  elStatus.innerHTML = "Found " + files_found.length + " items.";
  elItems.innerHTML = JSON.stringify(files_found);
  uploadFilesOnly();
});

function uploadFilesOnly() {
  elfinding.style.display = "block";
  // Reference: https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page
  $.ajax({
    url: "/link",
    type: "POST",
    data: {
      file_list: elItems.innerHTML,
      selected_endpoint: document.getElementById("endpoints").value,
    },
    success: function (response) {
      var res = JSON.parse(response);
      // alert(res);
      // alert(res.paths[0]);
      $("#lbl_finding_result").text(res.paths[0]);
      $("#lbl_path_msg").text(res.msg);
      elfindingResult.style.display = "block";
      elfinding.style.display = "none";
    },
    error: function (xhr) {
      alert(xhr);
      elfinding.style.display = "none";
    },
  });
}

function uploadFiles() {
  let formData = new FormData();
  formData.append("file_list", elItems.innerHTML);
  formData.append("lab_type", document.getElementById("lab_type").value);
  formData.append(
    "selected_endpoint",
    document.getElementById("endpoints").value
  );
  formData.append("dataset_id", document.getElementById("dataset_id").value);
  formData.append("description", document.getElementById("description").value);
  formData.append("tags", document.getElementById("tags").value);
  formData.append(
    "src_endpoint_path",
    document.getElementById("lbl_finding_result").value
  );
  fetch("http://localhost:5000/upload", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.json())
    .then((res) => {
      console.log("done uploading", res);
    })
    .catch((e) => {
      console.error(JSON.stringify(e.message));
    });
}
