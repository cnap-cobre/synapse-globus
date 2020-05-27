// import { parseComponent } from "vue-template-compiler";

var targetContainer = document.getElementById("target_div");
var eventSource = new EventSource("/stream");
eventSource.onmessage = function(e) {
  // targetContainer.innerHTML = e.data;
  // $(".progress-bar").css("width", e.data).text(e.data);

  if (e.data.length < 2) {
    return;
  }
  var res = JSON.parse(e.data);

  if (res.length < 1) {
    return;
  }

  for (var j = 0; j < res.length; j++) {
    var msg = res[j];
    if (res[j]["py/object"] == "usr.JobUpdate") {
      var job_update = res[j];
      var job_div = document.getElementById("job_" + job_update.job_id);
      if (job_div == null) {
        return;
      }
      var pb = $("#pb_" + job_update.job_id);
      pb.css("width", job_update.percent_done + "%");
      pb.text(job_update.percent_done + "%");

      if (job_update.percent_done == 100) {
        pb.removeClass(
          "progress-bar progress-bar-striped progress-bar-animated bg-info"
        );
        pb.addClass("progress-bar bg-success");
      }

      var lblmsg = $("#msg_" + job_update.job_id);
      lblmsg.innerHTML = job_update.status_msg;
      $("#msg_" + job_update.job_id).text(job_update.status_msg);
    }
  }
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
        function(fileobj) {
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
        function() {
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

elDrop.addEventListener("dragover", function(event) {
  event.preventDefault();
  elItems.innerHTML = 0;
});

elDrop.addEventListener("drop", async function(event) {
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
    success: function(response) {
      var res = JSON.parse(response);
      var elSrcPath = document.getElementById("src_endpoint_path_list");

      //Remove all existing options.
      var length = elSrcPath.options.length;
      for (i = length - 1; i >= 0; i--) {
        elSrcPath.remove(i);
      }

      if (res.paths.length > 0) {
        for (var i = 0; i < res.paths.length; i++) {
          var opt = res.paths[i];
          var el = document.createElement("option");
          el.textContent = opt;
          el.value = opt;
          elSrcPath.appendChild(el);
        }
      }

      $("#lbl_finding_result").text(res.paths[0]);
      $("#lbl_path_msg").text(res.msg);
      elfindingResult.style.display = "block";
      elfinding.style.display = "none";
    },
    error: function(xhr) {
      alert(String(xhr));
      elfinding.style.display = "none";
    },
  });
}

function uploadFiles() {
  let formData = new FormData();
  var src_ep = document.getElementById("endpoints");

  formData.append("file_list", elItems.innerHTML);
  formData.append("lab_type", document.getElementById("lab_type").value);
  formData.append("selected_endpoint", src_ep.value);
  formData.append(
    "src_endpoint_name",
    src_ep.options[src_ep.selectedIndex].text
  );
  ds_select = document.getElementById("dataset_id");
  formData.append("dataset_id", ds_select.value);
  formData.append(
    "dataset_name",
    ds_select.options[ds_select.selectedIndex].text
  );
  formData.append("description", document.getElementById("description").value);
  formData.append("tags", document.getElementById("tags").value);
  // formData.append(
  //   "src_endpoint_path",
  //   document.getElementById("lbl_finding_result").textContent
  // );
  var e = document.getElementById("src_endpoint_path_list");
  formData.append("src_endpoint_path", e.options[e.selectedIndex].value);

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
