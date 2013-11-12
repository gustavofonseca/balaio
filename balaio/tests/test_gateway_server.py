#coding: utf-8
import json
import sys
import os
import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound,HTTPAccepted, HTTPCreated
from sqlalchemy import create_engine
from webtest import TestApp
import transaction

from balaio import models, gateway_server
from .doubles import *
from .utils import db_bootstrap
from . import modelfactories


sys.path.append(os.path.dirname(__file__) + '/../')
global_engine = None


def setUpModule():
    """
    Initialize the database.
    """
    global global_engine
    global_engine = db_bootstrap()


def _load_fixtures(obj_list):

    with transaction.manager:
        models.ScopedSession.add_all(obj_list)


class FunctionalAPITest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        app = gateway_server.main(ConfigStub(), global_engine)
        self.testapp = TestApp(app)

    def tearDown(self):
        models.ScopedSession.remove()
        testing.tearDown()

    def test_root(self):
        resp = self.testapp.get('/', status=200)
        self.assertTrue('http server' in resp.body.lower())

    def test_GET_to_unavailable_resource(self):
        self.testapp.get('/api/v1/lokmshin/', status=404)


class AttemptFunctionalAPITest(unittest.TestCase):

    def setUp(self):
        self._loaded_fixtures = [self._makeOne() for i in range(3)]
        self.config = testing.setUp()

        app = gateway_server.main(ConfigStub(), global_engine)
        self.testapp = TestApp(app)

    def tearDown(self):
        transaction.abort()
        models.ScopedSession.remove()
        testing.tearDown()

    def _makeOne(self):
        import datetime
        attempt = modelfactories.AttemptFactory.create()
        attempt.started_at = datetime.datetime(2013, 10, 9, 16, 44, 29, 865787)
        return attempt

    def test_GET_to_available_resource(self):
        self.testapp.get('/api/v1/attempts/', status=200)

    def test_GET_to_one_attempt(self):
        attempt_id = self._loaded_fixtures[0].id
        attempt_checksum = self._loaded_fixtures[0].package_checksum
        articlepkg_id = self._loaded_fixtures[0].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/%s/' % attempt_id)

        expected = '''{"collection_uri": "",
                       "filepath": "/tmp/watch/xxx.zip",
                       "finished_at": null,
                       "articlepkg_id": %s,
                       "is_valid": true,
                       "started_at": "2013-10-09 16:44:29.865787",
                       "id": %s,
                       "package_checksum": "%s",
                       "resource_uri": "/api/v1/attempts/%s/"}''' % (articlepkg_id, attempt_id, attempt_checksum, attempt_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts(self):
        attempt0_id = self._loaded_fixtures[0].id
        attempt0_checksum = self._loaded_fixtures[0].package_checksum
        articlepkg0_id = self._loaded_fixtures[0].articlepkg.id

        attempt1_id = self._loaded_fixtures[1].id
        attempt1_checksum = self._loaded_fixtures[1].package_checksum
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        attempt2_id = self._loaded_fixtures[2].id
        attempt2_checksum = self._loaded_fixtures[2].package_checksum
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/')

        expected = '''{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": 0},
                       "objects": [
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"},
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"},
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"}
                        ]
                    }''' % (articlepkg0_id, attempt0_id, attempt0_checksum, attempt0_id,
                            articlepkg1_id, attempt1_id, attempt1_checksum, attempt1_id,
                            articlepkg2_id, attempt2_id, attempt2_checksum, attempt2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_limit(self):
        attempt0_id = self._loaded_fixtures[0].id
        attempt0_checksum = self._loaded_fixtures[0].package_checksum
        articlepkg0_id = self._loaded_fixtures[0].articlepkg.id

        attempt1_id = self._loaded_fixtures[1].id
        attempt1_checksum = self._loaded_fixtures[1].package_checksum
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        attempt2_id = self._loaded_fixtures[2].id
        attempt2_checksum = self._loaded_fixtures[2].package_checksum
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/?limit=45')

        expected = '''{"meta": {"previous": null, "next": null, "total": 3, "limit": 45, "offset": 0},
                       "objects": [
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"},
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"},
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"}
                    ]}'''% (articlepkg0_id, attempt0_id, attempt0_checksum, attempt0_id,
                            articlepkg1_id, attempt1_id, attempt1_checksum, attempt1_id,
                            articlepkg2_id, attempt2_id, attempt2_checksum, attempt2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_offset(self):
        attempt1_id = self._loaded_fixtures[1].id
        attempt1_checksum = self._loaded_fixtures[1].package_checksum
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        attempt2_id = self._loaded_fixtures[2].id
        attempt2_checksum = self._loaded_fixtures[2].package_checksum
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/?offset=1')

        expected = '''{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": "1"},
                       "objects": [
                         {"collection_uri": "",
                          "filepath": "/tmp/watch/xxx.zip",
                          "finished_at": null,
                          "articlepkg_id": %s,
                          "is_valid": true,
                          "started_at": "2013-10-09 16:44:29.865787",
                          "id": %s,
                          "package_checksum": "%s",
                          "resource_uri": "/api/v1/attempts/%s/"},
                         {"collection_uri": "",
                          "filepath": "/tmp/watch/xxx.zip",
                          "finished_at": null,
                          "articlepkg_id": %s,
                          "is_valid": true,
                          "started_at": "2013-10-09 16:44:29.865787",
                          "id": %s,
                          "package_checksum": "%s",
                          "resource_uri": "/api/v1/attempts/%s/"}
                        ]}''' % (articlepkg1_id, attempt1_id, attempt1_checksum, attempt1_id,
                                 articlepkg2_id, attempt2_id, attempt2_checksum, attempt2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_offset_and_limit(self):
        res = self.testapp.get('/api/v1/attempts/?offset=4&limit=78')
        expected = '{"meta": {"previous": null, "next": null, "total": 3, "limit": 78, "offset": "4"}, "objects": []}'

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_low_limit(self):
        attempt0_id = self._loaded_fixtures[0].id
        attempt0_checksum = self._loaded_fixtures[0].package_checksum
        articlepkg0_id = self._loaded_fixtures[0].articlepkg.id

        attempt1_id = self._loaded_fixtures[1].id
        attempt1_checksum = self._loaded_fixtures[1].package_checksum
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/?limit=2')

        expected = '''{"meta": {"previous": null, "next": "/api/v1/attempts/?limit=2&offset=2", "total": 3, "limit": 2, "offset": 0},
                       "objects": [
                         {"collection_uri": "",
                          "filepath": "/tmp/watch/xxx.zip",
                          "finished_at": null,
                          "articlepkg_id": %s,
                          "is_valid": true,
                          "started_at": "2013-10-09 16:44:29.865787",
                          "id": %s,
                          "package_checksum": "%s",
                          "resource_uri": "/api/v1/attempts/%s/"},
                         {"collection_uri": "",
                          "filepath": "/tmp/watch/xxx.zip",
                          "finished_at": null,
                          "articlepkg_id": %s,
                          "is_valid": true,
                          "started_at": "2013-10-09 16:44:29.865787",
                          "id": %s,
                          "package_checksum": "%s",
                          "resource_uri": "/api/v1/attempts/%s/"}
                        ]}''' % (articlepkg0_id, attempt0_id, attempt0_checksum, attempt0_id,
                                 articlepkg1_id, attempt1_id, attempt1_checksum, attempt1_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_low_offset_and_limit(self):
        attempt1_id = self._loaded_fixtures[1].id
        attempt1_checksum = self._loaded_fixtures[1].package_checksum
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        attempt2_id = self._loaded_fixtures[2].id
        attempt2_checksum = self._loaded_fixtures[2].package_checksum
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/?limit=2&offset=1')

        expected = '''{"meta": {"previous": null, "next": "/api/v1/attempts/?limit=2&offset=3", "total": 3, "limit": 2, "offset": "1"},
                       "objects": [
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"},
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"}
                         ]}'''% (articlepkg1_id, attempt1_id, attempt1_checksum, attempt1_id,
                                 articlepkg2_id, attempt2_id, attempt2_checksum, attempt2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_attempts_with_param_low_limit_and_offset(self):
        attempt2_id = self._loaded_fixtures[2].id
        attempt2_checksum = self._loaded_fixtures[2].package_checksum
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/attempts/?limit=1&offset=2')

        expected = '''{"meta": {"previous": "/api/v1/attempts/?limit=1&offset=1", "next": "/api/v1/attempts/?limit=1&offset=3", "total": 3, "limit": 1, "offset": "2"},
                       "objects": [
                           {"collection_uri": "",
                            "filepath": "/tmp/watch/xxx.zip",
                            "finished_at": null,
                            "articlepkg_id": %s,
                            "is_valid": true,
                            "started_at": "2013-10-09 16:44:29.865787",
                            "id": %s,
                            "package_checksum": "%s",
                            "resource_uri": "/api/v1/attempts/%s/"}
                         ]}''' % (articlepkg2_id, attempt2_id, attempt2_checksum, attempt2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))


class TicketFunctionalAPITest(unittest.TestCase):

    def setUp(self):
        self._loaded_fixtures = [self._makeOne() for i in range(3)]
        self.config = testing.setUp()
        app = gateway_server.main(ConfigStub(), global_engine)
        self.testapp = TestApp(app)

    def tearDown(self):
        transaction.abort()
        models.ScopedSession.remove()
        testing.tearDown()

    def _makeOne(self, id=1):
        import datetime
        ticket = modelfactories.TicketFactory.create()
        ticket.started_at = datetime.datetime(2013, 10, 9, 16, 44, 29, 865787)
        return ticket

    def test_GET_to_available_resource(self):
        self.testapp.get('/api/v1/tickets/', status=200)

    def test_GET_to_one_ticket(self):
        ticket1_id = self._loaded_fixtures[1].id
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        res = self.testapp.get('/api/v1/tickets/%s/' % ticket1_id)
        expected = '''{"title": "Erro no pacote xxx",
                       "finished_at": null,
                       "author": "Aberlado Barbosa",
                       "articlepkg_id": %s,
                       "comments": [],
                       "is_open": true,
                       "started_at": "2013-10-09 16:44:29.865787",
                       "id": %s,
                       "resource_uri": "/api/v1/tickets/%s/"}''' % (articlepkg1_id, ticket1_id, ticket1_id)
        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_tickets(self):
        ticket0_id = self._loaded_fixtures[0].id
        articlepkg0_id = self._loaded_fixtures[0].articlepkg.id

        ticket1_id = self._loaded_fixtures[1].id
        articlepkg1_id = self._loaded_fixtures[1].articlepkg.id

        ticket2_id = self._loaded_fixtures[2].id
        articlepkg2_id = self._loaded_fixtures[2].articlepkg.id

        res = self.testapp.get('/api/v1/tickets/')

        expected = '''{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": 0},
                       "objects": [
                          {"title": "Erro no pacote xxx",
                           "finished_at": null,
                           "author": "Aberlado Barbosa",
                           "articlepkg_id": %s,
                           "comments": [],
                           "is_open": true,
                           "started_at": "2013-10-09 16:44:29.865787",
                           "id": %s,
                           "resource_uri": "/api/v1/tickets/%s/"},
                          {"title": "Erro no pacote xxx",
                           "finished_at": null,
                           "author": "Aberlado Barbosa",
                           "articlepkg_id": %s,
                           "comments": [],
                           "is_open": true,
                           "started_at": "2013-10-09 16:44:29.865787",
                           "id": %s,
                           "resource_uri": "/api/v1/tickets/%s/"},
                          {"title": "Erro no pacote xxx",
                           "finished_at": null,
                           "author": "Aberlado Barbosa",
                           "articlepkg_id": %s,
                           "comments": [],
                           "is_open": true,
                           "started_at": "2013-10-09 16:44:29.865787",
                           "id": %s,
                           "resource_uri": "/api/v1/tickets/%s/"}
                    ]}''' % (articlepkg0_id, ticket0_id, ticket0_id,
                             articlepkg1_id, ticket1_id, ticket1_id,
                             articlepkg2_id, ticket2_id, ticket2_id)

        self.assertEqual(json.loads(res.body), json.loads(expected))

    def test_GET_to_tickets_with_param_limit(self):
        res = self.testapp.get('/api/v1/tickets/?limit=45')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 45, "offset": 0}, "objects": [{"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 1, "resource_uri": "/api/v1/tickets/1/"}, {"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 2, "resource_uri": "/api/v1/tickets/2/"}, {"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 3, "resource_uri": "/api/v1/tickets/3/"}]}'))

    def test_GET_to_tickets_with_param_offset(self):
        res = self.testapp.get('/api/v1/tickets/?offset=1')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": "1"}, "objects": [{"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 2, "resource_uri": "/api/v1/tickets/2/"}, {"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 3, "resource_uri": "/api/v1/tickets/3/"}]}'))

    def test_GET_to_tickets_with_param_offset_and_limit(self):
        res = self.testapp.get('/api/v1/tickets/?offset=4&limit=78')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 78, "offset": "4"}, "objects": []}'))

    def test_GET_to_tickets_with_param_low_limit(self):
        res = self.testapp.get('/api/v1/tickets/?limit=2')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": "/api/v1/tickets/?limit=2&offset=2", "total": 3, "limit": 2, "offset": 0}, "objects": [{"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 1, "resource_uri": "/api/v1/tickets/1/"}, {"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 2, "resource_uri": "/api/v1/tickets/2/"}]}'))

    def test_GET_to_tickets_with_param_low_offset_and_limit(self):
        res = self.testapp.get('/api/v1/tickets/?limit=2&offset=1')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": "/api/v1/tickets/?limit=2&offset=3", "total": 3, "limit": 2, "offset": "1"}, "objects": [{"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 2, "resource_uri": "/api/v1/tickets/2/"}, {"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 3, "resource_uri": "/api/v1/tickets/3/"}]}'))

    def test_GET_to_tickets_with_param_low_limit_and_offset(self):
        res = self.testapp.get('/api/v1/tickets/?limit=1&offset=2')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": "/api/v1/tickets/?limit=1&offset=1", "next": "/api/v1/tickets/?limit=1&offset=3", "total": 3, "limit": 1, "offset": "2"}, "objects": [{"title": "Erro no pacote xxx", "finished_at": null, "author": "Aberlado Barbosa", "articlepkg_id": 1, "comments": [], "is_open": true, "started_at": "2013-10-09 16:44:29.865787", "id": 3, "resource_uri": "/api/v1/tickets/3/"}]}'))

    def test_POST_to_create_ticket_without_message(self):
        res = self.testapp.post('/api/v1/tickets/',
                {
                 'articlepkg_id': 1,
                 'title': 'Article about xxx',
                 'ticket_author': 'Aberlado Barbosa',
                })

        self.assertEqual(res.status_code, 201)

    def test_POST_to_create_ticket_with_message(self):
        res = self.testapp.post('/api/v1/tickets/',
                {
                 'articlepkg_id': 1,
                 'title': 'Article about xxx',
                 'ticket_author': 'Aberlado Barbosa',
                 'message': 'Error on validation....'
                })

        self.assertEqual(res.status_code, 201)

    def test_POST_to_update_ticket_with_different_params(self):
        res_post = self.testapp.post('/api/v1/tickets/3/',
                {
                 'message': 'Error on validation....',
                 'is_open': 1,
                 'comment_author': 'bla bla'
                })

        self.assertEqual(res_post.status_code, 202)

        res_get = self.testapp.get('/api/v1/tickets/3/')

        res_json = json.loads(res_get.body)

        self.assertIn(res_json.get('comments')[0]['message'],
            'Error on validation....')

    def test_POST_to_update_ticket_unavailable_resource(self):
        self.testapp.post('/api/v1/tickets/87/',
                {
                 'articlepkg_id': 1,
                 'ticket_author': 'Aberlado Barbosa',
                 'message': 'Error on validation....',
                 'is_open': 1,
                 'comment_author': 'bla bla'
                }, status=404)

class PackageFunctionalAPITest(unittest.TestCase):

    def setUp(self):
        _load_fixtures(self._makeList())
        self.config = testing.setUp()
        app = gateway_server.main(ConfigStub(), global_engine)
        self.testapp = TestApp(app)

    def tearDown(self):
        models.ScopedSession.remove()
        testing.tearDown()

    def _makeOne(self, id=1):
        article = models.ArticlePkg(id=id,
                    journal_title='Associa... Brasileira',
                    article_title='Construction of a recombinant adenovirus...',
                    journal_pissn='0100-879X',
                    journal_eissn='0100-879X',
                    issue_year=1995,
                    issue_volume='67',
                    issue_number='8',
                    issue_suppl_volume=None,
                    issue_suppl_number=None)
        return article

    def _makeList(self):
        return [self._makeOne(), self._makeOne(2), self._makeOne(3)]

    def test_GET_to_available_resource(self):
        self.testapp.get('/api/v1/packages/', status=200)

    def test_GET_to_one_package(self):
        res = self.testapp.get('/api/v1/packages/1/')

        self.assertEqual(json.loads(res.body), json.loads('{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/1/", "id": 1, "issue_number": "8"}'))

    def test_GET_to_packages(self):
        res = self.testapp.get('/api/v1/packages/')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": 0}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/1/", "id": 1, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/2/", "id": 2, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/3/", "id": 3, "issue_number": "8"}]}'))

    def test_GET_to_packages_with_param_limit(self):
        res = self.testapp.get('/api/v1/packages/?limit=82')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 82, "offset": 0}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/1/", "id": 1, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/2/", "id": 2, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/3/", "id": 3, "issue_number": "8"}]}'))

    def test_GET_to_packages_with_param_offset(self):
        res = self.testapp.get('/api/v1/packages/?offset=1')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 20, "offset": "1"}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/2/", "id": 2, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/3/", "id": 3, "issue_number": "8"}]}'))

    def test_GET_to_packages_with_param_offset_and_limit(self):
        res = self.testapp.get('/api/v1/packages/?offset=4&limit=78')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": null, "total": 3, "limit": 78, "offset": "4"}, "objects": []}'))

    def test_GET_to_packages_with_param_low_limit(self):
        res = self.testapp.get('/api/v1/packages/?limit=2')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": "/api/v1/packages/?limit=2&offset=2", "total": 3, "limit": 2, "offset": 0}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/1/", "id": 1, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/2/", "id": 2, "issue_number": "8"}]}'))

    def test_GET_to_packages_with_param_low_offset_and_limit(self):
        res = self.testapp.get('/api/v1/packages/?limit=2&offset=1')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": null, "next": "/api/v1/packages/?limit=2&offset=3", "total": 3, "limit": 2, "offset": "1"}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/2/", "id": 2, "issue_number": "8"}, {"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/3/", "id": 3, "issue_number": "8"}]}'))

    def test_GET_to_packages_with_param_low_limit_and_offset(self):
        res = self.testapp.get('/api/v1/packages/?limit=1&offset=2')

        self.assertEqual(json.loads(res.body), json.loads('{"meta": {"previous": "/api/v1/packages/?limit=1&offset=1", "next": "/api/v1/packages/?limit=1&offset=3", "total": 3, "limit": 1, "offset": "2"}, "objects": [{"article_title": "Construction of a recombinant adenovirus...", "tickets": [], "issue_year": 1995, "journal_title": "Associa... Brasileira", "journal_pissn": "0100-879X", "journal_eissn": "0100-879X", "issue_suppl_number": null, "attempts": [], "issue_suppl_volume": null, "issue_volume": "67", "resource_uri": "/api/v1/packages/3/", "id": 3, "issue_number": "8"}]}'))


