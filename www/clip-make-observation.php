<?php

include("include.php");
include("traffic-vision.php");

$fps = 30;
if ($_GET['videoid'] == 4) {
	$fps = 10;
}

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
			'carblock' => $_REQUEST['carblock'],
			'carwait' => $_REQUEST['carwait'],
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

	<center>
	(See below the video for instructions)
	</center>

		<!-- 
		<b>Count:</b>
		<small>(hint: use 'c', 'b' and 'p' keys to count!)</small> -->
		<div class="row">
			<!--
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('mupBike');">(m)upBike <i class="fa fa-plus"></i></a> </div>
					<input id='mupBike' class="form-control" type="text" name="mupBike" value="0"/>
				</div>
			</div>
			-->
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('bike');">(b)ikes <i class="fa fa-plus"></i></a> </div>
					<input id='bike' class="form-control" type="text" name="bike" value="0"/>
				</div>
			</div>
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('carblock');">(c)arblocks <i class="fa fa-plus"></i></a> </div>
					<input id='carblock' class="form-control" type="text" name="carblock" value="0"/>
				</div>
			</div>
			<div class="col-sm-4 form-group">
				<div class="input-group">
					<div class="input-group-addon"><a href="javascript:up('carwait');">car(w)aits <i class="fa fa-plus"></i></a> </div>
					<input id='carwait' class="form-control" type="text" name="carwait" value="0"/>
				</div>
			</div>
		</div>

		<input class="form-control btn-success" type="Submit" value="Submit Data for Clip"/>
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
		<input class="form-control btn-success" type="Submit" value="Submit Data for Clip #<?php print $clip['id']; ?>"/>
	</div>

	<div class="col-sm-7">
		<div class="embed-responsive embed-responsive-16by9" id="videodiv">
			<video id="player" autoload="true" controls="controls" class="embed-responsive-item">
				<source type="video/mp4" src="<?php print $clip['url']; ?>"/>
			</video>
		</div>
		<a name="#instructions"></a><b>Instructions:</b>
		<ul>
			<li><a target="_blank" href="<?php print $video['streetview']; ?>">Open Google StreetView</a> to familiarize yourself with this street/intersection.</li>
			<li>Press
			<ul>
			<li>"<b>b</b>" to count bikes going by.</li>
			<li>"<b>c</b>" to count cars that block the bike lane.</li>
			<li>"<b>w</b>" to count cars that wait without blocking the lane.</li>
			<li>Or, click the buttons above.</li>
			</ul>
			</li>
			<li>If you see something else that seems important, press "o" to make an observation.
			<ul>
			<li>The video will pause automatically, and focus will jump to an observation box.</li>
			<li>Describe the problem in your own words</li>
			<li>The frame number should be populated for you.</li>
			<li>Click play, rinse, repeat!</li>
			</ul>
			</li>
			<li>Click the green <b>Submit Data for Clip</b> button to save.</li>
		</ul>
		<hr/>
	</div>
</div>

</form>

<!--
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
-->

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
window.onkeydown = function(e) {
	current = $('#videodiv').find('video').get(0).currentTime;
	if (e.keyCode == 37 && e.target == document.body) {
		$('#videodiv').find('video').get(0).currentTime = current - 0.5;
		e.preventDefault(); 
	}
	if (e.keyCode == 39 && e.target == document.body) {
		$('#videodiv').find('video').get(0).currentTime = current + 0.5;
		e.preventDefault(); 
	}
	if (e.keyCode == 32 && e.target == document.body) {
		e.preventDefault(); 
		$('video').each( function(i) {
			if (this.paused) {
				this.play();
			} else {
				this.pause();
			}
		});
	} 
};
$( "body" ).keypress(function(e) {
	if (doCount == 0) {
		return;
	}
	var code = e.keyCode || e.which;
	var k = String.fromCharCode(code);
	if (k == 'c') { up('carblock'); }
	if (k == 'w') { up('carwait'); }
	if (k == 'm') { up('mupBike'); }
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
