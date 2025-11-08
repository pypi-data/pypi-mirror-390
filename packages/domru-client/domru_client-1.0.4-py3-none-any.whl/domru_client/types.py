from pydantic import BaseModel, Field
from typing import Optional

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_expiry: float
    region: str

class AgreementCity(BaseModel):
    name: str

class AgreementAddress(BaseModel):
    full: str
    city: AgreementCity

class Agreement(BaseModel):
    number: str
    domain: str
    id : str
    providerId: int
    title: str
    address: AgreementAddress

class AgreementInfoPayment(BaseModel):
    balance: float
    pay_charges_sum: float = Field(None, alias="payChargesSum")

class AgreementInfoPersonalAddress(BaseModel):
    city: str
    street: str
    streetId: int
    house: int
    building: str
    flat: int

class AgreementInfoPersonal(BaseModel):
    fio: str
    agreement_id: int= Field(None, alias="agreementId")
    agreement: int
    agreement_type_id: int= Field(None, alias="agreementTypeId")
    address: AgreementInfoPersonalAddress

class AgreementInfo(BaseModel):
    payment: AgreementInfoPayment
    personal: AgreementInfoPersonal

class Region(BaseModel):
    name: str
    domain: Optional[str] = None
    provider_id: int 
    has_sso: int = 0