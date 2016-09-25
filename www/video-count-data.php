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
#$rows[] = $row;

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

#pr($rows);

top();
arrayOfMapToTable($res,null,function($k,$v){
	if (preg_match('/^http/',$v)) {
		return "<a href=\"$v\">$v</a>";
	} else {
		return $v;
	}
});
bottom();
#pr($res);

