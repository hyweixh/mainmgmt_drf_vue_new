from django.core.management.base import BaseCommand
from apps.devicemgmt.models import SubnetType


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化子网数据
        subnet_names = ['收费网', '监控网', '门架', '省部平台', '绿通网']

        for name in subnet_names:
            # 检查是否已存在具有相同名称的子网
            if not SubnetType.objects.filter(subnettypename=name).exists():
                # 如果不存在，则创建新记录
                SubnetType.objects.create(subnettypename=name)
                self.stdout.write(f'子网:{name}-->已成功添加到数据库。')
            else:
                # 如果已存在，则输出消息（可选）
                self.stdout.write(f'子网:{name}-->已存在于数据库中，不会重复添加。')

        self.stdout.write('子网信息数据初始化完成！')