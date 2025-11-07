# UpdatePaymentMethodRequestCreditCardInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expiration_month** | **int** | One or two digits expiration month (1-12).           | [optional] 
**expiration_year** | **int** | Four-digit expiration year.  | [optional] 
**security_code** | **str** | Optional. It is the CVV or CVV2 security code specific for the credit card or debit card. To ensure PCI compliance, this value is not stored and cannot be queried.   If securityCode code is not passed in the request payload, this operation only updates related fields in the payload. It does not validate the payment method through the gateway.  If securityCode is passed in the request payload, this operation retrieves the credit card information from payload and validates them through the gateway.  | [optional] 

## Example

```python
from zuora_sdk.models.update_payment_method_request_credit_card_info import UpdatePaymentMethodRequestCreditCardInfo

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePaymentMethodRequestCreditCardInfo from a JSON string
update_payment_method_request_credit_card_info_instance = UpdatePaymentMethodRequestCreditCardInfo.from_json(json)
# print the JSON string representation of the object
print(UpdatePaymentMethodRequestCreditCardInfo.to_json())

# convert the object into a dict
update_payment_method_request_credit_card_info_dict = update_payment_method_request_credit_card_info_instance.to_dict()
# create an instance of UpdatePaymentMethodRequestCreditCardInfo from a dict
update_payment_method_request_credit_card_info_from_dict = UpdatePaymentMethodRequestCreditCardInfo.from_dict(update_payment_method_request_credit_card_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


