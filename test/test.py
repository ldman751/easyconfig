import unittest
from option_manager import OptionManager
import configparser


@OptionManager.options(('option_a', 'option_a default value', 'option option_a default'),
                       ('option_b', 'option option_b default None'),
                       ('',),  # OptionManager.info.show 输出一条空行
                       ('option_c', '', 'option_c'))
class DemoA:
    def __init__(self, config_file):
        self.conf = configparser.ConfigParser()
        self.conf.read(config_file)
        self.section = self.setup_option(self, self.conf)


@OptionManager.options(('option_e', 'option option_e default None'),)
class DemoB(DemoA):
    def __init__(self, config_file):
        super(DemoB, self).__init__(config_file)


@OptionManager.options(('option_f', 'option option_f default None'),)
class DemoC(DemoA):
    def __init__(self, config_file):
        super(DemoC, self).__init__(config_file)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        config_file = "demo.ini"
        a = DemoA(config_file)
        self.assertEqual(a.OPTION_A(), "option_a default value")  # add assertion here
        self.assertIsNone(a.OPTION_B())  # add assertion here
        self.assertNotEqual(a.OPTION_C(), "")
        self.assertEqual(a.OPTION_C(), "option_c value in demo.ini")

        self.assertRaises(Exception, DemoB, config_file)

        c = DemoC(config_file)
        self.assertIsNone(c.OPTION_F())
        parm_default_value = 1
        self.assertEqual(c.OPTION_F(parm_default_value), parm_default_value)

        print("Output config demo")
        OptionManager.info.show()


if __name__ == '__main__':
    unittest.main()
