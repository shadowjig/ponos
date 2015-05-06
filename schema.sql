drop table if exists feeds;
create table feeds (
  feed_id integer primary key autoincrement,
  feed_title text not null,
  feed_url text not null
);