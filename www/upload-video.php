<?php
include('include.php');
top();
?>
<div class="row">
	<div class="col-sm-6 col-sm-offset-3">

	<?php

	include('config.php');

	$uploaderEmail = $_GET['uploaderEmail'];

	?>
    <center><h1>Upload a video to Traffic Vision</h1></center>
		<p>
		I'm working on automating a traffic monitoring system. The first step is to get video uploads
		from the community (in a way that's easier than shuffling USB memory sticks around. So, use
		this form to upload a file of any size (even multiple gigabytes!). I'll get an email that 
		you've done so and will take it from there.
		</p>

		<p>Tips for the video:</p>

		<ul>
		<li>Record stuff, preferably at least 30 minutes.</li>
		<li>Try not to move the camera too much, but if you do, don't worry about it.</li>
		</ul>

		<?php

		if ($uploaderEmail == '') {
			?>
			<form action="" method="get">
			To start, I need your email address so I can contact you after the video upload:
			<br/><br/>
			<input class="form-control" type="email" name="uploaderEmail" placeHolder="Email"/>
			<br/><br/>
      <input class="btn btn-primary" type="submit" value="Continue"/> 

			</form>
			<?php
		} else {

			$file = date('Ymd_His').'_'.$uploaderEmail.'_'.GUID();
			$date = gmdate('Y-m-d\TH:i:s\Z',time()+(3*60*60));
			$display_date = gmdate('Y-m-d H:i:s',time()+(3*60*60));
		
			#"expiration": "2016-12-01T00:00:00Z",
			$policy_doc = '
			{
			"expiration": "'.$date.'",
		  "conditions": [ 
		    {"bucket": "s3.kevino.ca"}, 
				["content-length-range", 1, 17179869184],
		    ["starts-with", "$key", "traffic-vision/uploads/'.$file.'"],
		    {"acl": "private"},
		    {"success_action_redirect": "http://app.kevino.ca/traffic-vision/www/upload-success.php"},
			]
			}';
		
			$policy_base64 = base64_encode($policy_doc);
		
			$sig = hash_hmac('sha1', $policy_base64, $aws_secret, true);
			$sig = base64_encode($sig);
			$sig = trim($sig);
			$signature = $sig;
			?>

    <form action="http://s3.kevino.ca.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
      <input id="filekey" type="hidden" name="key" value="traffic-vision/uploads/<?php print $file; ?>">
      <input type="hidden" name="AWSAccessKeyId" value="<?php print $aws_key; ?>"> 
      <input type="hidden" name="acl" value="private"> 
      <input type="hidden" name="success_action_redirect" value="http://app.kevino.ca/traffic-vision/www/upload-success.php">
      <input type="hidden" name="policy" value="<?php print $policy_base64; ?>">
      <input type="hidden" name="signature" value="<?php print $signature; ?>">
			<div class="step">
			<b>Choose a video file to upload:</b><br/>
      <input id="fileupload" name="file" type="file"> 
			</div>
			<div class="step">
      <input id="filesubmit" class="btn btn-primary" type="submit" value="Begin Upload"> 
			</div>

			<script>
			$('#fileupload').on('change',function(){
				var file = $("#fileupload").prop("files")[0];
				$("#filekey").val("traffic-vision/uploads/<?php print $file; ?>_"+file.name);
			});
			$('#filesubmit').on('click',function(){
				$("#filesubmit").val("... uploading ...");
			});
			</script>

    </form> 

		<?php
		}
		?>

	</div>
</div>
<?
bottom();
