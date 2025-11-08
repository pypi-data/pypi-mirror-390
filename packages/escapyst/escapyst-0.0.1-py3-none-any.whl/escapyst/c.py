#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# SPDX-FileCopyrightText: 2025 Jérôme Carretero <cJ-escapyst@zougloub.eu> & contributors
# SPDX-License-Identifier: MIT
# Escaping / unescaping for binary data using C string literals

"""

Encoding of arbitrary binary data in a format that is suitable
for C string literals.

Ref: ISO C § String literals

"""

import logging


logger = logging.getLogger(__name__)

def _get_buffer_view(in_bytes):
	mv = memoryview(in_bytes)
	if mv.ndim > 1 or mv.itemsize > 1:
		raise BufferError("object must be a single-dimension buffer of bytes.")
	return mv


ESCAPE_MAP = [f"\\x{i:02x}" for i in range(256)]

for i in range(256):
	octal = f"\\{i:o}"
	if len(octal) < len(ESCAPE_MAP[i]):
		ESCAPE_MAP[i] = octal

	c = chr(i)
	if c.isprintable() and i < 128:
		ESCAPE_MAP[i] = c

named_escapes = {
 ord('\n'): '\\n',
 ord('\t'): '\\t',
 ord('\r'): '\\r',
 ord('\b'): '\\b',
 ord('\f'): '\\f',
 ord('\v'): '\\v',
 ord('\a'): '\\a',
 ord('\\'): '\\\\',
 ord('"'): '\\"',
 ord("'"): "\\'",
}
for i, escape in named_escapes.items():
	ESCAPE_MAP[i] = escape

hexs = { _ for _ in b"0123456789abcdefABCDEF" }
octs = { _ for _ in b"01234567" }


ESCAPE_MAP_PRINTF = [ x for x in ESCAPE_MAP ]

named_escapes = {
 ord('$'): '\\$',
 ord("%"): "%%",
}

for i, escape in named_escapes.items():
	ESCAPE_MAP_PRINTF[i] = escape



def _encode(b: bytes, printf=False) -> str:
	"""
	Transform bytes into C printf-suitable strings
	"""

	if not printf:
		escape_map = ESCAPE_MAP
	else:
		escape_map = ESCAPE_MAP_PRINTF

	b = _get_buffer_view(b)
	s = []
	for idx_c, c in enumerate(b):
		x = escape_map[c]
		#logger.debug("at: %s %s", x, bytes(b[idx_c:]))
		if idx_c + 1 < len(b):
			# If there's a next character and we have a partial
			# hex/oct, we don't want to get the next character
			# to complete hex/oct representation
			if x.startswith("\\"):
				#logger.debug("next %s %s", x[1], b[idx_c+1])
				match x[1]:
					case 'x':
						if not printf:
							if b[idx_c+1] in hexs:
								x = f"\\x{c:02x}\"\""
						else:
							if (
							  len(x) < 4
							  and b[idx_c+1] in hexs
							 ):
								x = f"\\x{c:02x}"
					case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7':
						if not printf:
							if b[idx_c+1] in octs:
								x = f"\\x{c:02x}\"\""
						else:
							if (
							  len(x) < 5
							  and b[idx_c+1] in octs
							 ):
								x = f"\\x{c:02x}"

		s.append(x)

	return ''.join(s)


def _decode(s: str, codec="utf-8", errors="strict", printf=False) -> bytes:
	"""
	Transform C printf string into bytes
	"""

	unescaped = bytearray()
	i = 0
	n = len(s)
	while i < n:
		#logger.debug("at: %s", s[i:])
		if printf and s[i] == '%':
			if i + 1 < n and s[i+1] == '%':
				unescaped += b'%'
				i += 2
			else:
				raise ValueError(f"Invalid %-escape at position {i}")

		if not printf and s[i] == '"':
			if i + 1 < n and s[i+1] == '"':
				i += 2
			else:
				raise ValueError(f"Invalid \"-escape at position {i}")

		elif s[i] == '\\' and i + 1 < n:
			match s[i+1]:
				case 'n': unescaped += (b'\n'); i += 2
				case 't': unescaped += (b'\t'); i += 2
				case 'r': unescaped += (b'\r'); i += 2
				case 'b': unescaped += (b'\b'); i += 2
				case 'f': unescaped += (b'\f'); i += 2
				case 'v': unescaped += (b'\v'); i += 2
				case 'a': unescaped += (b'\a'); i += 2
				case '\'': unescaped += (b'\''); i += 2
				case '"': unescaped += (b'"'); i += 2
				case '\\': unescaped += (b'\\'); i += 2
				case '$': unescaped += (b'$'); i += 2
				case 'x':
					#logger.debug("hex: %s", s[i+1:])
					v = 0
					d = 0
					for j in range(2):
						p = i+1+1+j
						if p >= n:
							break
						x = s[p]
						try:
							v = v * 16 + int(x, 16)
							d += 1
						except Exception as e:
							raise
							break
					if d == 0:
						raise ValueError(f"Invalid hex escape at position {i}")
					unescaped.append(v)
					i += 2 + d
				case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7':
					#logger.debug("oct: %s", s[i+1:])
					v = int(s[i+1], 8)
					d = 1
					for j in range(2):
						p = i+1+1+j
						if p >= n:
							break
						x = s[p]
						try:
							v = v * 8 + int(x, 8)
							d += 1
						except ValueError:
							break
					if d == 0:
						raise ValueError(f"Invalid hex escape at position {i}")
					unescaped.append(v)
					i += 1 + d
				case c:
					if errors == "strict":
						raise ValueError(f"Invalid escape at position {i}")
					unescaped.append(ord(c))
					i += 2
		else:
			unescaped += s[i].encode(codec)
			i += 1
	return bytes(unescaped)




def encode(b: bytes) -> str:
	"""
	Transform bytes into C literal string
	"""
	return _encode(b, printf=False)


def decode(s: str, codec="utf-8", errors="strict") -> bytes:
	"""
	Transform C literal string into bytes
	"""
	return _decode(s, codec=codec, errors=errors, printf=False)

