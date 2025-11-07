# UpdateFulfillmentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_target_date** | **date** | The target date for the Fulfillment to be picked up by bill run for billing.  | [optional] 
**carrier** | **str** | The carrier of the Fulfillment. The available values can be managed in the Fulfillment Settings page under Billing Settings.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Fulfillment object.  | [optional] 
**description** | **str** | The description of the Fulfillment.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude Fulfillment related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.   **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude Fulfillment from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.   | [optional] 
**external_id** | **str** | The external id of the Fulfillment.  | [optional] 
**fulfillment_date** | **date** | The date of the Fulfillment.  | [optional] 
**fulfillment_location** | **str** | The fulfillment location of the Fulfillment. The available values can be managed in the Fulfillment Settings page under Billing Settings.  | [optional] 
**fulfillment_system** | **str** | The fulfillment system of the Fulfillment. The available values can be managed in the Fulfillment Settings page under Billing Settings.  | [optional] 
**fulfillment_type** | [**FulfillmentType**](FulfillmentType.md) |  | [optional] 
**order_line_item_id** | **str** | The reference id of the related Order Line Ite  | [optional] 
**quantity** | **float** | The quantity of the Fulfillment.  | [optional] 
**state** | [**FulfillmentState**](FulfillmentState.md) |  | [optional] 
**tracking_number** | **str** | The tracking number of the Fulfillment.  | [optional] 

## Example

```python
from zuora_sdk.models.update_fulfillment_request import UpdateFulfillmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateFulfillmentRequest from a JSON string
update_fulfillment_request_instance = UpdateFulfillmentRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateFulfillmentRequest.to_json())

# convert the object into a dict
update_fulfillment_request_dict = update_fulfillment_request_instance.to_dict()
# create an instance of UpdateFulfillmentRequest from a dict
update_fulfillment_request_from_dict = UpdateFulfillmentRequest.from_dict(update_fulfillment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


