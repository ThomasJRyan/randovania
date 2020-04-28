import dataclasses

import pytest

from randovania.game_description import data_reader
from randovania.generator import generator
from randovania.layout import configuration_factory
from randovania.layout.available_locations import AvailableLocationsConfiguration, RandomizationMode
from randovania.layout.hint_configuration import HintConfiguration
from randovania.layout.layout_configuration import LayoutConfiguration, LayoutDamageStrictness, LayoutElevators, \
    LayoutSkyTempleKeyMode
from randovania.layout.layout_description import LayoutDescription
from randovania.layout.permalink import Permalink
from randovania.layout.preset import Preset
from randovania.layout.starting_location import StartingLocation
from randovania.layout.translator_configuration import TranslatorConfiguration
from randovania.layout.trick_level import TrickLevelConfiguration
from randovania.resolver import resolver, debug


@pytest.mark.skip_resolver_tests
def test_resolver_with_log_file(test_files_dir):
    # Setup
    debug.set_level(0)

    description = LayoutDescription.from_file(test_files_dir.joinpath("log_files", "seed_a.json"))
    configuration = description.permalink.presets[0].layout_configuration
    patches = description.all_patches[0]

    # Run
    final_state_by_resolve = resolver.resolve(configuration=configuration,
                                              patches=patches)

    # Assert
    assert final_state_by_resolve is not None


def test_resolver_with_vanilla_layout(preset_manager, echoes_game_description):
    preset = preset_manager.default_preset
    vanilla_preset: Preset = dataclasses.replace(preset, layout_configuration=LayoutConfiguration(
        trick_level_configuration=TrickLevelConfiguration.default(),
        damage_strictness=LayoutDamageStrictness.STRICT,
        sky_temple_keys=LayoutSkyTempleKeyMode.NINE,
        elevators=LayoutElevators.VANILLA,
        starting_location=StartingLocation.with_elements([echoes_game_description.starting_location]),
        available_locations=AvailableLocationsConfiguration(RandomizationMode.FULL, frozenset()),
        major_items_configuration=configuration_factory.get_vanilla_major_items_configurations(),
        ammo_configuration=configuration_factory.get_default_ammo_configurations(),
        translator_configuration=TranslatorConfiguration(
            translator_requirement=configuration_factory.get_vanilla_actual_translator_configurations(),
            fixed_gfmc_compound=False,
            fixed_torvus_temple=False,
            fixed_great_temple=False,
        ),
        hints=HintConfiguration.default(),
    ))

    permalink = Permalink(
        seed_number=1000,
        spoiler=True,
        preset=vanilla_preset,
    )

    def status_report(x: str):
        pass

    patches = generator._create_randomized_patches(permalink, echoes_game_description, status_report)

    resolver_result = resolver.resolve(configuration=vanilla_preset.layout_configuration,
                                       game=echoes_game_description, patches=patches)
    assert resolver_result is not None
