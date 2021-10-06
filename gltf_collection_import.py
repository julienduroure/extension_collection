import bpy

bl_info = {
    "name": "glTF Import Collection extension",
    "category": "Generic",
    "version": (0, 1, 0),
    "blender": (2, 93, 0),
    'location': 'File > Import > glTF 2.0',
    'description': 'glTF Export Collection extension',
    'tracker_url': "https://github.com/KhronosGroup/glTF-Blender-IO/issues/",  # Replace with your issue tracker
    'isDraft': False,
    'developer': "(Your name here)", # Replace this
    'url': 'https://your_url_here',  # Replace this
}

glTF_extension_name = "EXT_collections"

class ExampleImporterExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Run this extension while importing glTF file.',
        default=True
        )

    test: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Test.',
        default=True
        )


class glTF2ImportUserExtension:

    def __init__(self):
        self.properties = bpy.context.scene.ExampleImporterExtensionProperties

        self.collections = {}

    def gather_import_node_after_hook(self, vnode, gltf_node, blender_object):
        if self.properties.enabled:
            if gltf_node.extensions and "EXT_collections" in gltf_node.extensions.keys():
                for c in gltf_node.extensions['EXT_collections']['collections']:
                    bpy.data.collections[self.collections[c]].objects.link(blender_object)
                    # remove from master collections
                    bpy.context.scene.collection.objects.unlink(blender_object)

    def recursive_tree_create(self, blender_scene, treenode, parent_coll):
        created_coll = bpy.data.collections.new(treenode['collection'])
        self.collections[treenode['collection']] = created_coll.name
        if parent_coll is None:
            blender_scene.collection.children.link(created_coll)
        else:
            parent_coll.children.link(created_coll)

        for c in treenode['children'] if 'children' in treenode.keys() else []:
            self.recursive_tree_create(blender_scene, c, created_coll)

    def gather_import_scene_before_hook(self, gltf_scene, blender_scene):
        if self.properties.enabled:
            if gltf_scene.extensions and "EXT_collections" in gltf_scene.extensions.keys():
                for c in gltf_scene.extensions["EXT_collections"]['tree']:
                    print("-->", c)
                    self.recursive_tree_create(blender_scene, c, None)

class GLTF_PT_UserExtensionPanel(bpy.types.Panel):

    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_import_user_extensions"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        print(operator.bl_idname)
        return operator.bl_idname == "IMPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.EXTCollectionProperties
        self.layout.prop(props, 'enabled')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.EXTCollectionProperties
        layout.active = props.enabled

        box = layout.box()
        box.label(text=glTF_extension_name)

        props = bpy.context.scene.ExampleExtensionProperties
        layout.prop(props, 'test', text="Test")

def register_panel():
    # Register the panel on demand, we need to be sure to only register it once
    # This is necessary because the panel is a child of the extensions panel,
    # which may not be registered when we try to register this extension
    try:
        bpy.utils.register_class(GLTF_PT_UserExtensionPanel)
    except Exception:
        print("Error register panel")
        pass

    # If the glTF exporter is disabled, we need to unregister the extension panel
    # Just return a function to the exporter so it can unregister the panel
    return unregister_panel


def unregister_panel():
    # Since panel is registered on demand, it is possible it is not registered
    try:
        bpy.utils.unregister_class(GLTF_PT_UserExtensionPanel)
    except Exception:
        pass

def register():
    bpy.utils.register_class(ExampleImporterExtensionProperties)
    bpy.types.Scene.ExampleImporterExtensionProperties = bpy.props.PointerProperty(type=ExampleImporterExtensionProperties)

def unregister():
    unregister_panel()
    bpy.utils.unregister_class(ExampleImporterExtensionProperties)
    del bpy.types.Scene.ExampleImporterExtensionProperties
