import bpy
from bpy.props import StringProperty, FloatProperty, CollectionProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty # type: ignore
from bpy.types import Operator, Panel, PropertyGroup


class WheelSettingsProperties(PropertyGroup):
    # --ГЕОМЕТРИЯ--
    # -Колесо-
    wheel_radius: FloatProperty(
        name="Wheel Radius",
        default=5.0,
        min=0.1,
        soft_max=25
    )
    wheel_thickness: FloatProperty(
        name="Wheel Thickness",
        default=0.3,
        min=0.01,
        soft_max=1
    )
    wheel_start_angle: FloatProperty(
        name="Wheel Start Angle",
        default=0.0,
        min=-360.0,
        max=360.0,
        step=1,
        subtype='ANGLE'
    )
    # -Пины-
    pin_radius: FloatProperty(
        name="Pin Radius",
        default=0.1,
        min=0.0,
        soft_max=1.0
    )
    pin_height:FloatProperty(
        name="Pin Height",
        default=0.5,
        min=0.0,
        soft_max=5.0,
        step=5
    )
    #pin_frequency пока не используется, для нее нужно дописывать create_pins (потом сделаю если надо будет)
    pin_frequency: IntProperty(
        name="Pin Frequency",
        default=1,
        min=0,
        soft_max=5,
    )
    # -Радианы(spoke)-
    spoke_width: FloatProperty(
        name="Spoke Width",
        default=0.1,
        min=0.0,
        soft_max=1.0,
        step=5
    )
    # -Текст-
    text_alignment: EnumProperty(
        name="Text Alignment",
        description="Select the text aligment relative to the 'aligment point'",
        items=[
            ('LEFT', "Left", 'ALIGN_LEFT', 0),
            ('CENTER', "Center", 'ALIGN_CENTER', 1),
            ('RIGHT', "Right", 'ALIGN_RIGHT', 2),
        ],
        default='RIGHT'
    )
    alignment_point: FloatProperty(
        name="Aligment Point",
        subtype='FACTOR',
        default=0.96,
        min=0.0,
        max=1.0,
        step = 1
    )
    text_size: FloatProperty(
        name="Text Size",
        default=0.4,
        min=0.0,
        soft_max=1.5
    )
    text_thickness: FloatProperty(
        name="Text Thickness",
        default=0.05,
        min=0.001,
        soft_max=0.1
    )
    # -Стрелка-
    lenght_arrow: FloatProperty(
        name="Lenght Arrow",
        default=1.5,
        soft_min=0.1,
        soft_max=10
    )
    width_arrow: FloatProperty(
        name="Width Arrow",
        default=0.9,
        soft_min=0.1,
        soft_max=10
    )
    thickness_arrow: FloatProperty(
        name="Thickness Arrow",
        default=0.2,
        soft_min=0.01,
        soft_max=5
    )
    arrow_angle: FloatProperty(
        name="Arrow Start Angle",
        default=0,
        min=-360.0,
        max=360.0,
        step=1,
        subtype='ANGLE',
        unit='ROTATION'
    )
    dist_between_edge_tip: FloatProperty(
        name="The Distance between Edge the Wheel and Tip of Arrow",
        default=0.1,
        soft_min=0.0,
        soft_max=5
    )
    arrow_p_of_r: FloatProperty( # ARROW_C
        name="Point rotation of the Arror",
        default=0.5,
        soft_min=0.0,
        soft_max=5
    )
    # -Анимация-
    loop_seconds: FloatProperty(
        name="Loop Seconds",
        default=8,
        min=0,
        soft_max=60
    )
    fps: IntProperty(
        name="FPS",
        default=60,
        soft_min=12,
        soft_max=360,
    )
    # -Физика_стрелки-
    moment_of_inertia: FloatProperty( # PHYS_I
        name="Moment of Inertia",
        default=0.01,
        soft_min=0.0,
        soft_max=0.1,
        step=0.1
    )
    atten_coeff: FloatProperty( # PHYS_B
        name="Attenuation Coefficient",
        default=0.5,
        soft_min=0.0,
        soft_max=1.5
    )
    spring_stiffness: FloatProperty( # PHYS_K
        name="Spring Stiffness",
        default=15.0,
        soft_min=0.0,
        soft_max=30.0
    )
    substep_calculation: IntProperty( # PHYS_SUBSTEPS
        name="Substep Calculation Arrow Phys",
        default=10,
        min=0,
        soft_max=100,
        step=1
    )
        # --- Вычисляемые свойства (формулы) ---
    def set_default_properties(self):
        # Доступаемся к дефолтным значениям через self или сбрасываем явно
        self.property_unset("wheel_radius")
        self.property_unset("wheel_thickness")
        self.property_unset("wheel_start_angle")
        self.property_unset("pin_radius")
        self.property_unset("pin_height")
        #self.property_unset("pin_frequency") # пока не используется
        self.property_unset("spoke_width")
        self.property_unset("text_alignment")
        self.property_unset("alignment_point")
        self.property_unset("text_size")
        self.property_unset("text_thickness")
        self.property_unset("lenght_arrow")
        self.property_unset("width_arrow")
        self.property_unset("thickness_arrow")
        self.property_unset("arrow_angle")
        self.property_unset("dist_between_edge_tip")
        self.property_unset("arrow_p_of_r")
        self.property_unset("loop_seconds")
        self.property_unset("fps")
        self.property_unset("moment_of_inertia")
        self.property_unset("atten_coeff")
        self.property_unset("spring_stiffness")
        self.property_unset("substep_calculation")

class DICTIONARY_SECTOR(PropertyGroup):
    sector_name : StringProperty(
        name = 'Sector Name',
        default = 'New Sector'
    )
    sector_weight : FloatProperty(
        name = 'Sector Weight',
        default = 1.0,
        min = 0.0,
        soft_max = 100.0,
        precision = 2,
        step = 5
    )

classes = (
    DICTIONARY_SECTOR,
    WheelSettingsProperties,
)