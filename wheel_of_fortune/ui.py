import bpy

class WHEEL_UL_sectors(bpy.types.UIList):
    """Пользовательский список для отрисовки секторов колеса"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # item - это текущий элемент из scene.my_wheel_variants
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            spl = row.split(align=True)
            spl.prop(item, "sector_name", text="")
            spl.prop(item, "sector_weight", text="Weight")

# --- ГЛАВНАЯ ПАНЕЛЬ ---
class VIEW3D_PT_wheel_main_panel(bpy.types.Panel):
    """Кнопки запекания геометрии и анимции"""
    bl_idname = "VIEW3D_PT_wheel_main_panel" # Уникальный ID для привязки саб-панелей
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Wheel Tool' 
    bl_label = "Wheel Generator"

    def draw(self, context):
        layout = self.layout
        #text_create_wheel = bpy.app.translations.pgettext("Create wheel")
        layout.operator("mesh.create_wheel", icon='MESH_CYLINDER', text="Create wheel")

        layout.separator()

        text_make_animation = bpy.app.translations.pgettext("Make animation")
        layout.operator("wheel.make_animation", icon='ACTION', text=text_make_animation)

class VIEW3D_PT_wheel_properties_subpanel(bpy.types.Panel):
    """Параметры генерации и анимции"""
    bl_idname = "VIEW3D_PT_wheel_properties_subpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Wheel Tool'
    
    bl_parent_id = "VIEW3D_PT_wheel_main_panel" # Ссылка на главную панель
    bl_label = "Properties"

    def draw(self, context):
        layout = self.layout
        #box = layout.box()

        layout.use_property_split = True
        
        # Делаем колонки компактными по вертикали (как на скриншоте)
        layout.use_property_decorate = False  # Отключает иконки ключевых кадров (точки справа), если они не нужны

        cfg = context.scene.my_wheel_settings

        text_set_default = bpy.app.translations.pgettext("Set default")
        layout.operator("wheel.reset_settings", text=text_set_default, icon='FILE_REFRESH')

        layout.separator()

        box = layout.box()
        box.label(text="Wheel", icon='MESH_CYLINDER')
        box.prop(cfg, "wheel_radius")
        box.prop(cfg, "wheel_thickness")
        box.prop(cfg, "wheel_start_angle")

        box = layout.box()
        box.label(text="Arrow", icon='TRIA_LEFT')
        box.prop(cfg, "lenght_arrow")
        box.prop(cfg, "width_arrow")
        box.prop(cfg, "thickness_arrow")
        box.prop(cfg, "arrow_angle")
        box.prop(cfg, "dist_between_edge_tip")
        box.prop(cfg, "arrow_p_of_r")

        box = layout.box()
        box.label(text="Text", icon='FONT_DATA')
        row = box.row(align=True)
        row.prop(cfg, "text_alignment", expand=True)
        box.prop(cfg, "alignment_point")
        box.prop(cfg, "text_size")
        #box.prop(cfg, "text_distance")
        box.prop(cfg, "text_thickness")

        box = layout.box()
        box.label(text="Pin", icon='PINNED')
        box.prop(cfg, "pin_radius")
        box.prop(cfg, "pin_height")

        box = layout.box()
        box.label(text="Spoke", icon='REMOVE')
        box.prop(cfg, "spoke_width")

        layout.separator()

        box = layout.box()
        box.label(text="Animation", icon='ACTION')
        box.prop(cfg, "start_frame")
        box.prop(cfg, "loop_seconds")
        box.prop(cfg, "fps")
        box.prop(cfg, "num_of_revol")
        box.prop(cfg, "rand_or_predet")
        box.prop(cfg, "resulting_sector")
        box.prop(cfg, "resulting_angle")
        box.prop(cfg, "accident_diff_angle")

        box = layout.box()
        box.label(text="Arrow physics", icon='PHYSICS')
        box.prop(cfg, "moment_of_inertia")
        box.prop(cfg, "atten_coeff")
        box.prop(cfg, "spring_stiffness")
        box.prop(cfg, "substep_calculation")
# --- САБ-ПАНЕЛЬ СЕКТОРОВ (СЛОВАРЯ) ---
class VIEW3D_PT_wheel_sectors_subpanel(bpy.types.Panel):
    """Панель элементов словаря"""
    bl_idname = "VIEW3D_PT_wheel_sectors_subpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Wheel Tool'
    
    bl_parent_id = "VIEW3D_PT_wheel_main_panel" # Ссылка на главную панель
    bl_label = "Sectors (Dictionary)"
    # bl_options = {'DEFAULT_CLOSED'} # Раскомментировать, чтобы панель была свернута по умолчанию если надо

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()

        row.template_list(
            "WHEEL_UL_sectors", "", 
            scene, "my_wheel_variants", 
            scene, "my_wheel_variants_index"
        )

        # Колонка с кнопками справа
        col = row.column(align=True)
        col.operator("wheel.add_sector", icon='ADD', text="")
        col.operator("wheel.remove_sector", icon='REMOVE', text="")

classes = (
    WHEEL_UL_sectors,
    VIEW3D_PT_wheel_main_panel,
    VIEW3D_PT_wheel_properties_subpanel,
    VIEW3D_PT_wheel_sectors_subpanel,
)