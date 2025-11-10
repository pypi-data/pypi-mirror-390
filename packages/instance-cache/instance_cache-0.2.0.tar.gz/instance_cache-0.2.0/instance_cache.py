"""
为类方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器

functools.lru_cache 和 cache 函数会保留对调用参数的强引用, 会影响这些参数正常的垃圾回收,
需要等待缓存超过 max_size 后弹出或手动调用 cache_clear, 比较麻烦
最常见的场景是作用在一般的类方法上, 保留参数 self 的引用后会影响整个类实例的垃圾回收

>>> from functools import cache
>>>
>>> class Test:
...     def method(self):
...         ...
...
...     @cache
...     def method_cache(self):
...         ...
...
...     def __del__(self):
...         print('delete!')
...
>>> Test().method()  # 正常垃圾回收
delete!
>>> Test().method_cache()  # 无法进行垃圾回收
>>> Test().method_cache()
>>> Test().method_cache()
>>> Test.method_cache.cache_clear()  # 手动清理缓存才会回收
delete!
delete!
delete!

此处提供一个一般类方法的结果缓存装饰器, 提供实例级别的缓存 (为每个实例单独创建缓存空间)
通过将缓存内容作为每个类实例的属性进行存储 (类似于 functools.cached_property), 避免影响类实例 self 的正常垃圾回收
其他调用参数在类实例被回收后也会正常回收
"""

import functools
import keyword
from collections import OrderedDict
from threading import Lock
from typing import Callable, NamedTuple, Optional, Sequence, Union
# import inspect  # 延迟导入
# import warnings  # 延迟导入


# python >= 3.7.0
__version__ = '0.2.0'

__all__ = ['CacheInfo', 'instance_cache']


class CacheInfo(NamedTuple):
    """缓存信息"""
    hits: int  # 缓存命中次数
    misses: int  # 缓存未命中次数
    maxsize: int  # 最大缓存数量
    currsize: int  # 打钱缓存大小


