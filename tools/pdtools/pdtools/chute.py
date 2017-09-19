import click
import json
import os
import yaml

from .helpers.chute import build_chute


def update_object(obj, path, callback=None):
    """
    Traverse a data structure ensuring all nodes exist.

    obj: expected to be a dictionary
    path: string with dot-separated path components
    callback: optional callback function (described below)

    When update_object reaches the parent of the leaf node, it calls the
    optional callback function. The arguments to the callback function are:

    - parent: dictionary containing the leaf node
    - key: string key for the leaf node in parent
    - created: boolean flag indicating whether any part of the path, including
        the leaf node needed to be created.

    If the callback function is None, update_object will still ensure that all
    components along the path exist. If the leaf needs to be created, it will
    be created as an empty dictionary.

    Example:
    update_object({}, 'foo.bar') -> {'foo': {'bar': {}}}

    Return value: Returns either the return value of callback, or if callback
    is None, returns the value of the leaf node.
    """
    parts = path.split(".")

    current = obj
    parent = obj
    created = False
    for part in parts:
        if len(part) == 0:
            raise Exception("Path ({}) is invalid".format(path))

        if not isinstance(current, dict):
            raise Exception("Cannot set {}, not a dictionary".format(path))

        # Create dictionaries along the way if path nodes do not exist,
        # but make note of the fact that the previous value did not exist.
        if part not in current:
            current[part] = {}
            created = True

        parent = current
        current = parent[part]

    if callback is not None:
        return callback(parent, parts[-1], created)
    else:
        return current


@click.group()
@click.pass_context
def chute(ctx):
    """
    Sub-tree for building chutes.
    """
    pass


@chute.command('create-wifi-interface')
@click.pass_context
@click.argument('essid')
def create_wifi_interface(ctx, essid):
    """
    Add a Wi-Fi interface (AP mode) to the chute configuration.
    """
    with open('paradrop.yaml', 'r') as source:
        chute = yaml.safe_load(source)

    # Make sure the config.net section exists.
    net = update_object(chute, 'config.net')

    # Only support adding the first Wi-Fi interface for now.
    if 'wifi' in net:
        print("Wi-Fi interface already exists in paradrop.yaml.")
        print("Please edit the file directly to make changes.")
        return

    net['wifi'] = {
        'type': 'wifi',
        'intfName': 'wlan0',
        'dhcp': {
            'lease': '12h',
            'start': 4,
            'limit': 250
        },
        'ssid': essid,
        'options': {
            'isolate': False,
            'hidden': False
        }
    }

    with open('paradrop.yaml', 'w') as output:
        yaml.safe_dump(chute, output, default_flow_style=False)


@chute.command()
@click.pass_context
def init(ctx):
    """
    Interactively create a paradrop.yaml file.

    This will ask the user some questions and then writes a paradrop.yaml file.
    """
    chute = build_chute()
    with open("paradrop.yaml", "w") as output:
        yaml.safe_dump(chute, output, default_flow_style=False)

    # If this is a node.js chute, generate a package.json file from the
    # information that the user provided.
    if chute.get('use', None) == 'node':
        if not os.path.isfile('package.json'):
            data = {
                'name': chute['config']['name'],
                'version': '1.0.0',
                'description': chute['description']
            }
            with open('package.json', 'w') as output:
                json.dump(data, output, sort_keys=True, indent=2)


@chute.command()
@click.pass_context
@click.argument('path')
@click.argument('value')
def set(ctx, path, value):
    """
    Set a value in the chute configuration file.

    Example: set config.web.port 80
    """
    with open('paradrop.yaml', 'r') as source:
        chute = yaml.safe_load(source)

    # Calling yaml.safe_load on the value does a little type interpretation
    # (e.g. numeric vs. string) and allows the user to directly set lists and
    # other structures.
    value = yaml.safe_load(value)

    def set_value(parent, key, created):
        if created:
            print("Creating new field {} = {}".format(path, value))
        else:
            current = parent[key]
            print("Changing {} from {} to {}".format(path, current, value))

        parent[key] = value

    update_object(chute, path, set_value)

    with open('paradrop.yaml', 'w') as output:
        yaml.safe_dump(chute, output, default_flow_style=False)
