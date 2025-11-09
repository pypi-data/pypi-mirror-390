class SpellCard:
    title: str
    description: str
    description_alignment: TextAlignment
    frame: str|None
    spell_image: str|None,
    additional_spell_images: list|None
    cost: SpellCost|None
    school_icon: str|None
    type_icon: str|None
    accuracy: str|None
    accuracy_colour: (int, int, int, int)|None
    booster_pack: str|None
    cloaked: bool
    no_pvp: bool
    no_pve: bool
    pierce: int
    level_requirement: int
    cannot_discard: bool
    essence_collection: bool
    single_use: bool
    def __new__(title = "",
    description = "",
    description_alignment = TextAlignment.center(),
    frame = None,
    spell_image = None,
    additional_spell_images = None,
    cost = SpellCost(0, False, 0, 0, 0, 0, 0, 0, 0, 0),
    school_icon = None,
    type_icon = None,
    accuracy = '0%',
    accuracy_colour = None,
    booster_pack = None,
    cloaked = False,
    no_pvp = False,
    no_pve = False,
    pierce = 0,
    level_requirement = 0,
    cannot_discard = False,
    essence_collection = False,
    single_use = False) -> SpellCard: ...

class TextAlignment:
    def center() -> TextAlignment:
        ...
    def left() -> TextAlignment:
        ...

class CardFactory:
    def __new__(settings: CardFactorySettings) -> CardFactory:
        ...

class CardFactorySettings:
    assets_path: str
    glyph_defs_path: str
    spell_title_font_path: str
    spell_description_font_path: str
    shadow_school_pip_path: str
    balance_school_pip_path: str
    death_school_pip_path: str
    fire_school_pip_path: str
    ice_school_pip_path: str
    life_school_pip_path: str
    myth_school_pip_path: str
    storm_school_pip_path: str
    rank_number_icons: [str]
    "rank_number_icons expects 21 pictures 0-20"
    rank_minus_icon: str
    rank_plus_icon: str
    rank_x_icon: str
    cloak_icon: str
    cloak_frame_icon: str
    pvp_only_icon: str
    pve_only_icon: str
    banned_icon: str
    single_use_icon: str
    cannot_discard_icon: str
    essence_collection_icon: str
    pierce_icon: str
    pierce_frame_icon: str
    level_requirement_icon: str
    default_icon_size: (int, int)
    default_wide_icon_size: (int, int)
    cache_madlibs: bool
    def __new__(assets_path = "", 
        glyph_defs_path = "", 
        spell_title_font_path = "", 
        spell_description_font_path = "",
        shadow_school_pip_path = "",
        balance_school_pip_path = "",
        death_school_pip_path = "",
        fire_school_pip_path = "",
        ice_school_pip_path = "",
        life_school_pip_path = "",
        myth_school_pip_path = "",
        storm_school_pip_path = "",
        rank_number_icons = [],
        rank_minus_icon = "",
        rank_plus_icon = "",
        rank_x_icon = "",
        cloak_icon = "",
        cloak_frame_icon = "",
        pvp_only_icon = "",
        pve_only_icon = "",
        banned_icon = "",
        single_use_icon = "",
        cannot_discard_icon = "",
        essence_collection_icon = "",
        pierce_icon = "",
        pierce_frame_icon = "",
        level_requirement_icon = "",
        default_icon_size = (16, 16), # For reference: old icon size was (20, 20)
        default_wide_icon_size = (32, 16), # (40, 20) for old wide icons
        cache_madlibs = True) -> CardFactorySettings:
        ...

class CardImage:
    def save(self, path: str):
        """
        Saves the image to the given path.

        :param path: The path to save the image to, do note the extension matters.
        """
        ...
    def to_memory(self):
        """
        Writes the image to a webp format in memory and returns the buffer.
        """

class SpellCost:
    base_cost: int
    variable_cost: bool
    shadow: int
    balance: int
    death: int
    fire: int
    ice: int
    life: int
    myth: int
    storm: int
    def __new__(base_cost = 0, variable_cost = False, shadow = 0, balance = 0, death = 0, fire = 0, ice = 0, life = 0, myth = 0, storm = 0) -> SpellCost:
        """
        Creates a new SpellCost object with the given parameters.

        :param base_cost: The base cost of the spell.
        :param variable_cost: Whether the spell has a variable cost.
        :param shadow: The shadow cost of the spell.
        :param balance: The balance cost of the spell.
        :param death: The death cost of the spell.
        :param fire: The fire cost of the spell.
        :param ice: The ice cost of the spell.
        :param life: The life cost of the spell.
        :param myth: The myth cost of the spell.
        :param storm: The storm cost of the spell.
        """
        ...