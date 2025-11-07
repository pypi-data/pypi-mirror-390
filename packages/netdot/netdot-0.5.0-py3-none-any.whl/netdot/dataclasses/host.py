from dataclasses import dataclass

from netdot.dataclasses.dns import RR
from netdot.dataclasses.ipblock import IPBlock


@dataclass
class Host():
    ipblocks: list[IPBlock]
    RRs: list[RR]

    @classmethod
    def from_DTO(cls, dto):
        """Populate the Host instance from a DTO (Data Transfer Object)."""
        extra_dto_keys = set(dto.keys()) - set(['Ipblock', 'RR'])
        if extra_dto_keys:
            raise ValueError(f"Unhandled DTO element for netdoot.Host.from_DTO: {extra_dto_keys}")

        if 'Ipblock' in dto:
            ipblocks = [
                IPBlock.from_DTO(ipblock)
                for ipblock in dto['Ipblock'].values()
            ]
        else:
            ipblocks = []
        if 'RR' in dto:
            rrs = [
                RR.from_DTO(rr)
                for rr in dto['RR'].values()
            ]
        else:
            rrs = []
        return cls(RRs=rrs, ipblocks=ipblocks)

    @property
    def names(self) -> list[str]:
        """Get a list of all hostnames (RR names) associated with this Host."""
        return [rr.name for rr in self.RRs if rr.name is not None]

    @property
    def addresses(self) -> list[str]:
        """Get a list of all IP addresses associated with this Host."""
        return [str(ipblock.address) for ipblock in self.ipblocks if ipblock.address is not None]