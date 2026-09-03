import random
import time
import math
import bmesh
import bpy


def get_random_color():
    return random.choice(
        [
            [0.92578125, 1, 0.0, 1],
            [0.203125, 0.19140625, 0.28125, 1],
            [0.8359375, 0.92578125, 0.08984375, 1],
            [0.16796875, 0.6796875, 0.3984375, 1],
            [0.6875, 0.71875, 0.703125, 1],
            [0.9609375, 0.9140625, 0.48046875, 1],
            [0.79296875, 0.8046875, 0.56640625, 1],
            [0.96484375, 0.8046875, 0.83984375, 1],
            [0.91015625, 0.359375, 0.125, 1],
            [0.984375, 0.4609375, 0.4140625, 1],
            [0.0625, 0.09375, 0.125, 1],
            [0.2578125, 0.9140625, 0.86328125, 1],
            [0.97265625, 0.21875, 0.1328125, 1],
            [0.87109375, 0.39453125, 0.53515625, 1],
            [0.8359375, 0.92578125, 0.08984375, 1],
            [0.37109375, 0.29296875, 0.54296875, 1],
            [0.984375, 0.4609375, 0.4140625, 1],
            [0.92578125, 0.16796875, 0.19921875, 1],
            [0.9375, 0.9609375, 0.96484375, 1],
            [0.3359375, 0.45703125, 0.4453125, 1],
        ]
    )

def safe_remove_object(obj):
    if obj is None:
        return 
    data = obj.data

    bpy.data.objects.remove(obj, do_unlink=True)

    if data and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        if isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)

def set_keyframe_to_ease_in_out(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    area = bpy.context.area
    if not area:
        print("Ошибка: не удалось определить текущее окно")
        return
    
    old_type = area.type
    
    try:
        area.type = 'DOPESHEET_EDITOR'
        
        bpy.ops.action.select_all(action='SELECT')
        
        bpy.ops.action.interpolation_type(type='QUART')
        bpy.ops.action.easing_type(type='EASE_OUT')
        
    finally:
        area.type = old_type
        
    bpy.context.view_layer.update()
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)

def animate_shape(obj, start_frame, end_frame):
    obj.keyframe_insert("rotation_euler", frame = start_frame)
    
    rturn = random.randint(3240, 3600)
    obj.rotation_euler.z += math.radians(rturn)
    
    obj.keyframe_insert("rotation_euler", frame = end_frame)
    
    wheel = bpy.data.objects.get("Wheel_Fortune_3D_Root")
    if wheel:
        set_keyframe_to_ease_in_out(wheel)
    
    return rturn

def calculate_pins_from_dict(data_dict):
    """Превращает словарь весов в список абсолютных углов штифтов в радианах"""
    total_weight = sum(data_dict.values())
    current_angle = 0.0
    pin_angles = []
    
    for weight in data_dict.values():
        pin_angles.append(current_angle)
        # Считаем долю сектора от полных 360 градусов (2 * pi)
        sector_angle = (weight / total_weight) * 2 * math.pi
        current_angle += sector_angle
        
    return pin_angles

