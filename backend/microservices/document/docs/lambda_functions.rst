Lambda Functions
================

.. toctree::
   :maxdepth: 1

   lambda_functions/document_create
   lambda_functions/document_delete
   lambda_functions/document_get
   lambda_functions/document_get_all_in_workspace
   lambda_functions/document_highlight_create
   lambda_functions/document_highlight_delete
   lambda_functions/document_highlight_note
   lambda_functions/document_link_create
   lambda_functions/document_link_delete
   lambda_functions/document_rename
   lambda_functions/document_tag_add
   lambda_functions/document_tag_remove
   lambda_functions/document_update_content


Error Response
--------------

.. autopydantic_model:: app.middleware.AppErrorResponseModel

Types
^^^^^

* EventValidationUserError
* BadOperationUserError
* EntityDoesNotExistUserError
* InternalError
