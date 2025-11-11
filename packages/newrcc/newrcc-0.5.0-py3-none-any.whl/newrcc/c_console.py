import contextlib
from typing import Union, Tuple, List, Iterable, Any, Optional

from build.lib.newrcc.c_color import TextColor
from newrcc import c_color as cc
from newrcc import c_error as ce

__all__ = [
    'ctext',
    'cprint',
    'ProcessBar',
    'TBlock',
    'TRow',
    'Table',
    'process'
]


def ctext(text: str,
          color: Union[None, str, cc.Color, Tuple[
              Union[cc.TextColor, Tuple[int, int, int]],
              Union[cc.BackgroundColor, Tuple[int, int, int]]
          ]],
          decorations: List[Union[cc.Decoration, str]] = None,
          reset: bool = True) -> str:
    if decorations is not None:
        for decoration in decorations:
            if isinstance(decoration, str):
                text = decoration + text
            else:
                text = str(decoration) + text
    if isinstance(color, cc.Color):
        text = str(color) + text
    elif isinstance(color, tuple):
        if isinstance(color[0], tuple):
            text = str(cc.TextColor(color[0])) + text
        else:
            text = str(color[0]) + text
        if isinstance(color[1], tuple):
            text = str(cc.BackgroundColor(color[1])) + text
        else:
            text = str(color[1]) + text
    elif isinstance(color, str):
        text = color + (cc.RESET + color).join(text.split(cc.RESET))
    elif color is not None:
        raise cc.CDError.CDUnexpectedColorInputError(color, 'colorfulText')
    if reset and color is not None:
        text += cc.RESET
    return text


def cprint(
        text: str,
        color: Union[str, cc.Color, Tuple[
            Union[cc.TextColor, str, Tuple[int, int, int]],
            Union[cc.BackgroundColor, str, Tuple[int, int, int]]
        ]],
        decorations: List[Union[cc.Decoration, str]] = None,
        reset: bool = True,
        end: str = '\n'
) -> None:
    print(ctext(text, color, decorations, reset), end=end)


