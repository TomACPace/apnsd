###############################################################################
#
# Copyright 2009, Sri Panyam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

MAX_PAYLOAD_LENGTH          = 256
DEVICE_TOKEN_LENGTH         = 32

APNS_DEVICE_TOKEN_LENGTH    = DEVICE_TOKEN_LENGTH
APNS_TIMESTAMP_LENGTH       = 4
APNS_LENGTH_LENGTH          = 2
APNS_TOTAL_FEEDBACK_LENGTH  = APNS_TIMESTAMP_LENGTH + APNS_LENGTH_LENGTH + APNS_DEVICE_TOKEN_LENGTH

DEFAULT_APNS_PROD_HOST      = "gateway.push.apple.com"
DEFAULT_APNS_PROD_PORT      = 2195
DEFAULT_APNS_DEV_HOST       = "gateway.sandbox.push.apple.com"
DEFAULT_APNS_DEV_PORT       = 2195

DEFAULT_FEEDBACK_PROD_HOST  = "feedback.push.apple.com"
DEFAULT_FEEDBACK_DEV_HOST   = "feedback.sandbox.push.apple.com"
DEFAULT_FEEDBACK_PROD_PORT  = 2196
DEFAULT_FEEDBACK_DEV_PORT   = 2196

DEFAULT_C2DM_LOGIN_URL      = "https://www.google.com/accounts/ClientLogin"


APNS_ERROR_NONE                 = 0
APNS_ERROR_PROCESSING           = 1
APNS_ERROR_MISSING_TOKEN        = 2
APNS_ERROR_MISSING_TOPIC        = 3
APNS_ERROR_MISSING_PAYLOAD      = 4
APNS_ERROR_INVALID_TOKEN_SIZE   = 5
APNS_ERROR_INVALID_TOPIC_SIZE   = 6
APNS_ERROR_INVALID_PAYLOAD_SIZE = 7
APNS_ERROR_INVALID_TOKEN        = 8
APNS_ERROR_UNKNOWN              = 255

