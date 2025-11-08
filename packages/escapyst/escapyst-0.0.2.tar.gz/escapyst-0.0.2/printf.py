#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# SPDX-FileCopyrightText: 2025 Jérôme Carretero <cJ-escapyst@zougloub.eu> & contributors
# SPDX-License-Identifier: MIT
# Escaping / unescaping for binary data using printf(1p)

"""

Encoding of arbitrary binary data in a format that is suitable
for the printf command-line utility (without additional arguments)
https://pubs.opengroup.org/onlinepubs/9799919799/utilities/printf.html

"""

from .c import (
 _encode,
 _decode,
)


def encode(b: bytes) -> str:
	"""
	:param b: binary data
	:return: printf argument
	"""
	return _encode(b, printf=True)


def decode(s: str, codec="utf-8", errors="strict") -> bytes:
	"""
	:param s: printf argument
	:return: binary data
	"""
	return _decode(s, codec=codec, errors=errors, printf=True)

