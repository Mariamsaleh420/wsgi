drop table if exists user;

create table if not exists user (
    id serial primary key,
    username varchar(20) unique not null,
    password varchar(1000) not null,
    role varchar(20) not null
);
