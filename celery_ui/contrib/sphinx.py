from __future__ import absolute_import
import os
from docutils import nodes
from sphinx import addnodes


DEBUG = False

def warn(msg):
    print 'WARNING: %s' % msg


class CeleryTaskTranslator(nodes.NodeVisitor):

    def __init__(self, *args, **kwargs):
        nodes.NodeVisitor.__init__(self, *args, **kwargs)

        self.indent = 0
        self.remove_indents = set()

        self.tasks = []
        self.current_task = None

        self.swallow_text = False

        self.in_arguments = False
        self.args_in_list = False
        self.in_return_type = False

    def encode(self, text):
        """Encode special characters in `text` & return."""
        # @@@ A codec to do these and all other HTML entities would be nice.
        text = unicode(text)
        return text.translate({
            ord('&'): u'&amp;',
            ord('<'): u'&lt;',
            ord('"'): u'&quot;',
            ord('>'): u'&gt;',
            ord('@'): u'&#64;', # may thwart some address harvesters
            # TODO: convert non-breaking space only if needed?
            0xa0: u'&nbsp;'}) # non-breaking space

    debug_nodes = set([])
    def dispatch_visit(self, node):
        node_name = node.__class__.__name__
        if DEBUG and node_name in self.debug_nodes:
            print ' ' * self.indent + node_name
            self.indent += 4

        return nodes.NodeVisitor.dispatch_visit(self, node)

    def dispatch_departure(self, node):
        node_name = node.__class__.__name__
        if node_name in self.debug_nodes:
            self.indent -= 4

        return nodes.NodeVisitor.dispatch_departure(self, node)

    def __getattr__(self, name):
        if name.find('visit_') == 0 and not hasattr(self, name):
            pass

        elif name.find('depart_') == 0 and not hasattr(self, name):
            pass

        return nodes.NodeVisitor.__getattr__(self, name)

    def visit_desc(self, node):
        self.current_task = {}

    def depart_desc(self, node):
        self.tasks.append(self.current_task)

    def visit_desc_signature(self, node):
        self.current_task['module_name'] = node.get('module')
        self.current_task['fullname'] = node.get('fullname')

    def depart_desc_signature(self, node):
        pass

    def visit_desc_annotation(self, node):
        assert len(node.children) == 1
        assert ''.join(map(str, node.children)) == '(task)'
        self.swallow_text = True

    def depart_desc_annotation(self, node):
        self.swallow_text = False

    def visit_Text(self, node):
        if self.swallow_text:
            pass
        else:
            text = node.astext()
            encoded = self.encode(text)
            warn('unhandled Text node: %s' % encoded)

    def depart_Text(self, node):
        pass

    def visit_desc_addname(self, node):
        assert len(node.children) == 1
        assert ''.join(map(str, node.children)) == self.current_task['module_name'] + '.'
        self.swallow_text = True

    def depart_desc_addname(self, node):
        self.swallow_text = False

    def visit_desc_name(self, node):
        assert len(node.children) == 1
        assert ''.join(map(str, node.children)) == self.current_task['fullname']
        self.swallow_text = True

    def depart_desc_name(self, node):
        self.swallow_text = False

    def visit_desc_parameterlist(self, node):
        self.swallow_text = True

    def depart_desc_parameterlist(self, node):
        self.swallow_text = False

    def visit_desc_parameter(self, node):
        # desc_parameter is a boiled down version of field so skip them
        pass

    def depart_desc_parameter(self, node):
        pass

    def visit_desc_content(self, node):
        description_nodes = []
        for c in node.children:
            assert isinstance(c, (nodes.paragraph, nodes.field_list))

            if isinstance(c, nodes.paragraph):
                description_nodes.append(c)
        text = ''.join(map(lambda n: n.astext(), description_nodes))
        self.current_task['description'] = self.encode(text)

    def depart_desc_content(self, node):
        pass

    def visit_paragraph(self, node):
        #text = node.astext()
        #encoded_paragraph = self.encode(text)
        self.swallow_text = True

    def depart_paragraph(self, node):
        self.swallow_text = False

    def visit_field_list(self, node):
        self.current_task['fields'] = []

    def depart_field_list(self, node):
        pass

    def visit_field(self, node):
        # if there are multiple arguments, the hierarchy looks like
        # this and list_item contains the arg info
        #field
        #    field_name
        #    field_body
        #        list_item
        #        list_item

        # if there's a single argument, field_body contains the arg info
        #field
        #    field_name
        #    field_body

        pass

    def depart_field(self, node):
        # these should have been set in field_name
        self.in_arguments = False
        self.in_return_type = False
        self.in_returns = False

    def visit_field_name(self, node):
        text = node.astext()
        if text == 'Parameters':
            self.in_arguments = True
        elif text == 'Returns':
            self.in_returns = True
        elif text == 'Return type':
            self.in_return_type = True
        else:
            warn('unknown field_name: %s' % text)

        self.swallow_text = True

    def depart_field_name(self, node):
        self.swallow_text = False

    def extract_arg_info(self, node):
        text = node.astext()
        start = text.find(' -- ')
        assert start > -1

        argument = {}
        argument['description'] = self.encode(text[start+4:])

        for subnode in node.traverse():
            if isinstance(subnode, nodes.strong):
                argument['name'] = self.encode(subnode.astext())
            elif isinstance(subnode, nodes.emphasis):
                argument['type'] = self.encode(subnode.astext())

        self.current_task['fields'].append(argument)

    def visit_field_body(self, node):
        text = node.astext()

        if self.in_arguments:
            if len(node.children) == 1 and isinstance(node.children[0], nodes.bullet_list):
                self.args_in_list = True
            else:
                self.extract_arg_info(node)

        elif self.in_returns:
            self.current_task['returns'] = self.encode(text)

        elif self.in_return_type:
            self.current_task['return_type'] = self.encode(text)

        else:
            warn('unknown field_body: %s' % text)

        self.swallow_text = True

    def depart_field_body(self, node):
        self.swallow_text = False

        self.args_in_list = False

    def visit_list_item(self, node):
        if self.in_arguments and self.args_in_list:
            self.extract_arg_info(node)

    def depart_list_item(self, node):
        pass

    def visit_only(self, node):
        # used by viewcode extension
        self.swallow_text = True

    def depart_only(self, node):
        self.swallow_text = False

    def visit_inline(self, node):
        # used by viewcode extension
        self.swallow_text = True

    def depart_inline(self, node):
        self.swallow_text = False

    def visit_literal_strong(self, node):
        #TODO figure out where this comes from
        pass

    def depart_literal_strong(self, node):
        pass

    def visit_strong(self, node):
        pass

    def depart_strong(self, node):
        pass

    def visit_pending_xref(self, node):
        pass

    def depart_pending_xref(self, node):
        pass

    def visit_emphasis(self, node):
        pass

    def depart_emphasis(self, node):
        pass

    def visit_bullet_list(self, node):
        pass

    def depart_bullet_list(self, node):
        pass