class AttemptsAPITest(unittest.TestCase):

    def setUp(self):
        self.req = testing.DummyRequest()
        self.req.registry.settings = {'http_server': {'version': 'v1'}}
        self.req.db = ObjectStub()
        self.req.db.query = QueryStub
        self.req.db.query.model = AttemptStub

    def test_view_attempts(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'articlepkg_id': 1},
                    'total': 200,
                    'objects': [AttemptStub().to_dict(), AttemptStub().to_dict()]}

        self.req.params = {'limit': 20, 'offset': 0, 'articlepkg_id': 1}
        self.req.db.query.found = True

        self.assertEqual(
            gateway_server.attempts(self.req),
            expected)

    def test_view_attempts_no_result(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'articlepkg_id': 1},
                    'total': 200,
                    'objects': []}

        self.req.params = {'limit': 20, 'offset': 0, 'articlepkg_id': 1}
        self.req.db.query.found = False

        self.assertEqual(
            gateway_server.attempts(self.req),
            expected)

    def test_view_attempt(self):
        expected = AttemptStub().to_dict()

        self.req.db.query.found = True
        self.req.matchdict = {'id': 1}
        self.assertEqual(
            gateway_server.attempt(self.req),
            expected)

    def test_view_attempt_no_result(self):
        self.req.db.query.found = False
        self.req.matchdict = {'id': 1}

        self.assertIsInstance(
            gateway_server.attempt(self.req),
            HTTPNotFound
        )


