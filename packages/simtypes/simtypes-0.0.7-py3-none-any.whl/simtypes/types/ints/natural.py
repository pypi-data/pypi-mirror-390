class NaturalNumberMeta(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, int) and instance > 0

class NaturalNumber(metaclass=NaturalNumberMeta):
    pass
