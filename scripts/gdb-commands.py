#!/usr/bin/env python3

import pefile
import os

class FindUefiMain(gdb.Command):
	def __init__(self):
		super(FindUefiMain, self).__init__("find-uefi-main", gdb.COMMAND_USER)

	def invoke(self, arg, from_tty):
		for t in gdb.selected_inferior().threads():
			if not (t.is_running() or t.is_stopped()):
				continue
			t.switch()
			if gdb.newest_frame().function() and gdb.newest_frame().function().name.startswith('eirUefiMain('):
				ready_var, _ = gdb.lookup_symbol('eir_gdb_ready')
				if not ready_var:
					print("warning: could not find 'eir_gdb_ready'")
				else:
					gdb.execute("set eir_gdb_ready=1")

				print(f"info: UEFI running on thread {t.num}")
				return

		print("error: could not find correct thread")
		return

class LoadPE(gdb.Command):
	def __init__(self):
		super(LoadPE, self).__init__("loadpe", gdb.COMMAND_USER)

	def usage(self):
		print("usage: loadpe <image base address> <PE executable> [ELF executable]")

	def invoke(self, arg, from_tty):
		args = arg.split(' ')

		if len(args) not in range(2, 4):
			self.usage()
			return

		try:
			image_base = int(args[0], 16)
		except ValueError:
			self.usage()
			return

		if not os.path.isfile(args[1]):
			print(f"file '{args[1]}' does not exist")
			return

		pe_path = args[1]
		symbol_file_path = pe_path

		if len(args) > 2:
			if not os.path.isfile(args[2]):
				print(f"file '{args[2]}' does not exist")
				return

			symbol_file_path = args[2]

		with open(pe_path, "rb") as f:
			data = f.read()
		pe = pefile.PE(data=data)
		sections = {}

		st_offset = pe.FILE_HEADER.PointerToSymbolTable + (pe.FILE_HEADER.NumberOfSymbols * 18)

		for section in pe.sections:
			name = section.Name.strip(b"\x00").decode("utf-8")

			if name.startswith("/"):
				offset = int(name[1:])
				new_name = pe.get_string_from_data(st_offset + offset, data).decode("ascii")
				name = new_name

			if name == ".reloc":
				continue

			if name.startswith("."):
				sections[name] = section.VirtualAddress + image_base

		sections_str = " -s ".join(" ".join((f"\"{name}\"", f"{address:#x}")) for name, address in sections.items() if name != ".text")
		pe_symbols = f"add-symbol-file {symbol_file_path} {sections['.text']:#x} -s {sections_str}"

		gdb.execute(pe_symbols)

class EfiGuidPrinter:
	_table = {
		'5B1B31A1-9562-11D2-8E3F-00A0C969723B': 'EFI_LOADED_IMAGE_PROTOCOL_GUID',
		'8868E871-E4F1-11D3-BC22-0080C73C8881': 'EFI_ACPI_20_TABLE_GUID',
		'9042A9DE-23DC-4A38-96FB-7ADED080516A': 'EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID',
		'964E5B22-6459-11D2-8E39-00A0C969723B': 'EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID',
		'B1B621D5-F19C-41A5-830B-D9152C69AAE0': 'EFI_DTB_TABLE_GUID',
	}

	def __init__(self, val):
		self.val = val

	def to_string(self):
		Data1 = int(self.val['data1'])
		Data2 = int(self.val['data2'])
		Data3 = int(self.val['data3'])
		Data4 = self.val['data4']
		guid = f'{Data1:08X}-{Data2:04X}-'
		guid += f'{Data3:04X}-'
		guid += f'{int(Data4[0]):02X}{int(Data4[1]):02X}-'
		guid += f'{int(Data4[2]):02X}{int(Data4[3]):02X}'
		guid += f'{int(Data4[4]):02X}{int(Data4[5]):02X}'
		guid += f'{int(Data4[6]):02X}{int(Data4[7]):02X}'

		return self._table.get(guid, guid)

def lookup_type(val):
	if str(val.type) == 'efi_guid':
		return EfiGuidPrinter(val)
	return None

gdb.pretty_printers.append(lookup_type)

FindUefiMain()
LoadPE()
