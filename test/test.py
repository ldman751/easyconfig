import unittest
import configparser
from easyconfig import EasyConfig

EasyConfig \
    .register('DEFAULT',
              ('option in default', 'option value', '')
              ) \
    .register('DemoA',
              ('option_a', 'option_a default value', 'option option_a default'),
              ('option_b', 'default_option_value', 'option option_b default: default_option_value'),
              ('',),  # OptionManager.info.show 输出一条空行
              ('option_c', 'option_c default is None'),
              ('option h', 'option_h default is None'),
              ) \
    .register('DemoB',
              ('option_d', "", 'option option_d default ”“'),
              ('o p t i o n.', "O_P_T_I_O_N_value", 'option option_d default ”“'),
              ('.option', "", '不是字母开头的option，不能用属性方式获取'),
              ('中文', "", '中文 option'),
              ('русский', "", 'русский option'),
              ) \
    .register('DemoC',
              ('option e', 'option option_e default None'),
              ('option h', 'option option_e default None'),
              )


class DemoA:
    def __init__(self, conf):
        self.conf = conf
        self.sp = EasyConfig.section_pack(self.conf, self.__class__)


class DemoB(DemoA):
    def __init__(self, conf):
        super().__init__(conf)


class DemoC(DemoA):
    def __init__(self, conf):
        super().__init__(conf)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        config_demo_data = """
[DEFAULT]
option in default = default_value
[DemoA]
option_a = option_a value in demo.ini
option h = option h value in demo.ini

[DemoC]
option h = option h value in demo.ini section DemoC
option f = DemoC name change to:OPTION_F
"""
        self.conf = configparser.ConfigParser()
        self.conf.read_string(config_demo_data)

        a = DemoA(self.conf)
        # 正常读取配置option_a
        self.assertEqual(a.sp.OPTION_A(), self.conf.get('DemoA', 'option_a'))

        # 读取带默认值的 option_b
        self.assertEqual(a.sp.OPTION_B(), self.conf.get('DemoA', 'option_b', fallback="default_option_value"))
        # 读取带默认值的 option_b, 默认值由参数制定
        self.assertEqual(a.sp.OPTION_B("default_pv"), self.conf.get('DemoA', 'option_b', fallback="default_pv"))

        # option_c 不存在时，未设置默认值，会有异常抛出
        self.assertRaises(Exception, a.sp.OPTION_C)
        # 读取带默认值的 option_c, 默认值由参数制定
        self.assertEqual(a.sp.OPTION_C("default_pv"), self.conf.get('DemoA', 'option_c', fallback="default_pv"))

        # 读取section=DEFAULT的option：
        self.assertEqual(a.sp.OPTION_IN_DEFAULT(), self.conf.get('DemoA', 'option in default'))

        b = DemoB(self.conf)
        # 读取父类的 option_a
        self.assertEqual(b.sp.OPTION_A(), self.conf.get('DemoA', 'option_a'))

        # 读取本类的 option_d
        self.assertEqual(b.sp.OPTION_D(), self.conf.get('DemoB', 'option_d', fallback=""))

        # 读取本类的 O_P_T_I_O_N_, field 名称: 由 option_name 大写，并用'_'替换非字母和数字
        self.assertEqual(b.sp.O_P_T_I_O_N_(), self.conf.get('DemoB', 'o p t i o n.', fallback="O_P_T_I_O_N_value"))

        # 不是字母开头的option，不能用属性方式获取
        self.assertEqual(b.sp(".option")(), self.conf.get('DemoB', '.option', fallback=""))
        self.assertEqual(b.sp("中文")(), self.conf.get('DemoB', '中文', fallback=""))

        # 想了一下，支持中文属性名还是比较酷
        self.assertEqual(b.sp.中文(), self.conf.get('DemoB', '中文', fallback=""))
        # 俄文也支持
        self.assertEqual(b.sp.РУССКИЙ(), self.conf.get('DemoB', 'русский', fallback=""))

        c = DemoC(self.conf)
        # option_a 来自父类
        self.assertEqual(c.sp.OPTION_A(), a.sp.OPTION_A())
        # option h 被子类覆盖
        self.assertNotEqual(c.sp.OPTION_H(), a.sp.OPTION_H())

        print("Output config demo")
        EasyConfig.info.show()


if __name__ == '__main__':
    unittest.main()
