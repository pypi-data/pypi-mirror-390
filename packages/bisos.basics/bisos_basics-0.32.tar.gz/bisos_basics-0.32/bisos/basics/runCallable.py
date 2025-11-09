#
# taken from https://pastebin.com/DHPdDU9W
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

class GTFO(Exception): pass
class ThisIsNotTheTypeYoureLookingFor(Exception): pass
class YouShallNotPass(Exception): pass
class GotSomeSplaininToDo(Exception): pass


class as_user(object):
    def __init__(self, user):

        if user is None:
            raise GTFO()
        elif not isinstance(user, str):
            raise ThisIsNotTheTypeYoureLookingFor()

        user = user.strip()

        # if len(user) == 0 or user == 'root':
        #     raise YouShallNotPass()

        self.__user = user

    @property
    def user(self):
        return self.__user

    def __call__(self, func):

        @functools.wraps(func)
        def inner(*args, **kwargs):
            proc_args = [
                "sudo",
                "-u",
                self.user,
                sys.executable,
                "-c",
                child_script]

            proc = subprocess.Popen(
                proc_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)


            ex = None
            retval = None

            try:
                send_data = marshal.dumps((
                func.__code__,
                    args,
                    kwargs))
                recv_data = proc.communicate(send_data)[0]


                retval = marshal.loads(recv_data)
            except Exception as e:
                ex = e

            returncode = proc.wait()
            if returncode != 0 or ex is not None:
                #raise GotSomeSplaininToDo(returncode, retval, ex)
                pass

            return retval

        return inner
