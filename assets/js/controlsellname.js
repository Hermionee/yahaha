$(document).ready(function() {
    var message = document.getElementById('message');
    var config, conversation;
    message.textContent = 'Click on the microphone to start audio search';

    document.getElementById('audio-control').onclick = function () {

        AWS.config.credentials = new AWS.Credentials("AKIAIDJKXWRJJVT7CUVQ", "th8G1I54xv4frxVm72Ewh2CrmpOijeffGXusbMeB", null);
        AWS.config.region = 'us-east-1';
        
        config = {
            lexConfig: { botName: "PhotoBot" }
        };

        conversation = new LexAudio.conversation(config, function (state) {
            message.textContent = state + '...';
           
        }, function (data) {
            console.log('Transcript: ', data.inputTranscript, ", Response: ", data["message"]);
            let i;
                if(data.message=="Ooops, Photo not found >_<"){
                	alert("Ooops, Photo not found >_<");
                }
                else if(!data.message.includes("https")){
                	alert("Sorry, can you repeat that?")
                }
                else{
        			$('.messages ul').empty();
	                let urls = data.message.split(" ");
	                for (i = 0; i < urls.length; i++) {
	                	if(urls[i]!=""){
	                    $('<li class="sent"><img src='+urls[i]+' height="200" ></li>').appendTo($('.messages ul'));
	                }
	                }
             	}
        }, function (error) {
            message.textContent = error;
            alert("Sorry, can you repeat that?")
        });
        conversation.advanceConversation();
    };
})
function uploadPhoto(){
		//document.getElementById("progressBar").hidden = false;
//get the element with id and replace the " " with "_"
		var file = document.getElementById("file-upload").files[0];
		var productname = document.getElementById("productname").value;
		productname = productname.replace(/ /g,"_");
		var description = document.getElementById("description").value;
		description = description.replace(/ /g,"_");
		var price = document.getElementById("price").value;
		price = price.replace(/ /g,"_");

		console.log(productname)
		console.log(price)
		console.log(description)

		if (file){
			console.log(file.name);
			if (!file.type.match('image.*')){
				alert("Please upload an image");
				return false;
			}
			//var progressBar = document.getElementById("progressBar");
			
			var xhr = new XMLHttpRequest();
		//	xhr.upload.onprogress = function(e) {
		//		var percentComplete = (e.loaded / e.total) * 100;
		//		progressBar.value = percentComplete;
		//	};

			xhr.onload = function() {
				if (xhr.status == 200) {
					alert("Sucess! Upload completed");
				} else {
					alert("Error! Upload failed");
				}
			};
			xhr.onerror = function() {
				alert("Error! Upload failed. Can not connect to server.");
			};

    		//define the new filename and use "+" to connect the different element 
			var filename = productname + "*" + description + "*" + price+".jpg";
			console.log(filename)
		//	progressBar.value = 0;
			xhr.open("PUT", "https://6k7kxevd8l.execute-api.us-east-1.amazonaws.com/test/upload?photo="+ filename);

			xhr.setRequestHeader("Content-Type", file.type);
			xhr.setRequestHeader("x-api-key", "xDyNorRaZcausLeJvQQCP6wPIBDW8XxG3i2Z4PPA");
			xhr.send(file);
			console.log(file.type);
			console.log(file);
			console.log(xhr);
		}
		else{
			alert("Select a photo!");
		}
	}

function encode_utf8(s) {
  return unescape(encodeURIComponent(s));
}

function decode_utf8(s) {
  return decodeURIComponent(escape(s));
}
		
function previewFile() {
  	var preview = document.querySelector('img');
  	var file    = document.querySelector('input[type=file]').files[0];
  	var reader  = new FileReader();

  	reader.addEventListener("load", function () {
    	preview.src = encode_utf8(reader.result);
  	}, false);

  	if (file) {
    	reader.readAsDataURL(file);
					
  	}
}

function UploadPPhoto(){
	var preview = document.querySelector('img');
	var file = document.querySelector('input[type=file]').files[0];
	var file_name = file.name;
	var file_type = file.type;
	var file_src = preview.src;
	file_src = file_src.replace('data:image/jpeg;base64,','');
	console.log(file_name);
	console.log(file_src);
	console.log(file_type);
	console.log(file);
	sdk.uploadPut({bucket: 'photocontainer', photo: file_name, 'Content-Type': file_type}, file_src, {});
	//console.log(response);
}

function newMessage() {
        $('.messages ul').empty();
		let message = document.getElementById("search").value;
        if(message == '') {
            return false;
        }
        let apigClient = apigClientFactory.newClient({
            apiKey: 'xDyNorRaZcausLeJvQQCP6wPIBDW8XxG3i2Z4PPA'});
        let body={

        };
        let params={
            q: message
        };
        let additionalParams={

        };
        apigClient.searchGet(params, body, additionalParams)
            .then(function(result){
            	console.log(result);
                let i;
                if(result["data"]["greeting"]=="Ooops, Photo not found >_<"){
                	alert("Ooops, Photo not found >_<");
                }
                else{
                	console.log(result);
	                let urls = result["data"]["greeting"].split("\n");
	                for (i = 0; i < urls.length; i++) {
	                	if(urls[i]!=""){
	                    $('<li class="sent"><img src='+urls[i]+' height="200" ></li>').appendTo($('.messages ul'));
	                }
	                }
             	}
            }).catch(function(result){
            console.log(result);
        });
    }