<?php

include("include.php");
include("traffic-vision.php");

$videoid = $_REQUEST['id'];
$format = $_REQUEST['format'];

$res = TrafficVision::getVideoCount($videoid);

if ($format == 'json') {
	print json_encode($res);
	return;
}

# convert to row/column/table format
$data = $res['data'];
$meta = $res['meta'];

$rows = array();

/*
$row = array();
foreach (array('videoid','clipid','sampleid','sampletime','userhash','url') as $k) {
	$row[] = $k;
}
foreach ($meta as $k => $v) {
	if ($k == '_OBSERVATION_') { continue; }
	$row[] = $k;
}
for ($i = 1; $i <= $meta['_OBSERVATION_']; $i++) {
	$row[] = "OBV_$i";
	$row[] = "OBV_".$i."_FRAME";
}
*/
#$rows[] = $row;

if ($format == 'html2') {
	top();
	?>
	<h1>Results for Video #<?php print $videoid; ?></h1>
	<table class="table table-bordered">
	<tr>
		<th>Video#</th>
		<th>Clip#</th>
		<th>Sample#</th>
		<th>Observations</th>
		<th>Details</th>
	</tr>
	<?php
	foreach ($data as $clip) {
		$first = 1;
		foreach ($clip['samples'] as $s) {
			?>
			<tr>
			<?php
			if ($first) {
				?>
				<td rowspan="<?php print count($clip['samples']); ?>">
				<?php print $clip['videoid'] ?>
				</td>
				<td rowspan="<?php print count($clip['samples']); ?>">
				<?php print $clip['clipid'] ?>
				</td>
				<?php
			}
			?>
				<td><a target="_blank" href="http://app.kevino.ca/traffic-vision/www/view-count.php?id=<?php print $s['sampleid']; ?>"><?php print $s['sampleid']; ?></a></td>
				<td>
				<?php
				if (count($s['observations']) == 0) {
					print "<i style=\"color: #c0c0c0;\">(no observations made)</i>";
				} else {
					?>
				<ul>
				<?php
				foreach ($s['observations'] as $o) {
					print "<li>{$o['note']} (#{$o['frame']})</li>";
				}
				?>
				</ul>
					<?php
				}
				?>
				</td>
				<td><a target="_blank" href="http://app.kevino.ca/traffic-vision/www/view-count.php?id=<?php print $s['sampleid']; ?>">view</a></td>
				<?php
			$first = 0;
			?>
			</tr>
			<?php
		}
	}
	?>
	</table>
	<?php
	bottom();
	return;
}

foreach ($data as $clip) {
	#pr($clip);
	foreach ($clip['samples'] as $s) {
		$row = array();
		foreach (array('videoid','clipid') as $k) {
			$row[$k] = $clip[$k];
		}
		foreach (array('sampleid','sampletime','userhash') as $k) {
			$row[$k] = $s[$k];
		}
		$row['url'] = 'http://app.kevino.ca/traffic-vision/www/view-count.php?id='.$s['sampleid'];
		foreach ($meta as $k => $v) {
			if (isset($s['counts'][$k])) {
				$row[$k] = $s['counts'][$k];
			}
		}
		$i = 1;
		$obs = $s['observations'];
		for ($i = 1; $i <= $meta['_OBSERVATION_']; $i++) {
			$row["OBV_$i"] = '';
			$row["OBV_$i"."_FRAME"] = '';
			if (count($obs) >= $i) {
				$o = $obs[$i-1];
				$row["OBV_$i"] = $o['note'];
				$row["OBV_$i"."_FRAME"] = $o['frame'];
			}
		}
		$rows[] = $row;
	}
}

$res = $rows;

if ($format == 'pr') {
	pr($res);
	return;
}
if ($format == 'csv') {

	header('Content-Type: application/csv');
	header('Content-Disposition: attachment; filename=trafficvision_video'.$videoid.'_'.time().'.csv');
	header('Pragma: no-cache');

	$cols = array();
	foreach ($res[0] as $k => $v) {
		$cols[] = $k;
		print "$k\t";
	}
	print "\n";
	foreach ($res as $r) {
		foreach ($cols as $c) {
			$v = $r[$c];
			$v = preg_replace('/,/',' - ',$v); # Excel is fucking brain dead. Data -> Text to Columns insists on also splitting on COMMA.
			print $v;
			print "\t";
		}
		print "\n";
	}
	return;
}

if ($format == 'html') {
	top();
	arrayOfMapToTable($res,null,function($k,$v){
		if (preg_match('/^http/',$v)) {
			return "<a href=\"$v\">link</a>";
		} else {
			return $v;
		}
	});
	bottom();
}

#pr($rows);

#pr($res);

