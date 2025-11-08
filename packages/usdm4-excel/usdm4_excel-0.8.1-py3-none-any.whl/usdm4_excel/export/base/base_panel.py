from .ct_version import CTVersion
from usdm4.api.code import Code
from usdm4.api.alias_code import AliasCode


class BasePanel:
    def __init__(self, ct_version: CTVersion):
        self.ct_version = ct_version

    def _pt_from_code(self, code: Code):
        return code.decode if code else ""

    def _pt_from_alias_code(self, code: AliasCode):
        if code is None or code.standardCode is None:
            return ""
        return code.standardCode.decode

    def _external_code(self, code: Code):
        return f"{code.codeSystem}: {code.code} = {code.decode}"
