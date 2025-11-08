class SplitStateError(Exception):
    pass


class SplitFormatError(Exception):
    pass


class SplitComplex:
    OUT = "out"
    IN_QUOTED = "in_quoted"
    OUT_QUOTED = "out_quoted"
    IN_NORMAL = "in_normal"
    ESC = "escape"

    def __init__(self, text: str):
        self.text = text

    def split(self):
        state = self.OUT
        result = []
        current = []
        exit = ""
        for c in self.text:
            # print(f"STATE: s: {state}, c: {c}")
            if state == self.OUT:
                current = []
                if c == ",":
                    result.append("")
                elif c in ['"', "'"]:
                    state = self.IN_QUOTED
                    exit = c
                elif c.isspace():
                    pass
                else:
                    state = self.IN_NORMAL
                    current.append(c)
            elif state == self.IN_QUOTED:
                if c == "\\":
                    state = self.ESC
                elif c == exit:
                    result.append("".join(current).strip())
                    state = self.OUT_QUOTED
                else:
                    current.append(c)
            elif state == self.OUT_QUOTED:
                if c == ",":
                    state = self.OUT
                else:
                    pass
            elif state == self.IN_NORMAL:
                if c == ",":
                    result.append("".join(current).strip())
                    state = self.OUT
                else:
                    current.append(c)
            elif state == self.ESC:
                if c == exit:
                    current.append(c)
                    state = self.IN_QUOTED
                else:
                    current.append("\\")
                    current.append(c)
            else:
                raise SplitStateError

        if state == self.OUT or state == self.OUT_QUOTED:
            pass
        elif state == self.IN_NORMAL:
            result.append("".join(current).strip())
        else:
            raise SplitFormatError
        return result
