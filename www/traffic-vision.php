<?php


function pr ($o) {
	print "<pre>";
	print_r($o);
	print "</pre>";
}

class TrafficVision {

	static public function getDB() {
		include("config.php");
		return $db;
	}

	static public function getVideos() {
		$db = self::getDB();
		$sql = " 
			select 
				v.id,
				v.recorded,
				p.id point,
				p.title
			from tv_video v
				join tv_point p on p.id = v.point
			order by v.recorded desc ";
		$query = $db->prepare($sql);
		$query->execute();
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		return $res;
	}

	static public function getVideoClips ($videoid) {
		$db = self::getDB();
		$sql = " 
			select 
				c.id,
				c.url,
				c.video
			from tv_videoclip c
			where
				c.video = :videoid
		";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		return $res;
	}

}

