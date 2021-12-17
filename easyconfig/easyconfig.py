#!/usr/bin/env python3
# ! -*- coding:utf-8 -*-
# coding:unicode_escape
"""
jeack_chen@hotmail.com
2021-12
"""

import configparser
import re
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
        self.options = {}
        for section in sections:
            for arg in EasyConfig.info.get_options(section):
                if len(arg) < 2:
                    continue
                self.options[arg[0]] = OptionPack(conf, section, *arg[:-1])
                field = OptionPack.to_field_name(arg[0])
                if field[0].isalpha() or can_field(field[0]):
                    setattr(self, field, self.options[arg[0]])

    def __call__(self, option):
        if option in self.options:
            return self.options[option]
        raise Exception(f"no option:{option}")


class OptionInfo:
    kDefault = "DEFAULT"

    def __init__(self):
        self.buf = {}

    def append(self, section, *options):
        if self.has(section):
            raise Exception(f"Option:append section:'{section}' existed.")
        index = -1 if section.upper() == self.kDefault else len(self.buf)
        self.buf[section.upper()] = (index, section, options)

    def has(self, section):
        return section.upper() in self.buf

    def get_options(self, section=None):
        """
        :param section:
        :return:
        """
        sect = self.kDefault if section is None else section.upper()
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
        cs = self.buf if len(sections) == 0 else self.buf.fromkeys([s.upper() for s in sections])
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
    def register(cls, section, *option_arg):
        cls.info.append(section.upper(), *option_arg)
        return cls

    @classmethod
    def section_pack(cls, conf: configparser.ConfigParser, sections):
        """
        :param conf:
        :param sections:
            if type(sections) done
            if type(sections) == type: sections = [c.__name__ for c in sections.mro() if c != object]
        :return:
        """
        if type(sections) == str:
            sections = [sections, ]
        elif type(sections) == type:
            sections = [c.__name__ for c in sections.mro() if c != object]
            sections.reverse()
        else:
            raise Exception(f"Bad sections.")

        for section in sections:
            if not cls.info.has(section):
                raise Exception(f"section:'{section}' has not been configured.")

        if OptionInfo.kDefault not in sections:
            sections.insert(0, OptionInfo.kDefault)

        return SectionPack(conf, sections)
