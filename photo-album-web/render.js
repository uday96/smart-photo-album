document.getElementById("displaytext").style.display = "none";
$('#label-input').tagsinput({
  tagClass: 'label label-default'
});

function resetData(){
    document.getElementById("displaytext").style.display = "none";
    document.getElementById("search-form").reset();
    document.getElementById("upload-form").reset();
    $('#label-input').tagsinput('removeAll');
    const imgs = document.getElementById("img-container");
    while (imgs.firstChild) {
        imgs.removeChild(imgs.lastChild);
    }
}

function searchPhoto(){

  var apigClient = apigClientFactory.newClient({
      apiKey: "fZhAIBczxyaptdmgpCFwK5FayQSeH1MZ4WlkDaB4"
  });

    var query = document.getElementById('search-input').value;
    console.log("Query: " + query)
    if (!query){
        document.getElementById("modalMsg").innerHTML = "Query cannot be empty";
        $('#modalContainer').modal('show');
        return;
    }

    query = query.trim();
    var body = { };
    var params = {q : query};
    var additionalParams = {
        headers: {
            'Content-Type':"application/json"
        }
    };

    apigClient.searchGet(params, body , additionalParams).then(function(res){
        console.log(res)
        resetData();

        if(res.data.length == 0)
        {
          document.getElementById("displaytext").innerHTML = "No Images Found !!!"
          document.getElementById("displaytext").style.display = "block";
        }

        res.data.forEach( function(obj) {
            var img = new Image();
            img.src = obj["image-url"];
            img.setAttribute("class", "banner-img");
            img.setAttribute("alt", "effy");
            document.getElementById("displaytext").innerHTML = "Images returned for '"+query+"' are : "
            document.getElementById("img-container").appendChild(img);
            document.getElementById("displaytext").style.display = "block";
          });
        }).catch( function(result){
    });
}

function getBinary(file){
    return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    };
    reader.onerror = error => reject(error);
    reader.readAsArrayBuffer(file);
  });
}

function uploadPhoto() {
   var file = document.getElementById('file-input').files[0];
   console.log(file);
   if (file == undefined){
       document.getElementById("modalMsg").innerHTML = "File not selected";
       $('#modalContainer').modal('show');
       return;
   }
   var labels = $("#label-input").val();
   console.log("Custom labels: " + labels);

   var image = getBinary(file).then(
     data => {
     console.log(data);
     var apigClient = apigClientFactory.newClient({
         apiKey: "fZhAIBczxyaptdmgpCFwK5FayQSeH1MZ4WlkDaB4"
     });

     var body = data;
     var params = {"file" : file.name, 'Content-Type': file.type, 'x-amz-meta-customLabels': labels};
     var additionalParams = {};
     apigClient.photosPut(params, body , additionalParams).then(function(res){
       if (res.status == 200) {
           document.getElementById("modalMsg").innerHTML = "Image uploaded successfully!";
           $('#modalContainer').modal('show');
           resetData();
       }
     })
   });

}