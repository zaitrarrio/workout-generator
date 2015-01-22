import base64
import uuid

test_string = str(uuid.uuid4())
print test_string
encoded_test_string = base64.b64encode(test_string)
print encoded_test_string
decoded_test_string = base64.b64decode(encoded_test_string)
print decoded_test_string
print test_string == decoded_test_string
