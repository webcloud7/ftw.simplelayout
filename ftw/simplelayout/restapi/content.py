from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.interfaces import ISimplelayoutLayer
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.serializer.site import SerializeSiteRootToJson
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
import json


class PersistenceDecoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PersistentMapping):
            return dict(obj)
        elif isinstance(obj, PersistentList):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def _sl_blocks_query(context):
    return {
        'path': {'depth': 1, 'query': '/'.join(context.getPhysicalPath())},
        'object_provides': ISimplelayoutBlock.__identifier__,
    }


def enrich_with_simplelayout(context, result):

    result['simplelayout'] = json.loads(json.dumps(
        IPageConfiguration(context).load(),
        cls=PersistenceDecoder)
    )

    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(_sl_blocks_query(context))

    blocks = getMultiAdapter(
        (brains, context.REQUEST), ISerializeToJson
    )(fullobjects=True)["items"]
    result['slblocks'] = {block['UID']: block for block in blocks}


@implementer(ISerializeToJson)
@adapter(ISimplelayout, Interface)
class SimplelayoutSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SimplelayoutSerializer, self).__call__(version=version, include_items=include_items)
        enrich_with_simplelayout(self.context, result)
        return result


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot, ISimplelayoutLayer)
class SimplelayoutSerializeSiteRootToJson(SerializeSiteRootToJson):
    def __call__(self, version=None):
        result = super(SimplelayoutSerializeSiteRootToJson, self).__call__(version=version)
        enrich_with_simplelayout(self.context, result)
        return result


@implementer(ISerializeToJson)
@adapter(ISimplelayoutBlock, Interface)
class SimplelayoutBlockSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SimplelayoutBlockSerializeToJson, self).__call__(version=version, include_items=include_items)

        result['block-configuration'] = {}
        properties = queryMultiAdapter((self.context, self.request), IBlockProperties)

        result['block-configuration'].update(json.loads(json.dumps(
            properties.get_storage(),
            cls=PersistenceDecoder)
        ))

        configuration = IBlockConfiguration(self.context)
        result['block-configuration'].update(json.loads(json.dumps(
            configuration.load(),
            cls=PersistenceDecoder)
        ))

        if IDexterityContainer.providedBy(self.context):
            result['items'] = SerializeFolderToJson(self.context, self.request)()['items']

        return result


@adapter(IRichText, IDexterityContent, ISimplelayoutLayer)
class CustomRichttextFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        value = self.get_value()
        result = json_compatible(value, self.context)
        if value:
            result[u'raw'] = json_compatible(value.raw)
        return result
