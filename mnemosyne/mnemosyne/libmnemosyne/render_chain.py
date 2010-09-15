#
# render_chain.py <Peter.Bienstman@UGent.be>
#

import copy

from mnemosyne.libmnemosyne.component import Component


class RenderChain(Component):

    """A RenderChain details the operations needed to get from the raw data
    in a card to a representation of its question and answer, in a form either
    suitable for displaying in a browser, or exporting to a text file, ... .

    First the raw data is sent through Filters, which perform operations which
    can be useful for many card types, like expanding relative paths.

    Then this data is assembled in the right order in a Renderer, which can be
    card type specific.

    'filters': list of Filter classes
    'renderers': list or Renderer classes

    Plugins can add Filters or Renderers for a new card type to a chain at run
    time.

    """

    component_type = "render_chain"
    id = "default"

    filters = []
    renderers = []

    def __init__(self, component_manager):
        # To have an nice syntax when defining renderers, we do the
        # instantiation here.
        Component.__init__(self, component_manager)
        self._filters = []
        for filter in self.filters:
            self._filters.append(filter(component_manager))
        self._renderers = []
        self._renderer_for_card_type = {}
        for renderer in self.renderers:
            renderer = renderer(component_manager)
            self._renderers.append(renderer)
            self._renderer_for_card_type[renderer.used_for] = renderer

    def register_filter(self, filter, in_front=False):

        """'filter' should be a class, not an instance."""
        
        filter = filter(self.component_manager)        
        if not in_front:
            self._filters.append(filter)
        else:
            self._filters.insert(0, filter)

    def register_renderer(self, renderer):

        """'renderer' should be a class, not an instance."""
        
        renderer = renderer(self.component_manager)
        self._renderer_for_card_type[renderer.used_for] = renderer

    def renderer_for_card_type(self, card_type):
        if card_type not in self._renderer_for_card_type:
            return self._renderer_for_card_type[None]
        else:
            return self._renderer_for_card_type[card_type]            

    def render_question(self, card, **render_args):
        fields = card.fact_view.q_fields
        return self._render_fields(card, fields, **render_args)
    
    def render_answer(self, card, **render_args):
        fields = card.fact_view.a_fields
        return self._render_fields(card, fields, **render_args)
    
    def _render_fields(self, card, fields, **render_args):
        # Note that the filters run only on the data, not on the full content
        # generated by the renderer, which would be much slower.
        data = copy.copy(card.card_type.fact_data(card))
        for field in fields:
            for filter in self._filters:
                data[field] = filter.run(data[field], **render_args)
        renderer = self.renderer_for_card_type(card.card_type)
        return renderer.render_fields(data, fields,
            card.card_type, **render_args)
