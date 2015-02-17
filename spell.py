import dbc
import os
import struct

class Spell:
    def effect(self, e):
        pass

class Spells:
    def __init__(self, vers_str):
        hp = os.path.expanduser('~/.ssi/' + vers_str)
        spell_path = os.path.join(hp, 'Spell.dbc')
        spell_icon_path = os.path.join(hp, 'SpellIcon.dbc')
        spell_duration_path = os.path.join(hp, 'SpellDuration.dbc')
        spell_range_path = os.path.join(hp, 'SpellRange.dbc')
        spell_radius_path = os.path.join(hp, 'SpellRadius.dbc')
        spell_casttime_path = os.path.join(hp, 'SpellCastTimes.dbc')

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

    def _radius(self, spell, i):
        try:
            v = self.spell_radius_dbc.table[spell.radius_index[i]].radius
            return int(v) if v.is_integer() else v
        except KeyError:
            return 0

    def radius(self, spell):
        """Returns list of radii of spell effects"""
        return [self._radius(spell, 0), self._radius(spell, 1),
                self._radius(spell, 2)]

    def cast_time(self, spell):
        """Returns cast time of spell"""
        try:
            return self.spell_casttime_dbc.table[
                spell.cast_time_index].cast_time
        except KeyError:
            return 0

    def schools(self, spell):
        """Returns list of school strings"""
        l = ['physical', 'holy', 'fire', 'nature', 'frost', 'shadow', 'arcane']
        mask = self.spell_dbc.table[spell.id].school_mask
        res = []
        for i in range(0, 7):
            if mask & (1 << i):
                res.append(l[i])
        return res
    
    def power_type(self, spell):
        """Returns string representation of power type"""
        if spell.power_type == 0xFFFFFFFE:
            return 'health'
        return [
            'mana', 'rage', 'focus', 'energy', 'happiness'][spell.power_type]

    def formula(self, spell, eff):
        """Returns string representation of base points formula"""
        # XXX: spell attr calc level

        base = spell.base_points[eff] + spell.base_dice[eff]
        rng = spell.die_sides[eff]
        real_per_level = spell.real_points_per_level[eff]
        per_cp = spell.points_per_cp[eff]

        s = str(base)
        surround = False
        if rng > 1:
            s += " to " + str(base + rng)
            surround = True # If any per is added, put ( and ) around expr
        if real_per_level > 0:
            if surround:
                s = '(' + s + ') + ' + '%.2f' % real_per_level + ' * level'
                surround = False
            else:
                s += ' + %.2f' % real_per_level + ' * level'
        if per_cp > 0:
            if surround:
                s = '(' + s + ') + ' + ' %.2f' % per_cp + ' * ComboPoints'
                surround = False
            else:
                s += ' + %.2f' % per_cp + ' * ComboPoints'

        return s

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
        return [dbc.Mapping(0, 'int', 'id'), dbc.Mapping(1, 'str', 'path')]

    def _duration_mapping(self):
        return [dbc.Mapping(0, 'int', 'id'),
                dbc.Mapping(1, 'int', 'duration'),
                dbc.Mapping(2, 'int', 'duration_per_level'),
                dbc.Mapping(3, 'int', 'max_duration')]

    def _range_mapping(self):
        return [dbc.Mapping(0, 'int',   'id'),
                dbc.Mapping(1, 'float', 'min'),
                dbc.Mapping(2, 'float', 'max')]

    def _radius_mapping(self):
        return [dbc.Mapping(0, 'int', 'id'), dbc.Mapping(1, 'float', 'radius')]

    def _casttime_mapping(self):
        return [dbc.Mapping(0, 'int', 'id'), dbc.Mapping(1, 'int', 'cast_time')]

def _2_4_3_mappings():
    return [
        dbc.Mapping(0,   'int',   'id'),
        dbc.Mapping(1,   'int',   'category'),
        dbc.Mapping(3,   'int',   'dispel'),
        dbc.Mapping(4,   'int',   'mechanic'),
        dbc.Mapping(5,   'int',   'attr', count = 7),
        dbc.Mapping(12,  'int',   'stances'),
        dbc.Mapping(13,  'int',   'stances_not'),
        dbc.Mapping(14,  'int',   'target_mask'),
        dbc.Mapping(22,  'int',   'cast_time_index'),
        dbc.Mapping(23,  'int',   'cooldown'),
        dbc.Mapping(24,  'int',   'category_cooldown'),
        dbc.Mapping(25,  'int',   'interrupt_flags'),
        dbc.Mapping(26,  'int',   'aura_interrupt_flags'),
        dbc.Mapping(27,  'int',   'channel_interrupt_flags'),
        dbc.Mapping(28,  'int',   'proc_flags'),
        dbc.Mapping(29,  'int',   'proc_chance'),
        dbc.Mapping(30,  'int',   'proc_charges'),
        dbc.Mapping(31,  'int',   'max_level'),
        dbc.Mapping(32,  'int',   'base_level'),
        dbc.Mapping(33,  'int',   'level'),
        dbc.Mapping(34,  'int',   'duration_index'),
        dbc.Mapping(35,  'int',   'power_type'),
        dbc.Mapping(36,  'int',   'power'),
        dbc.Mapping(40,  'int',   'range_index'),
        dbc.Mapping(62,  'sint',  'equipped_class'),
        dbc.Mapping(63,  'int',   'equipped_submask'),
        dbc.Mapping(64,  'int',   'equipped_invmask'),
        dbc.Mapping(65,  'int',   'effect', count = 3),
        dbc.Mapping(68,  'int',   'die_sides', count = 3),
        dbc.Mapping(71,  'int',   'base_dice', count = 3),
        dbc.Mapping(77,  'float', 'real_points_per_level', count = 3),
        dbc.Mapping(80,  'sint',  'base_points', count = 3),
        dbc.Mapping(83,  'sint',  'mechanic_effect', count = 3),
        dbc.Mapping(86,  'int',   'target_a', count = 3),
        dbc.Mapping(89,  'int',   'target_b', count = 3),
        dbc.Mapping(92,  'int',   'radius_index', count = 3),
        dbc.Mapping(95,  'int',   'aura', count = 3),
        dbc.Mapping(98,  'int',   'amplitude', count = 3),
        dbc.Mapping(101, 'float', 'multiple_value', count = 3),
        dbc.Mapping(104, 'int',   'chain', count = 3),
        dbc.Mapping(110, 'int',   'misc_a', count = 3),
        dbc.Mapping(113, 'int',   'misc_b', count = 3),
        dbc.Mapping(116, 'int',   'trigger', count = 3),
        dbc.Mapping(119, 'float', 'points_per_cp', count = 3),
        dbc.Mapping(124, 'int',   'icon_id'),
        dbc.Mapping(127, 'str',   'name'),
        dbc.Mapping(144, 'str',   'rank'),
        dbc.Mapping(178, 'str',   'tooltip'),
        dbc.Mapping(196, 'int',   'gcd_category'),
        dbc.Mapping(197, 'int',   'gcd'),
        dbc.Mapping(198, 'int',   'max_target_level'),
        dbc.Mapping(199, 'int',   'spell_family'),
        dbc.Mapping(200, 'long',  'spell_mask'),
        dbc.Mapping(202, 'int',   'max_targets'),
        dbc.Mapping(203, 'int',   'dmg_class'),
        dbc.Mapping(204, 'int',   'prevention'),
        dbc.Mapping(206, 'float', 'dmg_multiplier', count = 3),
        dbc.Mapping(215, 'int',   'school_mask'),
    ]
