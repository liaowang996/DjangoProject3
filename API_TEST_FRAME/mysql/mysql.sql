create database api_test ;
use api_test;

create table case_info(
    case_id varchar(10),
    case_name varchar(100) not null,
    is_run tinyint(1) not null DEFAULT 1,
    primary key (case_id)
)default charset=utf8;

create table case_step_info(
    case_id varchar(10) not null,
    case_step_name varchar(20) not null,
    api_id varchar(100) not null,
    get_value_type varchar(20) not null,
    variable_name varchar(20) not null,
    excepted_result_type varchar(20) not null,
    excepted_result varchar(300) not null,
    CONSTRAINT fk_case_id FOREIGN KEY(case_id) REFERENCES case_info(case_id)
)DEFAULT charset=utf8;


create table api_info(
    api_id varchar(100) not null,
    api_name varchar(100) not null,
    api_request_type varchar(10) not null,
    api_request_url varchar(300) not null,
    api_url_params varchar(300) not null,
    api_post_data varchar(1000) not null,
    primary key (api_id)
)default charset=utf8;


INSERT INTO case_info VALUES('case_01','注册接口',1);
INSERT INTO case_info VALUES('case_02','登录失败接口',1);
INSERT INTO case_info VALUES('case_03','登录失败接口1',1);


INSERT INTO api_info VALUES('api_0001','注册接口','POST','/api/register','{"email": "sydney@fife","password": "pistol"}','');

INSERT INTO api_info VALUES('api_0002','登录失败接口','POST','/api/login','{"email": "123123"}','');
INSERT INTO api_info VALUES('api_0003','登录失败接口1','POST','/api/login','{"email": "123123"}','');

INSERT INTO case_step_info VALUES('case_01','step_01','api_0001','正则匹配','total_pages','json键是否存在','total_pages','"total_pages":(.+?)');
INSERT INTO case_step_info VALUES('case_02','step_01','api_0002','无','','json键是否存在','error','');
INSERT INTO case_step_info VALUES('case_03','step_01','api_0003','无','','json键是否存在','error','');


