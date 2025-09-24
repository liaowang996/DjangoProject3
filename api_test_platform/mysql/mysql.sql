create database api_test ;
use api_test;

create table case_info(
    case_id varchar(10),
    case_name varchar(100) not null,
    is_run tinyint(1) not null DEFAULT 1,
    CaseInfo_id varchar(10),
    primary key (CaseInfo_id),
)default charset=utf8;
alter TABLE case_info MODIFY COLUMN is_run VARCHAR(4);

create table case_step_info(
    CaseStepInfo_id varchar(10),
    case_id varchar(10) not null,
    case_step_name varchar(20) not null,
    part_name varchar(255),
    api_id varchar(100) not null,
    get_value_type varchar(20) not null,
    variable_name varchar(20) not null,
    excepted_result_type varchar(20) not null,
    excepted_result varchar(300) not null,
    is_pass varchar(255),
    get_value_code varchar(255),
    CONSTRAINT fk_case_id FOREIGN KEY(CaseStepInfo_id) REFERENCES case_info(id)
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

SELECT
	b.case_id AS '测试用例编号',
	b.is_run AS '是否执行',
	a.part_name AS '模块名称',
	b.case_name AS '测试用例名称',
	a.case_step_name AS '测试用例步骤',
	c.api_name AS '接口名称',
	c.api_request_type AS '请求方式',
	c.api_request_url AS '请求地址',
	c.api_url_params AS '请求参数(get)',
	c.api_post_data AS '提交数据(post)',
	a.get_value_type AS '取值方式',
	a.variable_name AS '传值变量',
	a.get_value_code AS '取值代码',
	a.excepted_result_type AS '期望结果类型',
	a.excepted_result AS '期望结果',
	a.is_pass   AS '是否通过'
FROM
	case_step_info a
	LEFT JOIN case_info b ON a.CaseStepInfo_id = b.CaseInfo_id
	LEFT JOIN api_info c ON a.api_id = c.api_id
ORDER BY
    a.part_name,
	b.case_id,
	a.case_step_name;