<?php

$base=`dirname {$argv[0]}`;
$base = trim($base);
$base="$base/..";

include("$base/www/config.php");

$index = 1;
$point = $argv[$index++];
$recorded = $argv[$index++];

$sql = " insert into tv_video (point,recorded) values (:point,:recorded) ";
$query = $db->prepare($sql);
$val = array(
				'point' => $point,
				'recorded' => $recorded
);
$query->execute($val);
$id = $db->lastInsertId();

print "new video, id: $id\n";

