from base64 import b64decode
from math import floor
from typing import Dict, List, Optional, Tuple, Union, cast
from xml.dom.minidom import Attr, Document
import xml.dom.minidom as minidom
from typing import List
import numpy as np
import numpy.typing as npt
from array import array
from typing import Dict, MutableSequence, Optional

#Credit: Christopher Watford 
#sierra-ecg-tools package
#Source: https://github.com/sixlettervariables/sierra-ecg-tools/blob/master/pysierraecg/src/sierraecg/
#
#Copyright (c) 2022 Christopher Watford <christopher.watford@gmail.com>
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to
#deal in the Software without restriction, including without limitation the
#rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#sell copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#IN THE SOFTWARE.

class LzwDecoder(object):
    """Provides a decoder for LZW compression"""

    buffer: bytes
    offset = 0
    bits = 0
    max_code = 0

    bit_count = 0
    bit_buffer = 0

    previous: MutableSequence[int] = array("B", [])
    next_code = 256
    strings: Dict[int, MutableSequence[int]] = {}

    current: Optional[MutableSequence[int]] = None
    position = 0

    def __init__(self, buffer: bytes, bits: int):
        self.buffer = buffer
        self.bits = bits
        self.max_code = (1 << bits) - 2
        self.strings = {code: array("B", [code]) for code in range(256)}

    def read(self) -> int:
        if self.current is None or self.position == len(self.current):
            self.current = self._read_next_string()
            self.position = 0

        if len(self.current) > 0:
            byte = self.current[self.position] & 0xFF
            self.position += 1
            return byte

        return -1

    def read_bytes(self, count: int) -> MutableSequence[int]:
        return array("B", [self.read() for _ in range(count)])

    def _read_next_string(self) -> MutableSequence[int]:
        code = self._read_codepoint()
        if code >= 0 and code <= self.max_code:
            data: Optional[MutableSequence[int]] = None
            if code not in self.strings:
                data = self.previous[:]
                data.append(self.previous[0])
                self.strings[code] = data
            else:
                data = self.strings[code]

            if len(self.previous) > 0 and self.next_code <= self.max_code:
                next_data = self.previous[:]
                next_data.append(data[0])
                self.strings[self.next_code] = next_data
                self.next_code += 1

            self.previous = data
            return data

        return array("B", [])

    def _read_codepoint(self) -> int:
        code = 0
        while self.bit_count <= 24:
            if self.offset < len(self.buffer):
                next_byte = self.buffer[self.offset]
                self.offset += 1
                self.bit_buffer |= ((next_byte & 0xFF) << (24 - self.bit_count)) & 0xFFFFFFFF
                self.bit_count += 8
            elif self.bit_count < self.bits:
                return -1
            else:
                break

        code = (self.bit_buffer >> (32 - self.bits)) & 0x0000FFFF
        self.bit_buffer = ((self.bit_buffer & 0xFFFFFFFF) << self.bits) & 0xFFFFFFFF
        self.bit_count -= self.bits

        return code

def xli_decode(data: bytes, labels: List[str]) -> List[npt.NDArray[np.int16]]:
    samples: List[npt.NDArray[np.int16]] = []
    offset = 0
    while offset < len(data):
        header = data[offset : offset + 8]
        offset += 8

        size = int.from_bytes(header[0:4], byteorder="little", signed=True)
        start = int.from_bytes(header[6:], byteorder="little", signed=True)
        chunk = data[offset : offset + size]
        offset += size

        decoder = LzwDecoder(chunk, bits=10)

        buffer = []
        while -1 != (b := decoder.read()):
            buffer.append(b & 0xFF)

        if len(buffer) % 2 == 1:
            buffer.append(0)

        deltas = xli_decode_deltas(buffer, start)
        samples.append(deltas)

    return samples


def xli_decode_deltas(buffer: List[int], first: int) -> npt.NDArray[np.int16]:
    deltas = xli_unpack(buffer)
    x = int(deltas[0])
    y = int(deltas[1])
    last = first
    for i in range(2, len(deltas)):
        z = (y + y) - x - last
        last = int(deltas[i]) - 64
        deltas[i] = z
        x = y
        y = z
    return deltas

def xli_unpack(buffer: List[int]) -> npt.NDArray[np.int16]:
    unpacked: npt.NDArray[np.int16] = np.array(
        [0 for _ in range(int(len(buffer) / 2))], dtype=np.int16
    )
    for i in range(len(unpacked)):
        joined_bytes = (((buffer[i] << 8) | buffer[len(unpacked) + i]) << 16) >> 16
        unpacked[i] = np.array(joined_bytes).astype(np.int16)
    return unpacked

class UnsupportedXmlFileError(RuntimeError):
    """Raised when the XML file format is unsupported"""


class MissingXmlElementError(RuntimeError):
    """Raised when a required XML element is missing"""


