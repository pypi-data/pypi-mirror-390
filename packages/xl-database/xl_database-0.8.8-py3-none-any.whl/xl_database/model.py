from xl_database import db
from xl_database.mixins import DatabaseMixin, QueryMixin, MapperMixin
from xl_database.utils import time
from sqlalchemy import String, Text, Date, DateTime


class Model(DatabaseMixin, QueryMixin, MapperMixin, db.Model):
    __abstract__ = True
    __schema__ = {}
    __date__ = []
    __datetime__ = []
    __fuzzy__ = []
    __key_map__ = {}
    __key_derive_map__ = {}
    
    def __init_subclass__(cls, **kwargs):
        """在子类创建时自动检测字段并填充到对应的辅助列表"""
        super().__init_subclass__(**kwargs)
        cls._init_fuzzy_fields()
        cls._init_date_fields()
        cls._init_datetime_fields()
    
    @classmethod
    def _init_fuzzy_fields(cls):
        """初始化模糊查询字段列表"""
        try:
            if hasattr(cls, '__table__') and cls.__table__ is not None:
                auto_fuzzy = []
                for column_name, column in cls.__table__.columns.items():
                    if isinstance(column.type, (String, Text)):
                        auto_fuzzy.append(column_name)
                
                existing_fuzzy = getattr(cls, '__fuzzy__', [])
                if auto_fuzzy:  
                    cls.__fuzzy__ = list(set(existing_fuzzy + auto_fuzzy))
        except (AttributeError, TypeError):
            pass

    @classmethod
    def _init_date_fields(cls):
        """初始化日期字段列表"""
        try:
            if hasattr(cls, '__table__') and cls.__table__ is not None:
                auto_dates = []
                for column_name, column in cls.__table__.columns.items():
                    if isinstance(column.type, Date):
                        auto_dates.append(column_name)

                existing_dates = getattr(cls, '__date__', [])
                if auto_dates:
                    cls.__date__ = list(set(existing_dates + auto_dates))
        except (AttributeError, TypeError):
            pass

    @classmethod
    def _init_datetime_fields(cls):
        """初始化日期时间字段列表"""
        try:
            if hasattr(cls, '__table__') and cls.__table__ is not None:
                auto_datetimes = []
                for column_name, column in cls.__table__.columns.items():
                    if isinstance(column.type, DateTime):
                        auto_datetimes.append(column_name)

                existing_datetimes = getattr(cls, '__datetime__', [])
                if auto_datetimes:
                    cls.__datetime__ = list(set(existing_datetimes + auto_datetimes))
        except (AttributeError, TypeError):
            pass
    
    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.query.filter(*args, **kwargs)

    @classmethod
    def clean_params(cls, dict_):
        dict_ = dict_.copy()
        keys = list(dict_.keys())
        for key in keys:
            if key not in cls.keys():  # 无关字段过滤
                dict_.pop(key)
        return dict_

    @classmethod
    def keys(cls):
        return cls.__table__.columns.keys()

    def raw_json(self):
        return {key: self.__getattribute__(key) for key in self.keys()}

    def to_json(self):
        return self.to_json_()

    def to_json_(self):  # 新方法，待替换
        tmp = {}
        for k in self.keys():
            v = self.__getattribute__(k)
            tmp[k] = v
            if k in self.__date__:
                tmp[k] = self.format_date(v)
            elif k in self.__datetime__:
                tmp[k] = self.format_datetime(v)
            for key, func in self.__key_map__.items():
                if k == key:
                    tmp[k] = func(v)
            for key, map in self.__key_derive_map__.items():
                if k == key:
                    if isinstance(map, list):
                        for map_ in map:
                            name = map_['name']
                            func = map_['func']
                            tmp[name] = func(v)
                    else:
                        name = map['name']
                        func = map['func']
                        tmp[name] = func(v)
        return tmp

    @staticmethod
    def format_date(value):
        return time.format(value, 'YYYY-MM-DD') if value is not None else ''

    @staticmethod
    def format_datetime(value):
        return time.format(value, 'YYYY-MM-DD HH:mm:ss') if value is not None else None

    @classmethod
    def new(cls, dict_):
        return cls(**cls.clean_params(dict_))

    def add_one(self):
        """添加到数据库缓存"""
        db.session.add(self)
        db.session.flush()
        return self

    def update(self, dict_):
        """修改信息"""
        dict_ = self.clean_params(dict_)
        for k, v in dict_.items():
            setattr(self, k, v)
        return self

    def merge(self):
        """合并"""
        db.session.merge(self)
        return self
