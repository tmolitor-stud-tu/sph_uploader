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

//delete all pdf files and create new ones with uploaded contents, if given
clearstatcache();
foreach(glob(dirname(__FILE__)."/*.pdf") as $filename)
{
	@unlink($filename);
	echo "PDF file '".basename($filename)."' deleted successfully...\n";
}
foreach(array_keys($_FILES) as $i=>$entryname)
{
	$destfile=($i+1).".pdf";
	if($_FILES[$entryname]["error"]==UPLOAD_ERR_OK)
	{
		move_uploaded_file($_FILES[$entryname]["tmp_name"], dirname(__FILE__)."/$destfile");
		//echo "PDF $destfile ({$_FILES[$entryname]["tmp_name"]}) uploaded successfully to ".(dirname(__FILE__)."/$destfile")."...\n";
		echo "PDF file '{$_FILES[$entryname]["name"]}' uploaded successfully as '$destfile'...\n";
	}
}
echo "All done...\n";
?>