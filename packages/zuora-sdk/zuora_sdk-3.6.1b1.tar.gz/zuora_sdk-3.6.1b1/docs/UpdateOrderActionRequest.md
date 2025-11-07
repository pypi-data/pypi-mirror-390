# UpdateOrderActionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_action** | [**UpdateOrderAction**](UpdateOrderAction.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_action_request import UpdateOrderActionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderActionRequest from a JSON string
update_order_action_request_instance = UpdateOrderActionRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderActionRequest.to_json())

# convert the object into a dict
update_order_action_request_dict = update_order_action_request_instance.to_dict()
# create an instance of UpdateOrderActionRequest from a dict
update_order_action_request_from_dict = UpdateOrderActionRequest.from_dict(update_order_action_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


