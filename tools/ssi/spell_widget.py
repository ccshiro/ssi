import os
import urllib.parse
import urllib.request
from PyQt4 import QtCore, QtGui, QtWebKit, uic

class SpellWidget(QtWebKit.QWebView):
    def __init__(self, parent, spell, icons, spells):
        """
        parameters:
           parent: widget
           spell:  spell we're displaying
           icons:  to load icons from wowhead or not
           spells: spell.Spells object
        """
        super().__init__(parent)
        self.spell = spell
        self.icons = icons
        self.spells = spells
        
        # Note: The documentation says that external css should be located
        #       relative to baseUrl, but even when it is, it's not loaded. Not
        #       sure why not. We get around that like this.
        csspath = os.path.join('..', os.path.join('..',
            os.path.join('bootstrap', os.path.join('css'),
            os.path.join('bootstrap.min.css'))))
        self.css_url = QtCore.QUrl.fromLocalFile(os.path.abspath(csspath))
        self.load_html() 
        self.setHtml(self.html)
        self.settings().setUserStyleSheetUrl(self.css_url)

    def preferred_title(self):
        return str(self.spell.id)

    def load_html(self):
        """Load template and replace placeholders"""
        self.html = ''
        page = open('template.html')
        for line in page.readlines():
            self.html += line
        self.expand_placeholders()
        page.close()

    def _replace(self, dic):
        for i, j in dic.items():
            self.html = self.html.replace(i, str(j))

    def _human_time(self, ms):
        if ms == 0xFFFFFFFF:
            return "Infinite"
        elif ms == 0:
            return "None"

        s = ms / 1000.0

        hours = int(s / 3600)
        s -= hours * 3600
        mins = int(s / 60)
        s -= mins * 60
        secs = int(s) if s.is_integer() else s

        out = ""
        if hours > 0:
            out += str(hours) + (" hour" if hours == 1 else " hours")
        if mins > 0:
            out += (" " if len(out) > 0 else "")
            out += str(mins) + (" minute" if mins == 1 else " minutes")
        if secs > 0:
            out += (" " if len(out) > 0 else "")
            out += str(secs) + (" second" if secs == 1 else " seconds")
        return out

    def expand_placeholders(self):
        """Parses HTML, replacing placeholders"""
        icon_path = ''
        if self.icons:
            icon = self.spells.icon_path(self.spell).split('\\')[-1]
            icon_path = 'http://static.wowhead.com/images/wow/icons/large/'
            icon_path += icon.lower() + '.jpg'
        else:
            icon_path = urllib.parse.urljoin('file:',
                urllib.request.pathname2url(os.path.abspath('no_icon.png')))

        self._replace({
            # CSS
            '${BOOTSTRAP_CSS}': self.css_url.toString(),
            # Spell
            '${NAME}': self.spell.name,
            '${ID}': self.spell.id,
            '${TOOLTIP}': self.spell.tooltip,
            '${RANK}': self.spell.rank,
            '${ICON}': icon_path,
            # Basic
            '${DURATION_INDEX}': self.spell.duration_index,
            '${DURATION_HUMAN}':
                self._human_time(self.spells.duration(self.spell)),
            '${RANGE_INDEX}': self.spell.range_index,
            '${RANGE_MIN}': int(self.spells.range(self.spell).min),
            '${RANGE_MAX}': int(self.spells.range(self.spell).max),
            '${CAST_TIME_INDEX}': self.spell.cast_time_index,
            '${CAST_TIME_HUMAN}':
                self._human_time(self.spells.cast_time(self.spell)),
            '${POWER}': self.spell.power,
            '${POWER_TYPE}': self.spells.power_type(self.spell),
            '${LEVEL}': self.spell.level,
            '${BASE_LEVEL}': self.spell.base_level,
            '${MAX_LEVEL}': self.spell.max_level,
            '${SCHOOL_MASK}': hex(self.spell.school_mask),
            '${SCHOOLS}': ', '.join(self.spells.schools(self.spell)),
            '${COOLDOWN}': self._human_time(self.spell.cooldown),
            '${GCD}': self._human_time(self.spell.gcd),
            # Advanced
            '${CATEGORY}': self.spell.category,
            '${CATEGORY_COOLDOWN}':
                self._human_time(self.spell.category_cooldown),
            '${GCD_CATEGORY}': self.spell.gcd_category,
            '${DISPEL_TYPE}': self.spell.dispel,
            '${DISPEL_TYPE_STR}': self.spells.enum_val('dispels',
                self.spell.dispel),
            '${CLASS}': self.spell.spell_class,
            '${CLASS_STR}': self.spells.enum_val('spell_class',
                self.spell.spell_class),
            '${PREVENTION_TYPE}': self.spell.prevention,
            '${PREVENTION_TYPE_STR}':
                self.spells.enum_val('preventions', self.spell.prevention),
            '${MECHANIC}': self.spell.mechanic,
            '${MECHANIC_STR}': self.spells.enum_val('mechanics',
                self.spell.mechanic),
            '${TARGET_MASK}': hex(self.spell.target_mask),
            '${TARGET_MASK_STR}': self.spells.enum_mask(
                'target_flags', self.spell.target_mask),
            '${STANCES}': hex(self.spell.stances),
            '${STANCES_STR}': self.spells.enum_mask(
                'stances', self.spell.stances, 1),
            '${STANCES_NOT}': hex(self.spell.stances_not),
            '${STANCES_NOT_STR}': self.spells.enum_mask(
                'stances', self.spell.stances_not, 1),
            '${SPELL_FAMILY}': self.spell.spell_family,
            '${SPELL_FAMILY_STR}': self.spells.enum_val('families',
                self.spell.spell_family),
            '${SPELL_MASK}': hex(self.spell.spell_mask),
            '${MAX_TARGET_LEVEL}': self.spell.max_target_level,
            '${MAX_TARGETS}': self.spell.max_targets,
            '${EQUIPPED_ITEM_CLASS}': self.spell.item_class,
            '${EQUIPPED_ITEM_CLASS_STR}': self.spells.enum_val(
                'item_class', self.spell.item_class),
            '${EQUIPPED_ITEM_SUBCLASS}': hex(self.spell.item_subclass),
            '${EQUIPPED_ITEM_SUBCLASS_STR}': self.spells.enum_mask(
                'sub_class', self.spell.item_subclass,
                2, self.spell.item_class),
            '${EQUIPPED_ITEM_INVMASK}': hex(self.spell.inv_slot),
            '${EQUIPPED_ITEM_INVMASK_STR}': self.spells.enum_mask(
                'inv_slots' ,self.spell.inv_slot, 2),
            '${PROC_CHANCE}': self.spell.proc_chance,
            '${PROC_FLAGS}': hex(self.spell.proc_flags),
            '${PROC_FLAGS_STR}': self.spells.enum_mask('proc_flags',
                self.spell.proc_flags),
            '${PROC_CHARGES}': self.spell.proc_charges,
            '${INTERRUPT_FLAGS}': hex(self.spell.interrupt_flags),
            '${INTERRUPT_FLAGS_STR}': self.spells.enum_mask('interrupts',
                self.spell.interrupt_flags),
            '${AURA_INTERRUPT_FLAGS}': hex(self.spell.aura_interrupt_flags),
            '${AURA_INTERRUPT_FLAGS_STR}': self.spells.enum_mask(
                'aura_interrupts', self.spell.aura_interrupt_flags),
            '${CHANNEL_INTERRUPT_FLAGS}':
                hex(self.spell.channel_interrupt_flags),
            '${CHANNEL_INTERRUPT_FLAGS_STR}': self.spells.enum_mask(
                'channel_interrupts', self.spell.channel_interrupt_flags),
            '${ICON_ID}': self.spell.icon_id,
            '${ICON_PATH}': self.spells.icon_path(self.spell),
            '${ATTR0}': hex(self.spell.attr[0]),
            '${ATTR0_STR}': self.spells.enum_mask('attr0', self.spell.attr[0]),
            '${ATTR1}': hex(self.spell.attr[1]),
            '${ATTR1_STR}': self.spells.enum_mask('attr1', self.spell.attr[1]),
            '${ATTR2}': hex(self.spell.attr[2]),
            '${ATTR2_STR}': self.spells.enum_mask('attr2', self.spell.attr[2]),
            '${ATTR3}': hex(self.spell.attr[3]),
            '${ATTR3_STR}': self.spells.enum_mask('attr3', self.spell.attr[3]),
            '${ATTR4}': hex(self.spell.attr[4]),
            '${ATTR4_STR}': self.spells.enum_mask('attr4', self.spell.attr[4]),
            '${ATTR5}': hex(self.spell.attr[5]),
            '${ATTR5_STR}': self.spells.enum_mask('attr5', self.spell.attr[5]),
            '${ATTR6}': hex(self.spell.attr[6]),
            '${ATTR6_STR}': self.spells.enum_mask('attr6', self.spell.attr[6]),
            # Effect 0
            '${EFF0_EFFECT}': self.spell.effect[0],
            '${EFF0_EFFECT_STR}': self.spells.enum_val('effects',
                self.spell.effect[0]),
            '${EFF0_FORMULA}': self.spells.formula(self.spell, 0),
            '${EFF0_MULTIPLE_VALUE}': '%.2f' % self.spell.multiple_value[0],
            '${EFF0_DMG_MULTIPLIER}': '%.2f' % self.spell.dmg_multiplier[0],
            '${EFF0_AURA}': self.spell.aura[0],
            '${EFF0_AURA_STR}': self.spells.enum_val('auras',
                self.spell.aura[0]),
            '${EFF0_AMPLITUDE}': self.spell.amplitude[0],
            '${EFF0_TARGET_A}': self.spell.target_a[0],
            '${EFF0_TARGET_A_STR}':
                self.spells.enum_val('targets', self.spell.target_a[0]),
            '${EFF0_TARGET_B}': self.spell.target_b[0],
            '${EFF0_TARGET_B_STR}':
                self.spells.enum_val('targets', self.spell.target_b[0]),
            '${EFF0_RADIUS}': self.spells.radius(self.spell)[0],
            '${EFF0_RADIUS_INDEX}': self.spell.radius_index[0],
            '${EFF0_CHAIN}': self.spell.chain[0],
            '${EFF0_MISC_A}': self.spell.misc_a[0],
            '${EFF0_MISC_B}': self.spell.misc_b[0],
            '${EFF0_TRIGGER}': self.spell.trigger[0],
            '${EFF0_MECHANIC}': self.spell.mechanic_effect[0],
            '${EFF0_MECHANIC_STR}': self.spells.enum_val('mechanics',
                self.spell.mechanic_effect[0]),
            # Effect 1
            '${EFF1_EFFECT}': self.spell.effect[1],
            '${EFF1_EFFECT_STR}': self.spells.enum_val('effects',
                self.spell.effect[1]),
            '${EFF1_FORMULA}': self.spells.formula(self.spell, 1),
            '${EFF1_MULTIPLE_VALUE}': '%.2f' % self.spell.multiple_value[1],
            '${EFF1_DMG_MULTIPLIER}': '%.2f' % self.spell.dmg_multiplier[1],
            '${EFF1_AURA}': self.spell.aura[1],
            '${EFF1_AURA_STR}': self.spells.enum_val('auras',
                self.spell.aura[1]),
            '${EFF1_AMPLITUDE}': self.spell.amplitude[1],
            '${EFF1_TARGET_A}': self.spell.target_a[1],
            '${EFF1_TARGET_A_STR}':
                self.spells.enum_val('targets', self.spell.target_a[1]),
            '${EFF1_TARGET_B}': self.spell.target_b[1],
            '${EFF1_TARGET_B_STR}':
                self.spells.enum_val('targets', self.spell.target_b[1]),
            '${EFF1_RADIUS}': self.spells.radius(self.spell)[1],
            '${EFF1_RADIUS_INDEX}': self.spell.radius_index[1],
            '${EFF1_CHAIN}': self.spell.chain[1],
            '${EFF1_MISC_A}': self.spell.misc_a[1],
            '${EFF1_MISC_B}': self.spell.misc_b[1],
            '${EFF1_TRIGGER}': self.spell.trigger[1],
            '${EFF1_MECHANIC}': self.spell.mechanic_effect[1],
            '${EFF1_MECHANIC_STR}': self.spells.enum_val('mechanics',
                self.spell.mechanic_effect[1]),
            # Effect 2
            '${EFF2_EFFECT}': self.spell.effect[2],
            '${EFF2_EFFECT_STR}': self.spells.enum_val('effects',
                self.spell.effect[2]),
            '${EFF2_FORMULA}': self.spells.formula(self.spell, 2),
            '${EFF2_MULTIPLE_VALUE}': '%.2f' % self.spell.multiple_value[2],
            '${EFF2_DMG_MULTIPLIER}': '%.2f' % self.spell.dmg_multiplier[2],
            '${EFF2_AURA}': self.spell.aura[2],
            '${EFF2_AURA_STR}': self.spells.enum_val('auras',
                self.spell.aura[2]),
            '${EFF2_AMPLITUDE}': self.spell.amplitude[2],
            '${EFF2_TARGET_A}': self.spell.target_a[2],
            '${EFF2_TARGET_A_STR}':
                self.spells.enum_val('targets', self.spell.target_a[2]),
            '${EFF2_TARGET_B}': self.spell.target_b[2],
            '${EFF2_TARGET_B_STR}':
                self.spells.enum_val('targets', self.spell.target_b[2]),
            '${EFF2_RADIUS}': self.spells.radius(self.spell)[2],
            '${EFF2_RADIUS_INDEX}': self.spell.radius_index[2],
            '${EFF2_CHAIN}': self.spell.chain[2],
            '${EFF2_MISC_A}': self.spell.misc_a[2],
            '${EFF2_MISC_B}': self.spell.misc_b[2],
            '${EFF2_TRIGGER}': self.spell.trigger[2],
            '${EFF2_MECHANIC}': self.spell.mechanic_effect[2],
            '${EFF2_MECHANIC_STR}': self.spells.enum_val('mechanics',
                self.spell.mechanic_effect[2]),
        })
