function toggle (id){
	let expandable = document.getElementById(id);
	if (expandable.style.overflow == 'hidden') {
		expandable.style.overflow ='visible'; 
		expandable.style.whiteSpace = 'normal'; 
	}
	else {
		expandable.style.overflow = 'hidden'; 
		expandable.style.whiteSpace='nowrap';
	}
}