def doctree_read(app, doctree):
    visitor = CeleryTaskTranslator(doctree)

    for objnode in doctree.traverse(addnodes.desc):
        if objnode['objtype'] == 'task':
            objnode.walkabout(visitor)

    env = app.builder.env

    if not hasattr(env, '_celery_tasks'):
        env._celery_tasks = {}

    if visitor.tasks:
        key = visitor.tasks[0]['module_name']
        env._celery_tasks[key] = visitor.tasks


#TODO it might make sense to move the visitor entry point
# here instead of doctree_read, but it's not clear if the doctree
# is available in this event...
def source_read(app, docname, source_text):
    pass


def collect_pages(app):
    env = app.builder.env

    if not hasattr(env, '_celery_tasks'):
        return

    celery_tasks = env._celery_tasks
    #delattr(env, '_celery_tasks')

    STATIC_PREFIX = os.environ.get('CELERY_UI_STATIC_PREFIX', 'static')

    pagename = 'celery_tasks'
    template = 'celeryui.html'
    context = {
        'STATIC_PREFIX': STATIC_PREFIX,
        'task_lists': celery_tasks
    }

    if DEBUG:
        print 'Tasks being sent to template:'
        for module_name, task_list in celery_tasks.items():
            print module_name
            for task in task_list:
                print task
    yield (pagename, context, template)


def setup(app):
    app.connect('doctree-read', doctree_read)
    app.connect('source-read', source_read)
    app.connect('html-collect-pages', collect_pages)


#class MyHTMLBuilder(Builder):
#    name = 'celery'
#    format = 'celery'
#    out_suffix = '.html'
#    allow_parallel = True
#
#    def init(self):
#        self.translator_class = MyHTMLTranslator
#
#    def prepare_writing(self, docnames):
#        self.docwriter = MyHTMLWriter(self)
#
#    def finish(self):
#        pass
#
#
#class MyHTMLWriter(Writer):
#    def __init__(self, builder):
#        Writer.__init__(self)
#        self.builder = builder
#
#    def translate(self):
#        self.visitor = self.builder.translator_class(self.builder, self.document)
#
#        for objnode in self.document.traverse(addnodes.desc):
#            if objnode['objtype'] != 'task':
#                continue
#            objnode.walkabout(self.visitor)
