# Copyright (C) 2026 Frikadel_ka

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


'''
Аддон для генерации колеса фортуны

Функционал: 
-вводишь словарь или лист с выборами
-настраиваешь геометию колеса, текста и стрелки (радиус и толщина колеса, пины(stick), "радианы"(spoke), расположение и масштаб текста, вся геометрия стрелки вплоть до своей)
-настраиваешь анимацию
'''


bl_info = {
    "name": "Generated Wheel of Fortune",
    "author": "Frikadel_ka",
    "description": "This is an addon that creates and animates a wheel of fortune with many changeable parameters.",
    "blender": (4, 3, 0),
    "version": (0, 0, 1),
    "location": "View3D > Sidebar > Wheel Tool",
    "warning": "",
    "doc_url": "https://github.com/frikadel-ka/wheel-of-fortune-addon#readme",
    "tracker_url": "https://github.com/frikadel-ka/wheel-of-fortune-addon/issues",
    "category": "Generic",
}


from .wheel_of_fortune import ui
from .wheel_of_fortune.translations import translations_dict
from bpy.props import StringProperty, FloatProperty, CollectionProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty # type: ignore
import bpy #type: ignore

from .wheel_of_fortune import operators, properties
# import mathutils
classes = (
    *properties.classes,
    *operators.classes,
    *ui.classes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # 2. Привязываем коллекцию к объекту Сцены
    bpy.types.Scene.my_wheel_variants = CollectionProperty(
        type=properties.DICTIONARY_SECTOR,
        name="Wheel sectors",
        description="List of all sectors and their weights"
    )

    # Индекс выделенного элемента (необходим для работы UIList)
    bpy.types.Scene.my_wheel_variants_index = IntProperty(
        name="Index of the active sector",
        default=0
    )

    bpy.types.Scene.my_wheel_settings = PointerProperty(
        type=properties.WheelSettingsProperties,
        name="Wheel Settings"
    )

    bpy.app.translations.register(__name__, translations_dict)

def unregister():
    del bpy.types.Scene.my_wheel_variants
    del bpy.types.Scene.my_wheel_variants_index
    del bpy.types.Scene.my_wheel_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.translations.unregister(__name__)

if __name__ == "__main__":
    register()