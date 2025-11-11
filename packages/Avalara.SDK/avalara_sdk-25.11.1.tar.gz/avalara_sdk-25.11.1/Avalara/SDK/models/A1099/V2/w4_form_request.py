# coding: utf-8

"""
AvaTax Software Development Kit for Python.

   Copyright 2022 Avalara, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

    Avalara 1099 & W-9 API Definition
    ## 🔐 Authentication  Generate a **license key** from: *[Avalara Portal](https://www.avalara.com/us/en/signin.html) → Settings → License and API Keys*.  [More on authentication methods](https://developer.avalara.com/avatax-dm-combined-erp/common-setup/authentication/authentication-methods/)  [Test your credentials](https://developer.avalara.com/avatax/test-credentials/)  ## 📘 API & SDK Documentation  [Avalara SDK (.NET) on GitHub](https://github.com/avadev/Avalara-SDK-DotNet#avalarasdk--the-unified-c-library-for-next-gen-avalara-services)  [Code Examples – 1099 API](https://github.com/avadev/Avalara-SDK-DotNet/blob/main/docs/A1099/V2/Class1099IssuersApi.md#call1099issuersget) 

@author     Sachin Baijal <sachin.baijal@avalara.com>
@author     Jonathan Wenger <jonathan.wenger@avalara.com>
@copyright  2022 Avalara, Inc.
@license    https://www.apache.org/licenses/LICENSE-2.0
@version    25.11.1
@link       https://github.com/avadev/AvaTax-REST-V3-Python-SDK
"""

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class W4FormRequest(BaseModel):
    """
    W4FormRequest
    """ # noqa: E501
    type: Optional[StrictStr] = Field(default=None, description="The form type (always \"w4\" for this model).")
    employee_first_name: StrictStr = Field(description="The first name of the employee.", alias="employeeFirstName")
    employee_middle_name: Optional[StrictStr] = Field(default=None, description="The middle name of the employee.", alias="employeeMiddleName")
    employee_last_name: StrictStr = Field(description="The last name of the employee.", alias="employeeLastName")
    employee_name_suffix: Optional[StrictStr] = Field(default=None, description="The name suffix of the employee.", alias="employeeNameSuffix")
    tin_type: StrictStr = Field(description="Tax Identification Number (TIN) type.", alias="tinType")
    tin: StrictStr = Field(description="The taxpayer identification number (TIN).")
    address: Optional[StrictStr] = Field(default=None, description="The address of the employee. Required unless exempt.")
    city: Optional[StrictStr] = Field(default=None, description="The city of residence of the employee. Required unless exempt.")
    state: Optional[StrictStr] = Field(default=None, description="The state of residence of the employee. Required unless exempt.")
    zip: Optional[StrictStr] = Field(default=None, description="The ZIP code of residence of the employee. Required unless exempt.")
    marital_status: Optional[StrictStr] = Field(default=None, description="The marital status of the employee. Required unless exempt.  Available values:  - Single: Single or Married filing separately  - Married: Married filing jointly or qualifying surviving spouse  - MarriedBut: Head of household. Check only if you're unmarried and pay more than half the costs of keeping up a home for yourself and a qualifying individual.", alias="maritalStatus")
    last_name_differs: Optional[StrictBool] = Field(default=None, description="Indicates whether the last name differs from prior records.", alias="lastNameDiffers")
    num_allowances: Optional[StrictInt] = Field(default=None, description="The number of allowances claimed by the employee.", alias="numAllowances")
    other_dependents: Optional[StrictInt] = Field(default=None, description="The number of dependents other than allowances.", alias="otherDependents")
    non_job_income: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of non-job income.", alias="nonJobIncome")
    deductions: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of deductions claimed.")
    additional_withheld: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The additional amount withheld.", alias="additionalWithheld")
    exempt_from_withholding: Optional[StrictBool] = Field(default=None, description="Indicates whether the employee is exempt from withholding.", alias="exemptFromWithholding")
    office_code: Optional[StrictStr] = Field(default=None, description="The office code associated with the form.", alias="officeCode")
    e_delivery_consented_at: Optional[datetime] = Field(default=None, description="The date when e-delivery was consented.", alias="eDeliveryConsentedAt")
    signature: Optional[StrictStr] = Field(default=None, description="The signature of the form.")
    company_id: Optional[StrictStr] = Field(default=None, description="The ID of the associated company. Required when creating a form.", alias="companyId")
    reference_id: Optional[StrictStr] = Field(default=None, description="A reference identifier for the form.", alias="referenceId")
    email: Optional[StrictStr] = Field(default=None, description="The email address of the individual associated with the form.")
    __properties: ClassVar[List[str]] = ["eDeliveryConsentedAt", "signature", "type", "companyId", "referenceId", "email"]

    @field_validator('type')
    def type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['W4', 'W8Ben', 'W8BenE', 'W8Imy', 'W9']):
            raise ValueError("must be one of enum values ('W4', 'W8Ben', 'W8BenE', 'W8Imy', 'W9')")
        return value

    @field_validator('state')
    def state_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['AA', 'AE', 'AK', 'AL', 'AP', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'FM', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MH', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'PW', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY']):
            raise ValueError("must be one of enum values ('AA', 'AE', 'AK', 'AL', 'AP', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'FM', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MH', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'PW', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY')")
        return value

    @field_validator('marital_status')
    def marital_status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Single', 'Married', 'MarriedBut']):
            raise ValueError("must be one of enum values ('Single', 'Married', 'MarriedBut')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of W4FormRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "type",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if e_delivery_consented_at (nullable) is None
        # and model_fields_set contains the field
        if self.e_delivery_consented_at is None and "e_delivery_consented_at" in self.model_fields_set:
            _dict['eDeliveryConsentedAt'] = None

        # set to None if signature (nullable) is None
        # and model_fields_set contains the field
        if self.signature is None and "signature" in self.model_fields_set:
            _dict['signature'] = None

        # set to None if reference_id (nullable) is None
        # and model_fields_set contains the field
        if self.reference_id is None and "reference_id" in self.model_fields_set:
            _dict['referenceId'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of W4FormRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "eDeliveryConsentedAt": obj.get("eDeliveryConsentedAt"),
            "signature": obj.get("signature"),
            "type": obj.get("type"),
            "companyId": obj.get("companyId"),
            "referenceId": obj.get("referenceId"),
            "email": obj.get("email")
        })
        return _obj


