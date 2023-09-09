<?php
/*
 * pdf upload script, typical *.bat file for upload:
@echo off
set upload=
for %%f in (*.pdf) do set upload=%upload% -F "%%f=@%%f"
curl -X POST %upload% -H "X-Secret: PLEASE_FILL_IN_SOME_WRITE_SECRET" https://your-domain.com/upload.php
pause
 */

if(!hash_equals('PLEASE_FILL_IN_SOME_WRITE_SECRET', $_SERVER['HTTP_X_SECRET']))
{
	header('HTTP/1.1 403 Access denied');
	die('Access denied');
}

//delete all 4 pdf files and create new ones with uploaded contents, if given
clearstatcache();
for($i=0; $i<4; $i++)
{
	$destfile = ($i+1).".pdf";
	$entryname = ($i+1)."_pdf";
	@unlink(dirname(__FILE__)."/$destfile");
	//ohne diese if, werden die dateien neu durchnummeriert und dürfen jeden beliebigen namen tragen
	//mit dieser if, müssen sie schon auf dem quellrechner durchnummeriert sein
	/*if(isset($_FILES[$entryname]) && $_FILES[$entryname]["name"] != $destfile)
		echo "Ignoring unexpected file '{$_FILES[$entryname]["name"]}'...\n";
	else*/ if(isset($_FILES[$entryname]) && $_FILES[$entryname]["error"]==UPLOAD_ERR_OK)
	{
		move_uploaded_file($_FILES[$entryname]["tmp_name"], dirname(__FILE__)."/$destfile");
		//echo "PDF $destfile ({$_FILES[$entryname]["tmp_name"]}) uploaded successfully to ".(dirname(__FILE__)."/$destfile")."...\n";
		echo "PDF {$_FILES[$entryname]["name"]} ($destfile) uploaded successfully...\n";
	}
	else
		echo "PDF $destfile deleted successfully...\n";
}
echo "All done...\n";
?>