def animate_arrow(context, cfg, wheel_obj, arrow_obj, data_dict, total_frames, rollback_frames):
    local_pins = calculate_pins_from_dict(data_dict)
    
    hit_zone, exit_zone, max_deflection = angeles_extremum(cfg)

    
    I = cfg.moment_of_inertia 
    b = cfg.atten_coeff 
    k = cfg.spring_stiffness 
    dt = 1.0 / cfg.fps
    substeps = cfg.substep_calculation
    sub_dt = dt / substeps
    
    
    # Физические параметры стрелки
    deflection = 0.0
    ang_V = 0.0
    prev_deflection = 0.0
    
    wheel_obj.rotation_mode = 'XYZ'
    arrow_obj.rotation_mode = 'XYZ'
    
    if arrow_obj.animation_data and arrow_obj.animation_data.action:
        arrow_obj.animation_data_clear()

    # Берем положение колеса на "нулевом" кадре для плавного старта интерполяции
    context.scene.frame_set(0)
    prev_wheel_rot = wheel_obj.rotation_euler[2]

    calc_deflection = get_deflection_calculator(cfg)

    for frame in range(0, total_frames + 1):
        context.scene.frame_set(frame)
        current_wheel_rot = wheel_obj.rotation_euler[2]
        
        for step in range(1, substeps + 1):
            factor = step / substeps
            sub_wheel_rot = prev_wheel_rot + (current_wheel_rot - prev_wheel_rot) * factor
            
            any_collision = False
            max_kinematic_deflection = 0.0
            
            for pin_local_angle in local_pins:
                global_pin_angle = (pin_local_angle + sub_wheel_rot - cfg.arrow_angle) % (2 * math.pi)
                
                if global_pin_angle > math.pi:
                    normalized_angle = global_pin_angle - 2 * math.pi
                else:
                    normalized_angle = global_pin_angle
                
                # Если штифт в зоне контакта
                if -hit_zone <= normalized_angle <= exit_zone:
                    any_collision = True
                    pin_deflection = calc_deflection(normalized_angle)
                    # Если штифтов несколько, выбираем тот, который отклоняет сильнее всего
                    if pin_deflection > max_kinematic_deflection:
                        max_kinematic_deflection = pin_deflection
            
            # Считаем физику для текущего микро-шага (sub_dt)
            if any_collision or frame > total_frames-rollback_frames:
                # Фаза контакта: стрелка послушно следует за геометрией штифта
                deflection = max_kinematic_deflection
                # Вычисляем скорость: изменение координаты делить на микро-время
                delta_deflection = deflection - prev_deflection
                if abs(delta_deflection) < 0.0001:
                    ang_V = 0
                else:
                    ang_V = delta_deflection / sub_dt
            else:
                # Фаза свободного полета: работает пружина и трение
                a = - (b * ang_V + k * deflection) / I
                ang_V += a * sub_dt
                deflection += ang_V * sub_dt
            
            # Сохраняем значение для следующего микро-шага
            prev_deflection = deflection
            
        # Запоминаем позицию колеса для следующего кадра
        prev_wheel_rot = current_wheel_rot
        
        # Записываем ключ для стрелки (значение, которое накопилось к концу кадра)
        arrow_obj.rotation_euler[2] = -deflection + cfg.arrow_angle #+ 1.5708
        arrow_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
        
    context.scene.frame_set(1)
    return normalized_angle

def angeles_extremum(cfg):
    radius = cfg.pin_radius # Радиус палки
    wheel_radius = cfg.wheel_radius  # Радиус колеса
    c = cfg.arrow_p_of_r # Расстояние от точки кручения до вершины треугольника
    l = c - cfg.dist_between_edge_tip # Растояние от колеса до т. вращения стрелки
    b = cfg.width_arrow # Основание стрелки
    d = math.sqrt(2)/4
    a = math.sqrt((c+d)**2+(b/2)**2) # Боковая сторона треугольника
    e = wheel_radius + l - c # Расстояние от центра колеса до вершины при нулевом угле
    L = wheel_radius + radius
    M = c + radius
    N = wheel_radius + l # Расстояние от центра колеса до т. вр. стрелки
    p = (L + M + N) /2
    h = 2/N * math.sqrt(p*(p-L)*(p-M)*(p-N)) # Высота треугольника LMN на сторону N
    beta = math.asin(h/(wheel_radius+radius)) # Максимальный угол колеса
    alpha = math.asin(b/(2*a)) + math.asin((2*a*radius-b*e)/(2*a*wheel_radius))
    gamma = math.asin(h/(c+radius))
    
    return alpha, beta, gamma

