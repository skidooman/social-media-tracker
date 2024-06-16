function filter(url)
{
        document.getElementById('main').innerHTML='<h3>Retrieving data, please stand by...</h3>';

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

	answer = fetch(url, {
	  method: 'POST',
	  body: JSON.stringify({
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
function load_runs_inner(base_url, start_record, chunk_size, run_size) {
	  let new_start_record = start_record + chunk_size;

	  answer = fetch(base_url + '/' + start_record + '/' + chunk_size, {

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
	  {
	  	if (start_record==0) {
	   		document.getElementById('main').innerHTML+=data;
		}
		else {
			document.getElementById('main').getElementsByTagName('tbody')[0].innerHTML+=data;
		}
		if (new_start_record < run_size) setTimeout(load_runs_inner(base_url, new_start_record, chunk_size, run_size), 0);
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

	// How many runs are there total?
	runs = fetch('/get_total_runs', {
	  method: 'POST',
	  body: JSON.stringify({
	  }),
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
                load_runs_inner(remainder, start_record, chunk_size, data);

	  }).catch(error => console.error('Error:', error));

	 
	//alert(answer);
}
