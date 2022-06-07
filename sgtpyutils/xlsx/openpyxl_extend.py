import openpyxl


def exist(wb: openpyxl.Workbook, sheet_name: str) -> bool:
    return sheet_name in _sheets_dict(wb)


def _sheets_dict(wb: openpyxl.Workbook) -> dict:
    wb._sheets_dict = {}
    for x in wb._sheets:
        wb._sheets_dict[x.title] = x
    return wb._sheets_dict


def get_sheet_with_create(wb: openpyxl.Workbook, title: str = None, index: int = None, put_index: int = None, use_new_sheet: bool = False, prefix_index: int = None):
    """get a worksheet (at an optional index).
    and create one if not exist

    :param title: optional title of the sheet
    :type title: str
    :param index: optional position at which the sheet will be inserted
    :type index: int

    :return sheet,is_new_sheet
    """
    if not title is None:
        current_title = title if not prefix_index else f'{prefix_index}_{title}'
        e = exist(wb, current_title)
        if e:
            if use_new_sheet:
                return get_sheet_with_create(wb, title, index, put_index, use_new_sheet, prefix_index=prefix_index+1 if prefix_index else 1)
            return (wb[title], False)
        return (wb.create_sheet(title, put_index), True)
    if not index is None:
        if index >= 0 and index < len(wb.sheets):
            (wb.sheets[index], False)
    s_name = f'new_sheet_{len(wb.sheets)}'
    return (wb.create_sheet(s_name, put_index), True)
