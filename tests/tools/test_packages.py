# coding: utf-8
from StringIO import StringIO

from mock import patch
from httmock import urlmatch, HTTMock

from nose.tools import eq_

from acmd.tools import packages
from acmd import get_tool, Server


def test_tool_registration():
    tool = get_tool('packages')
    assert tool is not None


@urlmatch(netloc='localhost:4502')
def packages_mock(url, request):
    if url.path == '/crx/packmgr/service.jsp':
        with open('tests/test_data/packages_list.xml', 'rb') as f:
            return f.read()
    elif url.path.startswith('/crx/packmgr/service/.json/etc/packages'):
        return '{"status": "OK"}'
    else:
        raise Exception(url.path)


EXPECTED_LIST = """test_packages\tmock_package\t1.6.5
adobe/granite\tcom.adobe.coralui.rte-cq5\t5.6.18
adobe/granite\tcom.adobe.granite.activitystreams.content\t0.0.12
"""


@patch('sys.stdout', new_callable=StringIO)
def test_list_packages(stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        tool.execute(server, ['packages', 'list'])
        eq_(EXPECTED_LIST, stdout.getvalue())


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_upload_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'upload', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())

        status = tool.execute(server, ['packages', 'upload', '--raw', 'tests/test_data/mock_package.zip'])
        eq_(0, status)
        eq_('', stderr.getvalue())
        eq_(True, len(stdout.getvalue()) > 0)


@patch('sys.stdout', new_callable=StringIO)
@patch('sys.stderr', new_callable=StringIO)
def test_install_package(stderr, stdout):
    with HTTMock(packages_mock):
        tool = packages.PackagesTool()
        server = Server('localhost')

        status = tool.execute(server, ['packages', 'install', 'mock_package'])
        eq_(0, status)
        eq_('', stdout.getvalue())
        eq_('', stderr.getvalue())

        status = tool.execute(server, ['packages', 'install', '--raw', 'mock_package'])
        eq_(0, status)
        eq_('{"status": "OK"}\n', stdout.getvalue())
        eq_('', stderr.getvalue())
