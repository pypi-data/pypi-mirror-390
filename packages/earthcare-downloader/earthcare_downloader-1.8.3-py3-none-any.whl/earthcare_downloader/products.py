from collections.abc import Iterable
from enum import Enum
from typing import TypeAlias


class ESAProd(str, Enum):
    # L1 products
    ATL_NOM_1B = "ATL_NOM_1B"
    AUX_JSG_1D = "AUX_JSG_1D"
    BBR_NOM_1B = "BBR_NOM_1B"
    BBR_SNG_1B = "BBR_SNG_1B"
    CPR_NOM_1B = "CPR_NOM_1B"
    MSI_NOM_1B = "MSI_NOM_1B"
    MSI_RGR_1C = "MSI_RGR_1C"
    # L2 products
    AC__TC__2B = "AC__TC__2B"
    AM__ACD_2B = "AM__ACD_2B"
    AM__CTH_2B = "AM__CTH_2B"
    ATL_AER_2A = "ATL_AER_2A"
    ATL_ALD_2A = "ATL_ALD_2A"
    ATL_CTH_2A = "ATL_CTH_2A"
    ATL_EBD_2A = "ATL_EBD_2A"
    ATL_FM__2A = "ATL_FM__2A"
    ATL_ICE_2A = "ATL_ICE_2A"
    ATL_TC__2A = "ATL_TC__2A"
    BM__RAD_2B = "BM__RAD_2B"
    CPR_CD__2A = "CPR_CD__2A"
    CPR_CLD__2A = "CPR_CLD__2A"
    CPR_FMR__2A = "CPR_FMR__2A"
    CPR_TC__2A = "CPR_TC__2A"
    MSI_AOT__2A = "MSI_AOT__2A"
    MSI_CM__2A = "MSI_CM__2A"
    MSI_COP_2A = "MSI_COP_2A"


class JAXAProd(str, Enum):
    AC__CLP_2B = "AC__CLP_2B"
    ATL_CLA_2A = "ATL_CLA_2A"
    CPR_CLP_2A = "CPR_CLP_2A"
    CPR_ECO_2A = "CPR_ECO_2A"
    MSI_CLP_2A = "MSI_CLP_2A"


class OrbitData(str, Enum):
    AUX_ORBPRE = "AUX_ORBPRE"
    MPL_ORBSCT = "MPL_ORBSCT"


Product: TypeAlias = ESAProd | JAXAProd | OrbitData
ProductInput: TypeAlias = str | Product
ProductsInput: TypeAlias = ProductInput | Iterable[ProductInput]

VALID_PRODUCTS = (
    {e.value for e in ESAProd}
    | {e.value for e in JAXAProd}
    | {e.value for e in OrbitData}
)