class MissingXmlAttributeError(RuntimeError):
    """Raised when a required XML attribute is missing"""


class EcgLead:
    """Represents an ECG Lead"""

    label: str = ""
    sampling_freq: int = 0
    duration: int = 0
    samples: npt.NDArray[np.int16] = np.array([], dtype=np.int16)


class EcgRepbeat:
    """Represents an ECG Representive Beat"""

    label: str = ""
    sampling_freq: int = 0
    duration: int = 0
    resolution: float = 0
    method: str = ""
    samples: npt.NDArray[np.int16] = np.array([], dtype=np.int16)


class SierraEcgFile:
    """Represents a Sierra ECG File"""

    doc_type: str = ""
    doc_ver: str = ""
    leads: List[EcgLead] = []
    repbeats: Dict[str, EcgRepbeat] = {}


def read_file(filename: str, include_repbeats: bool = False) -> SierraEcgFile:
    """
    Read a Philips Sierra ECG file.
    
    Parameters
    ----------
    filename : str
        Path to the Philips Sierra ECG file.

    include_repbeats : bool
        Indicates whether to include representative beats.
        Default is False.

    Returns
    -------
    SierraEcgFile
        The parsed Philips Sierra ECG file.
    """
    xdom = minidom.parse(filename)
    root = get_node(xdom, "restingecgdata")
    (doc_type, doc_ver) = assert_version(root)

    leads, labels = assert_leads(root)

    lead_i = leads[0].samples
    lead_ii = leads[1].samples
    lead_iii = leads[2].samples
    lead_avr = leads[3].samples
    lead_avl = leads[4].samples
    lead_avf = leads[5].samples

    for i in range(len(lead_iii)):
        lead_iii[i] = lead_ii[i] - lead_i[i] - lead_iii[i]

    for i in range(len(lead_avr)):
        lead_avr[i] = -lead_avr[i] - floor((lead_i[i] + lead_ii[i]) / 2)

    for i in range(len(lead_avl)):
        lead_avl[i] = floor((lead_i[i] - lead_iii[i]) / 2) - lead_avl[i]

    for i in range(len(lead_avf)):
        lead_avf[i] = floor((lead_ii[i] + lead_iii[i]) / 2) - lead_avf[i]

    sierra_ecg_file = SierraEcgFile()
    sierra_ecg_file.doc_type = doc_type
    sierra_ecg_file.doc_ver = doc_ver
    sierra_ecg_file.leads = leads

    if include_repbeats:
        repbeats = assert_reps(root)
        sierra_ecg_file.repbeats = repbeats

    return sierra_ecg_file


def assert_version(elt: Document) -> Tuple[str, str]:
    doc_info = get_node(elt, "documentinfo")
    doc_type = get_text(get_node(doc_info, "documenttype"))
    doc_ver = get_text(get_node(doc_info, "documentversion"))
    if doc_type not in ["SierraECG", "PhilipsECG"] or doc_ver not in [
        "1.03",
        "1.04",
        "1.04.01",
        "1.04.02",
    ]:
        raise UnsupportedXmlFileError(f"Files of type {doc_type} {doc_ver} are unsupported")

    return (doc_type, doc_ver)


def assert_leads(elt: Document) -> Tuple[List[EcgLead], List[str]]:
    signal_details = get_node(get_node(elt, "dataacquisition"), "signalcharacteristics")
    parsed_waveforms = get_node(elt, "parsedwaveforms")

    sampling_freq = int(get_text(get_node(signal_details, "samplingrate")))
    duration = int(get_attr(parsed_waveforms, "durationperchannel"))

    labels = get_or_create_labels(signal_details, parsed_waveforms)
    waveform_data = get_waveform_data(signal_details, parsed_waveforms, labels)

    leads: List[EcgLead] = []
    for index, label in enumerate(labels):
        lead = EcgLead()
        lead.label = label
        lead.sampling_freq = sampling_freq
        lead.duration = duration
        lead.samples = waveform_data[index]
        leads.append(lead)

    return leads, labels


