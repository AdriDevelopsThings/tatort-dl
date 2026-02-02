def format_bytes(b: int) -> str:
    bf = float(b)
    if b > 1024 * 1024 * 1024:
        bf /= 1024 * 1024 * 1024
        return f"{bf:.2f} GiB"
    elif b > 1024 * 1024:
        bf /= 1024 * 1024
        return f"{bf:.2f} MiB"
    elif b > 1024:
        bf /= 1024
        return f"{bf:2f} KiB"
    return f"{b} B"


class ErrorLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(f"[YT-DLP ERROR] {msg}")