def get_deflection_calculator(cfg):

    c = cfg.arrow_p_of_r
    base = cfg.width_arrow
    R = cfg.wheel_radius
    r = cfg.pin_radius 
    D = R + cfg.arrow_p_of_r - cfg.dist_between_edge_tip
    
    # Считаем тяжелую математику один раз
    height = c + (math.sqrt(2) / 4)
    half_base = base / 2
    a = math.sqrt(height**2 + half_base**2)
    
    theta = math.asin(half_base / a)
    t = (height * base) / a
    
    def calculate(psi):
        l = math.sqrt(R**2 + D**2 - 2 * R * D * math.cos(psi))
        
        arg = (r + t) / l if l != 0 else 1.0
        alpha = math.asin(max(-1.0, min(1.0, arg)))
        beta = math.atan2(R * math.sin(psi), D - R * math.cos(psi))
        
        return 1.5 * math.pi + beta + alpha + theta
        
    return calculate


def calculate_rollback_target(cfg, final_wheel_rot, local_pins, hit_zone, exit_zone):
    """
    Крутит колесо назад математически, пока стрелка не распрямится.
    Возвращает целевой угол для отката и флаг, нужен ли вообще откат.
    """
    calc_deflection = get_deflection_calculator(cfg)
    current_rot = final_wheel_rot
    step = 0.005  # Шаг симуляции (в радианах)
    
    # Сначала проверим, отклонена ли стрелка в текущем финальном положении
    max_initial_deflection = 0.0
    for pin in local_pins:
        global_pin = (pin + current_rot - cfg.arrow_angle) % (2 * math.pi)
        norm_angle = global_pin if global_pin <= math.pi else global_pin - 2 * math.pi
        
        if -hit_zone <= norm_angle <= exit_zone:
            max_initial_deflection = max(max_initial_deflection, calc_deflection(norm_angle))
            
    # Если стрелка уже свободна, откат не нужен
    if max_initial_deflection <= 0.001:
        return current_rot, False

    # Ищем угол, при котором стрелка выпрямится
    while True:
        max_deflection = 0.0
        for pin in local_pins:
            global_pin = (pin + current_rot) % (2 * math.pi)
            norm_angle = global_pin if global_pin <= math.pi else global_pin - 2 * math.pi
            
            if -hit_zone <= norm_angle <= exit_zone:
                max_deflection = max(max_deflection, calc_deflection(norm_angle))
                
        if max_deflection <= 0.001:
            break  # Стрелка полностью выпрямилась
            
        current_rot -= step  # Откатываем колесо назад
        
        # Защита от бесконечного цикла (максимум откатываемся на половину сектора)
        if final_wheel_rot - current_rot > math.pi / 4:
            break
            
    return current_rot, True

def make_animation(data, cfg):
    wheel_root = bpy.data.objects.get("Wheel_Fortune_3D_Root")
    if wheel_root is None:

        def draw_error_message(self, context):
            self.layout.label(text="Ошибка: Объект 'Wheel_Fortune_3D_Root' не найден!", icon='ERROR')
            self.layout.label(text="Пожалуйста, добавьте или переименуйте объект в сцене.")
        # Вызов всплывающего окна
        bpy.context.window_manager.popup_menu(draw_error_message, title="Объект отсутствует", icon='CANCEL')

        return

    arrow = bpy.data.objects.get("Wheel_Arrow")
    if arrow is None:
        def draw_error_message(self, context):
            self.layout.label(text="Ошибка: Объект 'Wheel_Arrow' не найден!", icon='ERROR')
            self.layout.label(text="Пожалуйста, добавьте или переименуйте объект в сцене.")
        bpy.context.window_manager.popup_menu(draw_error_message, title="Объект отсутствует", icon='CANCEL')
        return

    main_frames = int(cfg.loop_seconds*cfg.fps)  # Длительность основного вращения
    
    # Запускаем основное вращение колеса
    animate_shape(wheel_root, 0, main_frames)
    
    # Подготовка данных для расчета отката
    local_pins = calculate_pins_from_dict(data) # data = sectors_dict
    hit_zone, exit_zone, _ = angeles_extremum(cfg)
    
    # Получаем угол колеса в конце основной анимации
    bpy.context.scene.frame_set(main_frames)
    final_rot = wheel_root.rotation_euler[2]
    
    # Вычисляем угол отката
    rollback_rot, needs_rollback = calculate_rollback_target(cfg, final_rot, local_pins, hit_zone, exit_zone)
    
    total_anim_frames = main_frames
    
    if needs_rollback:
        # Рассчитываем длительность отката
        rollback_frames = max(15, int(abs(final_rot - rollback_rot) / 0.01))
        total_anim_frames += rollback_frames
        
        # Ставим ключ на новый целевой угол
        wheel_root.rotation_euler[2] = rollback_rot
        wheel_root.keyframe_insert("rotation_euler", frame=total_anim_frames, index=2)
        
        action = wheel_root.animation_data.action
        
        if hasattr(action, "slots"):
            # Получаем активный слот объекта (или берем первый по умолчанию)
            slot = getattr(wheel_root.animation_data, "action_slot", action.slots[0])
            if not slot:
                slot = action.slots[0]
                
            layer = action.layers[0]
            strip = layer.strips[0]
            channelbag = strip.channelbag(slot, ensure=True)
            fcurves_data = channelbag.fcurves
        else:
            fcurves_data = action.fcurves
            
        fcurve = fcurves_data.find('rotation_euler', index=2)
        
        if fcurve:
            kf_main_end = fcurve.keyframe_points[-2]
            kf_main_end.interpolation = 'LINEAR'
        # -----------------------------------------
    
    # Запускаем физику стрелки на ВСЕ кадры (включая кадры отката)
    animate_arrow(bpy.context, cfg, wheel_root, arrow, data, total_anim_frames, rollback_frames if needs_rollback else 0)

