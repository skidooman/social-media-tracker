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
