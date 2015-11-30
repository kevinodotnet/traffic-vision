<?php

$base=`dirname {$argv[0]}`;
$base = trim($base);
$base="$base/..";

include("$base/www/config.php");

$index = 1;
$video = $argv[$index++];
$url = $argv[$index++];

$sql = " insert into tv_videoclip (video,url) values (:video,:url) ";
$query = $db->prepare($sql);
$val = array(
				'video' => $video,
				'url' => $url
);
$query->execute($val);
$id = $db->lastInsertId();

print "new videoclip, id: $id\n";

