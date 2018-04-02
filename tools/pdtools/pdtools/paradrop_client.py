import base64
import getpass
import os
import re

import builtins
import requests

from .devices.camera import Camera


LOCAL_DEFAULT_USERNAME = "paradrop"
LOCAL_DEFAULT_PASSWORD = ""

PARADROP_API_TOKEN = os.environ.get("PARADROP_API_TOKEN", None)
PARADROP_CHUTE_NAME = os.environ.get("PARADROP_CHUTE_NAME", None)


class ParadropClient(object):
    """
    Client for interacting with a Paradrop daemon instance.

    Here is a motivating example that is intended to be valid chute code:

    from pdtools import ParadropClient
    client = ParadropClient()
    for camera in client.get_cameras():
        img = camera.get_image()
    """
    def __init__(self, host=None):
        if host is None:
            host = "172.17.0.1"

        self.host = host
        self.base_url = "http://{}/api/v1".format(host)


    def add_ssh_key(self, key_text, user="paradrop"):
        """
        Add an authorized key for SSH access.
        """
        url = "{}/config/sshKeys/{}".format(self.base_url, user)
        data = {
            'key': key_text
        }
        return self.request("POST", url, json=data)

    def get_audio(self):
        """
        Get information about the audio subsystem.
        """
        url = self.base_url + "/audio/info"
        return self.request("GET", url)

    def get_chute(self, chute_name):
        """
        Get information about an installed chute.
        """
        url = self.base_url + "/chutes/" + chute_name
        return self.request("GET", url)

    def get_chute_cache(self, chute_name):
        """
        Get internal information about an installed chute.
        """
        url = "{}/chutes/{}/cache".format(self.base_url, chute_name)
        return self.request("GET", url)

    def get_chute_client(self, chute_name, network, client):
        """
        Get information about a chute's network client.
        """
        url = "{}/chutes/{}/networks/{}/stations/{}".format(self.base_url,
                chute_name, network, client)
        return self.request("GET", url)

    def get_chute_config(self, chute_name):
        """
        Get chute configuration.
        """
        url = "{}/chutes/{}/config".format(self.base_url, chute_name)
        return self.request("GET", url)

    def get_config(self):
        """
        Get node configuration.
        """
        url = self.base_url + "/config/hostconfig"
        return self.request("GET", url)

    def get_pdconf(self):
        """
        Get status of the pdconf subsystem.
        """
        url = self.base_url + "/config/pdconf"
        return self.request("GET", url)

    def get_provision(self):
        """
        Get provisioning status of the node.
        """
        url = self.base_url + "/config/provision"
        return self.request("GET", url)

    def list_audio_modules(self):
        """
        List modules loaded by the audio subsystem.
        """
        url = self.base_url + "/audio/modules"
        return self.request("GET", url)

    def list_audio_sinks(self):
        """
        List audio sinks.
        """
        url = self.base_url + "/audio/sinks"
        return self.request("GET", url)

    def list_audio_sources(self):
        """
        List audio sources.
        """
        url = self.base_url + "/audio/sources"
        return self.request("GET", url)

    def list_changes(self):
        """
        List queued or in-progress changes.
        """
        url = self.base_url + "/changes/"
        return self.request("GET", url)

    def list_chute_clients(self, chute_name, network):
        """
        List clients connected to the chute's network
        """
        url = "{}/chutes/{}/networks/{}/stations".format(self.base_url,
                chute_name, network)
        return self.request("GET", url)

    def list_chute_networks(self, chute_name):
        """
        List networks configured by the chute.
        """
        url = "{}/chutes/{}/networks".format(self.base_url, chute_name)
        return self.request("GET", url)

    def list_chutes(self):
        """
        List chutes installed on the node.
        """
        url = self.base_url + "/chutes/"
        return self.request("GET", url)

    def list_ssh_keys(self, user="paradrop"):
        """
        List authorized keys for SSH access.
        """
        url = "{}/config/sshKeys/{}".format(self.base_url, user)
        return self.request("GET", url)

    def load_audio_module(self, module_name):
        """
        Load a module into the audio subsystem.
        """
        url = "{}/audio/modules".format(self.base_url)
        data = {
            "name": module_name
        }
        return self.request("POST", url, json=data)

    def provision(self, id, key, controller=None, wamp=None):
        """
        Provision the node by connecting to a cloud controller.
        """
        url = self.base_url + "/config/provision"

        data = {
            'routerId': id,
            'apitoken': key
        }
        if controller is not None:
            data['pdserver'] = controller
        if wamp is not None:
            data['wampRouter'] = wamp

        return self.request("POST", url, json=data)

    def set_chute_config(self, chute_name, config):
        """
        Set chute configuration.
        """
        url = "{}/chutes/{}/config".format(self.base_url, chute_name)
        return self.request("PUT", url, json=config)

    def set_chute_variables(self, chute_name, config):
        """
        Set chute environment variables.
        """
        url = "{}/chutes/{}/restart".format(self.base_url, chute_name)
        data = {
            "environment": config
        }
        return self.request("POST", url, json=data)

    def set_config(self, config):
        """
        Set node configuration.
        """
        url = self.base_url + "/config/hostconfig"
        data = {
            'config': config
        }
        return self.request("PUT", url, json=data)

    def remove_chute(self, chute_name):
        """
        Remove a chute from the node.
        """
        url = self.base_url + "/chutes/" + chute_name
        return self.request("DELETE", url)

    def remove_chute_client(self, chute_name, network, client):
        """
        Remove a connected client from the chute's network.
        """
        url = "{}/chutes/{}/networks/{}/stations/{}".format(self.base_url,
                chute_name, network, client)
        return self.request("DELETE", url)

    def restart_chute(self, chute_name):
        """
        Restart a chute.
        """
        url = "{}/chutes/{}/restart".format(self.base_url, chute_name)
        return self.request("POST", url)

    def start_chute(self, chute_name):
        """
        Start a stopped chute.
        """
        url = "{}/chutes/{}/start".format(self.base_url, chute_name)
        return self.request("POST", url)

    def stop_chute(self, chute_name):
        """
        Stop a running chute.
        """
        url = "{}/chutes/{}/stop".format(self.base_url, chute_name)
        return self.request("POST", url)

    def trigger_pdconf(self):
        """
        Trigger pdconf to reload configuration.
        """
        url = self.base_url + "/config/pdconf"
        return self.request("PUT", url)



    def get_cameras(self, chute_name=PARADROP_CHUTE_NAME, network_name=None):
        """
        List cameras connected to a chute's network.

        Note: This only detects the subset of D-Link cameras that we currently
        support. We will add more devices as we test them.

        chute_name: if not specified, will be read from PARADROP_CHUTE_NAME
        network_name: if not specified, will include all of the chute's networks
        """
        if chute_name is None:
            raise Exception("chute_name was not specified")

        cameras = []
        leases = self.get_leases(chute_name, network_name)

        dlink_re = re.compile("(28:10:7b|b0:c5:54|01:b0:c5):.*")
        for lease in leases:
            match = dlink_re.match(lease['mac_addr'])
            if match is not None:
                cameras.append(Camera(lease['mac_addr'], lease['ip_addr']))

        return cameras

    def get_leases(self, chute_name=PARADROP_CHUTE_NAME, network_name=None):
        """
        List DHCP lease records for a chute's network.

        chute_name: if not specified, will be read from PARADROP_CHUTE_NAME
        network_name: if not specified, will include all of the chute's networks
        """
        if chute_name is None:
            raise Exception("chute_name was not specified")

        networks = []
        devices = []

        if network_name is not None:
            networks = [network_name]
        else:
            netlist = self.get_networks(chute_name)

            # In rare cases, get_networks returns None early in the chute
            # lifetime. Instead of causing an exception, treat it as an empty
            # list - no cameras detected yet.
            if netlist is not None:
                networks = [x['name'] for x in netlist]

        for net in networks:
            url = self.base_url + "/chutes/{}/networks/{}/leases".format(
                    chute_name, net)
            result = self.request("GET", url)
            if isinstance(result, list):
                devices.extend(result)

        return devices

    def get_networks(self, chute_name=PARADROP_CHUTE_NAME):
        """
        List networks owned by a chute.

        chute_name: if not specified, will be read from PARADROP_CHUTE_NAME
        """
        if chute_name is None:
            raise Exception("chute_name was not specified")

        url = self.base_url + "/chutes/{}/networks".format(chute_name)
        result = self.request("GET", url)

        return result

    def request(self, method, url, json=None, headers=None, **kwargs):
        """
        Issue a router API request.

        This will prompt for a username and password if necessary.
        """
        session = requests.Session()
        request = requests.Request(method, url, json=json, headers=headers, **kwargs)

        # TODO: Implement selectable auth methods including:
        # - Default username and password
        # - Prompt for username and password

        if PARADROP_API_TOKEN is None:
            # First try with the default username and password.
            # If that fails, prompt user and try again.
            userpass = "{}:{}".format(LOCAL_DEFAULT_USERNAME, LOCAL_DEFAULT_PASSWORD)

            encoded = base64.b64encode(userpass.encode('utf-8')).decode('ascii')
            session.headers.update({'Authorization': 'Basic {}'.format(encoded)})

        else:
            value = 'Bearer {}'.format(PARADROP_API_TOKEN)
            session.headers.update({'Authorization': value})

        prepped = session.prepare_request(request)

        while True:
            res = session.send(prepped)
            if res.status_code == 401:
                username = builtins.input("Username: ")
                password = getpass.getpass("Password: ")
                userpass = "{}:{}".format(username, password).encode('utf-8')
                encoded = base64.b64encode(userpass.encode('utf-8')).decode('ascii')

                session.headers.update({'Authorization': 'Basic {}'.format(encoded)})
                prepped = session.prepare_request(request)

            elif res.ok:
                return res.json()

            else:
                return None
