<?php


function pr ($o) {
	print "<pre>";
	print_r($o);
	print "</pre>";
}

class TrafficVision {

	const OBSERVATION_COUNT = 20;

	static public function getDB() {
		include("config.php");
		return $db;
	}

	static public function getCount ($id) {

		$db = self::getDB();
		$sql = " 
			select
				c.id countid,
				c.clip,
				c.created,
				c.userhash,
				vc.url video_url,
				p.title,
				p.streetview
			from tv_count c
				join tv_videoclip vc on vc.id = c.clip
				join tv_video v on v.id = vc.video
				join tv_point p on p.id = v.point
			where c.id = :id
		";
		$query = $db->prepare($sql);
		$query->execute(array('id'=>$id));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		$count = $res[0];

		$sql = " 
			select
				*
			from tv_count_data d
			where d.count = :id
		";
		$query = $db->prepare($sql);
		$query->execute(array('id'=>$id));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);

		$counts = array();
		$observations = array();

		foreach ($res as $r) {
			if ($r['tag'] == '_OBSERVATION_') {
				$observations[] = array( 
					'note' => $r['note'],
					'frame' => $r['frame']
				);
			} else {
				$counts[$r['tag']] = $r['num']; // [] = array( $r['tag'] => $r['num']);
			}
		}

		$count['counts'] = $counts;
		$count['observations'] = $observations;
		#$count['data'] = $res;

		return $count;
		
	}

	static public function saveCount ($count) {
		#pr($count);

		$hash = md5($_SERVER['HTTP_USER_AGENT'].$_SERVER['REMOTE_ADDR']);

		$sql = " insert into tv_count (clip,userhash) values (:clip,:userhash) ";
		$db = self::getDB();
		$query = $db->prepare($sql);
		$val = array(
			'clip' => $count['clipid'],
			'userhash' => $hash
		);
		$query->execute($val);
		$countid = $db->lastInsertId();


		foreach ($count['counts'] as $k => $v) {
			$sql = " insert into tv_count_data (count,tag,num) values (:countid,:tag,:num) ";
			$query = $db->prepare($sql);
			$val = array(
				'countid' => $countid,
				'tag' => $k,
				'num' => $v
			);
			$query->execute($val);
		}
		foreach ($count['observations'] as $o) {
			$sql = " insert into tv_count_data (count,tag,note,frame) values (:countid,:tag,:note,:frame) ";
			$query = $db->prepare($sql);
			$val = array(
				'countid' => $countid,
				'tag' => '_OBSERVATION_',
				'note' => $o['note'],
				'frame' => $o['frame']
			);
			$query->execute($val);
		}

		return $countid;
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

	static public function getVideoClipForObservation ($videoid) {
		$db = self::getDB();
		$sql = " 
			select 
				c.id,
				c.url,
				c.video
			from tv_videoclip c
			where
				c.video = :videoid
			order by
				rand()
			limit 1
		";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		return $res[0];
	}

	static public function getVideo ($videoid) {
		$db = self::getDB();
		$sql = " 
			select 
				v.id,
				v.recorded,
				p.id point,
				p.title,
				p.streetview
			from tv_video v
				join tv_point p on p.id = v.point
			where
				v.id = :videoid
		";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		return $res[0];
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

