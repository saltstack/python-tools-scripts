# Python Tools Scripts

This is a tool, similar to [invoke](https://www.pyinvoke.org).
It's more recent and uses [argparse](https://docs.python.org/3/library/argparse.html) under the hood
and some additional magic to define the CLI arguments.

To use it, you must have a `tools` package in your repository root.
On your `tools/__init__.py` import your scripts and *Python Tools Scripts* will add them to it's CLI.

## An Example Script `tools/vm.py`

```python
"""
These commands are used to create/destroy VMs, sync the local checkout
to the VM and to run commands on the VM.
"""

from ptscripts import Context, command_group

# Define the command group
vm = command_group(name="vm", help="VM Related Commands", description=__doc__)


@vm.command(
    arguments={
        "name": {
            "help": "The VM Name",
            "metavar": "VM_NAME",
            "choices": list(AMIS),
        },
        "key_name": {
            "help": "The SSH key name.",
        },
        "instance_type": {
            "help": "The instance type to use.",
        },
        "region": {
            "help": "The AWS regsion.",
        },
    }
)
def create(
    ctx: Context,
    name: str,
    key_name: str = None,
    instance_type: str = None,
    region: str = "eu-central-1",
):
    """
    Create VM.
    """
    vm = VM(ctx=ctx, name=name)
    vm.create(region_name=region, key_name=key_name, instance_type=instance_type)


@vm.command(
    arguments={
        "name": {
            "help": "The VM Name",
            "metavar": "VM_NAME",
        },
    }
)
def destroy(ctx: Context, name: str):
    """
    Destroy VM.
    """
    vm = VM(ctx=ctx, name=name)
    vm.destroy()
```

The, on your repository root, run:

```
❯ tools -h
usage: tools [-h] [--debug] {vm} ...

Python Tools Scripts

optional arguments:
  -h, --help   show this help message and exit
  --debug, -d  Show debug messages

Commands:
  {vm}
    vm         VM Related Commands

These tools are discovered under `<repo-root>/tools`.
```

```
❯ tools vm -h
usage: tools vm [-h] {create,destroy} ...

These commands are used to create/destroy VMs, sync the local checkout to the VM and to run commands on the VM.

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {create,destroy}
    create              Create VM.
    destroy             Destroy VM.
```
