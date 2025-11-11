import json
import decimal
import datetime
import base64


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            # # 将datetime对象转换为ISO格式字符串
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            # 将bytes转换为base64编码的字符串
            try:
                # 尝试将bytes解码为UTF-8字符串
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，回退到Base64编码
                return base64.b64encode(obj).decode('utf-8')
        # elif isinstance(obj, bson.timestamp.Timestamp):
        #     # # 将BSON时间戳转换为其时间表示的ISO格式字符串
        #     return obj.as_datetime().isoformat()
        # elif isinstance(obj, bson.objectid.ObjectId):
        #     # # 将ObjectId转换为字符串
        #     return str(obj)
        return super(LazyEncoder, self).default(obj)


def json2str(
        data: json,
        ensure_ascii: bool = False
):
    """
    在将json数据反序列化为str时，会遇到一些格式无法转换
    这里使用识别类型转换转为str
    目前支持类型：

    对于mongodb返回数据的处理：
        from bson import json_util
        default=json_util.default

    decimal --> str
    datetime.datetime --> str(%Y-%m-%d %H:%M:%S)
    datetime.date --> str(%Y-%m-%d)
    """
    return json.dumps(
        data,
        cls=LazyEncoder,
        ensure_ascii=ensure_ascii
    )
