from enum import Enum

from tiefeng.common.enums.enum_items import BaseEnum, EnumItem


class ApiType(BaseEnum, Enum):
    add = EnumItem(label='添加', value='add', description='添加单条记录',
                    ext_data={'api_path': '/item', 'method': ['POST']})
    read = EnumItem(label='查看', value='read', description='查看单条记录',
                    ext_data={'api_path': '/item/{item_id}', 'method': ['GET'], 'key_name':'id'})
    update = EnumItem(label='修改', value='update', description='修改单条记录',
                    ext_data={'api_path': '/item/{item_id}', 'method': ["PUT", "POST"], 'key_name':'id'})
    delete = EnumItem(label='删除', value='delete', description='删除单条记录',
                    ext_data={'api_path': '/item/{item_id}', 'method': ["DELETE"], 'key_name':'id'})
    batch_delete = EnumItem(label='批量删除', value='batch_delete', description='批量删除多条记录',
                      ext_data={'api_path': '/batch_delete', 'method': ["DELETE"], 'key_name':'id'})
    list = EnumItem(label='列表', value='list', description='查询所有记录',
                      ext_data={'api_path': '/list', 'method': ["GET", "POST"]})
    page = EnumItem(label='分页列表', value='page', description='分页查询多条记录',
                      ext_data={'api_path': '/page/{page_num}/{page_size}', 'method': ["GET", "POST"]})