class ProcessBar:
    def __init__(self,
                 prefix: str,
                 suffix: str,
                 total: int,
                 length: int = 20,
                 title_color: Union[str, cc.Color] = None,
                 frame_color: Union[str, cc.Color] = None,
                 show_frame_border: bool = True,
                 process_color: Union[str, cc.Color] = None,
                 value_color: Union[str, cc.Color] = None,
                 style: int = 1):
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.total = total
        self.process_color = process_color
        self.frame_color = frame_color
        self.show_frame_border = show_frame_border
        self.title_color = title_color
        self.value_color = value_color
        self.extra_length = (8 * (process_color is not None) + 8 * (frame_color is not None) +
                             8 * (title_color is not None) + 12 * (value_color is not None))
        self.process_length = self.extra_length
        self.style = style

    def draw(self, current: int) -> None:
        real_length = int(self.length * current // self.total)
        fix_length = max(len(self.prefix), len(self.suffix))

        def getProcess():
            _process = ''
            if self.style == 1:
                _process = (ctext('│' * self.show_frame_border, self.frame_color, reset=False) +
                            ctext('█' * real_length + ' ' * (self.length - real_length), self.process_color) +
                            ctext('│' * self.show_frame_border, self.frame_color))
            elif self.style == 2:
                _process = (ctext('│' * self.show_frame_border, self.frame_color, reset=False) +
                            ctext('█' * real_length, self.process_color) +
                            ctext('█' * (self.length - real_length), self.frame_color) +
                            ctext('│' * self.show_frame_border, self.frame_color))
            elif self.style == 3:
                _process = (ctext('│' * self.show_frame_border, self.frame_color, reset=False) +
                            ctext('━' * (real_length - 1), self.process_color, reset=False) +
                            '╸' * (self.length - real_length > 0) +
                            '━' * (self.length - real_length == 0) + cc.RESET +
                            ctext('━' * (self.length - real_length), self.frame_color, reset=False) +
                            ctext('│' * self.show_frame_border, self.frame_color))
            return _process

        if real_length < self.length:
            process = (ctext(self.prefix + ' ' * (fix_length - len(self.prefix)), self.title_color) +
                       ': ' +
                       getProcess() +
                       ' ' +
                       ctext(str(round(current / self.total * 100, 3)) + '% ', self.value_color))
            print(process, end='')
            self.process_length = len(process)
        else:
            process = (ctext(self.suffix + ' ' * (fix_length - len(self.suffix)), self.title_color) +
                       ': ' +
                       getProcess() +
                       ' ' +
                       ctext(str(round(current / self.total * 100, 3)) + '% ', self.value_color))
            print(process)

    def erase(self) -> None:
        print('\b' * (self.process_length + self.extra_length), end='', flush=True)

    def progress(self, iterator: Optional[Iterable[Any]] = None):
        self.total = self.total if iterator is None else len(iterator)
        for i in range(0, self.total):
            self.draw(i + 1)
            yield iterator[i] if iterator else i
            self.erase()


class TBlock:
    def __init__(self,
                 item,
                 across_rows: int = 1,
                 across_columns: int = 1,
                 isnone: bool = False):
        self.item = str(item)
        self.across_rows = across_rows
        self.across_columns = across_columns
        self.row_across = (across_rows != 1)
        self.column_across = (across_columns != 1)
        self.isnone = isnone

    def __str__(self):
        if self.isnone:
            return "<none>"
        else:
            return self.item


class TRow:
    def __init__(self, blocks: List[TBlock]):
        self.blocks = []
        for block in blocks:
            if block.column_across:
                self.blocks.append(block)
                i = 1
                for _ in range(0, block.across_columns - 1):
                    self.blocks.append(TBlock('', across_columns=block.across_columns - i, isnone=True))
                    i += 1
            else:
                self.blocks.append(block)
        length = 0
        across_rows = 0
        for block in blocks:
            length += block.across_columns
            across_rows = max(across_rows, block.across_rows)
        block_length = []
        for block in blocks:
            block_length.append(len(str(block)))
            if block.across_columns > 1:
                for i in range(0, block.across_columns - 1):
                    block_length.append(0)
        self.columns = length
        self.across_rows = across_rows
        self.block_length = block_length

    def __blocks_str__(self):
        string = '[ '
        for block in self.blocks:
            string += str(block) + ' '
        string += ']'
        return string

    def __str__(self):
        return f'row{"{"}across rows: {self.across_rows}, columns: {self.columns}, block length: {self.block_length}, blocks: {self.__blocks_str__()}{"}"}'


class Table:
    def getBlockMaxLength(self) -> List[int]:
        block_max_length = [0 for _ in self.rows[0].block_length]
        for _row in self.rows:
            if len(block_max_length) != len(_row.block_length):
                raise ce.CDTableBlockCountMismatchedError(_row, block_max_length)
            i = 0
            for length in _row.block_length:
                block_max_length[i] = max(length, block_max_length[i])
                i += 1
        return block_max_length

    def __init__(self, rows: List[TRow] = None):
        self.rows = rows
        row_length = 0
        column_length = 0
        for row in rows:
            row_length += row.across_rows
            column_length = max(column_length, row.columns)
        self.row_length = row_length
        self.column_length = column_length
        self.block_max_length = self.getBlockMaxLength()

    def append(self, row: TRow) -> None:
        self.rows.append(row)

    def getTableInfo(self) -> str:
        return (f'table{"{"}row_length: {self.row_length}, column_length: {self.column_length},'
                f' block max length: {self.block_max_length}{"}"}')

    def __str__(self) -> str:
        r_index = 0
        while r_index < self.row_length:
            if r_index == 0:
                print(end='┌')
                length_index = 0
                while length_index < len(self.block_max_length):
                    print(end='─' * self.block_max_length[length_index])
                    if length_index == len(self.block_max_length) - 1:
                        print(end='┐\n')
                    else:
                        if self.rows[r_index].blocks[length_index].column_across:
                            print(end='─')
                        else:
                            print(end='┬')
                    length_index += 1
                block_index = 0
                for block in self.rows[r_index].blocks:
                    if not block.isnone:
                        print(end='│' + str(block) + ' ' * (self.block_max_length[block_index] - len(str(block))))
                    else:
                        print(end=' ' * (self.block_max_length[block_index] + 1))
                    block_index += 1
                print(end='│\n')
            else:
                print(end='├')
                length_index = 0
                while length_index < len(self.block_max_length):
                    print(end='─' * self.block_max_length[length_index])
                    if length_index == len(self.block_max_length) - 1:
                        print(end='┤\n')
                    else:
                        if not self.rows[r_index].blocks[length_index].column_across and not \
                                self.rows[r_index - 1].blocks[length_index].column_across:
                            print(end='┼')
                        elif not self.rows[r_index].blocks[length_index].column_across and \
                                self.rows[r_index - 1].blocks[length_index].column_across:
                            print(end='┬')
                        elif self.rows[r_index].blocks[length_index].column_across and self.rows[r_index - 1].blocks[
                            length_index].column_across:
                            print(end='─')
                        elif self.rows[r_index].blocks[length_index].column_across and not \
                                self.rows[r_index - 1].blocks[length_index].column_across:
                            print(end='┴')
                    length_index += 1
                block_index = 0
                for block in self.rows[r_index].blocks:
                    if not block.isnone:
                        print(end='│' + str(block) + ' ' * (self.block_max_length[block_index] - len(str(block))))
                    else:
                        print(end=' ' * (self.block_max_length[block_index] + 1))
                    block_index += 1
                print(end='│\n')
            r_index += 1
        length_index = 0
        print(end='└')
        while length_index < len(self.block_max_length):
            print(end='─' * self.block_max_length[length_index])
            if length_index == len(self.block_max_length) - 1:
                print(end='┘\n')
            else:
                if self.rows[r_index - 1].blocks[length_index].column_across:
                    print(end='─')
                else:
                    print(end='┴')
            length_index += 1
        return ''


"""
─ │ ┌ ┐ └ ┘ ┼ ├ ┤ ┬ ┴ █ ▓ ▒ ░ ↑ ↓ ← → ● ◦ ․·‥°º▫◌◯◻⁺ⁱ⁼∙⋱﹒·−-⁎‣−■■■■■■■■■■■■■ ━ ━ ╺ ╸
"""


@contextlib.contextmanager
def process(
        prefix: str,
        suffix: str,
        total: int = 100,
        length: int = 20,
        title_color: Union[str, cc.Color] = cc.TextColor.BLUE,
        frame_color: Union[str, cc.Color] = cc.TextColor.WHITE,
        show_frame_border: bool = True,
        process_color: Union[str, cc.Color] = cc.TextColor.GREEN,
        value_color: Union[str, cc.Color] = cc.TextColor.WHITE,
        style: int = 1):
    bar = ProcessBar(
        prefix=prefix,
        suffix=suffix,
        total=total,
        length=length,
        title_color=title_color,
        frame_color=frame_color,
        show_frame_border=show_frame_border,
        process_color=process_color,
        value_color=value_color,
        style=style
    )
    try:
        yield bar.progress
    finally:
        bar.erase()


def demo_colorful_text():
    print("===== 彩色文本示例 =====")
    # 基础颜色输出
    cprint("普通红色文本", cc.TextColor.RED)
    cprint("绿色背景文本", (None, cc.BackgroundColor.GREEN))
    cprint("蓝底黄字", (cc.TextColor.YELLOW, cc.BackgroundColor.BLUE))

    # 自定义RGB颜色
    cprint("自定义粉色文本", cc.TextColor((255, 192, 203)))
    cprint("青蓝色背景", (None, cc.BackgroundColor((0, 255, 255))))

    # 带装饰的文本
    cprint("加粗+下划线文本", cc.TextColor.CYAN,
           decorations=[cc.Decoration.BOLD, cc.Decoration.L_UNDERLINE])
    print(ctext(f"Hello {ctext('inner text', TextColor.LIGHT_RED)} world!", TextColor.LIGHT_BLUE))


def demo_progress_bar():
    from time import sleep
    print("===== 进度条示例 =====")
    with process("下载 'newrcc' 中", "'newrcc' 下载完成", show_frame_border=False, style=3) as bar:
        for i in bar.progress():
            sleep(0.01)


if __name__ == "__main__":
    demo_colorful_text()
