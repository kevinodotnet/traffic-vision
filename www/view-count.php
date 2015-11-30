<?php

include("include.php");
include("traffic-vision.php");

$countid = $_REQUEST['id'];

$count = TrafficVision::getCount($countid);

pr($count);

print "countid: $countid";

