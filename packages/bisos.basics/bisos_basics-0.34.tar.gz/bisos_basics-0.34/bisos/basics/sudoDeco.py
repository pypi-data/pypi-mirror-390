#
# Taken from https://gist.github.com/barneygale/8ff070659178135b10b5e202a1ecaa3f
#

import sys, marshal, functools, subprocess

child_script = """
import marshal, sys, types;
fn, args, kwargs = marshal.loads(sys.stdin.buffer.read())
sys.stdout.buffer.write(
    marshal.dumps(
       types.FunctionType(fn, globals())(*args, **kwargs),
    )
)
"""

def sudo(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        proc_args = [
            "sudo",
            sys.executable,
            "-c",
            child_script]
        proc = subprocess.Popen(
            proc_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        send_data = marshal.dumps((
            fn.__code__,
            args,
            kwargs))
        recv_data = proc.communicate(send_data)[0]
        return marshal.loads(recv_data)
    return inner
