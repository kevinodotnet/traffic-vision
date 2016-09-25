<?php

include("include.php");
include("traffic-vision.php");

$videoid = $_REQUEST['videoid'];
$action = $_REQUEST['action'];

if ($videoid == '') {
	top();
	?>
	<h1>Pick a video</h1>
	<?php
	arrayOfMapToTable(TrafficVision::getVideos(),null,function($k,$v){
		if ($k == 'id') {
			return "<a href=\"clip-make-observation.php?videoid=$v\">$v</a>";
		}
		return "$v";
	});
	bottom();
	return;
}

if ($action == 'save') {
	#pr($_REQUEST);

	$count = array(
		'clipid' => $_REQUEST['clipid'],
		'counts' => array(
			'car' => $_REQUEST['car'],
			'bike' => $_REQUEST['bike'],
			'ped' => $_REQUEST['ped']
		)
	);

	$obs = array();

	for ($x = 0; $x < TrafficVision::OBSERVATION_COUNT; $x++) {
		if ($_REQUEST["obs_$x"] != '') {
			$ob = array('note'=> $_REQUEST["obs_$x"]);
			if ($_REQUEST["obs_frame_$x"] != '') {
				$ob['frame'] = $_REQUEST["obs_frame_$x"];
			}
			$obs[] = $ob;
		}
	}

	$count['observations'] = $obs;

	$id = TrafficVision::saveCount($count);
	header("Location: clip-make-observation.php?videoid=$videoid&savedcount=$id#observe");
	return;
}

# display observation form

top();

$video = TrafficVision::getVideo($videoid);
$clip = TrafficVision::getVideoClipForObservation($videoid);

