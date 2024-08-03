function edit(user_id, id)
{
	url = '/edit/' + user_id + '/' + id;
	window.location.href = url;
}

function edit_campaign(user_id, id)
{
	url = '/edit_campaign/' + user_id + '/' + id;
	window.location.href = url;
}

function del_campaign(user_id, id)
{
	if(confirm("Deleting ' + id + ' - Are you sure?")){
		url = '/delete_campaign/' + user_id + '/' + id;
		window.location.href = url;
	}
}

function delete_video_gui(video, runs)
{
	// If we are reaching here, we can delete the entry in the table and the selector
	// Delete the selector entry
	var selector = document.getElementById('artifact_selected');
	for (var j=1; j < selector.options.length; j++) {
		if (selector.options[j].value == video) {
			selector.remove(j);
			break;
		}
	}

	// Delete all the runs' checks, change for X
	for (var i=0; i < runs.length; i++) {
		var entry = document.getElementById('art_' + runs[i]);
		entry.innerHTML = 'X';
	}

	// Delete entry in the table
	var table = document.getElementById('artifacts');
	for (var j=1; j < table.rows.length; j++) {
		alert(table.rows[j].cells[0].innerHTML);
		if (table.rows[j].cells[0].innerHTML == video) { table.deleteRow(j); break;}
	}
}

function delete_video(video)
{
	// That "video" could be either the video_id or the video_div, if a video_id wasn't assigned yet
	// A video_div would start with '-'
	var video_id = video;
	if (video_id instanceof String) {
		// Eliminate this video in the database
		// First, find if this id is used in this campaign
		fetch('/get_runs_video/' + video_id)
		  .then(response => response.text())
		  .then(data => {
			alert(data);
			// If there are any run entries, these need to be eliminated later
			// But first try to delete the entry in the database
			fetch('/delete_runs_video/' + video_id)
			.then(response => response.code)
			.then(code => {
				if (code==200) { delete_video_gui(video_id, data); alert('video ' + video_id + ' erased');}
				else { alert('Error, video ' + video_id + ' not erased'); return;
				}
			})
			.catch (error => { alert(error); return;});
		
			}
		)
		  .catch(error => {
			alert(error); return;
			}
		);

	} else { console.log('int');  
		var table=document.getElementById('artifacts');
		for (var j=1; j < table.rows.length; j++){
			if (table.rows[j].cells[0].getElementsByTagName('div')[0].id == video + '_artifact_id'){
				table.deleteRow(j);
				break;
			}
		}
	}

}

var run_id_selected = 0;


function link_artifact() {
	const selected_video = document.getElementById('artifact_selected');
	const video = selected_video.options[selected_video.options.selectedIndex].value; // 42 (artifact)
	if (video == 'null') {
		answer = fetch('/delete_run_videos/' + run_id_selected)
		  .then(function(response){
			 //alert (response.text())
		  	return response.status;})
		  .then(function(code)
		  {
		   if (code == '200') {
			alert('command successful');
			document.getElementById('artifact_selector').style.visibility = 'hidden';
			// Make sure the run is marked with an x
			document.getElementById('art_' + run_id_selected).innerHTML = 'X';
		   }
		   else alert('Command failed: ' + code);
		}).catch(error => console.error('Error:', error))
	}
	else{
		// A new run vs video needs to be either added
		// OR updated
		// This is all taken care of in the backend
		answer = fetch('/add_run_videos/' + video + '/' + run_id_selected)
		  .then(function(response){
			 //alert (response.text())
		  	return response.status;})
		  .then(function(code)
		  {
		   if (code == '200') {
			alert('command successful');
			document.getElementById('artifact_selector').style.visibility = 'hidden';
			// Make sure that the item is marked with a checkmark
			document.getElementById('art_' + run_id_selected).innerHTML = '&check;';

		   }
		   else alert('Command failed: ' + code);
		}).catch(error => console.error('Error:', error))
		
	}
}

function linkArtifactToRun(run_div) {
	run_id_selected = run_div.substring(4);
	console.log(run_id_selected); 
	const div = document.getElementById(run_div);
	const rect = div.getBoundingClientRect();
	const selector = document.getElementById('artifact_selector');
	const selected_video = document.getElementById('artifact_selected');
	
	selector.style.position = 'absolute';
	selector.style.left = rect.x + rect.width + window.scrollX;
	selector.style.top = rect.y + window.scrollY;
	selector.style.visibility = 'visible';
	answer = fetch('/get_run_videos/' + run_id_selected)
		  .then(response => response.json())
		  .then(data => {
			for(var j = 0; selected_video.options.length; j++){
					if (selected_video.options[j].value == data){
						selected_video.options.selectedIndex = j;
						break;
					}
				}
			}
			)
		  .catch(error => {
			// We actually come here if the return is "none", which
			// means that we do not have an artifact for this run yet
			selected_video.options.selectedIndex = 0;
			}
			);
	
}

function load(url)
{
        document.getElementById('main').innerHTML='<h3>Retrieving data, please stand by...</h3>';
	inputs = document.getElementsByTagName('input');
	answer = fetch(url, {
	  method: 'POST',
	  body: JSON.stringify({
	  }),
	  headers: {
	    'Content-type': 'application/json; charset=UTF-8',
	  }
	  })
	  .then(function(response){
		 //alert (response.text())
	  	return response.text();})
	  .then(function(data)
	  {console.log(data);
	   document.getElementById('main').innerHTML =data;
	   initialize_sortable();
	   
	}).catch(error => console.error('Error:', error)); 
	//alert(answer);
}

