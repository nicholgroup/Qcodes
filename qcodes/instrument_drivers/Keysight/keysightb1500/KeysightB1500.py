from typing import Dict, Optional
from collections import defaultdict
import re

from qcodes import VisaInstrument
from .KeysightB1530A import B1530A
from .KeysightB1520A import B1520A
from .KeysightB1517A import B1517A
from .KeysightB1500_module import B1500Module
from .constants import SlotNr, ChannelList
from .message_builder import MessageBuilder


class KeysightB1500(VisaInstrument):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator="\r\n", **kwargs)

        self.by_slot = {}
        self.by_channel = {}
        self.by_class = defaultdict(list)

        self._find_modules()

    def add_module(self, name: str, module: B1500Module):
        super().add_submodule(name, module)

        self.by_class[module.INSTRUMENT_CLASS].append(module)
        self.by_slot[module.slot_nr] = module
        for ch in module.channels:
            self.by_channel[ch] = module

    def reset(self):
        """Performs an instrument reset.

        Does not reset error queue!
        """
        self.write("*RST")

    def get_status(self) -> int:
        return int(self.ask("*STB?"))

    # TODO: Data Output parser: At least for Format FMT1,0 and maybe for a
    # second (binary) format. 8 byte binary format would be nice because it
    # comes with time stamp
    # FMT1,0: ASCII (12 digits data with header) <CR/LF^EOI>

    def _find_modules(self):
        from .constants import UNT

        r = self.ask(MessageBuilder()
                     .unt_query(mode=UNT.Mode.MODULE_INFO_ONLY)
                     .message
                     )

        slot_population = parse_module_query_response(r)

        for slot_nr, model in slot_population.items():
            module = self.from_model_name(model, slot_nr, self)

            self.add_module(name=module.short_name, module=module)

    @staticmethod
    def from_model_name(model: str, slot_nr: int, parent: 'KeysightB1500',
                        name: Optional[str] = None) -> 'B1500Module':
        """
        Creates the correct instance type for instrument by model name.

        :param model: Model name such as 'B1517A'
        :param slot_nr: Slot number of this module (not channel numeber)
        :param parent: Reference to B1500 mainframe instance
        :param name: If `None` (Default) then the name is autogenerated from
            the instrument class.

        :return: A specific instance of `B1500Module`
        """
        if model == "B1517A":
            return B1517A(slot_nr=slot_nr, parent=parent, name=name)
        elif model == "B1520A":
            return B1520A(slot_nr=slot_nr, parent=parent, name=name)
        elif model == "B1530A":
            return B1530A(slot_nr=slot_nr, parent=parent, name=name)
        else:
            raise NotImplementedError("Module type not yet supported.")

    def enable_channels(self, channels: ChannelList = None):
        """
        Enables specified channels. If channels is omitted or `None`, all
        channels are enabled.
        """
        msg = MessageBuilder().cn(channels)

        self.write(msg.message)

    def disable_channels(self, channels: ChannelList = None):
        """
        Disables specified channels. If channels is omitted or `None`, all
        channels are disabled.
        """
        msg = MessageBuilder().cl(channels)

        self.write(msg.message)


def parse_module_query_response(response: str) -> Dict[SlotNr, str]:
    """
    Extract installed module info from str and return it as a dict.

    :param response: Response str to `UNT? 0` query.
    :return: Dict[SlotNr: model_name_str]
    """
    pattern = r";?(?P<model>\w+),(?P<revision>\d+)"

    moduleinfo = re.findall(pattern, response)

    return {
        SlotNr(slot_nr): model
        for slot_nr, (model, rev) in enumerate(moduleinfo, start=1)
        if model != "0"
    }