?>
<div class="row">
	<div class="col-sm-9">
		<h1><?php print $video['title']; ?> <small>(clip #<?php print $clip['id']; ?>)</small></h1>
	</div>
	<div class="col-sm-3 text-right">
		<?php
		$stats = $video['stats'];
		print "<b>{$stats['users']} users</b> have done <b>{$stats['counts']} counts</b> so far!";
		$savedcount = $_REQUEST['savedcount'];
		if ($savedcount != '') {
			?>
			<br/><small>Thanks! <a href="view-count.php?id=<?php print $savedcount; ?>">Your count has been saved</a>.</small>
			<?php
		}
		?>
	</div>
</div>

		<b>Quick Instructions:</b>
		<ul>
			<li><a target="_blank" href="<?php print $video['streetview']; ?>">Open Google StreetView</a> to familiarize yourself with this street/intersection.</li>
			<li>Play the video, watch for problematic interactions between cars/bikes/pedestrians.</li>
			<li>When you see one press 'o'. The video will pause automatically, and focus will jump to an observation box.</li>
			<li>Describe the problem in your own words</li>
			<li>The frame number should be populated for you.</li>
			<li>Click play, rinse, repeat!</li>
			<li>(fyi: we are no longer counting cars/bikes/peds)</li>
			<!-- <li>Count all pedestrians, even if they are on a sidewalk that doesn't "cross" a road.</li> -->
			<li><a href="#long">Read the long instructions</a> for more details or to contact the help team.</li>
		</ul>
		<hr/>

<script>
function up(id) {
	id = '#'+id;
	$(id).val( parseInt($(id).val()) + 1);
}
</script>

<form action="clip-make-observation.php?action=save" method="post">

<input type="hidden" name="videoid" value="<?php print $videoid; ?>"/>
<input type="hidden" name="clipid" value="<?php print $clip['id']; ?>"/>

<div id="observe" class="row" style="padding-top: 10px;">
	<div class="col-sm-5">

		<!--
		<b>Count:</b> <small>(hint: use 'c', 'b' and 'p' keys to count!)</small>
		<div class="row">
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('car');">cars <i class="fa fa-plus"></i></a> </div>
					<input id='car' class="form-control" type="text" name="car" value="0"/>
				</div>
			</div>
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('bike');">bikes <i class="fa fa-plus"></i></a> </div>
					<input id='bike' class="form-control" type="text" name="bike" value="0"/>
				</div>
			</div>
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('ped');">peds <i class="fa fa-plus"></i></a> </div>
					<input id='ped' class="form-control" type="text" name="ped" value="0"/>
				</div>
			</div>
		</div>
		-->

		<input class="form-control btn-primary" type="Submit" value="Submit Data for Clip #<?php print $clip['id']; ?>"/>
		<?php
		for ($x = 0; $x < TrafficVision::OBSERVATION_COUNT; $x++) {
			?>
			<div class="row" style="margin-top: 5px;">
				<div class="col-sm-1">
					#<?php print $x+1; ?>: 
				</div>
				<div class="col-sm-8">
					<input type="text" class="form-control observeinput" name="obs_<?php print $x; ?>"/>
				</div>
				<div class="col-sm-3">
					<input type="text" class="form-control" id="obs_frame_<?php print $x; ?>" name="obs_frame_<?php print $x; ?>" placeholder="frame#"/>
				</div>
			</div>
			<?php
		}
		?>
	</div>

	<div class="col-sm-7">
		<div class="embed-responsive embed-responsive-16by9" id="videodiv">
			<video id="player" autoload="true" controls="controls" class="embed-responsive-item">
				<source type="video/mp4" src="<?php print $clip['url']; ?>"/>
			</video>
		</div>
		<b>Suggested Observations and Things To Look For</b>
		<ul>
			<li>Cars turning right against the 'straight-green-arrow'</li>
			<li>Failing to stop at stop-sign. Running reds.</li>
			<li>Speeding (if you judge it faster than normal).</li>
			<li>Cars mounting sidewalks, using pedestrian spaces, to get around other cars.</li>
			<li>Bikes on sidewalks/crosswalks</li>
			<li>Cars blocking crosswalks, bike lanes</li>
			<li>Jaywalking; or crossing against the hand because the walk signal never goes on</li>
			<li><a href="#long">Read the long instructions</a> for more details or to contact the help team.</li>
		</ul>
		<b>Optional but helpful</b>: if you can note the "frame#" as well that's helpful.
	</div>
</div>

</form>

<div id="long">
<h2>Instructions</h2>

<p>
	Each traffic video clip is about a minute long, and shows one cycle of a traffic intersection. The clip starts at 10 seconds after 
	one light went red, and runs until 10 seconds after the other light goes red. This makes it easier to see the most important part of the cycle: when
	both lights are red, and drivers do the riskiest things.
	</p>
	<p>
	(If the videos were clipped at the moment both lights went red, then red-light running, etc, would be harder to 'see', since it would span two videos)
	</p>
	<p>
	The community (you!) is being asked to crowdsource the data from each clip. 
	</p>
	<p>
	Use the 'observations' form to note problems. For example, common problems at this intersection include left-turning drivers who proceed immediately 
	when the light turns green, drivers blocking the intersection, drivers who proceed into the intersection after the light has turned red, 
	curb-hopping to get around left-turning cars, and bicycles on the sidewalk or running the red. It's important to objectively note all these, 
	and any other problematic behaviour.
	</p>
	<p>
	Some sample observations. It is literally any observation you have, in your own words.
<b>Contact kevino@kevino.net or @odonnell_k if you need help or have suggestions!</b>
</p>




</div>

<script>
doCount = 1;
$( "input" ).focus(function() {
	doCount --;
	$('video').each( function(i) {
		this.pause();
	});
});
$( "input" ).focusout(function() {
	doCount ++;
	// $('video').each( function(i) { this.play(); });
});
$( "body" ).keypress(function(e) {
	if (doCount == 0) {
		return;
	}
	var code = e.keyCode || e.which;
	var k = String.fromCharCode(code);
	if (k == 'c') { up('car'); }
	if (k == 'b') { up('bike'); }
	if (k == 'p') { up('ped'); }
	if (k == 'o') { 
		$(".observeinput").each( function() {
			console.log(this);
			if (this.value == '') {
				// 'this' does not survive function call, must assign to local scope variable
				t = this;
				<?php
				// TODO: source start frame from DB instead of URL hack
				$startframe = $clip['url'];
				$startframe = preg_replace("/.*_/",'',$startframe);
				$startframe = preg_replace("/\..*/",'',$startframe);
				$startframe = preg_replace("/^0*/",'',$startframe);

				$fps = 30;
				if ($_GET['videoid'] == 4) {
					$fps = 10;
				}

				?>
				current = $('#videodiv').find('video').get(0).currentTime;
				frames = current*<?php print $fps; ?>;
				framenum = Math.round(<?php print $startframe; ?> + frames);
				inputindex = this.name.split('_')[1];
				$('#obs_frame_' + inputindex).val(framenum);
				setTimeout(function(){t.focus()},100);
				return false;
			}
		});
	}

});

</script>

<?php

bottom();
