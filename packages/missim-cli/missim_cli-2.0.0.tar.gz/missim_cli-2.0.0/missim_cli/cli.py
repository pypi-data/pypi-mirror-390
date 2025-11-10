import missim_cli.groups.git as git
import missim_cli.groups.base as base
import missim_cli.groups.setup as setup
import missim_cli.groups.image as image
from missim_cli.helpers import is_dev_version, get_missim_version
from missim_cli.banner import get_banner
import click
import os


def cli():
    dev_mode = is_dev_version()
    version = get_missim_version()
    mode = "Developer" if dev_mode else "User"
    banner = get_banner(mode, version)

    os.environ["MISSIM_CLI_DEV_MODE"] = "true" if dev_mode else "false"

    @click.group(help=banner)
    def missim_cli():
        pass

    missim_cli.add_command(base.configure)
    missim_cli.add_command(base.config)
    missim_cli.add_command(base.upgrade)
    missim_cli.add_command(base.up)
    missim_cli.add_command(base.down)
    missim_cli.add_command(base.authenticate)

    if dev_mode:
        missim_cli.add_command(base.bake)
        missim_cli.add_command(base.base_ue)
        missim_cli.add_command(base.compile)
        missim_cli.add_command(base.build)
        missim_cli.add_command(base.generate)
        missim_cli.add_command(base.test_core)
        missim_cli.add_command(base.ue_generate)
        missim_cli.add_command(image.generate_image)

        missim_cli.add_command(git.git)
        git.git.add_command(git.pull)

        missim_cli.add_command(setup.setup)
        setup.setup.add_command(setup.secrets)

    missim_cli()


if __name__ == "__main__":
    cli()
