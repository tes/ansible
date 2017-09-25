# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.facts.collector import BaseFactCollector


class Network:
    """
    This is a generic Network subclass of Facts.  This should be further
    subclassed to implement per platform.  If you subclass this,
    you must define:
    - interfaces (a list of interface names)
    - interface_<name> dictionary of ipv4, ipv6, and mac address information.

    All subclasses MUST define platform.
    """
    platform = 'Generic'

    # FIXME: remove load_on_init when we can
    def __init__(self, module, load_on_init=False):
        self.module = module

    # TODO: more or less abstract/NotImplemented
    def populate(self, collected_facts=None):
        return {}

    def _include_interface(self, device_name, default_ipv4=dict(), default_ipv6=dict()):
        interfaces_list = self.module.params.get('gather_network_interfaces', None)
        # if no limits are set include all interfaces
        if interfaces_list is None:
            return True
        # always include the default interfaces
        if default_ipv4 and device_name == default_ipv4.get('interface', None):
            return True
        if default_ipv6 and device_name == default_ipv6.get('interface', None):
            return True
        # include all requested interfaces
        for pat in interfaces_list:
            if fnmatch.fnmatch(device_name, pat):
                return True
        return False

class NetworkCollector(BaseFactCollector):
    # MAYBE: we could try to build this based on the arch specific implemementation of Network() or its kin
    name = 'network'
    _fact_class = Network
    _fact_ids = set(['interfaces',
                     'default_ipv4',
                     'default_ipv6',
                     'all_ipv4_addresses',
                     'all_ipv6_addresses'])

    IPV6_SCOPE = {'0': 'global',
                  '10': 'host',
                  '20': 'link',
                  '40': 'admin',
                  '50': 'site',
                  '80': 'organization'}

    def collect(self, module=None, collected_facts=None):
        collected_facts = collected_facts or {}
        if not module:
            return {}

        # Network munges cached_facts by side effect, so give it a copy
        facts_obj = self._fact_class(module)

        facts_dict = facts_obj.populate(collected_facts=collected_facts)

        return facts_dict
