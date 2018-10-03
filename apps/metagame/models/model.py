import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Model(ndb.Model):
    name = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    user_id = ndb.StringProperty()

    def to_json(self):
        return ({
            u'key_id': str(self.key.id()),
            u'name': self.name,
            u'description': self.description,
            u'user_id': self.user_id,
        })

class ModelResponse(messages.Message):
    """ a model's data """
    key_id = messages.IntegerField(1)
    name = messages.StringField(2)
    description = messages.StringField(3)
    response_message = messages.StringField(4)
    response_successful = messages.BooleanField(50)

class ModelRequest(messages.Message):
    """ a model request """
    key_id = messages.StringField(1)
    name = messages.StringField(2)
    description = messages.StringField(3)

MODEL_RESOURCE = endpoints.ResourceContainer(
    ModelRequest
)


class ModelCollection(messages.Message):
    """ multiple Models """
    models = messages.MessageField(ModelResponse, 1, repeated=True)
    more = messages.BooleanField(2)
    cursor = messages.StringField(3)
    sort_order = messages.StringField(4)
    direction = messages.StringField(5)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class ModelCollectionPageRequest(messages.Message):
    """ a model collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

MODEL_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    ModelCollectionPageRequest
)
