<?php

include("include.php");
include("traffic-vision.php");

top();

?>

<div class="row">
	<div class="col-sm-6">
		<h1 class="text-center">What is Traffic Vision?</h1>
		<p>Traffic Vision is a simple croudsourcing engine for
		measuring traffic (drivers, cyclists, pedestrians)
		on roads by cutting a long video into individual
		clips.</p>
		<p>Volunteers (you!) watch a clip and count the
		traffic, while also recording any ad-hoc observation
		they might find important.</p>
		<p>The Ottawa Citizen <a href="http://ottawacitizen.com/driving/citizen-science-hits-the-road-in-kitchissippi-traffic-study">wrote up an article</a>
		about the community effort. Lots of interesting tidbits there for additional reading.</p>
	</div>
	<div class="col-sm-6">
		<h1 class="text-center">What happens then?</h1>
		<p>
		We try to get multiple samples of the same clip by 
		different users to get data that is more reliable.
		That data is freely available to everyone to look at,
		but likely most useful to the person who shot the video
		in the first place.
		</p>
		<p>
		Councillor Jeff Leiper has already started taking the 
		count data, and community observations, to the city's
		traffic department.
		</p>
		<p>
		Ultimately the point is to improve safety through hard
		data and direct, explicit observation. I wanted to help
		because that's the exact type of direct action I think
		will be effective.
		</p>
		

	</div>
</div>
<div class="row">
	<div class="col-sm-6">
		<h1 class="text-center">How can I help?</h1>
		<p>
		The most valuable to contribution possible is to pick one
		of the videos below (likely the first one in the list) and
		do an observation. The more data we have, the better.
		</p>
		<p>
		I can't promise for certain, but I'm certainly open to 
		receiving videos (720p minimum quality) from you if you 
		want to record a problematic traffic situation. Probably
		best to contact me first. Volunteer time to run the 
		video through the processor is limited (but I love the
		challenge, so don't be shy).
		</p>
	</div>
	<div class="col-sm-6">
		<h1 class="text-center">Upload a video!</h1>
		<p>
		Have you identified a problem area/intersection/etc
		and would like the crowd to analyze it? 
		<a href="upload-video.php">Use the video upload form</a> that
		can accept huge files (multiple gigabytes). Upload your video
		and I'll get an email when it's done, and take it from there.
		</p>
		<p>
		If you're not sure how to record the video, drop kevino@kevino.net
		an email first.
		</p>
	</div>
</div>

<h1>Vision Video List</h1>
<table class="table table-bordered">
<tr>
	<th>Contribute</th>
	<th>Recorded</th>
	<th>Newest Sample At</th>
	<th>%Complete</th>
	<th>Location</th>
	<th>Street View</th>
	<th>Data</th>
</tr>

<?php
$videos = TrafficVision::getVideos();
foreach ($videos as $v) {
	$clazz = "btn-success";
	$doText = "Do a Sample";
	if ($v['id'] >= 3) {
		$perc = 100*$v['samples']/(3*$v['clips']);
		$perc = sprintf('%d%%',100*$v['samples']/(3*$v['clips']));
	} else {
		$perc = 100*$v['samples']/(2*$v['clips']);
		$perc = sprintf('%d%%',100*$v['samples']/(2*$v['clips']));
	}
	if ($perc >= 100 || $v['id'] <= 2) {
		$clazz = "btn-default";
		$doText = "Goal Reached";
	}
	print "<tr>";
	print "<td><a class=\"btn $clazz btn-xs\" href=\"clip-make-observation.php?videoid={$v['id']}\">$doText</a></td>";
	print "<td>".$v['recorded']."</td>";
	print "<td>".$v['max_count_date']."</td>";
	print "<td>".$perc."</td>";
	print "<td>".$v['title']."</td>";
	print "<td><a target=\"blank\" href=\"{$v['streetview']}\"><i class=\"fa fa-external-link\"></i></a></td>";
	print "<td>
		<a href=\"video-count-data.php?id={$v['id']}&format=csv\">csv</a>
		<a href=\"video-count-data.php?id={$v['id']}&format=json\">json</a>
		<a href=\"video-count-data.php?id={$v['id']}&format=html\">html</a>
		<a href=\"video-count-data.php?id={$v['id']}&format=html2\">html2</a>
	";
	print "</tr>";
}

?>
</table>
<?php

bottom();