def create_arrow_object(context, cfg, wheel_radius, wheel_thickness, matarrow, wheel_root, arrow_angle):

    # Проверяем, существует ли уже стрелка в сцене
    old_arrow = bpy.data.objects.get("Wheel_Arrow")
    if old_arrow:
        safe_remove_object(old_arrow)
    
    arrow_mesh = bpy.data.meshes.new("Wheel_Arrow_Mesh")
    arrow_obj = bpy.data.objects.new("Wheel_Arrow", arrow_mesh)
    
    context.scene.collection.objects.link(arrow_obj)

    height = cfg.lenght_arrow
    base = cfg.width_arrow
    thickness = cfg.thickness_arrow
    arrow_p_of_r = cfg.arrow_p_of_r

    dist_between_edge_tip = cfg.dist_between_edge_tip 

    bm = bmesh.new()

    half_base = base / 2.0

    # Геометрия создается так, чтобы острие было в (0-arrow_p_of_r,0,0), т.е. ориджин был на месте,
    # а тело стрелки уходило ВПРАВО (вдоль +X).
    # Нижняя плоскость (Z = 0)
    v_tip_bottom  = bm.verts.new((0, 0, 0))                       # Острие (Origin!)
    v_back_l_bot  = bm.verts.new((height, -half_base, 0))         # Задний левый
    v_back_r_bot  = bm.verts.new((height, half_base, 0))          # Задний правый

    # Верхняя плоскость (Z = thickness)
    v_tip_top     = bm.verts.new((0, 0, thickness))               # Острие верх
    v_back_l_top  = bm.verts.new((height, -half_base, thickness)) # Верхний левый
    v_back_r_top  = bm.verts.new((height, half_base, thickness))  # Верхний правый

    # Создаем грани
    bm.faces.new((v_tip_bottom, v_back_l_bot, v_back_r_bot))
    bm.faces.new((v_tip_top, v_back_r_top, v_back_l_top))

    bm.faces.new((v_tip_bottom, v_tip_top, v_back_l_top, v_back_l_bot))
    bm.faces.new((v_tip_bottom, v_back_r_bot, v_back_r_top, v_tip_top))
    bm.faces.new((v_back_l_bot, v_back_l_top, v_back_r_top, v_back_r_bot))

    bmesh.ops.translate(bm, vec=(-arrow_p_of_r, 0, 0), verts=bm.verts)

    bm.to_mesh(arrow_mesh)
    bm.free()
    
    arrow_obj.data.materials.append(matarrow)

    # Расстояние от центра колеса до острия стрелки
    dist = wheel_radius - dist_between_edge_tip + arrow_p_of_r

    x = dist * math.cos(arrow_angle)
    y = dist * math.sin(arrow_angle)
    z = wheel_thickness

    arrow_obj.location = (x, y, z)
    arrow_obj.rotation_euler = (0, 0, arrow_angle)
    arrow_obj.scale = (1.0, 1.0, 1.0)

    # Настройка Copy Location (с проверкой на дубликаты)
    loc_constraint = arrow_obj.constraints.get("Copy_Wheel_Location")
    if not loc_constraint:
        loc_constraint = arrow_obj.constraints.new(type='COPY_LOCATION')
        loc_constraint.name = "Copy_Wheel_Location"
    
    loc_constraint.target = wheel_root
    loc_constraint.use_offset = True
    
    return arrow_obj

