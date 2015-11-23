
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

