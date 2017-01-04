# code for example notebook

import math

from qcodes import MockInstrument, MockModel, Parameter, Loop, DataArray
from qcodes.utils.validators import Numbers


class RModel(MockModel):
    def __init__(self):
        self._gate = 1
        self._bias = 0
        self._resistance=1e9*(1.1-self._gate)
        super().__init__()

    def _update_resistance(self):
        self._resistance=1e9*(1.1-self._gate)


    def _output(self):
        # this model is just a resistor
        g=self._bias/self._resistance*1e9
        return g

    def fmt(self, value):
        return '{:.3f}'.format(value)

    def gate_set(self, parameter, value):
        if parameter == 'g':
            self._gate = float(value)
        elif parameter == 'rst' and value is None:
            self._gate = 0
        else:
            raise ValueError
        self._update_resistance()

    def gate_get(self, parameter):
        if parameter[0] == 'g':
            return self.fmt(self._gate)
        else:
            raise ValueError

    def bias_set(self, parameter, value):
        if parameter == 'b':
            self._bias = float(value)
        else:
            raise ValueError
        self._update_resistance()

    def bias_get(self, parameter):
        if parameter == 'b':
            return self.fmt(self._bias)
        else:
            raise ValueError

    def current_get(self, parameter):
        if parameter == 'c':
            return self.fmt(self._output())
        else:
            raise ValueError


# make our mock instruments
# real instruments would subclass IPInstrument or VisaInstrument
# or just the base Instrument instead of MockInstrument,
# and be instantiated with an address rather than a model
class MockGate(MockInstrument):
    def __init__(self, name, model=None, **kwargs):
        super().__init__(name, model=model, **kwargs)

        self.add_parameter('gate',
                           label='Gate Channel (V)',
                           get_cmd='g?',
                           set_cmd='g:{:.4f}',
                           get_parser=float,
                           vals=Numbers(0, 1))

        self.add_function('reset', call_cmd='rst')


class MockBias(MockInstrument):
    def __init__(self, name, model=None, **kwargs):
        super().__init__(name, model=model, **kwargs)

        # this parameter uses built-in sweeping to change slowly
        self.add_parameter('bias',
                           label='Bias Voltage (V)',
                           get_cmd='b?',
                           set_cmd='b:{:.4f}',
                           get_parser=float,
                           vals=Numbers(0, 1))


class MockCurrent(MockInstrument):
    def __init__(self, name, model=None, **kwargs):
        super().__init__(name, model=model, **kwargs)

        self.add_parameter('current',
                           label='Current (A)',
                           get_cmd='c?',
                           get_parser=float,
                           vals=Numbers(0,1))
#
#class GetWithThreshold(Parameter)


class AverageGetter(Parameter):
    def __init__(self, measured_param, sweep_values, delay):
        super().__init__(name='avg_' + measured_param.name)
        self._instrument = getattr(measured_param, '_instrument', None)
        self.measured_param = measured_param
        self.sweep_values = sweep_values
        self.delay = delay
        if hasattr(measured_param, 'label'):
            self.label = 'Average: ' + measured_param.label

    def get(self):
        loop = Loop(self.sweep_values, self.delay).each(self.measured_param)
        data = loop.run_temp()
        array = data.arrays[self.measured_param.full_name]
        return array.mean()


class AverageAndRaw(Parameter):
    def __init__(self, measured_param, sweep_values, delay):
        name = measured_param.name
        super().__init__(names=(name, 'avg_' + name))
        self._instrument = getattr(measured_param, '_instrument', None)
        self.measured_param = measured_param
        self.sweep_values = sweep_values
        self.delay = delay
        self.shapes = ((len(sweep_values),), None)
        set_array = DataArray(parameter=sweep_values.parameter,
                              preset_data=sweep_values)
        self.setpoints = ((set_array,), None)
        if hasattr(measured_param, 'label'):
            self.labels = (measured_param.label,
                           'Average: ' + measured_param.label)

    def get(self):
        loop = Loop(self.sweep_values, self.delay).each(self.measured_param)
        data = loop.run_temp()
        array = data.arrays[self.measured_param.full_name]
        return (array, array.mean())


class ArrayGetter(Parameter):
    """
    Example parameter that just returns a single array
    TODO: in theory you can make this same Parameter with
    name, label & shape (instead of names, labels & shapes) and altered
    setpoints (not wrapped in an extra tuple) and this mostly works,
    but when run in a loop it doesn't propagate setpoints to the
    DataSet. We could track down this bug, but perhaps a better solution
    would be to only support the simplest and the most complex Parameter
    forms (ie cases 1 and 5 in the Parameter docstring) and do away with
    the intermediate forms that make everything more confusing.
    """
    def __init__(self, measured_param, sweep_values, delay):
        name = measured_param.name
        super().__init__(names=(name,))
        self._instrument = getattr(measured_param, '_instrument', None)
        self.measured_param = measured_param
        self.sweep_values = sweep_values
        self.delay = delay
        self.shapes = ((len(sweep_values),),)
        set_array = DataArray(parameter=sweep_values.parameter,
                              preset_data=sweep_values)
        self.setpoints = ((set_array,),)
        if hasattr(measured_param, 'label'):
            self.labels = (measured_param.label,)

    def get(self):
        loop = Loop(self.sweep_values, self.delay).each(self.measured_param)
        data = loop.run_temp()
        array = data.arrays[self.measured_param.full_name]
        return (array,)
