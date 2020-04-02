drop table if exists users;
create table users (
    id integer primary key,
    username text unique not null,
    password text not null
);

/* Dummy user while developing. */ 
/* admin:malwifi */
insert into users (username, password) values 
    ("admin", "pbkdf2:sha256:150000$RmMj9SQQ$22e61582fffe02261f71e488a0a5e8386b41edf75b9fda4302682e080314d544");