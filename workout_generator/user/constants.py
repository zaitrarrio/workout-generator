from richenum import OrderedRichEnum
from richenum import OrderedRichEnumValue


class _StatusState(OrderedRichEnumValue):
    def __init__(self, index, canonical_name, display_name):
        super(_StatusState, self).__init__(index, canonical_name, display_name)


class StatusState(OrderedRichEnum):
    UNCONFIRMED = _StatusState(1, 'unconfirmed', 'Unconfirmed')
    ACTIVE = _StatusState(2, 'active', 'Active')
    DEACTIVATED = _StatusState(3, 'deactivated', 'Deactivated')

    ACTIVE_FREE_MEMBERSHIP = _StatusState(4, 'active_free', 'Active Free Membership')


class _GenderType(OrderedRichEnumValue):
    def __init__(self, index, canonical_name, display_name):
        super(_GenderType, self).__init__(index, canonical_name, display_name)


class GenderType(OrderedRichEnum):
    MALE = _GenderType(1, 'male', 'Male')
    FEMALE = _GenderType(2, 'female', 'male')
