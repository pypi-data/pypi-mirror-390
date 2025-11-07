"""Test Client Packets"""

from datetime import datetime
from uuid import UUID

import pytest

from layrz_protocol.constants import UTC
from layrz_protocol.packets import ImPacket


def test6_im() -> None:
  packet = ImPacket(
    chat_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
    timestamp=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
    message='Hello; World',
  )

  str_packet = packet.to_packet()
  assert isinstance(str_packet, str)
  assert str_packet == '<Im>1735689600;123e4567-e89b-12d3-a456-426614174000;Hello||| World;29D0</Im>'

  parsed_packet = ImPacket.from_packet(str_packet)
  assert isinstance(parsed_packet, ImPacket)
  assert parsed_packet.chat_id == packet.chat_id
  assert parsed_packet.timestamp == packet.timestamp
  assert parsed_packet.message == packet.message


if __name__ == '__main__':
  pytest.main([__file__])
  # test6_im()
