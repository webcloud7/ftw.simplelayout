from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from unittest2 import TestCase
import json


class TestAddableBlocksView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestAddableBlocksView, self).setUp()

    def test_addable_blocks_view(self):
        page = create(Builder('sl content page'))

        view = page.restrictedTraverse('@@addable-blocks.json')

        allowed_block_types = [item[0]
                               for item in view.addable_blocks()]
        result = list(allowed_block_types)
        result.sort()

        self.assertEquals(
            ['ftw-simplelayout-listingblock',
             'ftw-simplelayout-textblock'],
            result)

    def test_addable_blocks_json(self):
        page = create(Builder('sl content page'))
        view = page.restrictedTraverse('@@addable-blocks.json')
        addable_types_json = json.loads(view())

        self.maxDiff = None

        self.assertDictEqual(
            {u'title': u'ListingBlock',
             u'description': u'Use this block for File or listings or galleries',
             u'contentType': u'ftw-simplelayout-listingblock',
             u'actions': {u'edit': {u'description': u'Edit block', u'name': u'Edit'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.ListingBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[u'ftw-simplelayout-listingblock'])

        self.assertDictEqual(
            {u'title': u'TextBlock',
             u'description': u'Use this block for text and/or one image.',
             u'contentType': u'ftw-simplelayout-textblock',
             u'actions': {u'edit': {u'description': u'Edit block', u'name': u'Edit'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.TextBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[u'ftw-simplelayout-textblock'])
