from xl_database import db
from jsonschema import validate
from sqlalchemy import String, Text


class DatabaseMixin:
    __fuzzy__ = []
    __exact__ = []
    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def rollback():
        db.session.rollback()

    @staticmethod
    def query_(*args, **kwargs):
        return db.session.query(*args, **kwargs)

    @staticmethod
    def add_all(items):
        db.session.add_all(items)
        db.session.commit()
        return items


class QueryMixin:
    @classmethod
    def select(cls, params, conds):
        """模糊匹配筛选"""
        flts = []
        for cond in conds:
            value = params.get(cond)
            flts += [getattr(cls, cond).like(f'%{value}%')
                     ] if value not in [None, ''] else []
        return flts

    @classmethod
    def select_(cls, params, conds):
        """精确匹配筛选"""
        flts = []
        for cond in conds:
            value = params.get(cond)
            flts += [getattr(cls, cond) ==
                     value] if value not in [None, ''] else []
        return flts

    @classmethod
    def select_date(cls, attr_name, params):
        """日期范围筛选"""
        flts = []
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        flts += [getattr(cls, attr_name) >= start_date] if start_date else []
        flts += [getattr(cls, attr_name) <= end_date] if end_date else []
        return flts

    @staticmethod
    def all(cls, query, method='to_json'):
        """返回全部记录"""
        items = query.all()
        return [getattr(item, method)() for item in items]

    @staticmethod
    def paginate(query, params, method='to_json'):
        """分页查询"""
        page_num = int(params.get('page_num', '1'))
        page_size = int(params.get('page_size', '10'))
        pagination = query.paginate(page_num, per_page=page_size)
        return {
            'items': [getattr(item, method)() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages
        }


class MapperMixin:
    """ORM映射相关的Mixin类"""
    @staticmethod
    def jsonlize(items):
        return [item.to_json() for item in items]

    @classmethod
    def _validate_data(cls, data):
        """验证数据格式"""
        if hasattr(cls, '__schema__'):
            validate(instance=data, schema=cls.__schema__)

    @classmethod
    def add_(cls, data):
        """添加单条记录(内部方法)"""
        obj = cls.new(data)
        obj.add_one()
        return obj

    @classmethod
    def add(cls, data, sync=True):
        """添加单条记录"""
        cls._validate_data(data)
        obj = cls.add_(data)
        if sync:
            cls.commit()
        return obj
    
    @classmethod
    def add_list(cls, data_list, sync=True):
        """批量添加记录"""
        for item in data_list:
            cls.add(item, sync=False)
        if sync:
            cls.commit()

    @classmethod
    def save(cls, primary_key, data, sync=True):
        """保存记录(新增或更新)"""
        cls._validate_data(data)
        obj = cls.get_one(primary_key)
        if obj:
            obj.update(data)
            if sync:
                cls.commit()
        else:
            cls.add(data, sync=sync)

    @classmethod
    def get_one(cls, primary_key):
        """获取单条记录"""
        return cls.query.get(primary_key)

    @classmethod
    def delete_list(cls, sync=True, **kwargs):
        """删除记录"""
        cls.make_query(**kwargs).delete(synchronize_session=False)
        if sync:
            cls.commit()

    @classmethod
    def make_flts(cls, **kwargs):
        """构建过滤条件"""
        flts = []
        keys = cls.keys()
        for k, v in kwargs.items():
            print(k)
            if k in cls.__fuzzy__:
                print('fuzzy~')
                flts += [getattr(cls, k).like(f'%{v}%')] if v not in [None, ''] else []
            elif k in keys and v is not None:
                flts += [getattr(cls, k) == v]
        return flts

    @classmethod
    def make_query(cls, **kwargs):
        """构建查询"""
        flts = cls.make_flts(**kwargs)
        return cls.filter(*flts)

    @classmethod
    def _apply_order_by(cls, query, order_by):
        """应用排序"""
        if order_by:
            for order_key, order_way in order_by.items():
                order_attr = getattr(cls, order_key)
                query = query.order_by(order_attr.desc() if order_way == 'desc' else order_attr.asc())
        return query

    @classmethod
    def get_list(cls, order_by=None, **kwargs):
        """获取记录列表"""
        query = cls.make_query(**kwargs)
        query = cls._apply_order_by(query, order_by)
        return query.all()

    @classmethod
    def get_json(cls, primary_key):
        """获取单条记录的JSON表示"""
        obj = cls.get_one(primary_key)
        return obj.to_json() if obj else {}

    @classmethod
    def get_jsons(cls, page_num=None, page_size=None, order_by=None, **kwargs):
        """获取记录列表的JSON表示"""
        query = cls.make_query(**kwargs)
        query = cls._apply_order_by(query, order_by)
        
        if page_num or page_size:
            pagination = {
                'page_num': page_num or 1,
                'page_size': page_size or 20
            }
            return cls.paginate(query, pagination)
        
        items = query.all()
        return cls.jsonlize(items)

    @classmethod
    def get_attrs(cls, attr_names, **kwargs):
        """获取指定属性"""
        flts = cls.make_flts(**kwargs)
        attrs = [getattr(cls, attr_name) for attr_name in attr_names]
        return cls.query_(*attrs).filter(*flts).all()

    @classmethod
    def get_map(cls, attr_names):
        """获取属性映射"""
        rst_map = {}
        for item in cls.get_attrs(attr_names):
            a, b = item
            rst_map[a] = b
        return rst_map
