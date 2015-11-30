<?php

function arrayOfMapToTable ($rows,$cols,$formatter) {
	if (!isset($cols)) {
		$cols = array();
		foreach ($rows[0] as $k=>$v) {
			$cols[] = $k;
		}
	}
	?>
	<table class="table table-bordered">
		<tr>
		<?php foreach ($cols as $c) { print "<th>$c</th>"; } ?>
		</tr>
		<?php
		foreach ($rows as $r) {
			print "<tr>";
			foreach ($cols as $c) { print "<td>".$formatter($c,$r[$c])."</td>"; }
			print "</tr>";
		}
		?>
	</table>
	<?php
	
}

function top() {
	?>
	<html>
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
}

function bottom() {
	?>
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
	<?php
}
