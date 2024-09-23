def split_file(path: str) -> tuple[tuple[str, str, str]]:
    with open(path, "r") as f:
        lines = f.readlines()
        res = []
        for i, line in enumerate(lines):
            if line == "\n" or line.startswith("#"):
                continue
            res.append(tuple(line.strip().split()))
    return tuple(res)
