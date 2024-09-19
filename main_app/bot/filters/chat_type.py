from aiogram.types import Message,ContentType
from aiogram.filters import Filter
from aiogram.filters import BaseFilter

import openpyxl
from openpyxl.styles import Alignment

def align_cells(sheet, columns, alignment_type="left"):
    for col in columns:
        sheet.column_dimensions[col].width = 20
        for cell in sheet[col]:
            cell.alignment = Alignment(horizontal=alignment_type)

# def set_column_widths(sheet):
#     for col in ["A", "B", "C", "D", "E", "F", "G", "H"]:
#         sheet.column_dimensions[col].width = 20

def create_excel_with_data(all_users, true_users, false_users, file_name="output.xlsx"):
    try:
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)

        sheet_1 = workbook.create_sheet("Sheet_1")
        sheet_2 = workbook.create_sheet("Sheet_2")
        sheet_3 = workbook.create_sheet("Sheet_3")

        # set_column_widths(sheet_1)
        # set_column_widths(sheet_2)
        # set_column_widths(sheet_3)

        sheet_1.title = "All users"
        sheet_2.title = "True users"
        sheet_3.title = "False users"

        headers = ["id","Telegram ID", "Name", "School", "City", "Number", "Payment", "Language"]
        sheet_1.append(headers)
        sheet_2.append(headers)
        sheet_3.append(headers)

        for row in all_users:
            sheet_1.append(row)

        for row in true_users:
            sheet_2.append(row)

        for row in false_users:
            sheet_3.append(row)
        
        columns_to_align = ["A", "B", "C", "D", "E", "F", "G", "H"]
        align_cells(sheet_1, columns_to_align, alignment_type="right")
        align_cells(sheet_2, columns_to_align, alignment_type="right")
        align_cells(sheet_3, columns_to_align, alignment_type="right")


        workbook.save(file_name)
        print(f"Файл '{file_name}' успешно создан.")
        return file_name
    except Exception as e:
        print(f"Ошибка при создании Excel файла: {e}")
        return None



# # Пример данных
# user_data = [
#     [123456789, "John Doe", "School 1", "City A", "+1234567890", "Paid", "English"],
#     [987654321, "Jane Smith", "School 2", "City B", "+0987654321", "Unpaid", "Spanish"]
# ]

# create_excel_with_data(user_data, "user_data.xlsx")


class chat_type_filter(Filter):
    def __init__(self,chat_types:list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self,message:Message) -> bool:
        return message.chat.type in self.chat_types


class MediaFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        file = message.content_type in [ContentType.PHOTO, ContentType.DOCUMENT]
        return file if file else 'False'