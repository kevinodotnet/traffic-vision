<?php

$base=`dirname {$argv[0]}`;
$base = trim($base);
$base="$base/..";

include("$base/www/config.php");

$index = 1;
$lat = $argv[$index++];
$lon = $argv[$index++];
$title = $argv[$index++];

$sql = " insert into tv_point (lat,lon,title) values (:lat,:lon,:title) ";
$query = $db->prepare($sql);
$val = array(
				'lat' => $lat,
				'lon' => $lon,
				'title' => $title
);
$query->execute($val);
$id = $db->lastInsertId();

print "new point, id: $id\n";

