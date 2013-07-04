# coding: utf-8
import ConfigParser
import urllib2
import urllib
import sys
import xml.etree.ElementTree as etree
import json
from StringIO import StringIO

import plumber

# futurely scieloapi is package
import utils
from utils import SingletonMixin, Configuration
import notifier
from notifier import Request
from models import Attempt


config = Configuration.from_env()

STATUS_OK = 'ok'
STATUS_WARNING = 'w'
STATUS_ERROR = 'e'


def etree_nodes_value(etree, xpath):
    """
    Returns text of a given ``xpath`` of ``etree``
    """
    return '\n'.join([node.text for node in etree.findall(xpath)])


class Manager(object):
    """
    Interface for SciELO API
    """
    _main = 'MAIN/QUERY?username=USERNAME&api_key=API_KEY&format=json'

    def __init__(self, api_url='http:/????', username='', api_key=''):
        super(Manager, self).__init__()
        self.api_params['USERNAME'] = username
        self.api_params['API_KEY'] = api_key
        self.api_params['MAIN'] = api_url

        for key, param in self.api_params.items():
            self._main = self._main.replace(key, param)

    def do_query(self, query, params={}):
        """
        Consulta SciLO Manager API
        Returns JSON
        """
        try:
            r = urllib2.open(self._main.replace('QUERY', query) + '&'.join([key + '=' + value for key, value in params.items()])).read()
        except:
            r = '{}'
        return json.load(StringIO(r))

    def _item_id(self, query, data_label, match_value):
        """
        Find in all an item which ``data_label`` has a value that matches ``match_value``
        (esse metodo seria desnecessario se na api estivesse search)
        Returns item id
        """
        item_id = None
        all_items = json.load(self.do_query(query))

        meta = all_items.get('meta', {})
        total = meta.get('total_count', 0)
        offset = meta.get('offset', 0)
        limit = meta.get('limit', 0)

        found = [o for o in all_items.get('objects', {}) if o.get(data_label, '') == match_value]
        while found is [] and offset < total:
            offset += limit
            all_items = json.load(self.do_query(query, {'offset': offset}))
            found = [o for o in all_items.get('objects', {}) if o.get(data_label, '') == match_value]

        if not found is []:
            item_id = found[0].get('id', None)
        return item_id

    def journal(self, value, attribute='id'):
        item_id = value if attribute == 'id' else self._item_id('journals', attribute, value)
        return self.do_query('journals/' + item_id + '/')


class ValidationPipe(plumber.Pipe):
    """
    Specialized Pipe which validates the data and notifies the result
    """
    def __init__(self, data, manager_dep=Manager, notifier_dep=notifier.Notifier):
        super(ValidationPipe, self).__init__(data)
        self._notifier = notifier_dep()
        self._manager = manager_dep()

    def transform(self, data):
        # data = (Attempt, PackageAnalyzer)
        # PackagerAnalyzer.xml
        attempt, package_analyzer = data

        result_status, result_description = self.validate(package_analyzer)

        message = {
            'stage': self._stage_,
            'status': result_status,
            'description': result_description,
        }

        self._notifier.validation_event(message)

        return data

    def compare_registered_data_and_xml_data(self, package_analyzer):
        """
        Compare registered data in Manager to data in XML
        Returns [status, description]
        """
        registered_data = self._registered_data(package_analyzer)
        xml_data = self._xml_data(package_analyzer)

        if registered_data is None and xml_data == '':
            status, description = [STATUS_OK, xml_data]
        elif registered_data is None:
            status, description = [STATUS_ERROR, self._registered_data_label + ' not found in Manager']
        elif xml_data == '':
            status, description = [STATUS_ERROR, self._xml_data_label + ' not found in XML']
        elif xml_data == registered_data:
            status, description = [STATUS_OK, xml_data]
        else:
            status = STATUS_ERROR
            description = 'Data in XML and Manager do not match.' + '\n' + 'Data in Manager: ' + registered_data + '\n' + 'Data in XML: ' + xml_data
        return [status, description]


# Pipes to validate journal data
class AbbrevJournalTitleValidationPipe(ValidationPipe):
    """
    Check if journal-meta/abbrev-journal-title[@abbrev-type='publisher'] is the same as registered in Manager
    """
    def validate(self, package_analyzer):
        self._registered_data_label = 'title_iso'
        self._xml_data_label = './/journal-meta/abbrev-journal-title[@abbrev-type="publisher"]'
        return self.compare_registered_data_and_xml_data(package_analyzer)

    def _xml_data(self, package_analyzer):
        return etree_nodes_value(package_analyzer.xml, self._xml_data_label)

    def _registered_data(self, package_analyzer):
        return self._manager.journal(package_analyzer.meta['journal_title'], 'title').get(self._registered_data_label, None)


class NLMJournalTitleValidationPipe(ValidationPipe):
    """
    Check if journal-meta/journal-id[@journal-id-type='nlm-ta'] is the same as registered in Manager
    """
    def validate(self, package_analyzer):
        self._registered_data_label = 'medline_title'
        self._xml_data_label = './/journal-meta/journal-id[@journal-id-type="nlm-ta"]'
        return self.compare_registered_data_and_xml_data(package_analyzer)

    def _xml_data(self, package_analyzer):
        return etree_nodes_value(package_analyzer.xml, self._xml_data_label)

    def _registered_data(self, package_analyzer):
        return self._manager.journal(package_analyzer.meta['journal_title'], 'title').get(self._registered_data_label, None)

# Pipes to validate issue data


# Pipes to validate article data
class FundingCheckingPipe(ValidationPipe):
    """
    Check the absence/presence of funding-group and ack in the document

    funding-group is a mandatory element only if there is contract or project number
    in the document. Sometimes this information comes in Acknowledgments section.
    Return
    [STATUS_ERROR, ack]           if no founding-group, but Acknowledgments (ack) has number
    [STATUS_OK, founding-group]   if founding-group is present
    [STATUS_OK, ack]              if no founding-group, but Acknowledgments has no numbers
    [STATUS_WARNING, 'no funding-group and no ack'] if founding-group and Acknowledgments (ack) are absents
    """
    _stage_ = 'funding-group'

    def validate(self, package_analyzer):

        data = package_analyzer.xml

        funding_nodes = data.findall('.//funding-group')

        status, description = [STATUS_OK, etree.tostring(funding_nodes[0])] if funding_nodes != [] else [STATUS_WARNING, 'no funding-group']
        if not status == STATUS_OK:
            ack_node = data.findall('.//ack')
            description = etree.tostring(ack_node[0]) if ack_node != [] else 'no funding-group and no ack'
            status = STATUS_ERROR if self._contains_number(description) else STATUS_OK if description != 'no funding-group and no ack' else STATUS_WARNING
        return [status, description]

    def _contains_number(self, text):
        # if text contains any number
        return any((True for n in xrange(10) if str(n) in text))


ppl = plumber.Pipeline(FundingCheckingPipe)

if __name__ == '__main__':
    messages = utils.recv_messages(sys.stdin, utils.make_digest)
    try:
        results = [msg for msg in ppl.run(messages)]
    except KeyboardInterrupt:
        sys.exit(0)
