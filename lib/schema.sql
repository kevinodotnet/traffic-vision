
/* placaes where multiple recordings are made */
drop table if exists tv_videoclip;
drop table if exists tv_video;
drop table if exists tv_point;

create table tv_point (
  id mediumint not null auto_increment,
	lat decimal(10,8),
	lon decimal(10,8),
	title varchar(256),
  primary key (id)
) engine = innodb;

create table tv_video (
  id mediumint not null auto_increment,
	point mediumint not null,
	recorded datetime not null,
  primary key (id),
	constraint `tv_vid_fk1` foreign key (point) references tv_point (id)
) engine = innodb;

create table tv_videoclip (
  id mediumint not null auto_increment,
	video mediumint not null,
	url varchar(1024) not null,
  primary key (id),
	constraint `tv_videoclip_fk1` foreign key (video) references tv_video (id)
) engine = innodb;

/*

drop table if exists traffic_file;
create table traffic_file (
  id mediumint not null auto_increment,
  num int,
  primary key (id)
) engine = innodb;

drop table if exists traffic_count;
create table traffic_count (
  id mediumint not null auto_increment,
  num int,
	car int,
	bike int,
	ped int,
  created datetime default CURRENT_TIMESTAMP,
	ip varchar(20),
  primary key (id)
) engine = innodb;

create table traffic_observation (
  id mediumint not null auto_increment,
  count mediumint not null,
	observation varchar(1024),
  primary key (id)
) engine = innodb;

*/
