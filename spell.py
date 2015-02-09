import dbc
import os

class Spell:
    def effect(self, e):
        pass

class Spells:
    def __init__(self, vers_str):
        hp = os.path.expanduser('~/.ssi/' + vers_str)
        spell_path = os.path.join(hp , 'Spell.dbc')
        spell_icon_path = os.path.join(hp , 'SpellIcon.dbc')

        err = RuntimeError('Could not find needed files for version. Need:\n' +
            spell_path + '\n' + spell_icon_path)

        if not os.path.exists(hp) or not os.path.isdir(hp):
            raise err

        if (not os.path.exists(spell_path) or
            not os.path.exists(spell_icon_path)):
            raise err

        self.spell_dbc = dbc.Dbc(spell_path, self._mapping_for_vers(vers_str),
            Spell)
        self.spell_icon_dbc = dbc.Dbc(spell_icon_path, self._icon_mapping()) 

    def get_icon_path(self, spell):
        """Returns icon path of spell"""
        return next(
            x for x in self.spell_icon_dbc.table if x.id == spell.icon_id).path

    def _mapping_for_vers(self, vers_str):
        if vers_str == '2.4.3':
            return _2_4_3_mappings()
        else:
            raise RuntimeError('Unsupported version "' + vers_str + '.')

    def _icon_mapping(self):
        return [dbc.Mapping(0, int, 'id'), dbc.Mapping(1, str, 'path')]

    def iter(self, code):
        res = []
        regexp = __import__('re')
        for spell in self.spell_dbc.table:
            if eval(code, {'spell': spell, 're': regexp}) == True:
                res.append(spell)
        return res

def _2_4_3_mappings():
    return [
        dbc.Mapping(0,   int, 'id'),
        dbc.Mapping(1,   int, 'category'),
        dbc.Mapping(3,   int, 'dispel'),
        dbc.Mapping(4,   int, 'mechanic'),
        dbc.Mapping(5,   int, 'attr'),
        dbc.Mapping(6,   int, 'attr_ex1'),
        dbc.Mapping(7,   int, 'attr_ex2'),
        dbc.Mapping(8,   int, 'attr_ex3'),
        dbc.Mapping(9,   int, 'attr_ex4'),
        dbc.Mapping(10,  int, 'attr_ex5'),
        dbc.Mapping(11,  int, 'attr_ex6'),
        dbc.Mapping(12,  int, 'stances'),
        dbc.Mapping(13,  int, 'stances_not'),
        dbc.Mapping(124, int, 'icon_id'),
        dbc.Mapping(127, str, 'name'),
        dbc.Mapping(144, str, 'rank'),
    ]
