from datetime import datetime
from django.utils import timezone
import pytz


def parse_datetime_with_timezone(date_str, default_time="08:00:00"):
    """
    解析日期字符串，并返回带时区的 datetime 对象。
    支持两种格式：
    - 带有时间部分的日期字符串（如 '2024-08-20 12:30:00'）
    - 不带时间部分的日期字符串（如 '2024-08-20'），将自动补充时间部分为 "00:00:00"。

    :param date_str: 字符串格式的日期（可能包含时间部分）
    :param default_time: 如果日期没有时间部分，使用此默认时间补充
    :return: 带时区的 datetime 对象
    """
    # 先判断日期字符串是否包含时间部分
    if ' ' in date_str:
        # 如果有时间部分，直接解析
        naive_datetime = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    else:
        # 如果没有时间部分，补充默认时间
        date_str_with_time = date_str + ' ' + default_time
        naive_datetime = datetime.strptime(date_str_with_time, '%Y-%m-%d %H:%M:%S')

    # 转换为带时区的 datetime
    aware_datetime = timezone.make_aware(naive_datetime)

    return aware_datetime

from dateutil import parser


def parse_iso8601_with_timezone(iso8601_str):
    """
    解析 ISO 8601 格式的日期字符串，并返回带时区的 datetime 对象。
    支持带有时区（例如 '2025-02-21T03:13:57.058Z'）的时间字符串。

    :param iso8601_str: ISO 8601 格式的日期字符串（如 '2025-02-21T03:13:57.058Z'）
    :return: 带时区的 datetime 对象
    """
    try:
        # 使用 dateutil.parser.isoparse() 解析 ISO 8601 格式的日期字符串
        naive_datetime = parser.isoparse(iso8601_str)

        # 如果 datetime 对象已经包含时区信息，则不需要转换
        if naive_datetime.tzinfo is None:
            # 如果没有时区信息，我们假设它是 UTC 时间
            utc_datetime = naive_datetime.replace(tzinfo=pytz.utc)
        else:
            # 如果已经有时区信息，那么直接使用该时区
            utc_datetime = naive_datetime

        # 将 UTC 时间转换为北京时间（CST: UTC +8）
        cst_timezone = pytz.timezone('Asia/Shanghai')
        aware_datetime = utc_datetime.astimezone(cst_timezone)

    except ValueError as e:
        raise ValueError(f"无法解析 ISO 8601 时间格式: {iso8601_str}. 错误: {e}")

    return aware_datetime

def to_cst_str(iso_str: str) -> str:
    """
    把 ISO8601/Z 时间串转成上海时间格式化字符串
    不依赖 Django 配置环境
    """
    if not iso_str:
        return ''
    return parse_iso8601_with_timezone(iso_str).strftime('%Y-%m-%d %H:%M:%S')

def format_cst_time(time_str):
    """
    格式化时间为CST时间显示
    依赖 Django 配置环境
    """
    try:
        if isinstance(time_str, str):
            # 尝试解析ISO格式时间
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            # 转换为本地时间
            local_dt = timezone.localtime(dt)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return time_str
    except Exception:
        return time_str