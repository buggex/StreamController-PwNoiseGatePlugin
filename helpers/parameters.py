from enum import StrEnum

class ExtendedEnum(StrEnum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class DialParameters(ExtendedEnum):
    THRESHOLD = "threshold"
    ATTACK = "attack"
    HOLD = "hold"
    DECAY = "decay"
    RANGE = "range"

class ToogleParameters(ExtendedEnum):
    ENABLED = "enabled"

DialParametersDefaultStep = {
    DialParameters.THRESHOLD:  1,
    DialParameters.ATTACK:     5,
    DialParameters.HOLD:       10,
    DialParameters.DECAY:      10,
    DialParameters.RANGE:      1
}

DialParametersUnit = {
    DialParameters.THRESHOLD:  "dB",
    DialParameters.ATTACK:     "ms",
    DialParameters.HOLD:       "ms",
    DialParameters.DECAY:      "ms",
    DialParameters.RANGE:      "dB"
}

DialParametersTitle = { # TODO translate
    DialParameters.THRESHOLD:  "Threshold",
    DialParameters.ATTACK:     "Attack",
    DialParameters.HOLD:       "Hold",
    DialParameters.DECAY:      "Decay",
    DialParameters.RANGE:      "Range"
}

ToogleParametersTitle = { # TODO translate
    ToogleParameters.ENABLED:    "Enabled"
}
