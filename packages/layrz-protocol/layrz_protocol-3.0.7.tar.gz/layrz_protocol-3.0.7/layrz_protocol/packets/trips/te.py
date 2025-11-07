from __future__ import annotations

import sys
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from pydantic import Field, field_validator

from layrz_protocol.constants import UTC
from layrz_protocol.utils import CrcException, MalformedException, calculate_crc

from .base import TripPacket


class TePacket(TripPacket):
  """Te packet definition"""

  timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), description='Timestamp of the packet')
  trip_id: UUID = Field(..., description='Trip ID')
  distance_traveled: float = Field(0.0, description='Distance traveled in meters')
  max_speed: float = Field(0.0, description='Maximum speed in km/h')
  duration: timedelta = Field(default_factory=lambda: timedelta(0), description='Duration of the trip')

  @staticmethod
  def from_packet(raw: str) -> TePacket:
    """Create a packet from raw data"""
    if not raw.startswith('<Te>') or not raw.endswith('</Te>'):
      raise MalformedException('Invalid packet definition, should be <Te>...</Te>')

    parts = raw[4:-5].split(';')
    if len(parts) != 6:
      raise MalformedException('Invalid packet definition, should have 6 parts')

    received_crc: int
    try:
      received_crc = int(parts[-1], base=16)
    except ValueError:
      received_crc = 0

    calculated_crc: int = calculate_crc(f'{";".join(parts[:-1])};'.encode())

    if received_crc != calculated_crc:
      raise CrcException('Invalid CRC', received=received_crc, calculated=calculated_crc)

    try:
      timestamp = datetime.fromtimestamp(int(parts[0]), tz=UTC)
    except ValueError as e:
      raise MalformedException('Invalid timestamp, should be an int or float') from e

    try:
      trip_id = UUID(parts[1])
    except ValueError as e:
      raise MalformedException('Invalid trip_id, should be a valid UUID') from e

    try:
      distance_traveled = float(parts[2])
    except ValueError as e:
      raise MalformedException('Invalid distance_traveled, should be a float') from e
    try:
      max_speed = float(parts[3])
    except ValueError as e:
      raise MalformedException('Invalid max_speed, should be a float') from e
    try:
      duration = timedelta(seconds=int(parts[4]))
    except ValueError as e:
      raise MalformedException('Invalid duration, should be a int representing seconds') from e

    return TePacket(
      timestamp=timestamp,
      distance_traveled=distance_traveled,
      max_speed=max_speed,
      duration=duration,
      trip_id=trip_id,
    )

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};'
    raw += f'{str(self.trip_id)};'
    raw += f'{self.distance_traveled:.3f};'
    raw += f'{self.max_speed:.3f};'
    raw += f'{int(self.duration.total_seconds())};'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Te>{raw}{crc}</Te>'

  def __str__(self: Self) -> str:
    """String representation of the packet"""
    return self.to_packet()

  @field_validator('timestamp', mode='before')
  def _validate_timestamp(cls, value: Any) -> datetime:
    """Validate timestamp"""
    if value is None:
      return datetime.now(tz=UTC)

    if isinstance(value, (int, float)):
      return datetime.fromtimestamp(value, tz=UTC)

    if isinstance(value, datetime):
      return value

    return datetime.fromtimestamp(value, tz=UTC)
