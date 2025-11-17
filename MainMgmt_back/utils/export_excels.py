import pandas as pd
from django.http import HttpResponse
from openpyxl.utils import get_column_letter
from io import BytesIO
from openpyxl.styles import Font, Color, Alignment, Border, Side, PatternFill
# from openpyxl.styles import Border, Side, PatternFill

class ExcelExporter:
    def __init__(self, queryset, filename, table_name, headers):
        self.queryset = queryset
        self.filename = filename
        self.table_name = table_name
        self.headers = headers

    def export(self):
        # 使用字典映射字段名到 titlename
        field_to_title = {field.name: header['titlename'] for field, header in zip(self.queryset.model._meta.get_fields(include_parents=False), self.headers)}
        df_data = list(self.queryset.values_list(*field_to_title.keys()))
        df = pd.DataFrame(df_data, columns=field_to_title.values())

        # 设置字体和颜色
        font_color = Color(rgb='000000')  # Color对象rgb值方式，af94ff
        yichang_font_color = Color(rgb='FF0000')  # 红色
        font_style1 = Font(name='微软雅黑', sz=16, b=False, color=font_color)
        font_style2 = Font(name='微软雅黑', sz=12, b=False, color=font_color)
        font_style3 = Font(name='h1', sz=11, b=False, color=yichang_font_color)  # 异常字体


        # 创建HTTP响应
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f"attachment; filename={self.filename}"


        # 使用Pandas将DataFrame写入Excel（通过BytesIO）
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=self.table_name, index=False, startrow=1)
            workbook = writer.book
            worksheet = writer.sheets[self.table_name]

            # 设置纸张大小和方向（在 openpyxl 中，这些设置不会直接保存在文件中，但会在 Excel 中生效）
            # 纸张大小：例如 A4（9 表示 A4 纸）
            # 方向：'portrait' 表示纵向，'landscape' 表示横向
            worksheet.page_setup.paper_size = 8  # 8=A3纸,9=A4
            worksheet.page_setup.orientation = 'landscape'  # 横向

            # 设置列宽
            for col_idx, record in enumerate(self.headers, start=1):
                column_letter = get_column_letter(col_idx)
                worksheet.column_dimensions[column_letter].width = record['col_width']


            # 设置外边框为细实线
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            merge_range = f'A1:{get_column_letter(len(self.headers)) + "1"}'
            worksheet.merge_cells(merge_range)
            worksheet['A1'].font = Font(name='微软雅黑', sz=16, b=True, color=Color(rgb='000000'))
            worksheet.cell(1, 1).value = self.table_name
            worksheet.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center')

            # 冻结首行
            worksheet.freeze_panes = 'A2'
            align = Alignment(horizontal='center', vertical='center', wrapText=True)  # 自动换行
            # 两层循环遍历所有有数据的单元格,对每次单元格进行样式设置
            for i in range(1, worksheet.max_row + 1):
                for j in range(1, worksheet.max_column + 1):
                    worksheet.cell(i, j).border = thin_border  # 应用框样式到所有单元格
                    # worksheet.fill = gray_fill  # 应用灰色填充（模拟内部边框的效果，但不准确）
                    worksheet.cell(i, j).alignment = align
                    # 定义"异常"的字体颜色
                    if (str(worksheet.cell(i, j).value).strip() == '坏卡'):
                        worksheet.cell(i, j).font = font_style3
                    if (i == 2):
                        worksheet.cell(2, j).font = font_style2  # 定义表格标题字体和颜色

        # 保存Excel到response
        output.seek(0)
        response.write(output.getvalue())

        return response