class ArticlePkgAPITest(unittest.TestCase):

    def setUp(self):
        self.req = testing.DummyRequest()
        self.req.registry.settings = {'http_server': {'version': 'v1'}}
        self.req.db = ObjectStub()
        self.req.db.query = QueryStub
        self.req.db.query.model = ArticlePkgStub

    def test_view_packages(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'journal_title': 'Journal of ...'},
                    'total': 200,
                    'objects': [ArticlePkgStub().to_dict(), ArticlePkgStub().to_dict()]}

        self.req.params = {'limit': 20, 'offset': 0, 'journal_title': 'Journal of ...'}
        self.req.db.query.found = True

        self.assertEqual(
            gateway_server.list_package(self.req),
            expected)

    def test_view_packages_no_result(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'journal_title': 'Journal of ...'},
                    'total': 200,
                    'objects': []}
        self.req.params = {'limit': 20, 'offset': 0, 'journal_title': 'Journal of ...'}
        self.req.db.query.found = False

        self.assertEqual(
            gateway_server.list_package(self.req),
            expected)

    def test_view_package(self):
        expected = ArticlePkgStub().to_dict()

        self.req.db.query.found = True
        self.req.matchdict = {'id': 1}

        self.assertEqual(
            gateway_server.package(self.req),
            expected)

    def test_view_package_no_result(self):
        self.req.db.query.found = False
        self.req.matchdict = {'id': 1}

        self.assertIsInstance(
            gateway_server.attempt(self.req),
            HTTPNotFound
        )


