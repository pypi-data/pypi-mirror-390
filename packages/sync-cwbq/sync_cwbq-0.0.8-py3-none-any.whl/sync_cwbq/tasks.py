#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author     :zhaoyukai
# @Time       :2025/11/6 14:17

"""

"""
import redis

from pymongo import MongoClient
from loguru import logger
from .sync_cwbq import *
from odps import ODPS
from odps.tunnel import TableTunnel

odps_client = ODPS(
    os.getenv('ACCESS_ID'),
    os.getenv('ACCESS_KEY'),
    os.getenv('PROJECT_NAME'),
    os.getenv('ENDPOINT'),
)
mongo_client = MongoClient(mongo_uri)
redis_client = redis.from_url(redis_uri, decode_responses=True)

@app.task(bind=True, autoretry_for=(Exception,), max_retries=3)
def sync_to_odps(
        self,
        table_name: str,
        table_schema: dict,
        database: str,
        collection: str,
        condition: dict,
        filter_field: dict,
        partitions: str = None,
        overwrite: bool = True
):
    """
    :param table_name: 数仓表名
    :param table_schema: 表模型，这里是基于pydantic的数据模型
    :param database: mongodb的db
    :param collection: mongodb的collection
    :param condition: mongodb过滤条件
    :param filter_field: mongodb查询结果过滤字段
    :param partitions: 数仓分区表分区，默认非分区表
    :param overwrite: 是否覆盖写入，默认True
    :return:
    """
    is_sync_flag = False if not mongo_client[database][collection].count_documents(condition) else True
    if is_sync_flag:
        sync_table = odps_client.get_table(table_name)
        tunnel = TableTunnel(odps_client)
        upload_session = tunnel.create_upload_session(
            sync_table.name,
            partition_spec=f'pt={partitions}' if partitions is not None else None,
            create_partition=True,
            overwrite=overwrite
        )
        with upload_session.open_record_writer(0) as writer:
            for result in mongo_client[database][collection].find(condition, filter_field):
                record = sync_table.new_record([result[name] for name in table_schema.keys()])
                writer.write(record)
        upload_session.commit([0])
        logger.info(
            f"{os.getenv('PROJECT_NAME')} || {table_name} || {partitions} || {database} || {collection} || 上传到数仓成功!"
        )
    else:
        logger.warning(
            f"{os.getenv('PROJECT_NAME')} || {table_name} || {partitions} || {database} || {collection} || 未找到需要同步的数据!"
        )