def assert_reps(elt: Document) -> Dict[str, EcgRepbeat]:
    elt_repbeats = get_opt_node(elt, "repbeats")
    if elt_repbeats is None:
        return {}

    # get repbeats dataencoding
    encoding = get_attr(elt_repbeats, "dataencoding")

    # Optional in 1.03 files
    samplingrate = int(get_attr(elt_repbeats, "samplespersec", "0"))
    resolution = float(get_attr(elt_repbeats, "resolution", "0"))
    method = get_attr(elt_repbeats, "repbeatmethod", "")

    repbeats: Dict[str, EcgRepbeat] = {}
    for item in get_nodes(elt_repbeats, "repbeat"):
        repbeat = EcgRepbeat()
        repbeat.label = get_attr(item, "leadname")
        repbeat.sampling_freq = samplingrate
        repbeat.resolution = resolution
        repbeat.method = method

        waveform = get_opt_node(item, "waveform")
        if waveform is not None:
            duration = int(get_attr(waveform, "duration"))
            repbeat.duration = duration

            if encoding == "Base64":
                decoded_waveform_data = read_base64_encoding(get_text(waveform))
            else:
                raise UnsupportedXmlFileError(
                    f"Representative beat waveform data encoding unsupported: {encoding}"
                )

            repbeat.samples = np.frombuffer(decoded_waveform_data, dtype=np.int16)
        else:
            duration = int(get_attr(item, "duration"))
            repbeat.duration = duration

            # 1.03 schema included waveform data directly within the <repbeat> element
            if encoding == "Base64":
                decoded_waveform_data = read_base64_encoding(get_text(item))
            else:
                raise UnsupportedXmlFileError(
                    f"Representative beat waveform data encoding unsupported: {encoding}"
                )

            repbeat.samples = np.frombuffer(decoded_waveform_data, dtype=np.int16)

        repbeats[repbeat.label] = repbeat

    return repbeats


def get_waveform_data(
    signal_details: Document, parsed_waveforms: Document, labels: List[str]
) -> List[npt.NDArray[np.int16]]:
    sampling_freq = int(get_text(get_node(signal_details, "samplingrate")))
    duration = int(get_attr(parsed_waveforms, "durationperchannel"))
    sample_count = int(duration * (sampling_freq / 1000))

    encoding = get_attr(parsed_waveforms, "dataencoding")
    waveform_data = None
    if encoding == "Base64":
        waveform_data = read_base64_encoding(get_text(parsed_waveforms))
    else:
        raise UnsupportedXmlFileError(f"Waveform data encoding unsupported: {encoding}")

    compression_method = infer_compression(parsed_waveforms)
    if compression_method != "Uncompressed":
        if compression_method == "XLI":
            return xli_decode(waveform_data, labels)
        else:
            raise UnsupportedXmlFileError(
                f"Waveform data compression algorithm unsupported: {compression_method}"
            )

    return split_leads(waveform_data, len(labels), sample_count)


def read_base64_encoding(text: str) -> bytes:
    return b64decode(text)


def infer_compression(parsed_waveforms: Document) -> str:
    return get_attr(
        parsed_waveforms,
        "compressmethod",
        get_attr(parsed_waveforms, "compression", "Uncompressed"),
    )


def split_leads(
    waveform_data: bytes, lead_count: int, samples: int
) -> List[npt.NDArray[np.int16]]:
    all_samples: npt.NDArray[np.int16] = np.frombuffer(waveform_data, dtype=np.int16)
    leads: List[npt.NDArray[np.int16]] = []

    offset = 0
    while offset < lead_count * samples:
        lead = all_samples[offset : offset + samples]
        leads.append(lead)
        offset += samples

    return leads


def get_or_create_labels(signal_details: Document, parsed_waveforms: Document) -> List[str]:
    lead_labels = get_attr(parsed_waveforms, "leadlabels", "")
    if lead_labels != "":
        lead_count = int(get_attr(parsed_waveforms, "numberofleads"))
        return lead_labels.split(" ")[:lead_count]
    else:
        good_channels = int(get_text(get_node(signal_details, "numberchannelsallocated")))
        leads_used = get_text(get_node(signal_details, "acquisitiontype"))
        return [get_lead_name(leads_used, x + 1) for x in range(good_channels)]


def get_lead_name(leads_used: str, index: int) -> str:
    if leads_used in ["STD-12", "10-WIRE"]:
        if index == 1:
            return "I"
        elif index == 2:
            return "II"
        elif index == 3:
            return "III"
        elif index == 4:
            return "aVR"
        elif index == 5:
            return "aVL"
        elif index == 6:
            return "aVF"
        elif index > 6 and index <= 12:
            return f"V{index - 6}"

    return f"Channel {index}"


def get_node(xdoc: Document, tag_name: str) -> Document:
    xelt = get_opt_node(xdoc, tag_name)
    if xelt is None:
        raise MissingXmlElementError(tag_name)
    return xelt


def get_opt_node(xdoc: Document, tag_name: str) -> Optional[Document]:
    for xelt in xdoc.getElementsByTagName(tag_name):
        return cast(Document, xelt)
    return None


def get_nodes(xdoc: Document, tag_name: str) -> List[Document]:
    return [cast(Document, xelt) for xelt in xdoc.getElementsByTagName(tag_name)]


def get_attr(xdoc: Document, attr_name: str, default: Optional[str] = None) -> str:
    if attr_name in xdoc.attributes:
        return get_text(xdoc.attributes[attr_name])
    if default is None:
        raise MissingXmlAttributeError(attr_name)
    return default


def get_text(xdoc: Union[Document, Attr]) -> str:
    rc = []
    for node in xdoc.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return "".join(rc)