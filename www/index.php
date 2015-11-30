<?php

include("config.php");

$scale = 1.2;
$w = 640*$scale;
$h = 480*$scale;

function pr ($o) {
	print "<pre>";
	print_r($o);
	print "</pre>";
}

if ($_GET['action'] == 'view') {
	$num = intval($_GET['num']);
	?>
	<center>
				<video 
					autoload="true"
					controls="controls"
					width="<?php print $w?>px"
					>
					<source type="video/mp4" src="http://s3.kevino.ca/tmp/leiper_traffic_video/20151113_islandpark_byron_<?php print $num; ?>.mp4"/>
				</video>
				<br/>
				<br/>
				<br/>
				Want to help count traffic at this intersection? <a href="/traffic-video/">Click here!</a>
	</center>
	<?php
	return;
}

if ($_GET['action'] == 'download') {
	$sql = "
		select 
			c.id countid,
			num video,
			car,
			bike,
			ped,
			created,
			ip,
			o.observation
		from traffic_count c
			left join traffic_observation o on c.id = o.count
		order by
			c.id,
			o.id
	";
	$query = $db->prepare($sql);
	$query->execute();
	$res = $query->fetchAll(PDO::FETCH_ASSOC);

	$first = 1;

	header('Content-Type: application/csv');
	header('Content-Disposition: attachment; filename=traffic-'.time().'.csv');
	header('Pragma: no-cache');

	foreach ($res as $r) {
		if ($first == 1) {
			foreach ($r as $k => $v) {
				print "$k\t";
			}
			print "\n";
		}
		$first = 0;
		foreach ($r as $k => $v) {
			print "$v\t";
		}
		print "\n";
	}
	return;
}
if ($_POST['action'] == 'save') {

	# pr($_SERVER); return;

	$num = $_POST['num'];
	$car = $_POST['car'];
	$bike = $_POST['bike'];
	$ped = $_POST['ped'];

	$sql = " insert into traffic_count (num,car,bike,ped,ip) values (:num,:car,:bike,:ped,:ip) ";
	$query = $db->prepare($sql);
	$val = array(
		'num' => $num,
		'car' => $car,
		'bike' => $bike,
		'ped' => $ped,
		'ip' => $_SERVER['REMOTE_ADDR']
	);
	$query->execute($val);
	$id = $db->lastInsertId();

	for ($x = 0; $x < 10; $x++) {
		$key = "obs_$x";
		if ($_POST[$key] != '') {
			$query = $db->prepare(" insert into traffic_observation (count,observation) values (:count,:observation)");
			$query->execute(array('count'=>$id,'observation'=>$_POST[$key]));
		}
	}

	?>
<pre>
<b>Thanks!</b> Your data for video #<?php print $num; ?> has been saved.  <a href="/traffic-video/?action=view&num=<?php print $num; ?>">Click here</a> to view video #<?php print $num; ?> again!

Here's another video because <b>obviously</b> counting traffic is the funnest thing on the Internet!
</pre>
	<?php
}


# pick a random file

$sql = "
select
	num, sum(id) count
from
	(select n.num, (case when c.id is null then 0 else 1 end) id from traffic_file n left join traffic_count c on c.num = n.num) t
group by
	num
having 
	sum(id) < 6
order by
	sum(id), rand()
limit 1
	;
";
$query = $db->prepare($sql);
$query->execute();
$res = $query->fetch();
if ($_GET['d'] != '1' && !isset($res['num'])) {
	?>
	Looks like we've completed all the data capture! Thanks!
	<?php
	return;
}

$num = $res['num'];
if ($_GET['d'] == 1) {
	$num = 1000;
}

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<script src="mediaelement/build/mediaelement-and-player.min.js"></script>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>

	<link rel="stylesheet" href="mediaelement/build/mediaelementplayer.css" />
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">

	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.4.0/css/font-awesome.min.css">

	<style>
	body {
		padding: 5px;
	}
	</style>

</head>

<body>

<?php
?>

<form method="post" action="/traffic-video/">

<input type="hidden" name="action" value="save" />
<input type="hidden" name="num" value="<?php print $num; ?>"/>

<h3>Traffic Counting proof-of-concept</h3>

<div class="row">

