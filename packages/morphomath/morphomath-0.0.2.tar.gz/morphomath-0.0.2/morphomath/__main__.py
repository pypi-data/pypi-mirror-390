"""Command line interface entry point."""

import importlib

import click


class LazyGroup(click.Group):
    """Overwite clik.Group to layy import."""

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize the lazy importator."""
        self._lazy_commands = {}
        super().__init__(*args, **kwargs)

    def add_lazy_command(self, import_path: str, name: str) -> None:
        """Register a command without importing it immediately."""
        self._lazy_commands[name] = import_path

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command:
        """Import the function of the module."""
        if cmd_name in self._lazy_commands:
            module_path, func_name = self._lazy_commands[cmd_name].rsplit(".", 1)
            mod = importlib.import_module(module_path)
            return getattr(mod, func_name)

        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> list:
        """List all available command names (including lazy ones)."""
        cmds = set(super().list_commands(ctx))
        cmds.update(self._lazy_commands.keys())
        return sorted(cmds)


@click.group(cls=LazyGroup)
def main() -> None:
    """Perform morphological transformations."""


# same as main.add_command but with lazy import
main.add_lazy_command("morphomath.cli.doc.main", "doc")
main.add_lazy_command("morphomath.cli.test.main", "test")


if __name__ == "__main__":
    main()
