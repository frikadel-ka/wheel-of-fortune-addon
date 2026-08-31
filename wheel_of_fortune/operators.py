import bpy
from .utils import create_wheel, make_animation

class MESH_OT_reset_wheel_settings(bpy.types.Operator):
    """Сбросить параметры геометрии к значениям по умолчанию"""
    bl_idname = "wheel.reset_settings"  # Идентификатор оператора
    bl_label = "Reset settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Вызываем созданный метод прямо у настроек сцены
        context.scene.my_wheel_settings.set_default_properties()
        return {'FINISHED'}

class MESH_OT_make_animation(bpy.types.Operator):
    """Создать анимвцию колеса"""
    bl_idname = "wheel.make_animation"
    bl_label = "Make animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cfg = context.scene.my_wheel_settings
        
                # Собираем Python-словарь из коллекции
        sectors_dict = {
            item.sector_name: item.sector_weight 
            for item in context.scene.my_wheel_variants
        }

        make_animation(sectors_dict, cfg)

        return {'FINISHED'}

# ==========================================
# 2. ОПЕРАТОР (Кнопка действия)
# ==========================================
class MESH_OT_create_wheel(bpy.types.Operator):
    """Создать колесо"""
    bl_idname = "mesh.create_wheel"
    bl_label = "Create wheel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cfg = context.scene.my_wheel_settings

        # Собираем Python-словарь из коллекции
        sectors_dict = {
            item.sector_name: item.sector_weight 
            for item in context.scene.my_wheel_variants
        }
                
        create_wheel(context, sectors_dict, cfg)
        
        return {'FINISHED'}

class MESH_OT_add_sector(bpy.types.Operator):
    """Добавить новый сектор"""
    bl_idname = "wheel.add_sector"
    bl_label = "Add Sector"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # Добавляем новый элемент в коллекцию
        item = scene.my_wheel_variants.add()
        item.sector_name = f"Sector {len(scene.my_wheel_variants)}"
        item.sector_weight = 1.0

        # Переставляем выделение на свежесозданный элемент
        scene.my_wheel_variants_index = len(scene.my_wheel_variants) - 1

        return {'FINISHED'}

class MESH_OT_remove_sector(bpy.types.Operator):
    """Удалить выбранный сектор"""
    bl_idname = "wheel.remove_sector"
    bl_label = "Remove Sector"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Кнопка будет активна только если в коллекции есть хотя бы один элемент
        return len(context.scene.my_wheel_variants) > 0

    def execute(self, context):
        scene = context.scene
        index = scene.my_wheel_variants_index
        # Удаляем активный элемент
        scene.my_wheel_variants.remove(index)
        # Корректируем индекс, чтобы он не вышел за пределы массива после удаления
        scene.my_wheel_variants_index = min(max(0, index - 1), len(scene.my_wheel_variants) - 1)
        return {'FINISHED'}

classes = (
    MESH_OT_reset_wheel_settings,
    MESH_OT_add_sector,
    MESH_OT_remove_sector,
    MESH_OT_create_wheel,
    MESH_OT_make_animation,
)