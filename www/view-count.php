<?php

include("include.php");
include("traffic-vision.php");

$countid = $_REQUEST['id'];

$count = TrafficVision::getCount($countid);
$fps = 30;
if ($count['videoid'] == 4) {
	$fps = 10;
}

top();

?>

<div class="row">

	<div class="col-sm-6">
	<h3><?php print $count['title']; ?></h3>
	<table class="table table-bordered">
	<tr><th>Count Recorded</th><td><?php print $count['created']; ?></td></tr>
	<tr><th>Street View</th><td><a target="_blank" href="<?php print $count['streetview']; ?>">link <i class="fa fa-external-link"></i></a></td></tr>
	<?php
	foreach ($count['counts'] as $k=>$v) {
		if ($v == '') { continue; }
		?>
		<tr><th><?php print $k; ?></th><td><?php print $v; ?></td></tr>
		<?php
	}
	?>
	</table>
	<?php
	if (count($count['observations']) > 0) {
		?>
		<b>Observations:</b>
		<ul>
		<?php
		foreach ($count['observations'] as $o) {
			print "<li>".htmlentities($o['note']);
			if (isset($o['frame'])) {
				print " (frame <a href=\"javascript:gotoFrame({$o['frame']});\">{$o['frame']}</a>)";
			}
			print "</li>";
		}
		?>
		</ul>
		<?php
	}

	?>
	<script>
	function gotoFrame(num) {

				<?php
				// TODO: source start frame from DB instead of URL hack
				$startframe = $count['video_url'];
				print "// startframe: $startframe\n";
				$startframe = preg_replace("/.*_/",'',$startframe);
				print "// startframe: $startframe\n";
				$startframe = preg_replace("/\..*/",'',$startframe);
				print "// startframe: $startframe\n";
				$startframe = preg_replace("/^0+/",'',$startframe);
				print "// startframe: $startframe\n";
				if ($startframe == '') { $startframe = 0; }
				?>

				startFrame = <?php print $startframe; ?>;
				fps = <?php print $fps; ?>;

				console.log('----- jump to -----');
				console.log('startFrame: ' + startFrame);
				console.log('fps: ' + fps);
				console.log('num       : ' + num);
				frameDelta = (num - startFrame);
				console.log('frameDelta: ' + frameDelta);
				frameDelta = (num - startFrame)/fps;
				console.log('secondsDelta: ' + frameDelta);
				frameDelta = frameDelta-3; // go one second back to get context
				$('#videodiv').find('video').get(0).currentTime = frameDelta;
				$('video').each( function(i) {
					this.play();
				});
		
	}
	</script>
	<a class="btn btn-primary" href="clip-make-observation.php?videoid=<?php print $count['videoid']; ?>">Contribute by doing a count!</a>
	</div>
	
	<div class="col-sm-6">
		<div class="embed-responsive embed-responsive-16by9" id="videodiv">
			<video autoload="true" controls="controls" class="embed-responsive-item"><source type="video/mp4" src="<?php print $count['video_url']; ?>"/></video>
		</div>
	</div>
</div>

<?php
#pr($count);
bottom();