class TicketAPITest(unittest.TestCase):

    def setUp(self):
        self.req = testing.DummyRequest()
        self.req.registry.settings = {'http_server': {'version': 'v1'}}
        self.req.db = ObjectStub()
        self.req.db.query = QueryStub
        self.req.db.query.model = TicketStub
        self.req.db.add = lambda doc: None
        self.req.db.commit = lambda: None

    def test_view_tickets(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'articlepkg_id': 1},
                    'total': 200,
                    'objects': [TicketStub().to_dict(), TicketStub().to_dict()]}

        self.req.params = {'limit': 20, 'offset': 0, 'articlepkg_id': 1}
        self.req.db.query.found = True

        self.assertEqual(
            gateway_server.list_ticket(self.req),
            expected)

    def test_view_tickets_no_result(self):
        expected = {'limit': 20,
                    'offset': 0,
                    'filters': {'articlepkg_id': 1},
                    'total': 200,
                    'objects': []}

        self.req.params = {'limit': 20, 'offset': 0, 'articlepkg_id': 1}
        self.req.db.query.found = False

        self.assertEqual(
            gateway_server.list_ticket(self.req),
            expected)

    def test_view_ticket(self):
        expected = TicketStub().to_dict()

        self.req.db.query.found = True
        self.req.matchdict = {'id': 1}

        self.assertEqual(
            gateway_server.ticket(self.req),
            expected)

    def test_view_ticket_no_result(self):
        self.req.db.query.found = False
        self.req.matchdict = {'id': 1}

        self.assertIsInstance(
            gateway_server.ticket(self.req),
            HTTPNotFound
        )

    def test_new_ticket_no_comments(self):
        self.req.POST = {
            'articlepkg_id': 3,
            'ticket_author': 'ticket.author@scielo.org',
            'title': 'Ticket ....',
        }

        self.req.db.commit = lambda: None
        result = gateway_server.new_ticket(self.req)

        self.assertIsInstance(
            result,
            HTTPCreated
        )

    def test_view_update_ticket_and_not_found_ticket(self):
        from balaio.models import Ticket

        self.req.db.query.model = Ticket
        self.req.db.query.found = False

        self.req.db.rollback = lambda: None

        self.req.matchdict = {'id': 1}
        self.req.POST = {
            'is_open': False,
        }
        self.assertIsInstance(
            gateway_server.update_ticket(self.req),
            HTTPNotFound
        )

    def test_new_ticket_with_comments(self):
        self.req.POST = {
            'articlepkg_id': 3,
            'message': 'Corrigir ....',
            'ticket_author': 'ticket.author@scielo.org',
            'title': 'Ticket ....',
        }

        self.req.db.commit = lambda: None
        result = gateway_server.new_ticket(self.req)

        self.assertIsInstance(
            result,
            HTTPCreated
        )

    def test_view_update_ticket_no_comment(self):
        from balaio.models import Ticket

        self.req.db.query.model = Ticket
        self.req.db.query.found = True

        self.req.db.rollback = lambda: None

        self.req.matchdict = {'id': 1}
        self.req.POST = {
            'is_open': False,
        }
        self.assertIsInstance(
            gateway_server.update_ticket(self.req),
            HTTPAccepted
        )

    def test_view_update_ticket_with_comment(self):
        from balaio.models import Ticket
        self.req.db.query.model = Ticket
        self.req.db.query.found = True

        self.req.db.rollback = lambda: None

        self.req.matchdict = {'id': 1}
        self.req.POST = {
            'comment_author': 'username',
            'message': '....',
            'is_open': True,
        }
        self.assertIsInstance(
            gateway_server.update_ticket(self.req),
            HTTPAccepted
        )

class QueryFiltersTest(unittest.TestCase):

    def test_get_query_filter(self):
        expected = {'journal_pissn': '0100-879X',
                    'journal_eissn': '0900-879X',
                    }

        request_params = {
                            'format': 'json',
                            'offset': 20,
                            'limit': 50,
                            'journal_pissn': '0100-879X',
                            'journal_eissn': '0900-879X',
                        }

        model = ArticlePkgStub

        self.assertEqual(
            expected,
            gateway_server.get_query_filters(model, request_params)
        )
