from django.core.management.base import BaseCommand
from apps.lanepsaminfo.models import PsamStatus

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化部门数据
        psamstatus_names = ['正常', '坏卡']

        for name in psamstatus_names:
            # 检查是否已存在具有相同名称的psam卡状态
            if not PsamStatus.objects.filter(psamstatus=name).exists():
                # 如果不存在，则创建新记录
                PsamStatus.objects.create(psamstatus=name)
                self.stdout.write(f'Psam卡状态:{name}-->已成功添加到数据库。')
            else:
                # 如果已存在，则输出消息（可选）
                self.stdout.write(f'Psam卡状态:{name}-->已存在于数据库中，不会重复添加。')

        self.stdout.write('设备类型信息数据初始化完成！')