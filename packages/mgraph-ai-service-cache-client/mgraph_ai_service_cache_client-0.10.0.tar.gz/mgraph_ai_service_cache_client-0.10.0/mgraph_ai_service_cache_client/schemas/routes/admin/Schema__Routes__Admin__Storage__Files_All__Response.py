from typing                                                                         import List
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path   import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now


class Schema__Routes__Admin__Storage__Files_All__Response(Type_Safe):
    timestamp  : Timestamp_Now
    file_count : Safe_UInt
    files      : List[Safe_Str__File__Path]