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

from .base import AiPacket


class ImPacket(AiPacket):
  """Im packet definition"""

  timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC), description='Timestamp of the packet')
  chat_id: UUID = Field(..., description='Chat ID')
  message: str = Field(..., description='Message content')

  @staticmethod
  def from_packet(raw: str) -> ImPacket:
    """Create a packet from raw data"""
    if not raw.startswith('<Im>') or not raw.endswith('</Im>'):
      raise MalformedException('Invalid packet definition, should be <Im>...</Im>')

    parts = raw[4:-5].split(';')
    if len(parts) != 4:
      raise MalformedException('Invalid packet definition, should have 4 parts')

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
      chat_id = UUID(parts[1])
    except ValueError as e:
      raise MalformedException('Invalid chat_id, should be a valid UUID') from e

    message = parts[2].replace('|||', ';')

    return ImPacket(
      timestamp=timestamp,
      chat_id=chat_id,
      message=message,
    )

  def to_packet(self: Self) -> str:
    """Convert packet to raw data"""
    raw = f'{int(self.timestamp.timestamp())};'
    raw += f'{str(self.chat_id)};'
    raw += f'{self.message.replace(";", "|||")};'

    crc = str(hex(calculate_crc(f'{raw}'.encode())))[2:].upper().zfill(4)
    return f'<Im>{raw}{crc}</Im>'

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
