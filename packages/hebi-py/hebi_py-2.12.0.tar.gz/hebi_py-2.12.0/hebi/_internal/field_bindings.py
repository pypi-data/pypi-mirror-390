# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2017-2019 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

from .ffi.enums import (FeedbackFloatField, FeedbackHighResAngleField,
                        FeedbackUInt64Field, FeedbackEnumField, FeedbackIoBankField)
from .ffi.wrappers import FieldDetails

import typing
if typing.TYPE_CHECKING:
  from .ffi.wrappers import NumberedFieldDetails


_feedback_scalars = [
    FeedbackFloatField.BoardTemperature,
    FeedbackFloatField.ProcessorTemperature,
    FeedbackFloatField.Voltage,
    FeedbackFloatField.Velocity,
    FeedbackFloatField.Effort,
    FeedbackFloatField.VelocityCommand,
    FeedbackFloatField.EffortCommand,
    FeedbackFloatField.Deflection,
    FeedbackFloatField.DeflectionVelocity,
    FeedbackFloatField.MotorVelocity,
    FeedbackFloatField.MotorCurrent,
    FeedbackFloatField.MotorSensorTemperature,
    FeedbackFloatField.MotorWindingCurrent,
    FeedbackFloatField.MotorWindingTemperature,
    FeedbackFloatField.MotorHousingTemperature,
    FeedbackFloatField.BatteryLevel,
    FeedbackFloatField.PwmCommand,
    FeedbackHighResAngleField.Position,
    FeedbackHighResAngleField.PositionCommand,
    FeedbackHighResAngleField.MotorPosition,
    FeedbackUInt64Field.SequenceNumber,
    FeedbackUInt64Field.ReceiveTime,
    FeedbackUInt64Field.TransmitTime,
    FeedbackUInt64Field.HardwareReceiveTime,
    FeedbackUInt64Field.HardwareTransmitTime,
    FeedbackUInt64Field.SenderId,
    FeedbackEnumField.TemperatureState,
    FeedbackEnumField.MstopState,
    FeedbackEnumField.PositionLimitState,
    FeedbackEnumField.VelocityLimitState,
    FeedbackEnumField.EffortLimitState,
    FeedbackEnumField.CommandLifetimeState,
    FeedbackEnumField.ArQuality,
    FeedbackIoBankField.A,
    FeedbackIoBankField.B,
    FeedbackIoBankField.C,
    FeedbackIoBankField.D,
    FeedbackIoBankField.E,
    FeedbackIoBankField.F]


_feedback_scalars_map: 'dict[str, FieldDetails | NumberedFieldDetails.Subfield]' = {}


def __add_fbk_scalars_field(field: 'FieldDetails | NumberedFieldDetails.Subfield'):
  for alias in field.aliases:
    _feedback_scalars_map[alias] = field


def __populate_fbk_scalars_map():
  for entry in _feedback_scalars:

    field = entry.field_details

    if field is None:
      # TODO: THIS IS TEMPORARY. FIX THIS BY DEFINING FIELD_DETAILS FOR ALL FIELDS ABOVE
      continue

    if isinstance(field, FieldDetails):
      # Will be an instance of `MessageEnum`
      __add_fbk_scalars_field(field)
    else:
      for sub_field in field.scalars.values():
        # Unspecified class type: will have all functionality of `MessageEnum`
        __add_fbk_scalars_field(sub_field)


__populate_fbk_scalars_map()


def get_field_info(field_name: str):
  """Get the info object representing the given field name.

  The field binder is a lambda which accepts a group feedback instance and returns the input field name

  :param field_name:
  :return:
  """
  if field_name not in _feedback_scalars_map:
    raise KeyError(field_name)

  return _feedback_scalars_map[field_name]