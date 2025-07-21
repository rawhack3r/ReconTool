import shlex

try:
    cmd = "hello world"
    split_cmd = shlex.split(cmd)
    print(split_cmd)

    args = ["hello", "world"]
    joined_cmd = shlex.join(args)
    print(joined_cmd)

    quoted_str = shlex.quote("hello world")
    print(quoted_str)
except Exception as e:
    print(f"An error occurred: {e}")
