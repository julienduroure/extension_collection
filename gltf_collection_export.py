import bpy

bl_info = {
    "name": "glTF Export Collection extension",
    "category": "Generic",
    "version": (0, 1, 0),
    "blender": (2, 93, 0),
    'location': 'File > Export > glTF 2.0',
    'description': 'Export collection extension',
    'tracker_url': "https://github.com/KhronosGroup/glTF-Blender-IO/issues/",  # Replace with your issue tracker
    'isDraft': False,
    'developer': "Julien Duroure",
    'url': 'http://julienduroure.com',
}

# glTF extensions are named following a convention with known prefixes.
# See: https://github.com/KhronosGroup/glTF/tree/master/extensions#about-gltf-extensions
# also: https://github.com/KhronosGroup/glTF/blob/master/extensions/Prefixes.md
glTF_extension_name = "EXT_collections"

# Support for an extension is "required" if a typical glTF viewer cannot be expected
# to load a given model without understanding the contents of the extension.
# For example, a compression scheme or new image format (with no fallback included)
# would be "required", but physics metadata or app-specific settings could be optional.
extension_is_required = False

class EXTCollectionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Include this extension in the exported glTF file.',
        default=True
        )

def register():
    bpy.utils.register_class(EXTCollectionProperties)
    bpy.types.Scene.EXTCollectionProperties = bpy.props.PointerProperty(type=EXTCollectionProperties)

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


def unregister():
    unregister_panel()
    bpy.utils.unregister_class(EXTCollectionProperties)
    del bpy.types.Scene.EXTCollectionProperties

class GLTF_PT_UserExtensionPanel(bpy.types.Panel):

    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_export_user_extensions"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

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


class glTF2ExportUserExtension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.EXTCollectionProperties

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if self.properties.enabled:
            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}
            gltf2_object.extensions[glTF_extension_name] = self.Extension(
                name=glTF_extension_name,
                extension={"collections": [c.name for c in blender_object.users_collection]},
                required=extension_is_required
            )

    def recursive_tree(self, collection):
        current = {}
        current['collection'] = collection.name
        current['children'] = [self.recursive_tree(c) for c in collection.children]
        return current

    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        if self.properties.enabled:
            if gltf2_scene.extensions is None:
                gltf2_object.extensions = {}

            # Generate collection tree
            tree = [self.recursive_tree(c) for c in blender_scene.collection.children]
            gltf2_scene.extensions[glTF_extension_name] = self.Extension(
                name=glTF_extension_name,
                extension={"tree": tree},
                required=extension_is_required
            )
