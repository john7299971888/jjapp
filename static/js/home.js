function validateRIScoreInputForm() {

    borderColorEmpty();
	var biller     = document.getElementById('biller').value;
	var bill_amount= document.getElementById('bill_amount').value;
	var bill_date  = document.getElementById('bill_date').value;
	var due_date   = document.getElementById('due_date').value;

	if(biller.trim()==""){
		document.getElementById('biller').style.borderColor="#FF5733";
	}

	if(bill_amount.trim()==""){
		document.getElementById('bill_amount').style.borderColor="#FF5733";
	}

	if(bill_date.trim()==""){
		document.getElementById('bill_date').style.borderColor="#FF5733";
	}

	if(due_date.trim()==""){
		document.getElementById('due_date').style.borderColor="#FF5733";
	}


    if(biller.trim()!="" && bill_amount.trim()!="" && bill_date.trim()!="" && due_date.trim()!="") {
		borderColorEmpty();
		$("form#ri_score_data_form").submit();		
    }else{	      
		alert("Please fill mandatory fields.")			
		return false;		
	}	
}

function borderColorEmpty(){
	document.getElementById('biller').style.borderColor="";	
	document.getElementById('bill_amount').style.borderColor="";
	document.getElementById('bill_date').style.borderColor="";
	document.getElementById('due_date').style.borderColor="";		
}

$( function() {
	$( "#bill_date" ).datepicker({
		showAnim: 'slide',
		showOn: "button",
		buttonImage: "/static/images/calendar.gif",
		buttonImageOnly: true,
		buttonText: "Select date",
		dateFormat: 'mm/dd/yy'		
	});
	$( "#due_date" ).datepicker({
		showAnim: 'slide',
		showOn: "button",
		buttonImage: "/static/images/calendar.gif",
		buttonImageOnly: true,
		buttonText: "Select date",
		dateFormat: 'mm/dd/yy'		
	});		
});