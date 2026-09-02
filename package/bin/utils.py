def get_float_value(value):
    try:
        f = float(str(value).strip())
        return f
    except Exception:  # noqa: BLE001
        return 0.0
