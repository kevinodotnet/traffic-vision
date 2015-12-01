<?php

include("include.php");
include("traffic-vision.php");

$countid = $_REQUEST['id'];

$count = TrafficVision::getCount($countid);

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
				print " (frame {$o['frame']})";
			}
			print "</li>";
		}
		?>
		</ul>
		<?php
	}
	?>
	</div>
	
	<div class="col-sm-6">
		<div class="embed-responsive embed-responsive-16by9">
			<video autoload="true" controls="controls" class="embed-responsive-item">
				<source type="video/mp4" src="<?php print $count['video_url']; ?>"/>
			</video>
		</div>
	</div>
</div>

<?php
bottom();


