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
        spell_duration_path = os.path.join(hp , 'SpellDuration.dbc')
        spell_range_path = os.path.join(hp , 'SpellRange.dbc')
        spell_radius_path = os.path.join(hp , 'SpellRadius.dbc')
        spell_casttime_path = os.path.join(hp , 'SpellCastTimes.dbc')

        err = RuntimeError('Could not find needed files for version.' +
            '\n\nNeed:\n' +
            spell_path + '\n' + spell_icon_path + '\n' + spell_duration_path +
            '\n' + spell_range_path + '\n' + spell_radius_path + '\n' +
            spell_casttime_path)

        if not os.path.exists(hp) or not os.path.isdir(hp):
            raise err

        if (not os.path.exists(spell_path) or
            not os.path.exists(spell_icon_path) or
            not os.path.exists(spell_duration_path) or
            not os.path.exists(spell_range_path) or
            not os.path.exists(spell_radius_path) or
            not os.path.exists(spell_casttime_path)):
            raise err

        self.spell_dbc = dbc.Dbc(spell_path, self._mapping_for_vers(vers_str),
            'id', Spell)
        self.spell_icon_dbc = dbc.Dbc(spell_icon_path, self._icon_mapping(),
            'id')
        self.spell_duration_dbc = dbc.Dbc(spell_duration_path,
            self._duration_mapping(), 'id')
        self.spell_range_dbc = dbc.Dbc(spell_range_path,
            self._range_mapping(), 'id')
        self.spell_radius_dbc = dbc.Dbc(spell_radius_path,
            self._radius_mapping(), 'id')
        self.spell_casttime_dbc = dbc.Dbc(spell_casttime_path,
            self._casttime_mapping(), 'id')

    def icon_path(self, spell):
        """Returns icon path of spell"""
        return self.spell_icon_dbc.table[spell.icon_id].path

    def duration(self, spell):
        """Returns duration of spell"""
        try:
            return self.spell_duration_dbc.table[spell.duration_index].duration
        except KeyError:
            return 0

    def range(self, spell):
        """Returns range of spell"""
        return self.spell_range_dbc.table[spell.range_index]

    def radius(self, spell):
        """Returns list of radii of spell effects"""
        return [
            self.spell_radius_dbc.table[spell.eff_radius_index[0]].radius_index,
            self.spell_radius_dbc.table[spell.eff_radius_index[1]].radius_index,
            self.spell_radius_dbc.table[spell.eff_radius_index[2]].radius_index
            ]

    def cast_time(self, spell):
        """Returns cast time of spell"""
        try:
            return
            self.spell_casttime_dbc.table[spell.cast_time_index].cast_time
        except KeyError:
            return 0

    def iter(self, code):
        """Eval() code for each spell in DBC, returning a list of every spell
           that the code returns True for"""
        res = []
        regexp = __import__('re')
        for _, spell in self.spell_dbc.table.items():
            if eval(code,
                {'spell': spell, 're': regexp, 'spells': self}) == True:
                res.append(spell)
        return res

    def execute(self, code, result_id):
        """Exec code, handing over all spells, expecting a global variable
           of name in result_id to have a list of the ones to hand back to
           the caller"""
        scope = {'spells': self, 'dict': self.spell_dbc.table}
        exec(code, scope)
        return scope[result_id]

    def _mapping_for_vers(self, vers_str):
        if vers_str == '2.4.3':
            return _2_4_3_mappings()
        else:
            raise RuntimeError('Unsupported version "' + vers_str + '.')

    def _icon_mapping(self):
        return [dbc.Mapping(0, int, 'id'), dbc.Mapping(1, str, 'path')]

    def _duration_mapping(self):
        return [dbc.Mapping(0, int, 'id'),
                dbc.Mapping(1, int, 'duration'),
                dbc.Mapping(2, int, 'duration_per_level'),
                dbc.Mapping(3, int, 'max_duration')]

    def _range_mapping(self):
        return [dbc.Mapping(0, int,   'id'),
                dbc.Mapping(1, float, 'min'),
                dbc.Mapping(2, float, 'max')]

    def _radius_mapping(self):
        return [dbc.Mapping(0, int, 'id'), dbc.Mapping(1, int, 'radius')]

    def _casttime_mapping(self):
        return [dbc.Mapping(0, int, 'id'), dbc.Mapping(1, int, 'cast_time')]

def _2_4_3_mappings():
    return [
        dbc.Mapping(0,   int, 'id'),
        dbc.Mapping(1,   int, 'category'),
        dbc.Mapping(3,   int, 'dispel'),
        dbc.Mapping(4,   int, 'mechanic'),
        dbc.Mapping(5,   int, 'attr', count = 7),
        dbc.Mapping(12,  int, 'stances'),
        dbc.Mapping(13,  int, 'stances_not'),
        dbc.Mapping(22,  int, 'cast_time_index'),
        dbc.Mapping(34,  int, 'duration_index'),
        dbc.Mapping(40,  int, 'range_index'),
        dbc.Mapping(65,  int, 'effect', count = 3),
        dbc.Mapping(92,  int, 'eff_radius_index', count = 3),
        dbc.Mapping(124, int, 'icon_id'),
        dbc.Mapping(127, str, 'name'),
        dbc.Mapping(144, str, 'rank'),
    ]
