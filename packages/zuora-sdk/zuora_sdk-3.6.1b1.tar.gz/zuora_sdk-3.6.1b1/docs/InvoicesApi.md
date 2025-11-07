# zuora_sdk.InvoicesApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_create_standalone_invoices**](InvoicesApi.md#bulk_create_standalone_invoices) | **POST** /v1/invoices/batch | Create standalone invoices
[**bulk_post_invoices**](InvoicesApi.md#bulk_post_invoices) | **POST** /v1/invoices/bulk-post | Post invoices
[**bulk_update_invoices**](InvoicesApi.md#bulk_update_invoices) | **PUT** /v1/invoices | Update invoices
[**cancel_invoice**](InvoicesApi.md#cancel_invoice) | **PUT** /v1/invoices/{invoiceKey}/cancel | Cancel an invoice
[**create_invoice_taxation_items**](InvoicesApi.md#create_invoice_taxation_items) | **POST** /v1/invoices/{invoiceKey}/taxation-items | Create taxation items for an invoice
[**create_standalone_invoice**](InvoicesApi.md#create_standalone_invoice) | **POST** /v1/invoices | Create a standalone invoice
[**delete_invoice**](InvoicesApi.md#delete_invoice) | **DELETE** /v1/invoices/{invoiceKey} | Delete an invoice
[**email_invoice**](InvoicesApi.md#email_invoice) | **POST** /v1/invoices/{invoiceKey}/emails | Email an invoice
[**get_invoice**](InvoicesApi.md#get_invoice) | **GET** /v1/invoices/{invoiceKey} | Retrieve an invoice
[**get_invoice_application_parts**](InvoicesApi.md#get_invoice_application_parts) | **GET** /v1/invoices/{invoiceKey}/application-parts | List all application parts of an invoice
[**get_invoice_files**](InvoicesApi.md#get_invoice_files) | **GET** /v1/invoices/{invoiceKey}/files | List all files of an invoice
[**get_invoice_items**](InvoicesApi.md#get_invoice_items) | **GET** /v1/invoices/{invoiceKey}/items | List all items of an invoice
[**get_invoice_pdf_status**](InvoicesApi.md#get_invoice_pdf_status) | **GET** /v1/invoices/pdf-status | Retrieve PDF status of invoices in a batch.
[**get_taxation_items_of_invoice_item**](InvoicesApi.md#get_taxation_items_of_invoice_item) | **GET** /v1/invoices/{invoiceKey}/items/{itemId}/taxation-items | List all taxation items of an invoice item
[**post_invoice**](InvoicesApi.md#post_invoice) | **PUT** /v1/invoices/{invoiceKey}/post | Cancel an invoice
[**reverse_invoice**](InvoicesApi.md#reverse_invoice) | **PUT** /v1/invoices/{invoiceKey}/reverse | Reverse an invoice
[**update_invoice**](InvoicesApi.md#update_invoice) | **PUT** /v1/invoices/{invoiceKey} | Update an invoice
[**upload_file_for_invoice**](InvoicesApi.md#upload_file_for_invoice) | **POST** /v1/invoices/{invoiceKey}/files | Upload a file for an invoice
[**write_off_invoice**](InvoicesApi.md#write_off_invoice) | **PUT** /v1/invoices/{invoiceKey}/write-off | Write off an invoice


# **bulk_create_standalone_invoices**
> BulkCreateInvoicesResponse bulk_create_standalone_invoices(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create standalone invoices

Creates multiple standalone invoices for selling physical goods, services or other items on a non-recurring basis to your subscription customers.  To use this operation, you must have the \"Create Standalone Invoice\" and \"Modify Invoice\" user permissions. See [Billing Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/d_Billing_Roles) for more information. As of Zuora Release 2022.03.R5, newly created standard Billing users have the “Create Standalone Invoice” permission enabled by default.  ### Limitations  This operation has the following limitations: * You can create a maximum of 50 invoices in one request. * You can create a maximum of 1,000 invoice items in one request. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bulk_create_invoices_request import BulkCreateInvoicesRequest
from zuora_sdk.models.bulk_create_invoices_response import BulkCreateInvoicesResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    request = zuora_sdk.BulkCreateInvoicesRequest() # BulkCreateInvoicesRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create standalone invoices
        api_response = api_instance.bulk_create_standalone_invoices(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->bulk_create_standalone_invoices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->bulk_create_standalone_invoices: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**BulkCreateInvoicesRequest**](BulkCreateInvoicesRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**BulkCreateInvoicesResponse**](BulkCreateInvoicesResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulk_post_invoices**
> BulkPostInvoicesResponse bulk_post_invoices(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Post invoices

Posts multiple invoices.  You can post a maximum of 50 invoices in one single request. Additionally, you can also update invoice dates while posting the invoices. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bulk_post_invoices_request import BulkPostInvoicesRequest
from zuora_sdk.models.bulk_post_invoices_response import BulkPostInvoicesResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    request = zuora_sdk.BulkPostInvoicesRequest() # BulkPostInvoicesRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Post invoices
        api_response = api_instance.bulk_post_invoices(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->bulk_post_invoices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->bulk_post_invoices: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**BulkPostInvoicesRequest**](BulkPostInvoicesRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**BulkPostInvoicesResponse**](BulkPostInvoicesResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulk_update_invoices**
> CommonResponse bulk_update_invoices(request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Update invoices

Updates multiple invoices in batches with one call.   ### Limitations  This operation has the following limitations: * You can update a maximum of 50 invoices by one call. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bulk_update_invoices_request import BulkUpdateInvoicesRequest
from zuora_sdk.models.common_response import CommonResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    request = zuora_sdk.BulkUpdateInvoicesRequest() # BulkUpdateInvoicesRequest | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Update invoices
        api_response = api_instance.bulk_update_invoices(request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->bulk_update_invoices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->bulk_update_invoices: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**BulkUpdateInvoicesRequest**](BulkUpdateInvoicesRequest.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CommonResponse**](CommonResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_invoice**
> AsyncOperationResponse cancel_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Cancel an invoice

Cancel a specific invoice.  Whether to cancel an invoice synchronously or asynchronously depends on the number of invoice items contained in the invoice. By default, if an invoice contains less than 1000 items, the invoice is canceled synchronously. Otherwise, the invoice is canceled asynchronously. If you want to change the threshold, submit a request at <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.async_operation_response import AsyncOperationResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice to be canceled. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Cancel an invoice
        api_response = api_instance.cancel_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->cancel_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->cancel_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice to be canceled. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**AsyncOperationResponse**](AsyncOperationResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_invoice_taxation_items**
> GetTaxationItemsResponse create_invoice_taxation_items(invoice_key, body, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create taxation items for an invoice

Creates taxation items for an invoice. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.create_taxation_items_request import CreateTaxationItemsRequest
from zuora_sdk.models.get_taxation_items_response import GetTaxationItemsResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The unique ID or number of an invoice. For example, 8a8082e65b27f6c3015ba45ff82c7172 or INV00000001. 
    body = zuora_sdk.CreateTaxationItemsRequest() # CreateTaxationItemsRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create taxation items for an invoice
        api_response = api_instance.create_invoice_taxation_items(invoice_key, body, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->create_invoice_taxation_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->create_invoice_taxation_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The unique ID or number of an invoice. For example, 8a8082e65b27f6c3015ba45ff82c7172 or INV00000001.  | 
 **body** | [**CreateTaxationItemsRequest**](CreateTaxationItemsRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**GetTaxationItemsResponse**](GetTaxationItemsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_standalone_invoice**
> InvoiceResponse create_standalone_invoice(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create a standalone invoice

Creates a standalone invoice for selling physical goods, services or other items on a non-recurring basis to your subscription customers.  To use this operation, you must have the \"Create Standalone Invoice\" and \"Modify Invoice\" user permissions. See [Billing Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/d_Billing_Roles) for more information. As of Zuora Release 2022.03.R5, newly created standard Billing users have the “Create Standalone Invoice” permission enabled by default. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.create_invoice_request import CreateInvoiceRequest
from zuora_sdk.models.invoice_response import InvoiceResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    request = zuora_sdk.CreateInvoiceRequest() # CreateInvoiceRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create a standalone invoice
        api_response = api_instance.create_standalone_invoice(request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->create_standalone_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->create_standalone_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**CreateInvoiceRequest**](CreateInvoiceRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**InvoiceResponse**](InvoiceResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_invoice**
> OperationJobResponse delete_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Delete an invoice

Deletes a specific invoice.  Whether to delete an invoice synchronously or asynchronously depends on the number of invoice items contained in the invoice. By default, if an invoice contains less than 100 items, the invoice is deleted synchronously. Otherwise, the invoice is deleted asynchronously. If you want to change the threshold, submit a request at <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.operation_job_response import OperationJobResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice to be deleted. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Delete an invoice
        api_response = api_instance.delete_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->delete_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->delete_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice to be deleted. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**OperationJobResponse**](OperationJobResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **email_invoice**
> CommonResponse email_invoice(invoice_key, request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Email an invoice

Sends a posted invoice to the specified email addresses manually. ### Notes   - You must activate the **Manual Email For Invoice | Manual Email For Invoice** notification before emailing invoices. To include the invoice PDF in the email, select the **Include Invoice PDF** check box in the **Edit notification** dialog from the Zuora UI. See [Create and Edit Notifications](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/Notifications/C_Create_Notifications#section_2) for more information.    - Zuora sends the email messages based on the email template you set. You can set the email template to use in the **Delivery Options** panel of the **Edit notification** dialog from the Zuora UI. By default, the **Invoice Posted Default Email Template** template is used. See [Create and Edit Email Templates](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/Notifications/Create_Email_Templates) for more information.    - The invoices are sent only to the work email addresses or personal email addresses of the Bill To contact if the following conditions are all met:     * The `useEmailTemplateSetting` field is set to `false`.     * The email addresses are not specified in the `emailAddresses` field. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.common_response import CommonResponse
from zuora_sdk.models.email_billing_document_request import EmailBillingDocumentRequest
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    request = zuora_sdk.EmailBillingDocumentRequest() # EmailBillingDocumentRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Email an invoice
        api_response = api_instance.email_invoice(invoice_key, request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->email_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->email_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **request** | [**EmailBillingDocumentRequest**](EmailBillingDocumentRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CommonResponse**](CommonResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_invoice**
> InvoiceResponse get_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Retrieve an invoice

Retrieves a specific invoice. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.invoice_response import InvoiceResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Retrieve an invoice
        api_response = api_instance.get_invoice(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**InvoiceResponse**](InvoiceResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_invoice_application_parts**
> GetInvoiceApplicationPartsRequest get_invoice_application_parts(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

List all application parts of an invoice

**Note:** This operation is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  Retrieves information about the payments or credit memos that are applied to a specified invoice. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_invoice_application_parts_request import GetInvoiceApplicationPartsRequest
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List all application parts of an invoice
        api_response = api_instance.get_invoice_application_parts(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_invoice_application_parts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice_application_parts: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**GetInvoiceApplicationPartsRequest**](GetInvoiceApplicationPartsRequest.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_invoice_files**
> InvoiceFilesResponse get_invoice_files(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

List all files of an invoice

Retrieves the information about all PDF files of a specified invoice.   Invoice PDF files are returned in reverse chronological order by the value of the `versionNumber` field. **Note**: This API only retrieves the PDF files that have been generated. If the latest PDF file is being generated, it will not be included in the response. You can use the [Query](https://www.zuora.com/developer/api-references/api/operation/Action_Postquery) action to get the latest PDF file, for example: `\"select Body from Invoice where Id = '2c93808457d787030157e0324aea5158'\"`. See [Query an Invoice Body](https://knowledgecenter.zuora.com/Central_Platform/API/G_SOAP_API/E1_SOAP_API_Object_Reference/Invoice/Query_an_Invoice_Body_Field) for more information. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.invoice_files_response import InvoiceFilesResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    page_size = 20 # int | The number of records returned per page in the response.  (optional) (default to 20)
    page = 1 # int | The index number of the page that you want to retrieve. This parameter is dependent on `pageSize`. You must set `pageSize` before specifying `page`. For example, if you set `pageSize` to `20` and `page` to `2`, the 21st to 40th records are returned in the response.  (optional) (default to 1)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List all files of an invoice
        api_response = api_instance.get_invoice_files(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_invoice_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **page_size** | **int**| The number of records returned per page in the response.  | [optional] [default to 20]
 **page** | **int**| The index number of the page that you want to retrieve. This parameter is dependent on &#x60;pageSize&#x60;. You must set &#x60;pageSize&#x60; before specifying &#x60;page&#x60;. For example, if you set &#x60;pageSize&#x60; to &#x60;20&#x60; and &#x60;page&#x60; to &#x60;2&#x60;, the 21st to 40th records are returned in the response.  | [optional] [default to 1]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**InvoiceFilesResponse**](InvoiceFilesResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_invoice_items**
> InvoiceItemsResponse get_invoice_items(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

List all items of an invoice

Retrieves the information about all items of a specified invoice.  

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.invoice_items_response import InvoiceItemsResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    page_size = 20 # int | The number of records returned per page in the response.  (optional) (default to 20)
    page = 1 # int | The index number of the page that you want to retrieve. This parameter is dependent on `pageSize`. You must set `pageSize` before specifying `page`. For example, if you set `pageSize` to `20` and `page` to `2`, the 21st to 40th records are returned in the response.  (optional) (default to 1)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List all items of an invoice
        api_response = api_instance.get_invoice_items(invoice_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_invoice_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **page_size** | **int**| The number of records returned per page in the response.  | [optional] [default to 20]
 **page** | **int**| The index number of the page that you want to retrieve. This parameter is dependent on &#x60;pageSize&#x60;. You must set &#x60;pageSize&#x60; before specifying &#x60;page&#x60;. For example, if you set &#x60;pageSize&#x60; to &#x60;20&#x60; and &#x60;page&#x60; to &#x60;2&#x60;, the 21st to 40th records are returned in the response.  | [optional] [default to 1]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**InvoiceItemsResponse**](InvoiceItemsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_invoice_pdf_status**
> GetInvoicePdfStatusBatchResponse get_invoice_pdf_status(invoice_keys, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Retrieve PDF status of invoices in a batch.

Retrieves PDF statuses of a batch of invoices. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_invoice_pdf_status_batch_response import GetInvoicePdfStatusBatchResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_keys = 'invoice_keys_example' # str | The IDs or numbers of the invoices separated by commas. For example - \"?invoiceKeys=2c92c8955bd63cc1015bd7c151af02ab,4b65b8605bd63cc1015bd7c151af02cd,INV-0000001\". 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Retrieve PDF status of invoices in a batch.
        api_response = api_instance.get_invoice_pdf_status(invoice_keys, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_invoice_pdf_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice_pdf_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_keys** | **str**| The IDs or numbers of the invoices separated by commas. For example - \&quot;?invoiceKeys&#x3D;2c92c8955bd63cc1015bd7c151af02ab,4b65b8605bd63cc1015bd7c151af02cd,INV-0000001\&quot;.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**GetInvoicePdfStatusBatchResponse**](GetInvoicePdfStatusBatchResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_taxation_items_of_invoice_item**
> TaxationItemsDataResponse get_taxation_items_of_invoice_item(invoice_key, item_id, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

List all taxation items of an invoice item

Retrieves information about the taxation items of a specific invoice item.  

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.taxation_items_data_response import TaxationItemsDataResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001. 
    item_id = 'item_id_example' # str | The unique ID of an invoice item. For example, 2c86c8955bd63cc1015bd7c151af02ef. 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    page_size = 20 # int | The number of records returned per page in the response.  (optional) (default to 20)
    page = 1 # int | The index number of the page that you want to retrieve. This parameter is dependent on `pageSize`. You must set `pageSize` before specifying `page`. For example, if you set `pageSize` to `20` and `page` to `2`, the 21st to 40th records are returned in the response.  (optional) (default to 1)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List all taxation items of an invoice item
        api_response = api_instance.get_taxation_items_of_invoice_item(invoice_key, item_id, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, page_size=page_size, page=page, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->get_taxation_items_of_invoice_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_taxation_items_of_invoice_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The unique ID or number of an invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001.  | 
 **item_id** | **str**| The unique ID of an invoice item. For example, 2c86c8955bd63cc1015bd7c151af02ef.  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **page_size** | **int**| The number of records returned per page in the response.  | [optional] [default to 20]
 **page** | **int**| The index number of the page that you want to retrieve. This parameter is dependent on &#x60;pageSize&#x60;. You must set &#x60;pageSize&#x60; before specifying &#x60;page&#x60;. For example, if you set &#x60;pageSize&#x60; to &#x60;20&#x60; and &#x60;page&#x60; to &#x60;2&#x60;, the 21st to 40th records are returned in the response.  | [optional] [default to 1]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**TaxationItemsDataResponse**](TaxationItemsDataResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_invoice**
> AsyncOperationResponse post_invoice(invoice_key, post_async_invoice_request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Cancel an invoice

Post a specific invoice.  Whether to post an invoice synchronously or asynchronously depends on the number of invoice items contained in the invoice. By default, if an invoice contains less than 1000 items, the invoice is posted synchronously. Otherwise, the invoice is posted asynchronously. If you want to change the threshold, submit a request at <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.async_operation_response import AsyncOperationResponse
from zuora_sdk.models.post_async_invoice_request import PostAsyncInvoiceRequest
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice to be posted. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    post_async_invoice_request = zuora_sdk.PostAsyncInvoiceRequest() # PostAsyncInvoiceRequest | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Cancel an invoice
        api_response = api_instance.post_invoice(invoice_key, post_async_invoice_request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->post_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->post_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice to be posted. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **post_async_invoice_request** | [**PostAsyncInvoiceRequest**](PostAsyncInvoiceRequest.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**AsyncOperationResponse**](AsyncOperationResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reverse_invoice**
> ReverseInvoiceResponse reverse_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Reverse an invoice

**Note:** This operation is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  Reverses a posted invoice.   **Restrictions**  You are not allowed to reverse an invoice if any of the following restrictions is met: * Payments and credit memos are applied to the invoice. * The invoice is split. * The invoice is not in Posted status. * The total amount of the invoice is less than 0 (a negative invoice). * Using Tax Connector for Extension Platform to calculate taxes. * An invoice contains more than 2,000 items in total, including invoice items, discount items, and taxation items.  See [Invoice Reversal](https://knowledgecenter.zuora.com/CB_Billing/IA_Invoices/Reverse_Posted_Invoices) for more information. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.reverse_invoice_request import ReverseInvoiceRequest
from zuora_sdk.models.reverse_invoice_response import ReverseInvoiceResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    request = zuora_sdk.ReverseInvoiceRequest() # ReverseInvoiceRequest | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Reverse an invoice
        api_response = api_instance.reverse_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->reverse_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->reverse_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **request** | [**ReverseInvoiceRequest**](ReverseInvoiceRequest.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**ReverseInvoiceResponse**](ReverseInvoiceResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_invoice**
> UpdateInvoiceResponse update_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Update an invoice

Updates a specific invoice.  

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.update_invoice_request import UpdateInvoiceRequest
from zuora_sdk.models.update_invoice_response import UpdateInvoiceResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    request = zuora_sdk.UpdateInvoiceRequest() # UpdateInvoiceRequest | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Update an invoice
        api_response = api_instance.update_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->update_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->update_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **request** | [**UpdateInvoiceRequest**](UpdateInvoiceRequest.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**UpdateInvoiceResponse**](UpdateInvoiceResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file_for_invoice**
> UploadFileResponse upload_file_for_invoice(invoice_key, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, file=file)

Upload a file for an invoice

Uploads an externally generated invoice PDF file for an invoice that is in Draft or Posted status. To use this operation, you must enable the Modify Invoice permission. See [Billing Permissions](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/User_Roles/d_Billing_Roles) for more information. This operation has the following restrictions: - Only the PDF file format is supported. - The maximum size of the PDF file to upload is 4 MB. - A maximum of 50 PDF files can be uploaded for one invoice. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.upload_file_response import UploadFileResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice that you want to upload a PDF file for. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001. 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    file = None # bytearray | The PDF file to upload for the invoice.  (optional)

    try:
        # Upload a file for an invoice
        api_response = api_instance.upload_file_for_invoice(invoice_key, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, file=file)
        print("The response of InvoicesApi->upload_file_for_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->upload_file_for_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice that you want to upload a PDF file for. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV00000001.  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **file** | **bytearray**| The PDF file to upload for the invoice.  | [optional] 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **write_off_invoice**
> WriteOffInvoiceResponse write_off_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Write off an invoice

**Note:** This operation is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  Writes off a posted invoice.   By writing off an invoice, a credit memo is created and applied to the invoice. The generated credit memo items and credit memo taxation items are applied to invoice items and invoice taxation items based on the configured default application rule. If an invoice is written off, the balance of each invoice item and invoice taxation item must be zero.  If you set the **Create credit memos mirroring invoice items billing rule** to **Yes**, you can write off an invoice even if all its items have zero balance.  **Restrictions**: You cannot write off an invoice if any of the following restrictions is met: * The balance of an invoice has been changed before Invoice Settlement is enabled.   For example, before Invoice Settlement is enabled, any credit balance adjustments, invoice item adjustments, or invoice adjustments have been applied to an invoice. * An invoice contains more than 2,000 items in total, including invoice items, discount items, and taxation items. See [Invoice Write-off](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/IA_Invoices/Invoice_Write-Off) for more information.         

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.write_off_invoice_request import WriteOffInvoiceRequest
from zuora_sdk.models.write_off_invoice_response import WriteOffInvoiceResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.InvoicesApi(api_client)
    invoice_key = 'invoice_key_example' # str | The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001. 
    request = zuora_sdk.WriteOffInvoiceRequest() # WriteOffInvoiceRequest | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Write off an invoice
        api_response = api_instance.write_off_invoice(invoice_key, request, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of InvoicesApi->write_off_invoice:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->write_off_invoice: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_key** | **str**| The ID or number of the invoice. For example, 2c92c8955bd63cc1015bd7c151af02ab or INV-0000001.  | 
 **request** | [**WriteOffInvoiceRequest**](WriteOffInvoiceRequest.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**WriteOffInvoiceResponse**](WriteOffInvoiceResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

