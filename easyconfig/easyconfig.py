#!/usr/bin/env python3
# ! -*- coding:utf-8 -*-
# coding:unicode_escape
"""
jeack_chen@hotmail.com
2021-12
"""

import configparser
import re
from collections import defaultdict
from configparser import NoSectionError, NoOptionError

_UNSET = object()


def can_field(c):
    units = (
        ('\u4e00', '\u9fa5'),
        ('\u0410', '\u044f'),
    )
    for u in units:
        if u[0] <= c <= u[1]:
            return True
    return False


class OptionPack:
    def __init__(self, conf, section, option, value=_UNSET):
        self.conf, self.section, self.option, self.value = conf, section, option, value

    def __call__(self, value=_UNSET):
        try:
            return self.conf.get(self.section, self.option)
        except (NoSectionError, NoOptionError):
            if value is _UNSET and self.value is _UNSET:
                raise
            return value if value is not _UNSET else self.value

    @classmethod
    def to_field_name(cls, option):
        return re.sub(r'\W', '_', option.strip().upper())


class SectionPack:
    def __init__(self, conf, sections):
        self._options = {}
        alias = defaultdict(set)
        for section in sections:
            for arg in EasyConfig.info.get_options(section):
                if len(arg) < 2:
                    continue
                lower_option = arg[0].lower()
                self._options[lower_option] = OptionPack(conf, section, *arg[:-1])
                field = OptionPack.to_field_name(lower_option)
                if field[0].isalpha() or can_field(field[0]):
                    alias[field].add(lower_option)
                    setattr(self, field, self._options[lower_option])
        # 去掉有名字冲突的
        for field, option in alias.items():
            if len(option) > 1:
                delattr(self, field)

    def __call__(self, option: str, *args) -> OptionPack:
        """
        :param option: 需要获取的 option name
        :return: OptionPack
        """
        if option.lower() in self._options:
            return self._options[option.lower()](*args)
        if not hasattr(self, "sections"):
            self.sections = {op.section for op in self._options.values()}
        raise Exception(f"no option:{option} in section:{','.join(self.sections)}")

    def all_options(self):
        res = defaultdict(list)
        for op in self._options.values():
            res[op.section].append(op.option)
        return res


class OptionInfo:
    kDefault = "DEFAULT"

    def __init__(self):
        self.buf = {}

    def append(self, section, *options):
        if self.has(section):
            raise Exception(f"Option:append section:'{section}' existed.")
        index = -1 if section.lower() == self.kDefault else len(self.buf)
        self.buf[section.lower()] = (index, section, options)

    def has(self, section):
        return section.lower() in self.buf

    def get_options(self, section=None):
        """
        :param section:
        :return:
            ((option, default) or (option, ), ...)
        """
        sect = self.kDefault if section is None else section.lower()
        if sect == self.kDefault and self.kDefault not in self.buf:
            return tuple()
        return self.buf[sect][-1]

    @staticmethod
    def comment_format(comment):
        if len(comment.strip()) == 0:
            return ""
        return "# " + comment.replace('\n', '\n# ')

    def show(self, *sections):
        for line in self.config_data(*sections):
            print(line)

    def config_data(self, *sections):
        cs = self.buf if len(sections) == 0 else self.buf.fromkeys([s.lower() for s in sections])
        datas = sorted(cs.values(), key=lambda x: x[0])
        for d in datas:
            yield f"[{d[1]}]"
            for c in d[2]:
                if len(c[-1]) > 0:
                    yield self.comment_format(c[-1])
                num = len(c)
                if num >= 2:
                    yield f"{c[0]}={'' if num == 2 else '' if c[1] is None else c[1]}"
                yield ""


class EasyConfig:
    info = OptionInfo()

    @classmethod
    def register(cls, section: str, *option_arg: tuple):
        """
        :param section:
        :param option_arg: tuple
            ((option, default, comment) or (option, comment) or (comment,), ...)
        :return: cls
        """
        cls.info.append(section, *option_arg)
        return cls

    @classmethod
    def get_info(cls, *sections):
        return '\n'.join(cls.info.config_data(*sections))

    @classmethod
    def section_pack(cls, conf: configparser.ConfigParser, sections) -> SectionPack:
        """
        :param conf:
            configparser.ConfigParser
        :param sections:
            if type(sections) done
            if type(sections) == type: sections = [c.__name__ for c in sections.mro() if c != object]
        :return:
            SectionPack
        """
        if type(sections) == str:
            sections = [sections, ]
        elif type(sections) == type:
            sections = [c.__name__ for c in sections.mro() if c != object]
            sections.reverse()
        else:
            raise Exception(f"Bad sections type.")

        for section in sections:
            if not cls.info.has(section):
                raise Exception(f"section:'{section}' has not been configured.")

        if OptionInfo.kDefault not in sections:
            sections.insert(0, OptionInfo.kDefault)

        return SectionPack(conf, sections)
