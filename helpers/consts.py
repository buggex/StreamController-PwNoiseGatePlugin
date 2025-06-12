from enum import StrEnum

class ExtendedEnum(StrEnum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Paramerters(ExtendedEnum):
    ENABLED = "enabled"
    THRESHOLD = "threshold"
    ATTACK = "attack"
    HOLD = "hold"
    DECAY = "decay"
    RANGE = "range"

ParamertersDefaultStep = {
    Paramerters.THRESHOLD:  1,
    Paramerters.ATTACK:     5,
    Paramerters.HOLD:       10,
    Paramerters.DECAY:      10,
    Paramerters.RANGE:      1
}

ParamertersUnit = {
    Paramerters.THRESHOLD:  "dB",
    Paramerters.ATTACK:     "ms",
    Paramerters.HOLD:       "ms",
    Paramerters.DECAY:      "ms",
    Paramerters.RANGE:      "dB"
}

ParamertersTitle = { # TODO translate
    Paramerters.ENABLED:    "Enabled",
    Paramerters.THRESHOLD:  "Threshold",
    Paramerters.ATTACK:     "Attack",
    Paramerters.HOLD:       "Hold",
    Paramerters.DECAY:      "Decay",
    Paramerters.RANGE:      "Range"
}
