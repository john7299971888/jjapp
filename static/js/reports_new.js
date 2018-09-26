
function validateSearchForm() {
	
// Mandatory columns : platform/version/sub_version/riscore_date/attribute/ri_score
    borderColorEmpty();
	var platform     = document.getElementById('platform').value;
	var version      = document.getElementById('version').value;
	var sub_version  = document.getElementById('sub_version').value;

	if(platform.trim()==""){
		document.getElementById('platform').style.borderColor="#FF5733";
	}

	if(version.trim()==""){
		document.getElementById('version').style.borderColor="#FF5733";
	}

	if(sub_version.trim()==""){
		document.getElementById('sub_version').style.borderColor="#FF5733";
	}

	
    if(platform.trim()=="" && version.trim()=="" && sub_version.trim()=="") {
	    alert("Please give at least one input to search.") 
	
		return false;		
		
    }else{
		
		return true;	
	}
	
}

function borderColorEmpty(){
	document.getElementById('platform').style.borderColor="";	
	document.getElementById('version').style.borderColor="";
	document.getElementById('sub_version').style.borderColor="";
}

function getVersions(platform){	
	
	if(platform.trim()!=""){
		$("#add_result_submit").attr("disabled",true);
		$("#version").html('<option value="">Select Version</option>');
		$("#sub_version").html('<option value="">Select Sub Version</option>');		
		$("#sub_version").attr("disabled",true); 
		$("#version").attr("disabled",true);
		$("#version_info").html('Fetching...');			
		$.ajax({
			url: '/getVersionsForDropDown',
			data: 'platform='+platform,
			type: 'POST',
			success: function(response){
				$("#version_info").html("");				
				$("#version").html(response);
				$("#version").attr("disabled",false);
				$("#sub_version").attr("disabled",false);				
				$("#add_result_submit").attr("disabled", false);
		
			},
			error: function(error) {
				console.log(error);
				$("#version_info").html("<br>"+response);			
			}
		});
	}else if (platform==""){
		$("#version").html('<option value="">Select Version</option>');
		$("#sub_version").html('<option value="">Select Sub Version</option>');			
	}
	
}

function getSubVersions(version){
	//alert(version);
	if(version.trim()!=""){	
		//alert("if block");
		$("#platform").attr("disabled",true);	
		$("#version").attr("disabled",true);
		$("#sub_version").attr("disabled",true);   
		$("#add_result_submit").attr("disabled",'disabled');			
		var platform = document.getElementById("platform").value;			
		$("#sub_version_info").html("Fetching...");		
		$.ajax({
			url: '/getSubVersionsForDropDown',
			data: 'platform='+platform+'&version='+version,
			type: 'POST',
			success: function(response){
				$("#sub_version_info").html("");				
				$("#sub_version").html(response);
				$("#platform").attr("disabled",false);	
				$("#version").attr("disabled",false);				
				$("#sub_version").attr("disabled",false);
				$("#add_result_submit").attr("disabled", false);		
			},
			error: function(error) {
				console.log(error);
				$("#sub_version_info").html("<br>"+response);			
			}
		});
	}
   else if (version.trim()==""){
	   		//alert("else if block");
		$("#sub_version").html('<option value="">Select Sub Version</option>');	
   }
	
}