def use_mat(mat_name, base_color):
    mat_obj = bpy.data.materials.get(mat_name)
    if mat_obj is None:
        mat_obj = bpy.data.materials.new(name=mat_name)
        mat_obj.use_nodes = True
        nodearrow = mat_obj.node_tree.nodes
        principled = nodearrow.get("Principled BSDF")
        if principled:
            principled.inputs['Base Color'].default_value = base_color
            principled.inputs['Roughness'].default_value = 0.2
    return mat_obj

def create_sector_text(context, cfg, label, wheel_radius, text_thickness, wheel_thickness, mid_angle, wheel_root, mattext):
    font_curve = bpy.data.curves.new(type="FONT", name=f"text_curve_{label}")
    font_curve.body = label
    font_curve.align_x = cfg.text_alignment # LEFT, CENTER, RIGHT
    font_curve.align_y = 'CENTER'
    font_curve.size = cfg.text_size
    font_curve.extrude = text_thickness
    alignment_point = cfg.alignment_point

    text_obj = bpy.data.objects.new(f"Text_{label}", font_curve)
    context.scene.collection.objects.link(text_obj)
    text_obj.parent = wheel_root

    tx = (wheel_radius * alignment_point) * math.cos(mid_angle)
    ty = (wheel_radius * alignment_point) * math.sin(mid_angle)

    text_obj.location = (tx, ty, wheel_thickness + 0.005)
    text_obj.rotation_euler[2] = mid_angle 

    text_obj.data.materials.append(mattext)

    return text_obj

def fit_text_scales(context, text_objects, wheel_radius):
    context.view_layer.update()

    max_width = wheel_radius * 0.65
    for text_obj in text_objects:
        width = text_obj.dimensions.x
        if width > max_width:
            scale_factor = max_width / width
            text_obj.scale = (scale_factor, scale_factor, scale_factor)

def create_pins(x, y, angle, parent_obj, pin_radius, pin_height):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=pin_radius,
        depth=pin_height, # длина перекладины (при необходимости измените)
        location=(x, y, pin_height/2)
    )
    bar = bpy.context.object
    bar.rotation_euler = (0, 0, angle) # поворот вокруг Y на 90°, затем вокруг Z на угол
    bar.parent = parent_obj

def create_spoke(x, y, angle, wheel_thickness, parent_obj, wheel_radius, spoke_width):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=spoke_width/2,
        depth=wheel_radius, # длина перекладины (при необходимости измените)
        location=(x/2, y/2, wheel_thickness)
    )
    bar = bpy.context.object
    bar.rotation_euler = (0, 1.5708, angle) # поворот вокруг Y на 90°, затем вокруг Z на угол
    bar.parent = parent_obj