// This loads the run list - but by chunks
function load_runs_inner(base_url, start_record, chunk_size, run_size, my_body) {
	  console.log(base_url + ' ' + start_record + ' ' + chunk_size + ' '  + run_size);
	  let new_start_record = start_record + chunk_size;

	  answer = fetch(base_url + '/' + start_record + '/' + chunk_size, {

	  method: 'POST',
	  body: my_body,
	  headers: {
	    'Content-type': 'application/json; charset=UTF-8',
	  }
	  })
	  .then(function(response){
		 //alert (response.text())
	  	return response.text();})
	  .then(function(data)
	  {
		console.log(start_record);
	  	if (start_record==0) {
			console.log('in');
	   		document.getElementById('main').innerHTML+=data;
		}
		else {
			document.getElementById('main').getElementsByTagName('tbody')[0].innerHTML+=data;
		}
		if (new_start_record < run_size) setTimeout(load_runs_inner(base_url, new_start_record, chunk_size, run_size, my_body), 0);
		else document.getElementById('meter').remove()
	   
	}).catch(error => console.error('Error:', error));
	document.getElementById('progress_bar').value = new_start_record;
	initialize_sortable();
	//console.log('here ' + document.getElementById("main").getElementsByTagName('tbody').rows);
}

function load_runs(url)
{
        document.getElementById('main').innerHTML='<div id="meter"><h3>Retrieving data, please stand by...&nbsp;&nbsp;<progress id="progress_bar" value="0" max="100"> </progress></h3></div>';
	inputs = document.getElementsByTagName('input');
	my_body = JSON.stringify({})

	// How many runs are there total?
	runs = fetch('/get_total_runs', {
	  method: 'POST',
	  body: my_body,
	  headers: {
	    'Content-type': 'application/json; charset=UTF-8',
	  }
	  })
	  .then(function(response) {
		return response.text();})
	  .then(function(data) {
                document.getElementById('progress_bar').max = data;

		// The URL is campaign_id/start_record/chunk_size
		let last_slash = url.lastIndexOf('/');
		let chunk_size = parseInt(url.substring(last_slash+1,url.length));
		let remainder = url.substring(0,last_slash);
		last_slash = remainder.lastIndexOf('/');
		let start_record = parseInt(remainder.substring(last_slash+1, remainder.length));
		remainder = remainder.substring(0, last_slash);

		// While we have not extracted all rows, proceed in a recursive algorithm
                load_runs_inner(remainder, start_record, chunk_size, data, my_body);

	  }).catch(error => console.error('Error:', error));

	 
	//alert(answer);
}

function filter(url, runs_or_campaigns)
{
        document.getElementById('main').innerHTML='<div id="meter"><h3>Retrieving data, please stand by...&nbsp;&nbsp;<progress id="progress_bar" value="0" max="100"> </progress></h3></div>';

	var external_text= false;
        var internal_video = false;
        var external_video = false;
        var simple = false;
	var image = false;
        var original_date_before = false;
        var original_date_after= false;
	var linkedin = false;
	var tiktok = false;
	var youtube = false;
	var languages = [];

	if (document.getElementById('image').checked) image=true;
	if (document.getElementById('article').checked) external_text=true;
	if (document.getElementById('ivideos').checked) internal_video=true;
	if (document.getElementById('xvideos').checked) external_video=true;
	if (document.getElementById('simple').checked) simple=true;
	var start = document.getElementById('pub_end').value;
	var end = document.getElementById('pub_start').value;
	if (start.length) original_date_before=start;	
	if (end.length) original_date_after=end;	
	if (document.getElementById('linkedin').checked) linkedin=true;
	if (document.getElementById('tiktok').checked) tiktok=true;
	if (document.getElementById('youtube').checked) youtube=true;

	inputs = document.getElementsByTagName('input');
	languages = []
	for (var i=0; i < inputs.length; i++)
	{
		//alert(inputs[i].name);
		if (inputs[i].name == 'language')
		{
			//alert('CAUGHT ' + inputs[i].id);
			if (inputs[i].checked) languages.push(inputs[i].id);
		}
	}
	console.log(languages);

	my_body = JSON.stringify({
                image: image,
		external_text: external_text,
		internal_video: internal_video,
		external_video: external_video,
		simple: simple,
		original_date_before: original_date_before, 
		original_date_after: original_date_after,
		linkedin: linkedin,
		tiktok: tiktok,
		youtube: youtube,
		languages: languages,
	  })
	
	var answer = 0;
	console.log('/get_total_' + runs_or_campaigns);
	answer = fetch('/get_total_' + runs_or_campaigns, {
	  method: 'POST',
	  body: my_body,
	  headers: {
	    'Content-type': 'application/json; charset=UTF-8',
	  }
	  })
	  .then(function(response){
		 //alert (response.text())
	  	return response.text();})
	  .then(function(data)
	  {console.log(data);
                document.getElementById('progress_bar').max = data;
		// The URL is campaign_id/start_record/chunk_size
		console.log('url: ' + url); 
		let last_slash = url.lastIndexOf('/');
		let chunk_size = parseInt(url.substring(last_slash+1,url.length));
		let remainder = url.substring(0,last_slash);
		last_slash = remainder.lastIndexOf('/');
		let start_record = parseInt(remainder.substring(last_slash+1, remainder.length));
		remainder = remainder.substring(0, last_slash);

		// While we have not extracted all rows, proceed in a recursive algorithm
                load_runs_inner(remainder, start_record, chunk_size, data, my_body);

	   
	}).catch(error => console.error('Error:', error)); 

}
