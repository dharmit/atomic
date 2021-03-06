import argparse

from . import util
from Atomic.backendutils import BackendUtils

try:
    from . import Atomic
except ImportError:
    from atomic import Atomic # pylint: disable=relative-import

def cli(subparser):
    # atomic stop
    stopp = subparser.add_parser(
        "stop", help=_("execute container image stop method"),
        epilog="atomic will just stop the container if it is running, if "
        "image does not specify LABEL STOP")
    stopp.set_defaults(_class=Stop, func='stop')
    util.add_opt(stopp)
    stopp.add_argument("container", help=_("container name or ID"))
    stopp.add_argument("args", nargs=argparse.REMAINDER,
                          help=_("Additional arguments appended to the image "
                                 "stop method"))

ATOMIC_CONFIG = util.get_atomic_config()
storage = ATOMIC_CONFIG.get('default_storage', "docker")

class Stop(Atomic):
    def __init__(self):
        super(Stop, self).__init__()

    def stop(self):

        if self.args.debug:
            util.write_out(str(self.args))

        beu = BackendUtils()
        be, con_obj = beu.get_backend_and_container_obj(self.args.container, storage)
        con_obj.stop_args = con_obj.get_label('stop')
        if con_obj.stop_args and be.backend == 'docker':
            cmd = self.gen_cmd(con_obj.stop_args + self.quote(self.args.args))
            cmd = self.sub_env_strings(cmd)
            self.display(cmd)
            # There should be some error handling around this
            # in case it fails.  And what should then be done?
            util.check_call(cmd, env=self.cmd_env())

        be.stop_container(con_obj)