def create_wheel(context, sectors_dict, cfg):
    # Получаем местоположение курсора 
    cursor_loc = context.scene.cursor.location

    # Ищем существует ли такая пустышка
    wheel_root = bpy.data.objects.get("Wheel_Fortune_3D_Root")

    if wheel_root is not None:

        for child in tuple(wheel_root.children):
            safe_remove_object(child)
        # Проверяем совпадает ли положение (с учетом погрешности)
        if (wheel_root.location - cursor_loc).length > 0.0001:
            # Позиция не совпадает — удаляем старые объекты
            bpy.data.objects.remove(wheel_root, do_unlink=True)
            wheel_root = None  # Сбрасываем переменную для создания нового объекта

    # Создаем новую пустышку если ее нет (или если старая была удалена)
    if wheel_root is None:
        wheel_root = bpy.data.objects.new("Wheel_Fortune_3D_Root", None)
        # Задаем ей позицию 3D-курсора
        wheel_root.location = cursor_loc.copy()
        # Линкуем в коллекцию сцены
        context.scene.collection.objects.link(wheel_root)

    # ПАРАМЕТРЫ ИЗ CFG.
    wheel_radius = cfg.wheel_radius # Радиус колеса
    arrow_angle = cfg.arrow_angle # Угол стрелки
    pin_radius = cfg.pin_radius # Радиус пина
    pin_height = cfg.pin_height # Высота пина
    spoke_width = cfg.spoke_width # Толщина спицы
    wheel_thickness = cfg.wheel_thickness # Толщина колеса
    text_thickness = cfg.text_thickness # Толщина текста

    total_weight = sum(sectors_dict.values()) # Сумма весов
    current_angle = cfg.wheel_start_angle # объявление Текущего угла через начальный
    segments_per_degree = 2 # Кол-во сегментов на 1 градус (2 сег/гр)

    created_texts = []
    
    # Центр
    sph_is_none = bpy.data.objects.get("Center_Sphere") is None
    if sph_is_none: # ПЕРЕДЕЛАТЬ НА BMESH
        # Создаем структуру меша и объект напрямую
        sphere_mesh = bpy.data.meshes.new("Center_Sphere_Mesh")
        sphere_obj = bpy.data.objects.new("Center_Sphere", sphere_mesh)
        # Помещаем объект в сцену и делаем родителем wheel_root
        context.scene.collection.objects.link(sphere_obj)
        sphere_obj.parent = wheel_root
        # Генерируем сферу программно через BMesh
        
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.4)
        bm.to_mesh(sphere_mesh)
        bm.free() 

    matarrow = use_mat("MAT_ARROW", (1,0,0,1))
    create_arrow_object(context, cfg, wheel_radius, wheel_thickness, matarrow, wheel_root, arrow_angle)

    mattext = use_mat("TEXT", (0,0,0,0))

    for label, weight in sectors_dict.items():
        sector_angle = (weight / total_weight) * 2 * math.pi
        num_arc_points = max(3, int(math.degrees(sector_angle) * segments_per_degree)) # Расчет кол-ва т. дуги
        
        verts = [(0, 0, 0)]
        faces = []
        
        for i in range(num_arc_points + 1):
            angle = current_angle + (i / num_arc_points) * sector_angle # Расчет угла текущей вершины
            x = wheel_radius * math.cos(angle)
            y = wheel_radius * math.sin(angle)
            verts.append((x, y, 0))
            if i > 0:
                faces.append((0, i, i + 1))
                
        create_spoke(x, y, angle, wheel_thickness, wheel_root, wheel_radius, spoke_width)
        create_pins(x, y, angle, wheel_root, pin_radius, pin_height)
                
        mesh = bpy.data.meshes.new(f"mesh_{label}")
        sector_obj = bpy.data.objects.new(f"Sector_{label}", mesh)
        bpy.context.scene.collection.objects.link(sector_obj)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        sector_obj.parent = wheel_root
        
        # --- ДЕЛАЕМ СЕКТОР ОБЪЕМНЫМ ---
        solidify = sector_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = wheel_thickness
        solidify.offset = 1.0

        random_color = get_random_color()
        mat = use_mat(f"Mat_{label}", random_color)
        sector_obj.data.materials.append(mat)



        mid_angle = current_angle + sector_angle / 2

        text_obj = create_sector_text(context, cfg, label, wheel_radius, text_thickness, wheel_thickness, mid_angle, wheel_root, mattext)

        created_texts.append(text_obj)
        
        current_angle += sector_angle

    fit_text_scales(context, created_texts, wheel_radius)
    # print("Колесо создано!")
