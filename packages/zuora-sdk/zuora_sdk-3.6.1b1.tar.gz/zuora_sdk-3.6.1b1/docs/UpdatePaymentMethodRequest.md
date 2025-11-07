# UpdatePaymentMethodRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expiration_month** | **int** | One or two digits expiration month (1-12).           | [optional] 
**expiration_year** | **int** | Four-digit expiration year.  | [optional] 
**security_code** | **str** | Optional. It is the CVV or CVV2 security code specific for the credit card or debit card. To ensure PCI compliance, this value is not stored and cannot be queried.   If securityCode code is not passed in the request payload, this operation only updates related fields in the payload. It does not validate the payment method through the gateway.  If securityCode is passed in the request payload, this operation retrieves the credit card information from payload and validates them through the gateway.  | [optional] 
**account_holder_info** | [**UpdaterPaymentMethodRequestAccountHolderInfo**](UpdaterPaymentMethodRequestAccountHolderInfo.md) |  | [optional] 
**account_key** | **str** | The ID of the customer account associated with this payment method, such as &#x60;2x92c0f859b0480f0159d3a4a6ee5bb6&#x60;.  **Note:** You can use this field to associate an orphan payment method with a customer account. If a payment method is already associated with a customer account, you cannot change the associated payment method through this operation. You cannot remove the previous account ID and leave this field empty, either.  | [optional] 
**auth_gateway** | **str** | Specifies the ID of the payment gateway that Zuora will use to authorize the payments that are made with the payment method.   This field is not supported in updating Credit Card Reference Transaction payment methods.  | [optional] 
**currency_code** | **str** | The currency used for payment method authorization.  | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**ip_address** | **str** | The IPv4 or IPv6 information of the user when the payment method is created or updated. Some gateways use this field for fraud prevention. If this field is passed to Zuora, Zuora directly passes it to gateways.   If the IP address length is beyond 45 characters, a validation error occurs.  For validating SEPA payment methods on Stripe v2, this field is required.  | [optional] 
**mandate_info** | [**PaymentMethodRequestMandateInfo**](PaymentMethodRequestMandateInfo.md) |  | [optional] 
**processing_options** | [**PaymentMethodRequestProcessingOptions**](PaymentMethodRequestProcessingOptions.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_payment_method_request import UpdatePaymentMethodRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePaymentMethodRequest from a JSON string
update_payment_method_request_instance = UpdatePaymentMethodRequest.from_json(json)
# print the JSON string representation of the object
print(UpdatePaymentMethodRequest.to_json())

# convert the object into a dict
update_payment_method_request_dict = update_payment_method_request_instance.to_dict()
# create an instance of UpdatePaymentMethodRequest from a dict
update_payment_method_request_from_dict = UpdatePaymentMethodRequest.from_dict(update_payment_method_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


