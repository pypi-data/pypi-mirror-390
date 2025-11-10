def set(hex):
    return f"\033[38;2;{int(hex[1:3], 16)};{int(hex[3:5], 16)};{int(hex[5:], 16)}m"

def reset():
    return "\033[0m"