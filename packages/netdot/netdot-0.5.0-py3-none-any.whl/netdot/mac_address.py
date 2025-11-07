import re

MAC_ADDRESS_BYTE_COUNT = 12


class MACAddress:
    """Represent a MAC Address, consistently."""

    def __init__(self, raw):
        self._address = self._strip_tokens(raw)
        self._validate(self._address)

    def __str__(self):
        return self.format()

    def __repr__(self):
        return f"MACAddress('{self._address}')"

    def __eq__(self, other):
        if not isinstance(other, MACAddress):
            return False
        return self._address.lower() == other._address.lower()

    def __hash__(self):
        return hash(self._address)

    def format(self, *, delimiter='', lowercase=True) -> str:
        """Get a representation of this MACAddress, formatted according to arguments.

        Args:
            delimiter (str, optional): The delimiter to be used between each byte-pair in the MAC Address.
                E.g. '-' => aa-bb-cc-dd-ee-ff. Defaults to no delimiter.
            lowercase (bool, optional): Ensure all alpha characters are lowercase.
                Pass `False` to ensure alpha characters are uppercase instead.

        Returns:
            str: The MACAddress, as a pretty string.
        """
        if lowercase:
            mac_address = self._address.lower()
        else:
            mac_address = self._address.upper()
        mac_address = MACAddress._reassemble_mac(mac_address, delimiter)
        return mac_address

    @staticmethod
    def _strip_tokens(raw_mac):
        # Remove any whitespaces & delimiters
        return re.sub(r'[\s.:-]', '', raw_mac)

    @staticmethod
    def _reassemble_mac(mac_bytes, delimiter):
        two_char_chunks = [str(mac_bytes[i : i + 2]) for i in range(0, 12, 2)]
        return delimiter.join(two_char_chunks)

    @staticmethod
    def _validate(mac_bytes):
        """Validate a MAC Address.

        Args:
            mac_bytes (str): The MAC Address, without ANY extra delimiters/characters.

        Raises:
            ValueError: If not a valid MAC Address.
        """
        if not mac_bytes.isalnum():
            raise ValueError(
                f'Unable to parse MAC Address, invalid characters: {mac_bytes}'
            )
        if len(mac_bytes) != MAC_ADDRESS_BYTE_COUNT:
            raise ValueError(
                f'Unable to parse MAC Address, invalid length (expect {MAC_ADDRESS_BYTE_COUNT}, was {len(mac_bytes)}): {mac_bytes}'
            )
