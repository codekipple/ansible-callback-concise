# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: codekipple_concise
    type: stdout
    short_description: codekipple_concise Ansible screen output
    description:
        - Concise output callback
'''

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from ansible.utils.color import stringc, hostcolor
from pprint import pprint

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'codekipple_concise'
    current_host = ''
    current_role = ''

    def _command_generic_msg(self, host, result, caption):
        ''' output the result of a command run '''

        buf = "%s | %s | rc=%s >>\n" % (host, caption, result.get('rc', -1))
        buf += result.get('stdout', '')
        buf += result.get('stderr', '')
        buf += result.get('msg', '')

        return buf + "\n"

    def v2_runner_on_failed(self, result, ignore_errors=False):

        self._handle_exception(result._result)
        self._handle_warnings(result._result)

        if result._task.action in C.MODULE_NO_JSON and 'module_stderr' not in result._result:
            self._display.display(self._command_generic_msg(result._host.get_name(), result._result, "FAILED"), color=C.COLOR_ERROR)
        else:
            self._display.display("%s | FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_ERROR)

    def v2_runner_on_ok(self, result):
        self._clean_results(result._result, result._task.action)

        self._handle_warnings(result._result)

        if result._result.get('changed', False):
            color = C.COLOR_CHANGED
            state = 'CHANGED'
        else:
            color = C.COLOR_OK
            state = 'SUCCESS'

        output_host = False;
        output_role = False;

        if self.current_host != result._host:
            self.current_host = result._host
            output_host = True

        if result._task._role and self.current_role != result._task._role:
            self.current_role = result._task._role
            output_role = True

        okTick = stringc(u'\u2713', color);

        taskName = "%s" % result._task_fields['name']

        if not taskName:
            taskName = result._task_fields['action']

        if output_host:
            host = "%s" % result._host
            self._display.display("")
            self._display.display("Host: " + host + " 🌍")
            self._display.display("==============================")

        if output_role:
            roleName = "%s" % result._task._role.get_name()
            self._display.display("")
            self._display.display(" Role: " + roleName + " 🗂")
            self._display.display(" ------------------------------")

        self._display.display("  " + okTick + " " + taskName)

    def v2_runner_on_skipped(self, result):
        skipped = stringc('skipped', 'bright yellow'); # should use C.COLOR_SKIP in future
        taskName = "%s" % result._task_fields['name']
        self._display.display("  " + skipped + " " + taskName)

    def v2_runner_on_unreachable(self, result):
        self._display.display("%s | UNREACHABLE! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_UNREACHABLE)

    def v2_on_file_diff(self, result):
        if 'diff' in result._result and result._result['diff']:
            self._display.display(self._get_diff(result._result['diff']))

    def _handle_warnings(self, res):
        ''' display warnings, if enabled and any exist in the result '''
        if C.ACTION_WARNINGS:
            if 'warnings' in res and res['warnings']:
                for warning in res['warnings']:
                    self._display.display("    " + u'\u21b3' + " " + "[warning]: " + warning, C.COLOR_WARN)
                del res['warnings']
            if 'deprecations' in res and res['deprecations']:
                for warning in res['deprecations']:
                    self._display.deprecated(**warning)
                del res['deprecations']
