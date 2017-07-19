
	<?php
	include('config.php');
	include('include.php');
	top();
	$bucket = $_GET['bucket'];
	$key = $_GET['key'];

	$key = preg_replace('/tra.*\//','',$key);

	mail("kevino@kevino.net","traffic-vision upload: $key",$key);

	?>

	<h1>Success!</h1>
	Your file has been uploaded, and Kevin has been notified by email that file# "<?php print $key; ?>" is ready for processing..
	<br/>
	<br/>
	<a class="btn btn-primary" href="upload-video.php">Upload another</a>.
	<br/>
	<br/>
	
	<small>reference# <?php print $key; ?></small>

	<?php
	bottom();

