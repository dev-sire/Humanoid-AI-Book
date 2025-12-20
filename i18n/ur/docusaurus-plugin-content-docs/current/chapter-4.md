---
id: chapter-4
title: "Chapter 4: NVIDIA Isaac Integration"
sidebar_label: "Chapter 4: NVIDIA Isaac Integration"
week: 6-7
---

## جائزہ

یہ باب NVIDIA Isaac Sim پر مرکوز ہے، جو روبوٹکس سمولیشن اور AI ٹریننگ کے لیے ایک طاقتور پلیٹ فارم ہے۔

## مقاصد

- NVIDIA Isaac Sim کی صلاحیتوں کو سمجھیں۔
- ROS 2 کو Isaac Sim کے ساتھ مربوط کرنے کا طریقہ سیکھیں۔
- AI ٹریننگ کے لیے Isaac Sim کی خصوصیات کو دریافت کریں۔

## بنیادی مواد

NVIDIA Isaac Sim ایک قابل توسیع روبوٹکس سمولیشن ایپلی کیشن اور مصنوعی ڈیٹا جنریشن ٹول ہے جو AI پر مبنی روبوٹس کو طاقت دیتا ہے۔ یہ NVIDIA Omniverse پر بنایا گیا ہے اور AI پر مبنی روبوٹس کی تیاری، جانچ اور تربیت کے لیے فوٹو ریئلسٹک، جسمانی طور پر درست ورچوئل ماحول فراہم کرتا ہے۔

### ROS 2 انٹیگریشن

Isaac Sim میں ROS 2 کے لیے بلٹ ان سپورٹ ہے، جو آپ کی موجودہ ROS 2 ایپلی کیشنز کے ساتھ بغیر کسی رکاوٹ کے انضمام کی اجازت دیتا ہے۔ آپ Isaac Sim سے ROS 2 عنوانات تک ڈیٹا شائع کرنے کے لیے ROS 2 برج کا استعمال کر سکتے ہیں، اور سمولیشن میں اشیاء کو کنٹرول کرنے کے لیے ROS 2 کے عنوانات کو سبسکرائب کر سکتے ہیں۔

## مثالیں۔

### اسحاق سم کو ROS 2 سے جوڑنا

یہاں ایک سادہ Python اسکرپٹ کی ایک مثال ہے جو Isaac Sim میں ایک کیوب بناتی ہے اور اپنی پوزیشن کو ROS 2 موضوع پر شائع کرتی ہے۔

`` ازگر
کاربوہائیڈریٹ درآمد کریں۔
omni.isaac.kit import SimulationApp سے

CONFIG = \{"renderer": "RayTracedLighting", "headless": False\}
simulation_app = SimulationApp(CONFIG)

omni.isaac.core امپورٹ ورلڈ سے
omni.isaac.core.objects سے کیوبائڈ درآمد کریں۔
omni.isaac.ros2_bridge کو ros2_bridge کے بطور درآمد کریں۔

دنیا = دنیا()
world.scene.add_default_ground_plane()

# کیوب بنائیں
کیوب = world.scene.add( 
cuboid.VisualCuboid( 
prim_path="/World/random_cube"، 
name="my_cube"، 
پوزیشن=[0، 0، 1.0]، 
پیمانہ=[0.5، 0.5، 0.5]، 
رنگ=[1.0، 0، 0]، 
)
)

# ROS 2 پل شروع کریں۔
ros2_bridge.activate_ros_bridge()

# ... (ROS 2 موضوع پر کیوب پوزیشن شائع کرنے کے لیے کوڈ)

# نقلی چلائیں۔
جبکہ simulation_app.is_running(): 
world.step(render=True)

simulation_app.close()
``

## اعداد و شمار

![Isaac Sim میں روبوٹ](../../../../static/img/chap-4.png)

*شکل 1: فوٹو ریئلسٹک آئزک سم ماحول میں ایک پیچیدہ روبوٹ ماڈل۔*

## خلاصہ

اس باب نے NVIDIA Isaac Sim اور روبوٹکس سمولیشن اور AI ٹریننگ کے لیے اس کی صلاحیتوں کا ایک جائزہ فراہم کیا۔ ہم نے آر او ایس 2 کے ساتھ آئزک سم کو مربوط کرنے کے طریقے کی ایک مثال بھی دیکھی۔ اگلے باب میں، ہم ویژن-لینگویج-ایکشن ماڈلز کو تلاش کریں گے۔