<div class="col-sm-3">
					<p><b>Quick Instructions</b>: Count the cars, cyclists and pedestrians that cross
					through the intersection during this brief video clip. Count everything, in both
					directions, even after the red/green cycle changes.</p>
					<p><b>Ignore anything that is in the intersection</b> at the start of the clip. It was already counted by someone else at the end of their clip.</p>
					<p><b>Enter your results</b> in the fields, click submit! You can use the up/down arrows if you want, or just count in your head.</p>
					<p><b>Notice anything bad?</b> Enter it in the free-form "observation" fields. 
					(car/bike burning red, left-turning cars jumping the green. See long instructions for more examples.)</p>
					<p><b>Still not sure?</b> <a href="#longread">Read the longer instructions below</a>, or email kevino@kevino.net or twitter <a href="http://twitter.com/odonnell_k">@odonnell_k</a>.</p>

					<script>
					function up(id) {
						id = '#'+id;
						$(id).val( parseInt($(id).val()) + 1);
					}
					function down(id) {
						id = '#'+id;
						$(id).val( parseInt($(id).val()) - 1);
					}

					</script>

				<div class="row">
								<div class="col-sm-4">cars:<br/><input id='car' class="form-control" type="text" name="car" value="0"/>
								<a href="javascript:up('car');" <i class="fa fa-2x fa-arrow-up"></i></a>
								<a href="javascript:down('car');" <i class="fa fa-2x fa-arrow-down" style="float: right;"></i></a>
								</div>
								<div class="col-sm-4">bikes:<input id='bike' class="form-control" type="text" name="bike" value="0"/>
								<a href="javascript:up('bike');" <i class="fa fa-2x fa-arrow-up"></i></a>
								<a href="javascript:down('bike');" <i class="fa fa-2x fa-arrow-down" style="float: right;"></i></a>
								</div>
								<div class="col-sm-4">peds:<input id='ped' class="form-control" type="text" name="ped" value="0"/>
								<a href="javascript:up('ped');" <i class="fa fa-2x fa-arrow-up"></i></a>
								<a href="javascript:down('ped');" <i class="fa fa-2x fa-arrow-down" style="float: right;"></i></a>
								</div>
					</div>

					<p>Enter any (optional) observations below, like red light running, etc.</p>

		<br/>
		<input class="form-control" type="Submit"/>
	</div>

	<div class="col-sm-9">
					<!-- autoplay="true" -->
				<video 
					autoload="true"
					controls="controls"
					width="<?php print $w?>px"
					>
					<source type="video/mp4" src="http://s3.kevino.ca/tmp/leiper_traffic_video/20151113_islandpark_byron_<?php print $num; ?>.mp4"/>
				</video>
	</div>

</div>


	<?php
	for ($x = 0; $x < 10; $x++) {
		?>
	<div class="row" style="margin-top: 5px;">
	<div class="col-sm-3">
		Observation <?php print $x+1; ?>: 
	</div>
	<div class="col-sm-9">
		<input type="text" class="form-control" name="obs_<?php print $x; ?>"/>
	</div>
	</div>
		<?php
	}
	?>
</form>

	<a name="longread" id="longread"></a><h1>Detailed Instructions</b></h1>
	<p>
	Each traffic video clip is about a minute long, and shows one cycle of traffic intersection at Island Park and Byron. The clip starts at 10 seconds after 
	one light went red, and runs until 10 seconds after the other light goes red. This makes it easier to see the most important part of the cycle: when
	both lights are red, and drivers do the riskiest things.
	</p>
	<p>
	(If the videos were clipped at the moment both lights went red, then red-light running, etc, would be harder to 'see', since it would span two videos)
	</p>
	<p>
	The community (you!) is being asked to crowdsource the data from each clip. Use the up/down arrows to count, or just
	keep track in your head then fill in the values for each box before clicking submit. The cars sometimes come too fast to click.
	</p>
	<p>
	Count every car that you see enter the intersection reguardless of the red lights or direction. This means you will be counting cars in one direction
	at the start, then a few cars after they get the green in the other direction.
	</p>
	<p>
	Use the 'observations' form to note problems. For example, common problems at this intersection include left-turning drivers who proceed immediately 
	when the light turns green, drivers blocking the intersection, drivers who proceed into the intersection after the light has turned red, 
	curb-hopping to get around left-turning cars, and bicycles on the sidewalk or running the red. It's important to objectively note all these, 
	and any other problematic behaviour.
	</p>
	<p>
	Some sample observations. It is literally any observation you have, in your own words.
<ul>
<li>One car in nb IDP lane makes left after light is red.</li>
<li>One left-turning car in nb IPD lane does not yield green light, proceeds through intersection at start of phase</li>
<li>Cars stops in intersection mid-phase almost blocking intersection for opposite direction left turning car</li>
<li>Car begins to enter intersection after red, has to brake suddenly to stop as pedestrians, bikes begins their crossing</li>
<li>One nb IPD car makes turn after red light</li>
<li>Cyclist runs through red light</li>
<li>Cyclist riding through north side crosswalk (to get to eb Byron Park path) rather than make proper left turn</li>
</ul>
	</p>


	
	<script type="text/javascript">
	
		var _gaq = _gaq || [];
		_gaq.push(['_setAccount', 'UA-6324294-15']);
		_gaq.push(['_trackPageview']);
		(function() {
		var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
		ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
		})();

		$('video,audio').mediaelementplayer();
	
	</script>

</body>
</html>




