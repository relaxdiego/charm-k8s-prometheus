import logging

logger = logging.getLogger()

from ops.framework import (
    EventSource,
    Object,
    ObjectEvents,
    StoredState
)
from ops.charm import RelationEvent
from adapters.framework import FrameworkAdapter


class PrometheusNewClientEvent(RelationEvent):
    pass


class PrometheusEvents(ObjectEvents):
    new_client = EventSource(PrometheusNewClientEvent)


class PrometheusInterface(Object):
    on = PrometheusEvents()
    state = StoredState()

    def __init__(self, charm, relation_name):
        super().__init__(charm, relation_name)
        self.fw = FrameworkAdapter(self.framework)
        self.relation_name = relation_name
        self.fw.observe(charm.on[relation_name].relation_joined,
                        self.on_relation_joined)
        self.state.set_default(apps=[])

    def render_relation_data(self):
        logging.debug('render-relation-data in')
        for relation in self.model.relations[self.relation_name]:
            relation.data[self.model.unit]['prometheus-port'] = \
                str(self.framework.model.config['advertised-port'])
        logging.debug('render-relation-data out')

    def on_relation_joined(self, event):
        logging.debug("on-joined")
        if event.app not in self.state.apps:
            self.state.apps.append(event.app.name)
            logging.debug("emit new-client")
            self.on.new_client.emit(event.relation)
        self.render_relation_data()