class _Cache:
    """内部类, 缓存"""
    __slots__ = ('cache', 'maxsize', 'hits', 'misses', 'lock')

    sentinel = object()

    def __init__(self, maxsize):
        """初始化方法"""
        self.cache = OrderedDict() if maxsize is not None else {}  # 缓存字典
        self.maxsize = maxsize  # 最大缓存数量
        self.hits = 0  # 统计命中缓存次数
        self.misses = 0  # 统计未命中缓存次数
        self.lock = Lock()  # 线程锁对象

    @property
    def currsize(self):
        """当前缓存大小"""
        return len(self.cache)

    def get(self, key):
        """获取缓存内容, 返回 _Cache.sentinel 时表示无缓存"""
        with self.lock:
            if key in self.cache:
                self.hits += 1
                if self.maxsize is not None:
                    self.cache.move_to_end(key, last=True)
                value = self.cache[key]
                return value
            self.misses += 1
            return _Cache.sentinel

    def put(self, key, value):
        """添加一条缓存"""
        with self.lock:
            if key in self.cache:
                return
            self.cache[key] = value
            if self.maxsize is not None:
                if self.currsize > self.maxsize:
                    self.cache.popitem(last=False)

    def clear(self):
        """清空缓存并重置缓存信息"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def get_info(self):
        """获取缓存信息"""
        with self.lock:
            return CacheInfo(self.hits, self.misses, self.maxsize, self.currsize)


class _KeyMake:
    """内部类, 缓存键"""
    __slots__ = ('precise_key', 'sig', 'cache_properties')

    kwargs_mark = object()
    properties_mark = object()

    def __init__(self, precise_key, method, cache_properties):
        """初始化方法"""
        self.precise_key = precise_key  # 是否精确缓存
        if self.precise_key:
            import inspect
            try:
                self.sig = inspect.signature(method)  # 类方法签名
            except ValueError:
                self.precise_key = False
                import warnings
                warnings.warn('failed to get function signature, downgraded to non-precise caching',
                              UserWarning, stacklevel=2)
        self.cache_properties = cache_properties  # 额外缓存的类属性名称

    def make(self, instance, args, kwargs):
        """创建缓存键"""
        key = []
        if self.precise_key:
            bound = self.sig.bind(instance, *args, **kwargs)
            bound.apply_defaults()
            args, kwargs = bound.args[1:], bound.kwargs
            if args:
                key.extend(args)
            if kwargs:
                key.append(_KeyMake.kwargs_mark)
                for k in sorted(kwargs):
                    key.append(k)
                    key.append(kwargs[k])
        else:
            if args:
                key.extend(args)
            if kwargs:
                key.append(_KeyMake.kwargs_mark)
                for item in kwargs.items():
                    key.extend(item)
        if self.cache_properties:
            key.append(_KeyMake.properties_mark)
            for item in self.cache_properties:
                key.append(getattr(instance, item, None))
        key = tuple(key)
        return key


def instance_cache(
        maxsize: Optional[int] = 128,
        cache_properties: Union[str, Sequence[str]] = (),
        precise_key: bool = False,
        _cache_name: str = None
) -> Callable[[Callable], Callable]:
    """
    为类方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器工厂

    该装饰器会在每个类实例首次运行时, 为其添加一个内部缓存属性, 默认的属性名称为:
        '_cached_' + method.__name__ + id(wrapper)
    用户不应当直接操作这个属性

    该装饰器同时会为类方法添加三个函数:
        cache_info(instance)    查看某一实例的缓存统计信息
        cache_clear(instance)   清空某一实例的缓存结果
        cache_parameters()      查看缓存参数信息

    由于使用字典来缓存结果, 因此传给该函数的位置和关键字参数必须为 hashable

    该缓存方法线程安全, 但如果另一个线程在初始调用完成并被缓存之前执行了额外的调用则被包装的函数可能会被多次调用

    参数:
    :param maxsize: 单个实例的缓存数量限制 (非所有实例共享), 为 None 时表示无限制, 默认为 128
    :param cache_properties: 额外缓存一些类属性在调用时的值, 类属性不存在时值视为 None
    :param precise_key: 是否以牺牲一些性能为代价, 使用更精确的参数缓存策略 (默认为 False)
        若 precise_key 为 True, 则以下调用方式的参数均视为相同 (method 方法按示例中定义), 会命中同一缓存:
            foo.method()
            foo.method(1)
            foo.method(y=2)
            foo.method(1, 2)
            foo.method(x=1, y=2)
            foo.method(y=2, x=1)
            foo.method(1, y=2)
        反之只有完全相同的调用才会被视为相同参数, 但此时性能会显著提高
        建议内部接口使用 precise_key = False, 对外接口使用 precise_key = True
    :param _cache_name: 当默认的内部缓存属性名会发生冲突时, 可以手动指定其他名称

    示例:
    >>> from instance_cache import instance_cache
    >>>
    >>> class Test:
    ...     @instance_cache()
    ...     def method(self, x=1, y=2):
    ...         print('run')
    ...         ...  # 耗时操作
    ...         return 1
    ...
    ...     def __del__(self):
    ...         print('delete!')
    ...
    >>> foo = Test()
    >>> foo.method(1, 2)
    run
    1
    >>> foo.method(1, 2)  # 命中缓存, 不运行方法直接返回结果
    1
    >>> Test.method.cache_info(foo)  # 查看实例的缓存信息
    CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
    >>> # Test.method.cache_clear(foo)  # 清空实例的缓存并重置缓存信息
    >>> del foo  # 立刻进行垃圾回收
    delete!

    一个绝妙的配方: @property + @instance_cache(cache_properties=(...))
    可以实现带缓存的类方法转类属性功能, 与 @functools.cached_property 不同的是,
    该类属性可以绑定一些计算时用到的其他类属性, 当其他类属性发生变化时, 可以自动更新该类属性的结果
    """
    # 参数验证
    if maxsize is not None:
        if not isinstance(maxsize, int):
            raise TypeError(f'maxsize must be an integer or None, not {type(maxsize)!r}')
        if maxsize < 0:
            maxsize = 0

    if isinstance(cache_properties, str):
        cache_properties = cache_properties.replace(',', ' ').split()
    cache_properties = tuple(set(cache_properties))
    for item in cache_properties:
        if not isinstance(item, str):
            raise TypeError(f'cache_properties must be strings, not {type(item)!r}')
        if not item.isidentifier():
            raise ValueError(f'cache_properties must be valid identifiers: {item!r}')
        if keyword.iskeyword(item):
            raise ValueError(f'cache_properties can not be keywords: {item!r}')

    precise_key = bool(precise_key)

    if _cache_name is not None:
        if not isinstance(_cache_name, str):
            raise TypeError(f'_cache_name must be a string, not {type(_cache_name)!r}')
        if not _cache_name.isidentifier():
            raise ValueError(f'_cache_name must be a valid identifier: {_cache_name!r}')
        if keyword.iskeyword(_cache_name):
            raise ValueError(f'_cache_name can not be a keyword: {_cache_name!r}')

    def decorating_function(method: Callable) -> Callable:
        """类方法缓存装饰器"""

        if maxsize is None or maxsize > 0:
            make_key = _KeyMake(precise_key, method, cache_properties)

            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                key = make_key.make(self, args, kwargs)
                cache = _get_cache(self)
                value = cache.get(key)
                if value is _Cache.sentinel:  # 未命中缓存
                    value = method(self, *args, **kwargs)
                    cache.put(key, value)
                return value

            def cache_clear(instance) -> None:
                """清空某一实例的缓存并重置缓存信息"""
                cache = _get_cache(instance)
                cache.clear()

            def cache_parameters() -> dict:
                """查看缓存参数信息"""
                return {
                    'maxsize': maxsize,
                    'cache_properties': cache_properties,
                    'precise_key': make_key.precise_key  # 防止因获取函数签名失败而降级为非精确缓存
                }

        else:  # 无缓存
            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                cache = _get_cache(self)
                with cache.lock:
                    cache.misses += 1
                value = method(self, *args, **kwargs)
                return value

            def cache_clear(instance) -> None:
                """清空某一实例的缓存并重置缓存信息"""
                cache = _get_cache(instance)
                with cache.lock:
                    cache.misses = 0

            def cache_parameters() -> dict:
                """查看缓存参数信息"""
                return {
                    'maxsize': maxsize,
                    'cache_properties': cache_properties,
                    'precise_key': precise_key
                }

        def cache_info(instance) -> CacheInfo:
            """查看某一实例的缓存信息"""
            cache = _get_cache(instance)
            return cache.get_info()

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.cache_parameters = cache_parameters

        # 缓存属性的添加和获取
        cache_name = _cache_name if _cache_name is not None else \
            f'_cache_{method.__name__}_{id(wrapper)}'  # 加一个 id 后缀是因为方法名可能重复 (比如类方法的重载), 并且降低和其他属性名冲突的概率
        method_lock = Lock()

        def _get_cache(instance):
            # 为类实例添加缓存属性并获取
            if not hasattr(instance, cache_name):  # 减少持有锁
                with method_lock:
                    if not hasattr(instance, cache_name):
                        setattr(instance, cache_name, _Cache(maxsize))
            return getattr(instance, cache_name)

        return wrapper

    return decorating_function
