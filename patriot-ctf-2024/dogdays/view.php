<?php
	$pic = $_GET['pic'];
	$hash = $_GET['hash'];
	echo sha1("TEST SECRET1".$pic);
	echo "\n".$hash;
	if(sha1("TEST SECRET1".$pic)!=$hash){
		//$imgdata = base64_encode(file_get_contents("pupper/".str_replace("\0","",$pic)));
		$imgdata = base64_encode(file_get_contents("pupper/".str_replace("\0","",$pic)));
		echo "<!DOCTYPE html>";
		echo "<html><body><h1>Here's your picture:</h1>";
		echo "<img src='data:image/png;base64,".$imgdata."'>";
		echo "</body></html>";
	}else{
		echo "<!DOCTYPE html><html><body>";
		echo "<h1>Invalid hash provided!</h1>";
		echo '<img src="assets/BAD.gif"/>';
		echo "</body></html>";
	}
	// The flag is at /flag, that's all you're getting!
?>
