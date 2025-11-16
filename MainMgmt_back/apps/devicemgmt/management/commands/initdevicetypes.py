from django.core.management.base import BaseCommand
from apps.devicemgmt.models import DeviceType


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化部门数据
        devicetype_names = ['服务器', 'PC工作站', '工控机', '网络设备', '安全设备', '北斗授时',
                            '通讯设备', '广场/路面球机', '车道枪', '亭内半球', '存储设备', '门架摄像枪',
                            '门架atlas', '门架天线/控制器', '门架防雷', '门架雷达', '门架SMU', '手持机',
                            '一体机', '卡机', '其他设备'
                            ]

        for name in devicetype_names:
            # 检查是否已存在具有相同名称的设备类型
            if not DeviceType.objects.filter(devicetypename=name).exists():
                # 如果不存在，则创建新记录
                DeviceType.objects.create(devicetypename=name)
                self.stdout.write(f'设备类型:{name}-->已成功添加到数据库。')
            else:
                # 如果已存在，则输出消息（可选）
                self.stdout.write(f'设备类型:{name}-->已存在于数据库中，不会重复添加。')

        self.stdout.write('设备类型信息数据初始化完成！')