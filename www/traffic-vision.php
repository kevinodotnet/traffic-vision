<?php


function pr ($o) {
	print "<pre>";
	print_r($o);
	print "</pre>";
}

class TrafficVision {

	const OBSERVATION_COUNT = 20;

	static public function getClip ($clipid) {
		$db = self::getDB();
		$sql = "
			select 
				*
			from
				tv_videoclip vc where vc.id = :clipid
		";
		pr($sql);
		$query = $db->prepare($sql);
		$query->execute(array('clipid'=>$clipid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);
		return $res;

	}

	static public function getVideoCount ($videoid) {
		$db = self::getDB();
		$sql = " 
			select tag, max(c) max_c from (
			select
				v.id videoid,
				vc.id clipid,
				c.id sampleid,
				d.tag,
				count(1) c
			from tv_video v
				join tv_videoclip vc on vc.video = v.id
				join tv_count c on c.clip = vc.id
				join tv_count_data d on d.count = c.id
			where 
				v.id = :videoid
			group by 
				v.id, 
				vc.id, 
				c.id, 
				d.tag
			) t group by tag;
		";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);

		$tags = array();
		foreach ($res as $r) {
			$tags[$r['tag']] = $r['max_c'];
		}

		$sql = " 
			select
				v.id videoid,
				vc.id clipid,
				vc.url clipurl,
				c.id sampleid,
				d.tag,
				d.num,
				d.note,
				d.frame,
				c.created sampletime,
				c.userhash
			from tv_video v
				join tv_videoclip vc on vc.video = v.id
				join tv_count c on c.clip = vc.id
				join tv_count_data d on d.count = c.id
			where v.id = :videoid
			order by 
				v.id, 
				vc.id, 
				c.id, 
				d.tag
			;
		";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$res = $query->fetchAll(PDO::FETCH_ASSOC);

		# "fold" the results to one row per sampleID

		$data = array();
		foreach ($res as $r) {

			if (!isset($data[$r['clipid']])) {
				#pr("NEW for ".$r['clipid'] . ' sample: ' . $r['sampleid']);
				# initialize a new clip

				$clip = array();

				# clip level details
				foreach (array('videoid','clipid','clipurl') as $k) { $clip[$k] = $r[$k]; }

				#$cliptags = array(); foreach ($tags as $k => $v) { $cliptags[$k] = array(); }
				#$clip['tags'] = $cliptags;

				$clip['samples'] = array();

				#$clip['counts'] = array();
				#$clip['observations'] = array();

				$data[$r['clipid']] = $clip;

			}

			# a clip has multiple samples
			$clip = $data[$r['clipid']];

			# a sample has multiple rows, one for each tag
			$samples = $clip['samples'];

			if (!isset($samples[$r['sampleid']])) {
				$samples[$r['sampleid']] = array(
					'sampleid' => $r['sampleid'],
					'sampletime' => $r['sampletime'],
					'userhash' => $r['userhash'],
					'counts' => array(),
					'observations' => array()
				);
			}
			$sample = $samples[$r['sampleid']];

 			if ($r['tag'] == '_OBSERVATION_') {
 				$obs = &$sample['observations'];
 				$obs[] = array(
 					'note' => $r['note'],
 					'frame' => $r['frame']
 				);
 			} else {
 				$counts = &$sample['counts'];
 				$counts[$r['tag']] = $r['num'];
 			}

			$samples[$r['sampleid']] = $sample;
			$clip['samples'] = $samples;
			$data[$r['clipid']] = $clip;

		}

		$res = array(
			'meta' => $tags,
			'data' => $data
		);

		return $res;
	}

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
				p.streetview,
				v.id videoid
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
        left(v.recorded,10) recorded, 
        p.id point,
        p.title,
        p.streetview,
        count(distinct(vc.id)) clips,
        sum(case when c.id is null then 0 else 1 end) samples,
				max(c.created) max_count_date
      from tv_video v 
        join tv_point p on p.id = v.point
        join tv_videoclip vc on vc.video = v.id
        left join tv_count c on c.clip = vc.id
      group by
        v.id,
        v.recorded, 
        p.id,
        p.title,
        p.streetview
      order by v.recorded desc
			";
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
				c.video,
				sum(case when cc.id is null then 0 else 1 end) counts
			from tv_videoclip c
				left join tv_count cc on cc.clip = c.id
			where
				c.video = :videoid
			group by
				c.id,
				c.url,
				c.video
			order by
				sum(case when cc.id is null then 0 else 1 end),
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
		$res = $res[0];

		$sql = " select count(c.id) counts, count(distinct(userhash)) users from tv_count c join tv_videoclip vc on vc.id = c.clip where vc.video = :videoid ";
		$query = $db->prepare($sql);
		$query->execute(array('videoid'=>$videoid));
		$stats = $query->fetchAll(PDO::FETCH_ASSOC);
		$res['stats'] = $stats[0];

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






