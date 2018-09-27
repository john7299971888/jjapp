function validateRIScoreInputForm_Update() {

   //Mandatory columns : platform/version/sub_version/riscore_date/attribute/ri_score
    borderColorEmpty();
	var platform     = document.getElementById('platform').value;
	var version      = document.getElementById('version').value;
	var sub_version  = document.getElementById('sub_version').value;
	var riscore_date = document.getElementById('riscore_date').value;
	var ri_score     = document.getElementById('ri_score').value;
	var edit_id      = document.getElementById('edit_id').value;	
	

	if(platform.trim()==""){
		document.getElementById('platform').style.borderColor="#FF5733";
	}

	if(version.trim()==""){
		document.getElementById('version').style.borderColor="#FF5733";
	}

	if(sub_version.trim()==""){
		document.getElementById('sub_version').style.borderColor="#FF5733";
	}

	if(riscore_date.trim()==""){
		document.getElementById('riscore_date').style.borderColor="#FF5733";
	}

	if(ri_score.trim()==""){
		document.getElementById('ri_score').style.borderColor="#FF5733";
	}	
	
	
    if(platform.trim()!="" && version.trim()!="" && sub_version.trim()!="" && riscore_date.trim()!="" && ( parseFloat(ri_score.trim())>=1 && parseFloat(ri_score.trim())<=10)) {
		borderColorEmpty();
		query_string="platform="+platform+"&version="+version+"&sub_version="+sub_version+"&edit_id="+edit_id;
    	$.ajax({
			url: '/check-ri-score-data-exist-edit',
			data: query_string,
			type: 'POST',
			success: function(response) {
				if(response.trim()==="not-ok"){
					alert("This combination of platform,version,&sub-verion is already exist.")
					document.getElementById('platform').style.borderColor = "#FF5733";
					document.getElementById('version').style.borderColor = "#FF5733";		
					document.getElementById('sub_version').style.borderColor = "#FF5733";
				}else if(response.trim()==="ok"){					
					$("form#ri_score_data_form").submit();					
				}				
			},
			error: function(error) {
			    alert(error)
				console.log(error);
				return false;
			}
		});	
		return false;		
		
    }else{
		if (ri_score.trim()!=""){
				if(parseFloat(ri_score.trim())>=1 && parseFloat(ri_score.trim())<=10){				

				}else{
					document.getElementById('ri_score').style.borderColor="#FF5733";
					alert("RI Score should be between 1 to 10.");					
				}	
		}
		alert("Please fill mandatory fields.")			
		return false;	
	}	
}

function borderColorEmpty(){
	document.getElementById('platform').style.borderColor="";	
	document.getElementById('version').style.borderColor="";
	document.getElementById('sub_version').style.borderColor="";
	document.getElementById('riscore_date').style.borderColor="";
	document.getElementById('ri_score').style.borderColor="";		
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

function IsValidID(cdets,element_name){

	$("#add_result_submit").attr("disabled",'disabled');
    document.getElementById("cdets_error").style.display = "none";	
	if(cdets){
		$("#cdets_api_result").html("Validating...");
		$("#ddts").attr("disabled", true);		
		$.ajax({
			url: '/isValidCDETS',
			data: 'cdets='+cdets,
			type: 'POST',
			success: function(response){
                if(response=="INVALID"){
					$("#ddts").attr("disabled", false);				
					$("#cdets_api_result").html("<br>"+response);
				}else{				
					$("#cdets_api_result").html("");
					$("#ddts").attr("disabled", false);						
					$("#add_result_submit").attr("disabled", false);				
				}		
			},
			error: function(error) {
				console.log(error);
				$("#cdets_api_result").html("<br>"+response);			
			}
		});
	}else{
		$("#ddts").attr("disabled", false);		
		$("#add_result_submit").attr("disabled", false);
		$("#cdets_api_result").html("");		
	}
	
}