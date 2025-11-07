from .initializer import VarianceScaling

def he_normal():
    return VarianceScaling(scale=2.0, mode="fan_in", distribution="truncated_normal")

def he_uniform():
    return VarianceScaling(scale=2.0, mode="fan_in", distribution="uniform")

def xavier_normal():
    return VarianceScaling(scale=1.0, mode="fan_avg", distribution="truncated_normal")

def xavier_uniform():
    return VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform")

def lecun_normal():
    return VarianceScaling(scale=1.0, mode="fan_in", distribution="truncated_normal")

def lecun_uniform():
    return VarianceScaling(scale=1.0, mode="fan_in", distribution="uniform")

